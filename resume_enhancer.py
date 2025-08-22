# Resume enhancement via Groq API
import streamlit as st

import json
from resume_storage import load_resumes, save_resume
from utils import get_groq_api_key
from langchain_groq import ChatGroq


def call_groq_enhance_api(resume, api_key):
    llm = ChatGroq(
        groq_api_key=api_key,
        model_name="openai/gpt-oss-20b",
        temperature=1,
    )
    prompt = f"""
    You are an expert resume coach. Enhance the following resume to improve its impact and provide constructive feedback. Return ONLY the result as a JSON object with the same structure as the input resume, and a 'feedback' field with your suggestions. Do not include any explanation or extra text, only the JSON object.
    Resume:
    {json.dumps(resume, indent=2)}
    """
    response = llm.invoke(prompt)
    response_text = (
        str(response.content) if hasattr(response, "content") else str(response)
    )
    import re

    match = re.search(r"\{.*\}", response_text, re.DOTALL)
    if match:
        json_str = match.group(0)
        try:
            enhanced_resume = json.loads(json_str)
            return enhanced_resume
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


def resume_enhancer_page():
    st.title("Resume Enhancer")
    user = st.session_state.get("user")
    if not user:
        st.warning("Please log in.")
        return
    resumes = load_resumes(user)
    if not resumes:
        st.info("No resumes found. Please create one first.")
        return
    selected_resume_name = st.selectbox(
        "Select Resume to Enhance", [r["name"] for r in resumes]
    )
    resume_data = next(r for r in resumes if r["name"] == selected_resume_name)
    if st.button("Enhance Resume"):
        api_key = get_groq_api_key()
        if not api_key:
            st.error("Groq API key not found in .env file.")
            return
        with st.spinner("Enhancing resume using Groq LLM..."):
            enhanced = call_groq_enhance_api(resume_data, api_key)
        if enhanced:
            st.success("Resume enhanced!")
            st.markdown("## Enhanced Resume (Editable)")
            edited_resume = json.loads(json.dumps(enhanced))
            feedback = edited_resume.pop("feedback", None)
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
            if feedback:
                st.markdown(f"### Feedback\n{feedback}")
            if st.button("Save as New Resume"):
                new_name = st.text_input("New Resume Name")
                if new_name:
                    save_resume(user, new_name, edited_resume)
                    st.success("Enhanced resume saved as new copy.")
            if st.button("Override Existing Resume"):
                save_resume(user, selected_resume_name, edited_resume)
                st.success("Existing resume overridden with enhanced version.")
