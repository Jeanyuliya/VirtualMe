"""Subject profile rendering - the human-readable SUBJECT.md artifact."""

from __future__ import annotations

from virtualme.storage.db import Subject


def render_subject_md(subject: Subject) -> str:
    """Render a subject profile as a human-readable Markdown card."""
    title = subject.display_name or subject.interviewee_id
    lines = [
        f"# Subject: {title}",
        "",
        f"- Interviewee ID: {subject.interviewee_id}",
        f"- Display name: {subject.display_name or ''}",
        f"- Domain: {subject.domain.value}",
        f"- Goal: {subject.goal or ''}",
        f"- Status: {subject.status.value}",
        f"- Created at: {subject.created_at or ''}",
        f"- Updated at: {subject.updated_at or ''}",
        "",
    ]
    return "\n".join(lines)
