from pathlib import Path


def load_identity_seed(path: str = "identity/identity_seed.md") -> str:
    seed_path = Path(path)

    if not seed_path.exists():
        raise FileNotFoundError(f"Identity Seed not found: {seed_path}")

    return seed_path.read_text(encoding="utf-8")


def identity_preview(max_chars: int = 500) -> str:
    seed = load_identity_seed()
    return seed[:max_chars]