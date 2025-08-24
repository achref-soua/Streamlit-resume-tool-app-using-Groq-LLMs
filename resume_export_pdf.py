import streamlit as st
import json
from resume_storage import load_resumes
from utils import get_groq_api_key
from langchain_groq import ChatGroq
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import io


def generate_pdf(resume_data):
    """Generate a PDF resume in memory from resume_data."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    story = []

    # Contact info
    contact = resume_data.get("contact", {})
    story.append(Paragraph(f"<b>{contact.get('full_name', '')}</b>", styles["Title"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"Email: {contact.get('email', '')}", styles["Normal"]))
    story.append(Paragraph(f"Phone: {contact.get('phone', '')}", styles["Normal"]))
    story.append(
        Paragraph(f"Location: {contact.get('location', '')}", styles["Normal"])
    )
    if contact.get("linkedin"):
        story.append(Paragraph(f"LinkedIn: {contact['linkedin']}", styles["Normal"]))
    if contact.get("github"):
        story.append(Paragraph(f"GitHub: {contact['github']}", styles["Normal"]))
    story.append(Spacer(1, 12))

    # Summary
    if "summary" in resume_data and resume_data["summary"]:
        story.append(Paragraph("<b>Summary</b>", styles["Heading2"]))
        story.append(Paragraph(resume_data["summary"], styles["Normal"]))
        story.append(Spacer(1, 12))

    # Experience
    if "experience" in resume_data:
        story.append(Paragraph("<b>Experience</b>", styles["Heading2"]))
        for exp in resume_data["experience"]:
            story.append(
                Paragraph(
                    f"{exp.get('title', '')} at {exp.get('company', '')} "
                    f"({exp.get('start', '')} - {exp.get('end', '')})",
                    styles["Normal"],
                )
            )
            if exp.get("bullets"):
                for bullet in exp["bullets"]:
                    story.append(Paragraph(f"• {bullet}", styles["Normal"]))
            if exp.get("tech_stack"):
                story.append(Paragraph(f"Tech: {exp['tech_stack']}", styles["Italic"]))
            story.append(Spacer(1, 6))

    # Education
    if "education" in resume_data:
        story.append(Paragraph("<b>Education</b>", styles["Heading2"]))
        for edu in resume_data["education"]:
            story.append(
                Paragraph(
                    f"{edu.get('degree', '')} in {edu.get('field', '')} "
                    f"at {edu.get('school', '')} ({edu.get('start', '')} - {edu.get('end', '')})",
                    styles["Normal"],
                )
            )
            story.append(Spacer(1, 6))

    # Projects
    if "projects" in resume_data:
        story.append(Paragraph("<b>Projects</b>", styles["Heading2"]))
        for proj in resume_data["projects"]:
            story.append(
                Paragraph(
                    f"{proj.get('name', '')} ({proj.get('start', '')} - {proj.get('end', '')})",
                    styles["Normal"],
                )
            )
            if proj.get("bullets"):
                for bullet in proj["bullets"]:
                    story.append(Paragraph(f"• {bullet}", styles["Normal"]))
            if proj.get("tech_stack"):
                story.append(Paragraph(f"Tech: {proj['tech_stack']}", styles["Italic"]))
            story.append(Spacer(1, 6))

    # Skills
    if "skills" in resume_data and resume_data["skills"]:
        story.append(Paragraph("<b>Skills</b>", styles["Heading2"]))
        story.append(Paragraph(resume_data["skills"], styles["Normal"]))

    # Certificates
    if "certificates" in resume_data:
        story.append(Paragraph("<b>Certificates</b>", styles["Heading2"]))
        for cert in resume_data["certificates"]:
            story.append(
                Paragraph(
                    f"{cert.get('name', '')} - {cert.get('issuer', '')} ({cert.get('date', '')})",
                    styles["Normal"],
                )
            )

    # Publications
    if "publications" in resume_data:
        story.append(Paragraph("<b>Publications</b>", styles["Heading2"]))
        for pub in resume_data["publications"]:
            story.append(
                Paragraph(
                    f"{pub.get('title', '')} ({pub.get('publisher', '')}, {pub.get('date', '')})",
                    styles["Normal"],
                )
            )
            if pub.get("link"):
                story.append(Paragraph(f"Link: {pub['link']}", styles["Normal"]))

    doc.build(story)
    buffer.seek(0)
    return buffer


def resume_export_pdf_page():
    st.title("Export Resume as PDF")
    user = st.session_state.get("user")
    if not user:
        st.warning("Please log in.")
        return
    resumes = load_resumes(user)
    if not resumes:
        st.info("No resumes found. Please create one first.")
        return
    selected_resume_name = st.selectbox(
        "Select Resume to Export", [r["name"] for r in resumes]
    )
    resume_data = next(r for r in resumes if r["name"] == selected_resume_name)

    if st.button("Export as PDF"):
        with st.spinner("Generating PDF resume..."):
            pdf_file = generate_pdf(resume_data)

        st.success("PDF resume generated!")
        st.download_button(
            label="⬇️ Download your professional resume PDF",
            data=pdf_file,
            file_name=f"{selected_resume_name}.pdf",
            mime="application/pdf",
        )
