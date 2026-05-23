"""
Parse manually curated markdown immigration briefs into structured docs
for the embedding pipeline. Each H3 section becomes one document.
"""

from pathlib import Path
from datetime import datetime

MANUAL_DOCS_DIR = Path(__file__).parent / "manual_docs"

COUNTRY_MAP = {
    "singapore": "SG",
    "netherlands": "NL",
    "canada": "CA",
    "united kingdom": "GB",
    "germany": "DE",
    "australia": "AU",
    "ireland": "IE",
    "uae": "AE",
    "new zealand": "NZ",
    "portugal": "PT",
}


def parse_md_to_docs(md_path: Path) -> list[dict]:
    """
    Parse a markdown file into structured docs.
    Each H3 section (###) becomes one document.
    Country is inferred from the parent H2 section.
    """
    text = md_path.read_text(encoding="utf-8")
    lines = text.split("\n")

    docs = []
    current_country = None
    current_visa_type = None
    current_lines = []

    for line in lines:
        if line.startswith("## "):
            # Save previous section
            if current_country and current_visa_type and current_lines:
                content = "\n".join(current_lines).strip()
                if len(content) > 100:
                    docs.append({
                        "country_code": current_country,
                        "visa_type": current_visa_type,
                        "content": content,
                        "source_url": f"manual:{md_path.name}",
                        "scraped_at": datetime.now().isoformat(),
                    })
            # Detect country from H2
            heading = line.lstrip("# ").strip().lower()
            current_country = None
            for key, code in COUNTRY_MAP.items():
                if key in heading:
                    current_country = code
                    break
            current_visa_type = None
            current_lines = []

        elif line.startswith("### "):
            # Save previous section
            if current_country and current_visa_type and current_lines:
                content = "\n".join(current_lines).strip()
                if len(content) > 100:
                    docs.append({
                        "country_code": current_country,
                        "visa_type": current_visa_type,
                        "content": content,
                        "source_url": f"manual:{md_path.name}",
                        "scraped_at": datetime.now().isoformat(),
                    })
            current_visa_type = line.lstrip("# ").strip()
            current_lines = []

        else:
            if current_country and current_visa_type:
                current_lines.append(line)

    # Save last section
    if current_country and current_visa_type and current_lines:
        content = "\n".join(current_lines).strip()
        if len(content) > 100:
            docs.append({
                "country_code": current_country,
                "visa_type": current_visa_type,
                "content": content,
                "source_url": f"manual:{md_path.name}",
                "scraped_at": datetime.now().isoformat(),
            })

    return docs


def load_manual_md_docs() -> list[dict]:
    docs = []
    for md_path in MANUAL_DOCS_DIR.glob("*.md"):
        file_docs = parse_md_to_docs(md_path)
        for d in file_docs:
            print(f"  [OK] {d['country_code']} / {d['visa_type']} ({len(d['content'])} chars)")
        docs.extend(file_docs)
    return docs


if __name__ == "__main__":
    docs = load_manual_md_docs()
    print(f"\nTotal: {len(docs)} sections parsed")
