# Guide Opérationnel : Mini-RL Hybride (Train-Remote / Infer-Local)

Ce guide décrit l'architecture et la procédure complète pour déployer et opérer le **Mini-RL (auto-amélioration continue)** au sein de l'écosystème Antigravity / SuperGravity / ANSE, optimisé pour une machine hôte Linux avec 32 Go de RAM et sans GPU récent.

---

## Architecture : Le Modèle Train-Remote / Infer-Local

```text
  [ Machine Développeur (Linux 32 Go RAM / CPU) ]          [ RunPod Disposable GPU (~0.30$/h) ]
 ──────────────────────────────────────────────────       ─────────────────────────────────────────
  1. Télémétrie IDE / Traces Redis                        3. Entraînement DPO ultra-rapide
     (Code généré A vs Code corrigé A')                      - Base: Qwen/Qwen2.5-Coder-3B (ou 7B)
     (Distance Levenshtein + Preuves Lean 4)                 - Unsloth (2x speed, -60% VRAM)
                            │                                        │
                            ▼ (export JSONL)                         ▼
                     [ Dataset DPO ] ────────────────────────► [ Entraînement LoRA ]
                                                                     │
                                                                     ▼
  5. Inférence 100% Locale (Ollama / CPU) ◄─────────────────── [ Export GGUF Q4_K_M ]
     - Modelfile: anse/guard/modelfiles/Modelfile.ag-critic      (Taille: ~2.2 Go)
     - Temps de réponse: 15 à 30 tokens/s sur CPU
     - Filtrage instantané pré-exécution (< 50 ms)
```

---

## Phase 1 : Datasets Hugging Face Recommandés

1. **Anti-Stub / Anti-Triche (Gardien)** :
   - 🏆 **`Vezora/Code-Preference-Pairs`** : Paires `(chosen, rejected)` éliminant les stubs (`pass`, `// TODO`), les implémentations naïves et les failles de complexité.
2. **Revue de Code Approfondie** :
   - 🛡️ **`alenphilip/Code-Review-Assistant`** : 13k+ exemples axés sur les vulnérabilités, la performance et le code idiomatique.
3. **Prouveur Formel Lean 4** :
   - 📐 **`yuanhezhang/lean4-stat-learning-theory-random`** : Traces tactiques de preuves Lean 4 validées formellement.

---

## Phase 2 : Modèle et Empreinte Locale (32 Go RAM sans GPU)

* **Modèle de Référence** : `unsloth/Qwen2.5-Coder-3B` (ou `Qwen2.5-Coder-7B`)
* **Format** : Binaire quantifié GGUF 4-bit (`Q4_K_M`)
* **Empreinte Mémoire** : ~2.2 Go de RAM (3B) ou ~4.5 Go de RAM (7B).
* **Vitesse CPU** : 15 à 30 tokens/seconde sur processeur moderne, parfaitement fluide pour un critic de validation.

---

## Phase 3 : Entraînement Low-Cost sur RunPod (Budget : ~0.30$)

Le script clé en main est disponible dans le repo : [`scripts/train_dpo_critic.py`](file:///home/xavkal/xdev/AutoevolveAI/scripts/train_dpo_critic.py).

### Commandes sur l'instance RunPod (RTX 3090 / 4000 Ada) :

```bash
# 1. Installation des dépendances optimisées Unsloth
pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"
pip install trl peft accelerate bitsandbytes datasets

# 2. Lancement du fine-tuning DPO et export GGUF direct
python scripts/train_dpo_critic.py \
  --model_name "unsloth/Qwen2.5-Coder-3B" \
  --dataset_name "Vezora/Code-Preference-Pairs" \
  --max_steps 200 \
  --learning_rate 5e-6 \
  --export_gguf_name "antigravity-critic-3b" \
  --quantization "q4_k_m"
```

Une fois le fichier `antigravity-critic-3b.Q4_K_M.gguf` généré, le rapatrier sur la machine locale et **détruire l'instance RunPod**.

---

## Phase 4 : Inférence 100% Locale sur Linux (CPU / RAM)

### 1. Installation d'Ollama
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### 2. Création de l'Agent Gardien Local
À l'emplacement du fichier GGUF téléchargé :
```bash
ollama create ag-critic -f anse/guard/modelfiles/Modelfile.ag-critic
```

### 3. Test de validation immédiat
```bash
ollama run ag-critic "Évalue ce code: def fetch_data(): return None # TODO"
```
Sortie attendue :
```json
{"status": "REJECT", "reason": "Présence d'un return None en dur et d'un marqueur TODO. Le code est incomplet."}
```

---

## Phase 5 : Intégration Automatisée dans le Gateway & Swarm

Le module [`anse/guard/critic.py`](file:///home/xavkal/xdev/AutoevolveAI/anse/guard/critic.py) interroge directement Ollama via HTTP (`http://localhost:11434/api/generate`).

Dans [`gateway.py`](file:///home/xavkal/xdev/AutoevolveAI/gateway.py) :
- Activer l'interception systématique :
  ```bash
  export ANSE_GATEWAY_CRITIC_ENABLED=true
  export ANSE_CRITIC_URL="http://localhost:11434"
  export ANSE_CRITIC_MODEL="ag-critic"
  ```
- Tout code généré par Gemini Ultra est inspecté en $< 50\text{ ms}$. S'il est rejeté, l'erreur est renvoyée à Gemini sans déclencher de calcul lourd dans le bac à sable ou le compilateur Lean 4.
