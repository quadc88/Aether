from pathlib import Path
import re
import yaml

from aether.time.clock import now, now_display, now_iso, get_timezone
from aether.memory.timeline.recorder import record_event


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


def get_episodic_dir() -> Path:
    episodic_dir = get_vault_dir() / "episodic"
    episodic_dir.mkdir(parents=True, exist_ok=True)
    return episodic_dir


def slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")[:80] or "untitled"


def write_episode(
    title: str,
    summary: str,
    details: str = "",
    importance: str = "normal",
    tags: list[str] | None = None,
    related_files: list[str] | None = None,
    record_timeline: bool = True,
) -> dict:
    episodic_dir = get_episodic_dir()

    timestamp = now()
    date_part = timestamp.strftime("%Y-%m-%d")
    time_part = timestamp.strftime("%H%M%S")
    slug = slugify(title)

    file_name = f"{date_part}-{time_part}-{slug}.md"
    file_path = episodic_dir / file_name

    tags = tags or []
    related_files = related_files or []

    frontmatter = {
        "type": "episodic_memory",
        "title": title,
        "created": now_iso(),
        "timezone": get_timezone(),
        "importance": importance,
        "tags": tags,
        "related_files": related_files,
    }

    markdown = "---\n"
    markdown += yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False)
    markdown += "---\n\n"
    markdown += f"# {title}\n\n"
    markdown += f"**Time:** {now_display()}  \n"
    markdown += f"**Timezone:** {get_timezone()}  \n"
    markdown += f"**Importance:** {importance}  \n\n"
    markdown += "## Summary\n\n"
    markdown += f"{summary.strip()}\n\n"

    if details.strip():
        markdown += "## Details\n\n"
        markdown += f"{details.strip()}\n\n"

    if tags:
        markdown += "## Tags\n\n"
        markdown += "\n".join([f"- {tag}" for tag in tags])
        markdown += "\n\n"

    if related_files:
        markdown += "## Related Files\n\n"
        markdown += "\n".join([f"- `{file}`" for file in related_files])
        markdown += "\n\n"

    file_path.write_text(markdown, encoding="utf-8")

    timeline_event = None

    if record_timeline:
        timeline_event = record_event(
            event_type="episodic_memory",
            title=title,
            description=summary,
            importance=importance,
            related_files=[str(file_path)] + related_files,
        )

    return {
        "title": title,
        "file_path": str(file_path),
        "created": frontmatter["created"],
        "timezone": get_timezone(),
        "importance": importance,
        "tags": tags,
        "timeline_event": timeline_event,
    }


def list_episodes(limit: int = 20) -> list[dict]:
    episodic_dir = get_episodic_dir()

    files = sorted(
        episodic_dir.glob("*.md"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )

    episodes = []

    for file_path in files[:limit]:
        episodes.append(
            {
                "file_name": file_path.name,
                "file_path": str(file_path),
                "modified_time": file_path.stat().st_mtime,
            }
        )

    return episodes


def latest_episode() -> dict | None:
    episodes = list_episodes(limit=1)

    if not episodes:
        return None

    file_path = Path(episodes[0]["file_path"])

    return {
        **episodes[0],
        "content": file_path.read_text(encoding="utf-8"),
    }