# Resume builder forms
import streamlit as st
from resume_storage import save_resume, load_resumes
from utils import validate_resume_name


def resume_builder_page():
    st.title("Resume Builder")
    user = st.session_state.get("user")
    if not user:
        st.warning("Please log in.")
        return
    resumes = load_resumes(user)
    st.subheader("Your Resumes")
    selected_resume = st.selectbox(
        "Select Resume", [r["name"] for r in resumes] + ["New Resume"]
    )
    if selected_resume == "New Resume":
        resume_name = st.text_input("Resume Name")
        if not validate_resume_name(resume_name):
            st.error("Invalid or duplicate resume name.")
            return
        resume_data = {}
    else:
        resume_data = next(r for r in resumes if r["name"] == selected_resume)
        resume_name = resume_data["name"]

    # Section selection
    all_sections = [
        "Contact Info",
        "Summary",
        "Experience",
        "Education",
        "Projects",
        "Skills",
        "Certificates",
        "Publications",
    ]
    # Only use valid section names for default
    valid_defaults = [
        s
        for s in (resume_data.keys() if resume_data else ["Contact Info", "Summary"])
        if s in all_sections
    ]
    selected_sections = st.multiselect(
        "Select sections to add", all_sections, default=valid_defaults
    )

    # Contact Info (now before Summary)
    if "Contact Info" in selected_sections:
        st.subheader("Contact Info")
        contact = resume_data.get("contact", {})
        contact["full_name"] = st.text_input(
            "Full Name", value=contact.get("full_name", "")
        )
        contact["phone"] = st.text_input("Phone Number", value=contact.get("phone", ""))
        contact["email"] = st.text_input("Email", value=contact.get("email", ""))
        contact["location"] = st.text_input(
            "Location", value=contact.get("location", "")
        )
        contact["linkedin"] = st.text_input(
            "LinkedIn", value=contact.get("linkedin", "")
        )
        contact["github"] = st.text_input("GitHub", value=contact.get("github", ""))
        resume_data["contact"] = contact

    # Summary (after Contact Info)
    if "Summary" in selected_sections:
        st.subheader("Summary")
        resume_data["summary"] = st.text_area(
            "Summary", value=resume_data.get("summary", "")
        )

    # Helper for multi-entry sections
    def multi_entry_section(section, fields):
        st.subheader(section)
        entries = resume_data.get(section.lower(), [])
        if f"{section}_count" not in st.session_state:
            st.session_state[f"{section}_count"] = len(entries) if entries else 1
        # count = st.session_state[f"{section}_count"]
        if st.button(f"+ Add {section}"):
            st.session_state[f"{section}_count"] += 1
        # Remove entry by index
        remove_indices = []
        entries = entries[: st.session_state[f"{section}_count"]]
        while len(entries) < st.session_state[f"{section}_count"]:
            entries.append({f: "" for f in fields})
        for i in range(st.session_state[f"{section}_count"]):
            cols = st.columns([6, 1])
            with cols[0]:
                st.markdown(f"**{section} {i + 1}**")
                for f in fields:
                    # For 'end' field in Experience, Education, Projects, add 'Present' option
                    if f == "end" and section in [
                        "Experience",
                        "Education",
                        "Projects",
                    ]:
                        present_key = f"{section}_present_{i}"
                        is_present = st.checkbox(
                            "Present",
                            value=entries[i].get("present", False),
                            key=present_key,
                        )
                        if is_present:
                            entries[i][f] = "Present"
                            entries[i]["present"] = True
                        else:
                            entries[i][f] = st.text_input(
                                f"{f.title()} {i + 1}",
                                value=entries[i].get(f, ""),
                                key=f"{section}_{f}_{i}",
                            )
                            entries[i]["present"] = False
                    else:
                        entries[i][f] = st.text_input(
                            f"{f.title()} {i + 1}",
                            value=entries[i].get(f, ""),
                            key=f"{section}_{f}_{i}",
                        )
            with cols[1]:
                if st.button("Remove", key=f"remove_{section}_{i}"):
                    remove_indices.append(i)
        # Actually remove marked entries
        if remove_indices:
            for idx in sorted(remove_indices, reverse=True):
                entries.pop(idx)
            st.session_state[f"{section}_count"] = len(entries)
        resume_data[section.lower()] = entries

    # Experience
    if "Experience" in selected_sections:
        def experience_section():
            section = "Experience"
            fields = ["company", "title", "bullets", "start", "end", "tech_stack"]
            st.subheader(section)
            entries = resume_data.get(section.lower(), [])
            if f"{section}_count" not in st.session_state:
                st.session_state[f"{section}_count"] = len(entries) if entries else 1
            if st.button(f"+ Add {section}"):
                st.session_state[f"{section}_count"] += 1
            remove_indices = []
            entries = entries[: st.session_state[f"{section}_count"]]
            while len(entries) < st.session_state[f"{section}_count"]:
                entries.append({f: "" for f in fields})
                entries[-1]["bullets"] = [""]
            for i in range(st.session_state[f"{section}_count"]):
                cols = st.columns([6, 1])
                with cols[0]:
                    st.markdown(f"**{section} {i + 1}**")
                    for f in fields:
                        if f == "bullets":
                            # Bullet point logic inspired by projects section
                            if f"bullets_count_{i}" not in st.session_state:
                                existing_bullets = entries[i].get("bullets", [])
                                if isinstance(existing_bullets, str):
                                    existing_bullets = [existing_bullets]
                                st.session_state[f"bullets_count_{i}"] = len(existing_bullets) if existing_bullets else 1
                            bullets = entries[i].get("bullets", [])
                            if isinstance(bullets, str):
                                bullets = [bullets]
                            bullets = bullets[: st.session_state[f"bullets_count_{i}"]]
                            while len(bullets) < st.session_state[f"bullets_count_{i}"]:
                                bullets.append("")
                            for j in range(st.session_state[f"bullets_count_{i}"]):
                                bullets[j] = st.text_input(
                                    f"Experience {i + 1} - Bullet {j + 1}",
                                    value=bullets[j],
                                    key=f"exp_{i}_bullet_{j}",
                                )
                            bullet_cols = st.columns([1, 1])
                            with bullet_cols[0]:
                                if st.button("+ Add Bullet", key=f"add_bullet_{i}"):
                                    st.session_state[f"bullets_count_{i}"] += 1
                            with bullet_cols[1]:
                                if st.button("Remove Bullet", key=f"remove_bullet_{i}"):
                                    if st.session_state[f"bullets_count_{i}"] > 1:
                                        st.session_state[f"bullets_count_{i}"] -= 1
                            entries[i]["bullets"] = bullets[: st.session_state[f"bullets_count_{i}"]]
                        elif f == "end":
                            present_key = f"{section}_present_{i}"
                            is_present = st.checkbox(
                                "Present",
                                value=entries[i].get("present", False),
                                key=present_key
                            )
                            if is_present:
                                entries[i][f] = "Present"
                                entries[i]["present"] = True
                            else:
                                entries[i][f] = st.text_input(
                                    f"{f.title()} {i + 1}",
                                    value=entries[i].get(f, ""),
                                    key=f"{section}_{f}_{i}"
                                )
                                entries[i]["present"] = False
                        else:
                            entries[i][f] = st.text_input(f, value=entries[i].get(f, ""), key=f"{section}_{f}_{i}")
                with cols[1]:
                    if st.button("Remove", key=f"remove_{section}_{i}"):
                        remove_indices.append(i)
            if remove_indices:
                for idx in sorted(remove_indices, reverse=True):
                    entries.pop(idx)
                st.session_state[f"{section}_count"] = len(entries)
            resume_data[section.lower()] = entries
        experience_section()

    # Education
    if "Education" in selected_sections:
        multi_entry_section("Education", ["school", "degree", "field", "start", "end"])

    # Projects
    if "Projects" in selected_sections:
        def projects_section():
            section = "Projects"
            fields = ["title", "bullets", "start", "end", "tech_stack"]
            st.subheader(section)
            entries = resume_data.get(section.lower(), [])
            if f"{section}_count" not in st.session_state:
                st.session_state[f"{section}_count"] = len(entries) if entries else 1
            if st.button(f"+ Add {section}"):
                st.session_state[f"{section}_count"] += 1
            remove_indices = []
            entries = entries[: st.session_state[f"{section}_count"]]
            while len(entries) < st.session_state[f"{section}_count"]:
                entries.append({f: "" for f in fields})
                entries[-1]["bullets"] = [""]
            for i in range(st.session_state[f"{section}_count"]):
                cols = st.columns([6, 1])
                with cols[0]:
                    st.markdown(f"**{section} {i + 1}**")
                    for f in fields:
                        if f == "bullets":
                            if f"bullets_count_{section}_{i}" not in st.session_state:
                                existing_bullets = entries[i].get("bullets", [])
                                if isinstance(existing_bullets, str):
                                    existing_bullets = [existing_bullets]
                                st.session_state[f"bullets_count_{section}_{i}"] = len(existing_bullets) if existing_bullets else 1
                            bullets = entries[i].get("bullets", [])
                            if isinstance(bullets, str):
                                bullets = [bullets]
                            bullets = bullets[: st.session_state[f"bullets_count_{section}_{i}"]]
                            while len(bullets) < st.session_state[f"bullets_count_{section}_{i}"]:
                                bullets.append("")
                            for j in range(st.session_state[f"bullets_count_{section}_{i}"]):
                                bullets[j] = st.text_input(
                                    f"Project {i + 1} - Bullet {j + 1}",
                                    value=bullets[j],
                                    key=f"proj_{i}_bullet_{j}",
                                )
                            bullet_cols = st.columns([1, 1])
                            with bullet_cols[0]:
                                if st.button("+ Add Bullet", key=f"add_bullet_{section}_{i}"):
                                    st.session_state[f"bullets_count_{section}_{i}"] += 1
                            with bullet_cols[1]:
                                if st.button("Remove Bullet", key=f"remove_bullet_{section}_{i}"):
                                    if st.session_state[f"bullets_count_{section}_{i}"] > 1:
                                        st.session_state[f"bullets_count_{section}_{i}"] -= 1
                            entries[i]["bullets"] = bullets[: st.session_state[f"bullets_count_{section}_{i}"]]
                        else:
                            entries[i][f] = st.text_input(f, value=entries[i].get(f, ""), key=f"{section}_{f}_{i}")
                with cols[1]:
                    if st.button("Remove", key=f"remove_{section}_{i}"):
                        remove_indices.append(i)
            if remove_indices:
                for idx in sorted(remove_indices, reverse=True):
                    entries.pop(idx)
                st.session_state[f"{section}_count"] = len(entries)
            resume_data[section.lower()] = entries
        projects_section()

    # Skills
    if "Skills" in selected_sections:
        st.subheader("Skills")
        resume_data["skills"] = st.text_area(
            "Skills", value=resume_data.get("skills", "")
        )

    # Certificates
    if "Certificates" in selected_sections:
        multi_entry_section("Certificates", ["name", "issuer", "date"])

    # Publications
    if "Publications" in selected_sections:
        multi_entry_section("Publications", ["title", "publisher", "date", "link"])

    # Save/update/duplicate
    if st.button("Save Resume"):
        save_resume(user, resume_name, resume_data)
        st.success("Resume saved.")

    # Visualize Resume
    if selected_resume != "New Resume":
        st.markdown("### Actions")
        if st.button("Visualize Resume"):
            st.markdown("## Resume Preview")
            preview = next((r for r in resumes if r["name"] == selected_resume), None)
            if preview:
                contact = preview.get("contact", {})
                if contact:
                    st.markdown(
                        f"**Contact Info**: {contact.get('phone', '')} | {contact.get('email', '')} | {contact.get('location', '')} | [LinkedIn]({contact.get('linkedin', '')}) | [GitHub]({contact.get('github', '')})"
                    )
                if preview.get("summary"):
                    st.markdown(f"**Summary**: {preview['summary']}")
                if preview.get("experience"):
                    st.markdown("**Experience**:")
                    for exp in preview["experience"]:
                        st.markdown(
                            f"- **{exp.get('title', '')}** at {exp.get('company', '')} ({exp.get('start', '')} - {exp.get('end', '')})\n  {exp.get('bullets', '')}"
                        )
                if preview.get("education"):
                    st.markdown("**Education**:")
                    for edu in preview["education"]:
                        st.markdown(
                            f"- **{edu.get('degree', '')}** in {edu.get('field', '')} at {edu.get('school', '')} ({edu.get('start', '')} - {edu.get('end', '')})"
                        )
                if preview.get("projects"):
                    st.markdown("**Projects**:")
                    for proj in preview["projects"]:
                        st.markdown(
                            f"- **{proj.get('title', '')}**: {proj.get('description', '')} [Tech: {proj.get('tech', '')}] [Link]({proj.get('link', '')})"
                        )
                if preview.get("skills"):
                    st.markdown(f"**Skills**: {preview['skills']}")
                if preview.get("certificates"):
                    st.markdown("**Certificates**:")
                    for cert in preview["certificates"]:
                        st.markdown(
                            f"- {cert.get('name', '')} ({cert.get('issuer', '')}, {cert.get('date', '')})"
                        )
                if preview.get("publications"):
                    st.markdown("**Publications**:")
                    for pub in preview["publications"]:
                        st.markdown(
                            f"- {pub.get('title', '')} ({pub.get('publisher', '')}, {pub.get('date', '')}) [Link]({pub.get('link', '')})"
                        )
            else:
                st.info("No resume data to preview.")
        if st.button("Delete Resume"):
            from resume_storage import delete_resume

            delete_resume(user, resume_name)
            st.success(f"Resume '{resume_name}' deleted.")
