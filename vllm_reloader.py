#!/usr/bin/env python3
"""
vLLM Runtime LoRA Hot-Reloader:
Interacts with vLLM's dynamic adapter endpoints to swap weights without downtime.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import httpx


def unload_vllm_adapter(client: httpx.Client, adapter_name: str) -> bool:
    """Attempts to evict an active LoRA adapter from vLLM memory."""
    print(f"🔄 Unloading prior adapter alias '{adapter_name}'...")
    try:
        resp = client.post(
            "/v1/unload_lora_adapter",
            json={"lora_name": adapter_name},
        )
        if resp.status_code == 200:
            print(f"✅ Successfully evicted old '{adapter_name}' from vLLM memory.")
            return True
        print(f"Notice: Unload returned status {resp.status_code}. Proceeding to mount.")
        return False
    except Exception as err:
        print(f"Notice: Unload request skipped or unreachable ({err}). Proceeding to mount.")
        return False


def load_vllm_adapter(client: httpx.Client, adapter_name: str, adapter_path: Path) -> bool:
    """Mounts a newly trained LoRA adapter checkpoint into vLLM runtime."""
    resolved_path = str(adapter_path.resolve())
    print(f"🚀 Loading new adapter '{adapter_name}' from {resolved_path}...")
    try:
        resp = client.post(
            "/v1/load_lora_adapter",
            json={
                "lora_name": adapter_name,
                "lora_path": resolved_path,
            },
        )
        if resp.status_code == 200:
            print(f"✅ vLLM hot-reload succeeded: '{adapter_name}' is active.")
            return True
        print(f"❌ Failed to load LoRA into vLLM: {resp.status_code} - {resp.text}")
        return False
    except Exception as err:
        print(f"❌ Exception connecting to vLLM load endpoint: {err}")
        return False


def hot_reload_vllm_adapter(
    adapter_name: str,
    adapter_path: Path,
    vllm_base_url: str = "http://localhost:8000",
    client: httpx.Client | None = None,
) -> bool:
    """Zero-downtime adapter swap: unloads existing adapter and loads the updated version."""
    if client is not None:
        unload_vllm_adapter(client, adapter_name)
        return load_vllm_adapter(client, adapter_name, adapter_path)

    with httpx.Client(base_url=vllm_base_url, timeout=30.0) as managed_client:
        unload_vllm_adapter(managed_client, adapter_name)
        return load_vllm_adapter(managed_client, adapter_name, adapter_path)


def main() -> None:
    """CLI Entrypoint for manual vLLM hot-reloading."""
    parser = argparse.ArgumentParser(description="Hot-reload LoRA adapter into running vLLM")
    parser.add_argument("--name", default="antigravity-local", help="LoRA adapter alias name")
    parser.add_argument("--path", required=True, help="Path to adapter checkpoint directory")
    parser.add_argument("--url", default="http://localhost:8000", help="vLLM base URL")
    args = parser.parse_args()

    success = hot_reload_vllm_adapter(
        adapter_name=args.name,
        adapter_path=Path(args.path),
        vllm_base_url=args.url,
    )
    if success:
        print("🎯 Hot-reload completed successfully.")
    else:
        print("⚠️ Hot-reload failed.")


__all__ = [
    "unload_vllm_adapter",
    "load_vllm_adapter",
    "hot_reload_vllm_adapter",
    "main",
]


if __name__ == "__main__":
    main()
