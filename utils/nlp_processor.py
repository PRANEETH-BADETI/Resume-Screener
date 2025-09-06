import streamlit as st
import spacy
from sentence_transformers import SentenceTransformer, util
import google.generativeai as genai
import re
import os


# Assuming nlp and sbert_model are loaded in app.py and passed or imported
def load_models():
    """Loads models and API keys. This is for modularity, assuming app.py handles caching."""
    try:
        nlp = spacy.load("en_core_web_sm")
    except Exception as e:
        st.error(f"The spaCy model 'en_core_web_sm' is not installed. Please install it.")
        st.stop()

    sbert_model = SentenceTransformer('all-MiniLM-L6-v2')

    try:
        genai.configure(api_key=st.secrets['api']["GEMINI_API_KEY"])
        gemini_model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        st.error(f"Error configuring Gemini API: {e}")
        st.stop()

    return nlp, sbert_model, gemini_model


def extract_skills(text, job_skills, nlp_model):
    doc = nlp_model(text.lower())
    extracted = []
    job_skills_lower = {skill.lower() for skill in job_skills}

    for token in doc:
        if token.text in job_skills_lower:
            extracted.append(token.text)

    for chunk in doc.noun_chunks:
        if chunk.text.lower() in job_skills_lower:
            extracted.append(chunk.text.lower())

    return list(set(extracted))


def extract_years_of_experience(text):
    text_lower = text.lower()
    match = re.search(r'(\d+)\s*\+?\s*years? of experience|(\d+)\s*\+?\s*years? experience', text_lower)
    if match:
        return int(match.group(1) or match.group(2))
    return 0


def get_relevance_score(job_desc_text, resume_text, skills_weight, experience_weight, sbert_model, nlp_model,
                        gemini_model):
    # 1. Semantic Score
    job_desc_embedding = sbert_model.encode(job_desc_text, convert_to_tensor=True)
    resume_embedding = sbert_model.encode(resume_text, convert_to_tensor=True)
    cosine_score = util.pytorch_cos_sim(job_desc_embedding, resume_embedding).item()

    # 2. Skill Match Score
    job_entities = nlp_model(job_desc_text)
    job_skills_list = [ent.text for ent in job_entities.ents if ent.label_ == "SKILL"]
    resume_skills = extract_skills(resume_text, job_skills_list, nlp_model)
    if len(job_skills_list) > 0:
        skill_match_score = len(resume_skills) / len(job_skills_list)
    else:
        skill_match_score = 0

    # 3. Years of Experience Score
    years_of_experience = extract_years_of_experience(resume_text)
    if years_of_experience > 0:
        experience_score = min(years_of_experience / 10.0, 1.0)
        exp_w = experience_weight
    else:
        experience_score = 0
        exp_w = 0

    # 4. Hybrid Composite Score
    total_effective_weight = skills_weight + exp_w
    semantic_weight = 100 - total_effective_weight
    if semantic_weight < 0:
        semantic_weight = 0

    composite_score = (
                              (cosine_score * semantic_weight) +
                              (skill_match_score * skills_weight) +
                              (experience_score * exp_w)
                      ) / 100

    prompt = f"""
    You are an expert HR Manager. Analyze the following job description and resume.
    The candidate's profile includes:
    - Detected Skills: {', '.join(resume_skills) if resume_skills else 'None'}
    - Years of Experience: {years_of_experience}

    Provide a concise summary (2-3 sentences) of the candidate's fit, highlighting key strengths and any notable gaps. The summary should be recruiter-friendly and brief.

    Job Description:
    {job_desc_text[:1000]}...

    Resume:
    {resume_text[:1000]}...

    Respond in markdown format.
    """
    explanation_response = gemini_model.generate_content(prompt)
    explanation = explanation_response.text

    return composite_score, explanation, resume_skills, years_of_experience