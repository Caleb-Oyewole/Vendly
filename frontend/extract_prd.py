import sys, subprocess

SRC = r"C:\Users\USER\Downloads\Vendly_Frontend_Spec (1).pdf"
OUT = r"C:\Users\USER\frontend\prd.txt"


def ensure(mod, pkg=None):
    try:
        return __import__(mod)
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", pkg or mod], check=True)
        return __import__(mod)


pypdf = ensure("pypdf")
reader = pypdf.PdfReader(SRC)
parts = []
for i, page in enumerate(reader.pages, 1):
    parts.append(f"\n===== PAGE {i} =====\n")
    parts.append(page.extract_text() or "")
text = "".join(parts)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(text)
print(f"pages={len(reader.pages)} chars={len(text)} -> {OUT}")
