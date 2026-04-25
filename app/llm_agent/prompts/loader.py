from pathlib import Path


class PromptLoader:
    def __init__(self, base_dir: Path | None = None):
        default_dir = Path(__file__).resolve().parent / "templates"
        self.base_dir = base_dir or default_dir

    def load(self, name: str) -> str:
        path = self.base_dir / f"{name}.txt"
        return path.read_text(encoding="utf-8")

