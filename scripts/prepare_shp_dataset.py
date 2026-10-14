import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datasets import load_dataset

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CACHE_DIR = "/media/xavkal/3ada43de-fc4a-43bd-a9f8-cf396fd17033/home/xavkal/hf_cache"
OUTPUT_PATH = "/home/xavkal/xdev/AutoevolveAI/results/dpo_scientific_dissemination.jsonl"
TARGET_SUBREDDITS = {
    "askscience",
    "askphysics",
    "askacademia",
    "askengineers",
    "MachineLearning",
    "math",
    "physics"
}

def process_row(row: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Process a single row from SHP dataset."""
    domain_raw = row.get("domain", "")
    domain_clean = domain_raw.split("_")[0]
    
    if domain_clean not in TARGET_SUBREDDITS:
        return None
        
    prompt = row.get("history", "")
    label = row.get("labels")
    
    if label == 1:
        chosen = row.get("human_ref_A", "")
        rejected = row.get("human_ref_B", "")
    else:
        chosen = row.get("human_ref_B", "")
        rejected = row.get("human_ref_A", "")
        
    return {
        "prompt": prompt,
        "chosen": chosen,
        "rejected": rejected,
        "subreddit": domain_clean
    }

def main() -> None:
    """Main pipeline execution."""
    logger.info("Loading SHP dataset into secondary disk cache...")
    try:
        ds = load_dataset("stanfordnlp/shp", cache_dir=CACHE_DIR, split="train")
    except Exception as e:
        logger.error(f"Failed to load dataset: {e}")
        return

    logger.info(f"Loaded {len(ds)} records. Filtering for STEM subreddits...")
    Path(OUTPUT_PATH).parent.mkdir(parents=True, exist_ok=True)
    
    processed_count = 0
    try:
        with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
            for row in ds:
                record = process_row(row)
                if record:
                    f.write(json.dumps(record) + "\n")
                    processed_count += 1
                    
        logger.info(f"Saved {processed_count} DPO pairs to {OUTPUT_PATH}")
    except Exception as e:
        logger.error(f"Error during processing: {e}")

if __name__ == "__main__":
    main()
