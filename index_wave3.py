import sys
import os

sys.path.insert(0, os.path.abspath("."))
from anse.memory.chroma_rag import ChromaRAG

def main():
    rag = ChromaRAG(persist_directory=".chroma_db")
    
    code = """
static ESP6_HANDLERS: SyncWrapper<AtomicPtr<xfrm6_protocol>> = SyncWrapper::new(AtomicPtr::new(ptr::null_mut()));

// Accessing it
let mut handler = (*ESP6_HANDLERS.get_mut()).load(Ordering::Acquire);
"""

    prompt = """
How to safely expose a mutable global static variable that contains an `AtomicPtr` without triggering the Rust `static_mut` lint?
"""
    
    rag.index_code_solution(
        doc_id="wave3_sync_wrapper_atomicptr",
        code_content=code,
        task_prompt=prompt,
        language="rust",
        energy=0.0,
        metadata={"wave": "3", "concept": "SyncWrapper around AtomicPtr"}
    )
    print("Successfully indexed Wave 3 solution into ChromaDB LTM.")

if __name__ == "__main__":
    main()
