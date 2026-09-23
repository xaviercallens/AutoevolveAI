# ANSE Red Team & Test-Time Compute Specification

## 1. Reproduction du "Test-Time Compute" (MCTS, PRM & GRPO)
Pour que l'agent Red Team ne réponde pas d'un coup, mais déploie un arbre de réflexion (Monte Carlo Tree Search) et apprenne par renforcement via l'algorithme GRPO.

* **[huggingface/open-r1](https://github.com/huggingface/open-r1)** : Projet phare pour reproduire le pipeline d'entraînement "Deep Think" en open source. Les scripts serviront pour entraîner des modèles locaux avec GRPO en utilisant les scores d'énergie physique ($E$) comme fonction de récompense pure.
* **[queelius/mcts-reasoning](https://github.com/queelius/mcts-reasoning) (ou [NumberChiffre/mcts-llm](https://github.com/NumberChiffre/mcts-llm))** : Implémentation de MCTS par-dessus les LLMs. Permet d'injecter un "Juge d'étapes" (Process Evaluator). Si l'étape valide une aberration physique, la branche est élaguée (backtrack).
* **[RyanLiu112/Awesome-Process-Reward-Models](https://github.com/RyanLiu112/Awesome-Process-Reward-Models)** : Modèles PRM (Process Reward Models) pour noter la rigueur mathématique de chaque ligne.

## 2. L'Interface Neuro-Symbolique (Pont Python ↔ Lean 4)
Pour inspecter l'arbre formel et détecter les "Junk Values" et vérifier les axiomes cachés.

* **[lean-dojo/LeanDojo](https://github.com/lean-dojo/LeanDojo)** : Infrastructure pour l'IA dans Lean 4. Transforme le compilateur en un Gym Environment pour Python. La Red Team extrait l'AST de Lean, lit l'état de la preuve étape par étape, et détecte les failles.
* **[Paper-Proof/paperproof](https://github.com/Paper-Proof/paperproof)** : Rend visuellement l'arbre de déduction des preuves Lean 4 (idéal pour le Command Deck).

## 3. Orchestration & Serveurs MCP (Le Système Nerveux)
Pour coordonner l'Agent Coder, l'Agent Lean, et l'Auditeur Red Team.

* **[langchain-ai/langgraph](https://github.com/langchain-ai/langgraph)** : Création de flux agentiques cycliques. Mémorise dans Redis. Boucle: Coder -> Sandbox Physique -> Red Team -> [Si Rejet, boucle au Coder].
* **[modelcontextprotocol/python-sdk](https://github.com/modelcontextprotocol/python-sdk) & [jlowin/fastmcp](https://github.com/jlowin/fastmcp)** : Transforme la Sandbox d'exécution d'énergie et le compilateur Lean en Serveurs MCP.

## 4. Fuzzing & Anti-Hallucination Physique (Hardness)
Pour empêcher les "tautologies numériques" identifiées lors de l'audit.

* **[HypothesisWorks/hypothesis](https://github.com/HypothesisWorks/hypothesis)** : Property-Based Testing en Python. Fuzze le code en injectant des singularités extrêmes (infinis, zéros, valeurs subnormales).
* **[boxed/mutmut](https://github.com/boxed/mutmut)** : Mutation Testing. Modifie secrètement le code pour tester la robustesse des tests. Déclenche le Penalty Wall ($E=10^6$) si le test passe à tort.

## 5. Inférence Locale (Contraintes 32 Go RAM CPU/petit GPU)
* **[ollama/ollama](https://github.com/ollama/ollama)** : Inférence C++ (Llama.cpp) pour déployer des LLMs en local (ex: deepseek-r1:14b ou qwen2.5-coder:14b).
* **[unslothai/unsloth](https://github.com/unslothai/unsloth)** : Optimisation d'entraînement (Fine-tuning). Utilisé pour entraîner le modèle sur Runpod/GPU local avec 2x plus de rapidité et 60% de VRAM en moins.
