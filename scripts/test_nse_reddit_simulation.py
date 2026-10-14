from anse.community.hf_audience_models import OllamaQwenGenerator
import logging
import sys

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)

def run_simulation():
    print("Initializing Qwen2.5-1.5b Local Engine...")
    generator = OllamaQwenGenerator()
    
    paper_title = "OpenAI NSE / Euler Physical Verification: A Physical Reading, Not a Physical Refutation"
    paper_summary = (
        "OpenAI's Lean 4 proof of finite-time blow-up for the forced 3D Navier-Stokes equations is mathematically correct. "
        "However, our thermodynamic audit shows that the physical continuum model breaks down at 0.7 nm (cavitation and viscous heating), "
        "long before the mathematical singularity. We propose a Physics-Informed Formal Proof Search (PI-FPS) layer to bound AI proofs within physical reality."
    )
    
    print("\n--- TEST 1: Title Generation ---")
    title = generator.generate_candidate_title(paper_title, "constructive_skepticism")
    print(f"Generated Title: {title}")
    
    print("\n--- TEST 2: Reply to Pure Math Skeptic ---")
    comment_1 = "But isn't the Clay millennium problem purely mathematical? Why does it matter if the water boils at 0.7 nm if the equations themselves blow up?"
    reply_1 = generator.generate_comment_reply(comment_1, paper_summary)
    print(f"Comment: {comment_1}\nReply: {reply_1}")
    
    print("\n--- TEST 3: Reply to AI Hype ---")
    comment_2 = "This is proof that AGI will solve all of physics in the next 5 years. Human physicists are obsolete."
    reply_2 = generator.generate_comment_reply(comment_2, paper_summary)
    print(f"Comment: {comment_2}\nReply: {reply_2}")

if __name__ == "__main__":
    run_simulation()
