import importlib
for m in ["fitz", "pdfplumber", "pypdf", "pysat", "pycosat", "pdfminer"]:
    try:
        importlib.import_module(m)
        print(m, "ok")
    except Exception as e:
        print(m, "NO", e)
