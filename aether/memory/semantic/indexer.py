from pathlib import Path
import json
import math
import re
import hashlib
import yaml

from aether.time.clock import now_iso, get_timezone


VECTOR_DIM = 1024


def load_aether_config(path: str = "config/aether.yaml") -> dict:
    config_path = Path(path)

    if not config_path.exists():
        return {}

    with config_path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def get_vault_dir() -> Path:
    config = load_aether_config()
    paths = config.get("paths", {})
    vault_dir = paths.get("vault_dir", "vault")
    return Path(vault_dir)


def get_vector_db_dir() -> Path:
    config = load_aether_config()
    paths = config.get("paths", {})
    vector_db_dir = paths.get("vector_db_dir", "vector_db")
    vector_db_path = Path(vector_db_dir)
    vector_db_path.mkdir(parents=True, exist_ok=True)
    return vector_db_path


def get_index_path() -> Path:
    return get_vector_db_dir() / "semantic_index.json"


def tokenize(text: str) -> list[str]:
    """
    Lightweight tokenizer:
    - English / numbers: word tokens
    - Chinese characters: individual character tokens
    This is not perfect semantic embedding, but it is enough for the first local memory search foundation.
    """
    text = text.lower()

    english_tokens = re.findall(r"[a-z0-9_]+", text)
    chinese_tokens = re.findall(r"[\u4e00-\u9fff]", text)

    return english_tokens + chinese_tokens


def token_hash(token: str) -> int:
    digest = hashlib.md5(token.encode("utf-8")).hexdigest()
    return int(digest, 16) % VECTOR_DIM


def text_to_vector(text: str) -> dict[str, float]:
    tokens = tokenize(text)

    if not tokens:
        return {}

    vector: dict[int, float] = {}

    for token in tokens:
        idx = token_hash(token)
        vector[idx] = vector.get(idx, 0.0) + 1.0

    norm = math.sqrt(sum(value * value for value in vector.values()))

    if norm == 0:
        return {}

    normalized = {str(idx): value / norm for idx, value in vector.items()}

    return normalized


def cosine_similarity(vector_a: dict[str, float], vector_b: dict[str, float]) -> float:
    if not vector_a or not vector_b:
        return 0.0

    if len(vector_a) > len(vector_b):
        vector_a, vector_b = vector_b, vector_a

    score = 0.0

    for key, value in vector_a.items():
        score += value * vector_b.get(key, 0.0)

    return score


def read_markdown_files() -> list[Path]:
    vault_dir = get_vault_dir()

    if not vault_dir.exists():
        return []

    return sorted(vault_dir.rglob("*.md"))


def extract_title(content: str, fallback: str) -> str:
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("# "):
            return line.replace("# ", "", 1).strip()

    return fallback


def build_semantic_index() -> dict:
    markdown_files = read_markdown_files()
    documents = []

    for file_path in markdown_files:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        title = extract_title(content, fallback=file_path.stem)

        vector = text_to_vector(content)

        documents.append(
            {
                "title": title,
                "file_path": str(file_path),
                "relative_path": str(file_path.relative_to(get_vault_dir())),
                "content_preview": content[:500],
                "vector": vector,
                "indexed_at": now_iso(),
                "timezone": get_timezone(),
            }
        )

    index = {
        "type": "semantic_memory_index",
        "version": "0.1.0",
        "created": now_iso(),
        "timezone": get_timezone(),
        "vector_dim": VECTOR_DIM,
        "document_count": len(documents),
        "documents": documents,
    }

    index_path = get_index_path()
    index_path.write_text(
        json.dumps(index, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    return {
        "index_path": str(index_path),
        "document_count": len(documents),
        "created": index["created"],
        "timezone": index["timezone"],
    }


def load_semantic_index() -> dict:
    index_path = get_index_path()

    if not index_path.exists():
        return {
            "type": "semantic_memory_index",
            "version": "0.1.0",
            "document_count": 0,
            "documents": [],
        }

    return json.loads(index_path.read_text(encoding="utf-8"))


def search_semantic_memory(query: str, limit: int = 5) -> list[dict]:
    index = load_semantic_index()
    query_vector = text_to_vector(query)

    results = []

    for document in index.get("documents", []):
        score = cosine_similarity(query_vector, document.get("vector", {}))

        if score <= 0:
            continue

        results.append(
            {
                "score": round(score, 4),
                "title": document.get("title"),
                "file_path": document.get("file_path"),
                "relative_path": document.get("relative_path"),
                "content_preview": document.get("content_preview"),
                "indexed_at": document.get("indexed_at"),
            }
        )

    results.sort(key=lambda item: item["score"], reverse=True)

    return results[:limit]


def semantic_memory_status() -> dict:
    index = load_semantic_index()

    return {
        "index_path": str(get_index_path()),
        "document_count": index.get("document_count", 0),
        "created": index.get("created"),
        "timezone": index.get("timezone"),
        "vector_dim": index.get("vector_dim", VECTOR_DIM),
    }