# Resume adaptation via Groq API
import streamlit as st
import json
from resume_storage import load_resumes, save_resume
from utils import get_groq_api_key


# Use ChatGroq for LLM calls
from langchain_groq import ChatGroq


def call_groq_api(resume, job_desc, api_key):
    llm = ChatGroq(
        groq_api_key=api_key,
        model_name="openai/gpt-oss-20b",
        temperature=1,
    )
    prompt = f"""
    You are an expert resume writer and job matching specialist. Your job is to:
    - Analyze the resume and the job description below.
    - Adapt and rewrite the resume to best match the job requirements, highlighting relevant skills, experience, and achievements.
    - Use strong action verbs, quantifiable results, and ensure the resume is ATS-friendly and tailored for the specific role.
    - Make sure the resume is concise, impactful, and avoids unnecessary repetition.
    - Return ONLY the result as a JSON object with the same structure as the input resume. Do not include any explanation or extra text, only the JSON object.
    Resume:
    {json.dumps(resume, indent=2)}
    Job Description:
    {job_desc}
    """
    response = llm.invoke(prompt)
    # Convert AIMessage to string if needed
    response_text = (
        str(response.content) if hasattr(response, "content") else str(response)
    )
    import re

    match = re.search(r"\{.*\}", response_text, re.DOTALL)
    if match:
        json_str = match.group(0)
        try:
            adapted_resume = json.loads(json_str)
            return adapted_resume
        except Exception:
            st.error(
                "Groq LLM returned a response, but it was not valid JSON. Please try again or refine your prompt."
            )
            return None
    else:
        st.error(
            "Groq LLM did not return any JSON. Please try again or refine your prompt."
        )
        return None


def resume_adapter_page():
    st.title("Job Description Adaptation")
    user = st.session_state.get("user")
    if not user:
        st.warning("Please log in.")
        return
    resumes = load_resumes(user)
    if not resumes:
        st.info("No resumes found. Please create one first.")
        return
    selected_resume_name = st.selectbox(
        "Select Resume to Adapt", [r["name"] for r in resumes]
    )
    resume_data = next(r for r in resumes if r["name"] == selected_resume_name)
    job_desc = st.text_area("Paste Job Description Here")
    if st.button("Adapt Resume"):
        api_key = get_groq_api_key()
        if not api_key:
            st.error("Groq API key not found in .env file.")
            return
        with st.spinner("Adapting resume using Groq LLM..."):
            adapted = call_groq_api(resume_data, job_desc, api_key)
        if adapted:
            st.success("Resume adapted!")
            # Show editable form for adapted resume
            st.markdown("## Adapted Resume (Editable)")
            edited_resume = json.loads(json.dumps(adapted))
            for k, v in edited_resume.items():
                if isinstance(v, str):
                    edited_resume[k] = st.text_area(k.title(), value=v)
                elif isinstance(v, list):
                    st.markdown(f"### {k.title()}")
                    for i, item in enumerate(v):
                        for subk, subv in item.items():
                            edited_resume[k][i][subk] = st.text_input(
                                f"{k.title()} {i + 1} - {subk.title()}",
                                value=subv,
                                key=f"{k}_{subk}_{i}",
                            )
            # Save options
            if st.button("Save as New Resume"):
                new_name = st.text_input("New Resume Name")
                if new_name:
                    save_resume(user, new_name, edited_resume)
                    st.success("Adapted resume saved as new copy.")
            if st.button("Override Existing Resume"):
                save_resume(user, selected_resume_name, edited_resume)
                st.success("Existing resume overridden with adapted version.")
