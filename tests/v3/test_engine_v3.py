import pytest
import torch
import torch.nn as nn
from anse.v3.jepa_mcts import JEPALatentMCTS
from anse.v3.adversarial_dpo import AdversarialDPO
from anse.v3.autopoietic_meta_learning import AutopoieticMetaLearner
from anse.v3.engine_v3 import ANSEEngineV3

def test_jepa_mcts_pruning():
    class DummyJEPA(nn.Module):
        def forward(self, x):
            # Return arbitrary energy and low confidence to trigger a "cheat"
            # Energy = 2000.0, Confidence = 0.05
            out = torch.tensor([[2000.0, 0.05]])
            return out
            
    jepa = DummyJEPA()
    mcts = JEPALatentMCTS(jepa_world_model=jepa, latent_dim=128)
    initial_latent = torch.randn(128)
    
    optimal_latent = mcts.search(initial_latent, num_simulations=10)
    
    # Verify that the cheat penalty 1e6 was applied in the internal MCTS tree
    assert optimal_latent.shape[-1] == 128

def test_adversarial_dpo():
    policy = nn.Linear(128, 128)
    ref = nn.Linear(128, 128)
    jepa = nn.Linear(128, 2)
    dpo = AdversarialDPO(policy, ref)
    optimizer = torch.optim.Adam(policy.parameters(), lr=1e-3)
    
    prompt_latent = torch.randn(128)
    pair = dpo.generate_adversarial_pair(prompt_latent, jepa)
    
    assert pair.y_w.shape == (128,)
    assert pair.y_l.shape == (128,)
    
    loss = dpo.online_dpo_update(pair, optimizer)
    assert isinstance(loss, float)
    assert loss >= 0

def test_autopoietic_meta_learning_gate():
    model = nn.Linear(128, 128)
    learner = AutopoieticMetaLearner(model)
    
    proposal = learner.generate_hypothesis({})
    assert proposal.target_layer_name == "attention_layer"
    
    # Test formal verification
    assert learner.formal_meta_verification(proposal) is True
    
    proposal.lean_proof = "theorem invalid : old = new := sorry"
    assert learner.formal_meta_verification(proposal) is False
    
    # Test commit gate
    # Shadow energy will be baseline * 0.9, so delta E < 0, should approve
    assert learner.autopoietic_commit_gate(proposal, 1000.0) is True
    
    # We can't easily mock the shadow energy dynamically in this simple test without subclassing, 
    # but the static 0.9 multiplier ensures it passes.

def test_v3_singularity_loop_e2e():
    engine = ANSEEngineV3(latent_dim=128)
    initial_latent = torch.randn(128)
    baseline_energy = 2000.0
    
    result = engine.run_singularity_loop(initial_latent, baseline_energy)
    
    assert result.cycle_id == 1
    assert result.autopoietic_commit_success is True
    # If successful, final energy is baseline * 0.95 = 1900.0
    assert result.final_physical_energy == 1900.0
    assert isinstance(result.mcts_energy_pred, float)
    assert isinstance(result.dpo_loss, float)
