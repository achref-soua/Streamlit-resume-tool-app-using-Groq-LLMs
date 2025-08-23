"""Resume components module for handling different sections of a resume."""

from typing import Dict, List, Any, Optional
import streamlit as st


def render_contact_info(resume_data: Dict[str, Any]) -> Dict[str, str]:
    """Render the contact information section of the resume.

    Args:
        resume_data: Dictionary containing resume data

    Returns:
        Updated contact information dictionary
    """
    st.subheader("Contact Info")
    contact = resume_data.get("contact", {})
    fields = {
        "full_name": "Full Name",
        "phone": "Phone Number",
        "email": "Email",
        "location": "Location",
        "linkedin": "LinkedIn",
        "github": "GitHub",
    }

    for field, label in fields.items():
        contact[field] = st.text_input(label, value=contact.get(field, ""))

    return contact


def render_text_section(title: str, key: str, resume_data: Dict[str, Any]) -> str:
    """Render a simple text section (like Summary or Skills).

    Args:
        title: Section title to display
        key: Dictionary key for the section
        resume_data: Dictionary containing resume data

    Returns:
        Updated text content
    """
    st.subheader(title)
    return st.text_area(title, value=resume_data.get(key, ""))


def handle_bullets(entries: List[Dict[str, Any]], i: int, section: str) -> List[str]:
    """Handle bullet points for a section entry.

    Args:
        entries: List of section entries
        i: Current entry index
        section: Section name

    Returns:
        List of bullet points
    """
    if f"bullets_count_{i}" not in st.session_state:
        existing_bullets = entries[i].get("bullets", [])
        if isinstance(existing_bullets, str):
            existing_bullets = [existing_bullets]
        st.session_state[f"bullets_count_{i}"] = (
            len(existing_bullets) if existing_bullets else 1
        )

    bullets = entries[i].get("bullets", [])
    if isinstance(bullets, str):
        bullets = [bullets]
    bullets = bullets[: st.session_state[f"bullets_count_{i}"]]

    while len(bullets) < st.session_state[f"bullets_count_{i}"]:
        bullets.append("")

    for j in range(st.session_state[f"bullets_count_{i}"]):
        bullets[j] = st.text_input(
            f"{section} {i + 1} - Bullet {j + 1}",
            value=bullets[j],
            key=f"{section.lower()}_{i}_bullet_{j}",
        )

    bullet_cols = st.columns([1, 1])
    with bullet_cols[0]:
        if st.button("+ Add Bullet", key=f"add_bullet_{section}_{i}"):
            st.session_state[f"bullets_count_{i}"] += 1

    with bullet_cols[1]:
        if st.button("Remove Bullet", key=f"remove_bullet_{section}_{i}"):
            if st.session_state[f"bullets_count_{i}"] > 1:
                st.session_state[f"bullets_count_{i}"] -= 1

    return bullets[: st.session_state[f"bullets_count_{i}"]]


def render_section_entry(
    section: str,
    fields: List[str],
    entries: List[Dict[str, Any]],
    i: int,
    has_bullets: bool = False,
) -> Optional[Dict[str, Any]]:
    """Render a single entry in a section.

    Args:
        section: Section name
        fields: List of field names
        entries: List of section entries
        i: Current entry index
        has_bullets: Whether the section has bullet points

    Returns:
        Updated entry dictionary or None if entry should be removed
    """
    cols = st.columns([6, 1])
    entry = entries[i]

    with cols[0]:
        st.markdown(f"**{section} {i + 1}**")
        for f in fields:
            if f == "bullets" and has_bullets:
                entry["bullets"] = handle_bullets(entries, i, section)
            else:
                entry[f] = st.text_input(
                    f"{f.title()} {i + 1}",
                    value=entry.get(f, ""),
                    key=f"{section}_{f}_{i}",
                )

    with cols[1]:
        if st.button("Remove", key=f"remove_{section}_{i}"):
            return None

    return entry


def render_section(
    section: str,
    fields: List[str],
    resume_data: Dict[str, Any],
    has_bullets: bool = False,
) -> List[Dict[str, Any]]:
    """Render a complete section of the resume.

    Args:
        section: Section name
        fields: List of field names
        resume_data: Dictionary containing resume data
        has_bullets: Whether the section has bullet points

    Returns:
        Updated list of entries for the section
    """
    st.subheader(section)
    entries = resume_data.get(section.lower(), [])

    if f"{section}_count" not in st.session_state:
        st.session_state[f"{section}_count"] = len(entries) if entries else 1

    if st.button(f"+ Add {section}"):
        st.session_state[f"{section}_count"] += 1

    entries = entries[: st.session_state[f"{section}_count"]]
    while len(entries) < st.session_state[f"{section}_count"]:
        entries.append({f: "" for f in fields})

    updated_entries = []
    for i in range(st.session_state[f"{section}_count"]):
        entry = render_section_entry(section, fields, entries, i, has_bullets)
        if entry is not None:
            updated_entries.append(entry)

    if len(updated_entries) < len(entries):
        st.session_state[f"{section}_count"] = len(updated_entries)

    return updated_entries
