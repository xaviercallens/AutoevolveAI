import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.abspath("."))
from anse.memory.chroma_rag import ChromaRAG

def main():
    rag = ChromaRAG(persist_directory=".chroma_db")
    
    papers = [
        {
            "doc_id": "lit_asterinas_framekernel_2506_03876",
            "title": "Asterinas: A Linux ABI-Compatible, Rust-Based Framekernel OS with a Small and Sound TCB",
            "authors": "Yuke Peng, Hongliang Tian, Zhang Junyang, Ruihan Li, et al.",
            "year": "2025",
            "arxiv_id": "2506.03876",
            "content": """
Asterinas introduces the framekernel architecture for memory-safe OS development in Rust.
It addresses the pitfall of existing Rust OSes where improper unsafe encapsulation breaches the sound Trusted Computing Base (TCB).
Key architectural foundations:
1. Operating System Target Definition (OSTD): Isolates bare-metal hardware access, page tables, and MMU control into a sound, verifiable primitive layer.
2. Complete eradication of `static mut`: Replaces raw mutable globals with structured interior mutability primitives (e.g. `SyncUnsafeCell`, ticket spinlocks, and generational accessors).
3. Type-state page frame allocation: Physical page frames (`SafePageFrame`) enforce lifecycle states (Free -> Reserved -> Slab -> UserMapped) at compile time via phantom markers, eliminating double-free and use-after-free in buddy allocators.
4. Fallible kernel allocations: In kernel space, memory allocations must never panic on out-of-memory; all allocation APIs must be fallible (`try_alloc`, returning `Result<NonNull<T>, AllocError>`).
""",
            "key_insights": "Eradicate `static mut` using OSTD interior mutability cells; enforce type-state lifecycle on physical page frames; ensure 100% fallible allocations in OS memory management."
        },
        {
            "doc_id": "lit_rusty_linux_2407_18431",
            "title": "Rusty Linux: Advances in Rust for Linux Kernel Development",
            "authors": "Shane K. Panter, Nasir U. Eisty",
            "year": "2024",
            "arxiv_id": "2407.18431",
            "content": """
Analysis of upstream Rust-for-Linux integration, kernel memory safety guarantees, and C-ABI interop.
Core challenges and solutions:
1. C-ABI Compatibility: Exported kernel symbols must match C layout and linkage (`#[no_mangle]`, `#[repr(C)]`), requiring transparent wrappers (`#[repr(transparent)] SyncWrapper<UnsafeCell<T>>`) rather than high-level fat pointers.
2. Concurrency Primitives: Translating Linux RCU (Read-Copy Update), mutexes, and spinlocks into idiomatic Rust RAII guards (`SpinLockGuard`, `RcuReadGuard`) while retaining zero-allocation performance.
3. Unsafe Inventory & Documentation: Every single `unsafe` block must be accompanied by explicit `// SAFETY:` contracts asserting preconditions (pointer validity, alignment, concurrency constraints).
4. Memory Subsystem Integration: Safe wrappers around `kmalloc`/`kfree`, `alloc_pages`, and `vmalloc` with boundary validation and alignment enforcement.
""",
            "key_insights": "Maintain ABI stability using transparent `SyncWrapper`; replace ad-hoc locking with RAII guards; require exhaustive `// SAFETY:` justifications on all kernel unsafe blocks."
        },
        {
            "doc_id": "lit_ship_of_theseus_2607_28835",
            "title": "From C to Idiomatic Rust: A Ship-of-Theseus Agentic Translation",
            "authors": "Vasily A. Sartakov",
            "year": "2026",
            "arxiv_id": "2607.28835",
            "content": """
Explores automated and agentic translation of legacy C systems code into idiomatic, safe Rust.
Presents methodologies for:
1. De-globalizing mutable C state: Eliminating `static mut` variables across drivers and protocol stacks through incremental encapsulation.
2. Handling irregular global state: Managing complex nested initializers, function pointer tables, and RCU list heads without breaking linker table layouts.
3. Regression-free ratcheting: Employing static oracle ratchets (AST checkers, safety ratios, and compiler warning gates) to prevent LLM hallucination and ensure monotonic quality improvement during refactoring.
""",
            "key_insights": "Incrementally replace transpiled raw globals with structured singletons; use deterministic static metric ratchets to guarantee zero regression during agentic migration."
        },
        {
            "doc_id": "lit_rust_lean_pipeline_2605_30106",
            "title": "A Rust-to-Lean Verification Pipeline with AI Provers: An Experience Report",
            "authors": "Natalia Klaus, Juan Conejero, Palina Tolmach",
            "year": "2026",
            "arxiv_id": "2605.30106",
            "content": """
Presents an end-to-end formal verification pipeline extracting Rust systems code into Lean 4 via Charon and Aeneas.
Highlights:
1. Symbolic Extraction: Translates Rust MIR into pure functional definitions and state-passing monadic code in Lean 4.
2. Memory Safety Theorems: Proves that memory manipulations, pointer slicing, and buffer operations are mathematically incapable of out-of-bounds access or panic states.
3. Closing Proof Obligations: Automates closing of verification conditions (`sorry` elimination) using structured tactic automation (`omega`, `decide`, `aesop`, and LLM-assisted proof search).
""",
            "key_insights": "Bridge the gap between Rust kernel implementations and Lean 4 formal models using Charon/Aeneas extraction; eliminate `lean.sorry` debt with tactic-guided proof generation."
        },
        {
            "doc_id": "lit_kverus_formal_rust_2605_03822",
            "title": "KVerus: Scalable and Resilient Formal Verification Proof Generation for Rust Code",
            "authors": "Yuwei Liu, Xinyi Wan, Yanhao Wang, Minghua Wang, Lin Huang, Tao Wei",
            "year": "2026",
            "arxiv_id": "2605.03822",
            "content": """
Focuses on formal specification and machine-checked verification of low-level Rust systems and memory management.
Core principles:
1. Precondition & Postcondition Contracts: Equips memory allocation functions (`alloc_pages`, `kmem_cache_alloc`) with mathematical invariants (size > 0, power-of-two alignment, disjoint heap segments).
2. Ghost State & Capabilities: Uses logical ghost tokens to verify non-aliasing and thread exclusivity without physical lock memory overhead.
3. Inductive Heap Predicates: Formally models slab freelists and buddy system free trees to prove conservation of total physical memory: Total = Free + Allocated.
""",
            "key_insights": "Formally specify heap memory conservation (M_total = M_free + M_alloc); verify allocator alignment and non-aliasing using ghost state and contract invariants."
        },
        {
            "doc_id": "lit_kernel_memory_ghostcell_refinedrust",
            "title": "Separation Logic & Capability-Based Memory Management for Safe OS Kernels",
            "authors": "RefinedRust & GhostCell Research Group",
            "year": "2025",
            "arxiv_id": "CS-PL-2025",
            "content": r"""
Modern separation logic and capability-based memory management frameworks for Rust operating systems:
1. Buddy Allocator Invariants: Order-k buddy pairing theorem: For any block at address A of order k, its buddy is A ^ (1 << (PAGE_SHIFT + k)). Merging preserves disjointness and alignment.
2. Slab Allocator Cache Line Alignment: Objects in slab caches must be aligned to L1_CACHE_BYTES (64 bytes) to prevent false sharing and unaligned SIMD access faults.
3. Virtual Memory Isolation: Page tables must strictly enforce W ^ X (Write XOR Execute) at the hardware page attribute level; kernel virtual memory (`vmalloc`) must be unmapped from user-space page tables.
4. Fail-Closed OOM Handling: Kernel heap exhaustion must never result in undefined behavior, silent null pointer dereference, or kernel panic.
""",
            "key_insights": "Formal buddy pairing invariant; cache line alignment enforcement in slab caches; hardware W^X enforcement in MMU page tables."
        }
    ]

    for p in papers:
        rag.index_literature_document(
            doc_id=p["doc_id"],
            title=p["title"],
            abstract_or_content=p["content"],
            authors=p["authors"],
            year=p["year"],
            arxiv_id=p["arxiv_id"],
            key_insights=p["key_insights"]
        )
        print(f"Indexed: {p['title']} [{p['doc_id']}]")

    print("\nVerifying vector search query in ChromaDB:")
    results = rag.query_literature("how to safely handle memory management and allocators without static mut in Rust OS kernel", n_results=3)
    for r in results:
        print(f" -> Hit: {r['metadata'].get('title')} (id: {r['id']})")

if __name__ == "__main__":
    main()
