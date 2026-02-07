from pathlib import Path

def load_md(file_path: str) -> str:
    assert file_path.endswith(".md"), "File must be a markdown file"
    path = Path(file_path)
    # .read_text() handles opening, reading, and closing
    return path.read_text(encoding="utf-8")