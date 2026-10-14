from datasets import load_dataset
ds = load_dataset("stanfordnlp/shp", cache_dir="/media/xavkal/3ada43de-fc4a-43bd-a9f8-cf396fd17033/home/xavkal/hf_cache", split="train", streaming=True)
domains = set()
for i, row in enumerate(ds):
    domains.add(row.get('domain', '').split('_')[0])
    if i > 10000:  # just check the first 10k to see if it covers a lot, actually streaming might be sorted. Let's not stream, or just stream entirely.
        pass

print("Sample domains:", domains)
