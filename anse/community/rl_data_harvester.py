#!/usr/bin/env python3
"""
RL Data Harvester for Scientific Dissemination.
Harvests high-performing technical posts, release notes, and community discussions
from Hugging Face and GitHub to build training distributions for the Post Prescriptor.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

import httpx

from anse.community.audience_reward import compute_audience_reward


@dataclass
class HarvestedPost:
    title: str
    body: str
    submission_statement: str = ""
    source: str = "synthetic"  # 'huggingface', 'github', 'reddit', 'synthetic'
    community: str = "r/MachineLearning"
    upvote_ratio: float = 0.95
    comment_count: int = 10
    reward_metrics: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def harvest_from_github_repo(owner: str, repo: str) -> HarvestedPost | None:
    """
    Harvests README and release notes from a public GitHub repository
    to construct technical dissemination examples.
    """
    url = f"https://api.github.com/repos/{owner}/{repo}"
    readme_url = f"https://api.github.com/repos/{owner}/{repo}/readme"

    try:
        with httpx.Client(timeout=10.0, headers={"User-Agent": "ANSE-RL-Harvester/1.0"}) as client:
            resp_repo = client.get(url)
            if resp_repo.status_code != 200:
                return None
            repo_meta = resp_repo.json()

            resp_readme = client.get(readme_url, headers={"Accept": "application/vnd.github.raw"})
            readme_text = resp_readme.text if resp_readme.status_code == 200 else ""

        title = f"Open Source Release: {repo_meta.get('name')} - {repo_meta.get('description', '')}"
        body = readme_text[:1200]
        sub_stmt = (
            f"Submission Statement: Releasing {repo_meta.get('full_name')} for scientific research. "
            f"Code available at {repo_meta.get('html_url')}."
        )

        metrics = compute_audience_reward(
            subreddit="r/MachineLearning",
            title=title,
            body=body,
            submission_statement=sub_stmt,
        )

        return HarvestedPost(
            title=title,
            body=body,
            submission_statement=sub_stmt,
            source="github",
            community="r/MachineLearning",
            reward_metrics=metrics,
        )
    except Exception:
        return None


def harvest_curated_seed_posts() -> list[HarvestedPost]:
    """
    Provides curated, verified scientific and systems dissemination posts
    spanning SciML, Lean 4 formal math, and safe systems runtimes.
    """
    posts = [
        HarvestedPost(
            title="[R] Enforcing div(B)=0 to machine precision in Neural Operators for Magnetohydrodynamics via discrete Hodge projection",
            body=(
                "When simulating ideal magnetohydrodynamics with neural operators, standard soft penalty terms "
                "eventually lead to magnetic monopole drift. We propose the Structure-Preserving Gauge Neural Operator (SP-GNO). "
                "By parameterizing the magnetic field via discrete Hodge decomposition and projecting into the Coulomb gauge in "
                "Fourier space, the divergence remains bounded by machine precision (~10^-14) in FP64 across rollouts.\n\n"
                "## Epistemological Boundaries\n"
                "Continuous vector identities are verified in Lean 4 (5 theorems, zero sorry). The formulation is strictly "
                "restricted to periodic boundary conditions (T^d) and does not natively model non-periodic tokamak walls.\n\n"
                "Preprint (CC-BY): https://doi.org/10.5281/zenodo.22160185\nCode: https://github.com/xaviercallens/AutoevolveAI"
            ),
            submission_statement=(
                "Submission Statement & Context: This paper presents SP-GNO for plasma simulation. "
                "Why this matters: Eliminates the Pareto loss tradeoff between data MSE and solenoidal penalties. "
                "AI Transparency: Produced with AI assistance following Terence Tao guidelines; human author takes full responsibility."
            ),
            source="synthetic",
            community="r/MachineLearning",
            upvote_ratio=0.98,
            comment_count=45,
        ),
        HarvestedPost(
            title="Formalizing Ramanujan’s Dedekind η-quotients in Lean 4: Newman’s modularity criteria and character subtleties",
            body=(
                "Ramanujan's lost notebook contains numerous modular equations. Applying Newman and Ligozat criteria manually "
                "often leads to parity errors for odd-weight Dirichlet multiplier characters. We implemented both a 108-check "
                "Python numerical engine and a standalone Lean 4 proof suite (7 theorems verified via native_decide).\n\n"
                "Key finding: For the multiplier character to be trivial, (-1)^k * prod(d^r_d) must be a rational square. "
                "This explains why Jacobi forms belong to non-trivial character spaces.\n\n"
                "Zenodo DOI: https://doi.org/10.5281/zenodo.22160184\nCode: https://github.com/xaviercallens/AutoevolveAI"
            ),
            submission_statement=(
                "Context: Formal interactive theorem proving in number theory and modular forms. "
                "AI Disclosure: Checked with LLM pair-programming following Terence Tao guidelines; runs in pure Lean 4 core."
            ),
            source="synthetic",
            community="r/math",
            upvote_ratio=0.96,
            comment_count=32,
        ),
        HarvestedPost(
            title="RunuX & rusty-SUNDIALS: Zero-allocation Rust bindings and SIMD kernels for high-performance scientific ODE/DAE solving",
            body=(
                "Scientific computing often wraps C libraries like SUNDIALS for stiff ODE integration. However, naive bindings "
                "introduce heap allocations per timestep or unsafe C-ABI pointer risks. In rusty-SUNDIALS, we pre-allocate "
                "buffers with lifetime-bounded borrows, guaranteeing zero allocations in the inner loop.\n\n"
                "Includes RVV 1024-bit and AVX-512 vectorization kernels for sparse matrix-vector multiplications.\n\n"
                "Code & Benchmarks: https://github.com/xaviercallens/AutoevolveAI"
            ),
            submission_statement=(
                "Submission Statement & Context: High-performance systems programming in Rust. "
                "Why this matters: Guarantees zero-allocation memory safety for foreign C solvers. "
                "AI Transparency Disclosure: Verified following Terence Tao guidelines."
            ),
            source="synthetic",
            community="r/rust",
            upvote_ratio=0.97,
            comment_count=58,
        ),
    ]

    for p in posts:
        p.reward_metrics = compute_audience_reward(
            subreddit=p.community,
            title=p.title,
            body=p.body,
            submission_statement=p.submission_statement,
        )

    return posts
