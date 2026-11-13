import sys
import os

# Add local path to sys.path
sys.path.insert(0, os.path.abspath("."))
from anse.memory.chroma_rag import ChromaRAG

def main():
    rag = ChromaRAG(persist_directory=".chroma_db")
    
    code = """
#[repr(transparent)]
pub struct SyncWrapper<T>(pub core::cell::UnsafeCell<T>);

unsafe impl<T> Sync for SyncWrapper<T> {}

impl<T> SyncWrapper<T> {
    pub const fn new(value: T) -> Self {
        Self(core::cell::UnsafeCell::new(value))
    }
    #[inline(always)]
    pub unsafe fn get_mut(&self) -> &mut T {
        // SAFETY: The caller must guarantee exclusive access or single-threaded context.
        // For FFI globals, the kernel handles external synchronization.
        unsafe { &mut *self.0.get() }
    }
}
"""

    prompt = """
How to safely expose a mutable global static variable (C-ABI extern "C") without triggering the Rust `static_mut` lint in the 2024 edition, while guaranteeing memory safety in a single-threaded or externally locked kernel module initialization context?
"""
    
    rag.index_code_solution(
        doc_id="wave2_sync_wrapper_ffi",
        code_content=code,
        task_prompt=prompt,
        language="rust",
        energy=0.0,
        metadata={"wave": "2", "concept": "static_mut replacement for C-ABI"}
    )
    print("Successfully indexed Wave 2 solution into ChromaDB LTM.")

if __name__ == "__main__":
    main()
