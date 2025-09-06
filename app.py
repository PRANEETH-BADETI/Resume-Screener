import streamlit as st
from streamlit_pdf_viewer import pdf_viewer
import os
import io
import logging

from db.db_manager import save_screening_session, get_screening_sessions
from utils.data_parser import parse_document, save_uploaded_file
from utils.nlp_processor import get_relevance_score, load_models

# Set up logging
logging.basicConfig(filename='app.log', level=logging.INFO)

def log_error(message):
    logging.error(message)
    st.error(message)


# ====================
# Configuration
# ====================
# Load models once using Streamlit's cache
nlp, sbert_model, gemini_model = load_models()


# ====================
# Streamlit UI
# ====================
def set_view_resume(data, name):
    st.session_state['viewing_resume'] = data
    st.session_state['viewing_resume_name'] = name


def clear_view_resume():
    st.session_state['viewing_resume'] = None
    st.session_state['viewing_resume_name'] = None


def main():
    st.title("AI-Powered Resume Screener")
    st.markdown("Upload a job description and a batch of resumes to rank the best candidates instantly.")

    if 'user_id' not in st.session_state:
        st.session_state['user_id'] = 'anonymous_user'
    if 'page' not in st.session_state:
        st.session_state['page'] = 'home'
    if 'viewing_resume' not in st.session_state:
        st.session_state['viewing_resume'] = None
    if 'viewing_resume_name' not in st.session_state:
        st.session_state['viewing_resume_name'] = None
    if 'ranked_candidates' not in st.session_state:
        st.session_state['ranked_candidates'] = []

    st.sidebar.title("Navigation")
    if st.sidebar.button("Home"):
        st.session_state['page'] = 'home'
        clear_view_resume()
        st.rerun()
    if st.sidebar.button("History"):
        st.session_state['page'] = 'history'
        clear_view_resume()
        st.rerun()

    if st.session_state['page'] == 'home':
        st.header("New Screening Session")
        with st.sidebar:
            st.header("Upload Files")
            job_desc_file = st.file_uploader("Upload Job Description", type=["pdf", "docx", "txt"])
            resume_files = st.file_uploader("Upload Resumes", type=["pdf", "docx", "txt"], accept_multiple_files=True)
            st.markdown("---")
            st.header("Settings")
            skills_weight = st.slider("Skills Weight", 0, 100, 50, key='skills_weight')
            experience_weight = st.slider("Experience Weight", 0, 100, 50, key='experience_weight')

        if st.button("Run Screening"):
            if not job_desc_file or not resume_files:
                st.error("Please upload both a job description and at least one resume.")
            else:
                with st.spinner("Processing documents..."):
                    job_desc_text = parse_document(job_desc_file)
                    if not job_desc_text:
                        st.error("Failed to parse the job description file. Please try a different format.")
                        st.stop()

                    ranked_candidates = []
                    for resume_file in resume_files:
                        resume_text = parse_document(resume_file)
                        if resume_text:
                            file_path = save_uploaded_file(resume_file)
                            if not file_path:
                                continue

                            score, explanation, _, _ = get_relevance_score(
                                job_desc_text, resume_text, skills_weight, experience_weight, sbert_model, nlp,
                                gemini_model
                            )

                            ranked_candidates.append({
                                "filename": resume_file.name,
                                "score": score,
                                "explanation": explanation,
                                "file_path": file_path
                            })

                    ranked_candidates.sort(key=lambda x: x["score"], reverse=True)

                    st.session_state['ranked_candidates'] = ranked_candidates
                    save_screening_session(st.session_state['user_id'], job_desc_text, ranked_candidates)
                    st.success("Screening complete! Here are the results:")

        if st.session_state['ranked_candidates']:
            for i, candidate in enumerate(st.session_state['ranked_candidates']):
                score_percentage = round(candidate["score"] * 100)
                st.subheader(f"{i + 1}. {candidate['filename']} (Score: {score_percentage}%)")
                st.markdown(candidate["explanation"])

                if 'file_path' in candidate and os.path.exists(candidate['file_path']):
                    with open(candidate['file_path'], 'rb') as f:
                        file_content = f.read()

                    st.button(f"View Preview", key=f"preview_home_{i}",
                              on_click=set_view_resume, args=(file_content, candidate['filename']))

                    st.download_button(
                        label=f"Download {candidate['filename']}",
                        data=file_content,
                        file_name=candidate["filename"],
                        mime="application/octet-stream",
                        key=f"download_{i}"
                    )
                else:
                    st.info("File preview not available.")

                st.markdown("---")

        if st.session_state['viewing_resume']:
            st.subheader(f"Resume Preview: {st.session_state['viewing_resume_name']}")
            pdf_viewer(input=st.session_state['viewing_resume'], width=700)
            if st.button("Close Preview", key="close_preview", on_click=clear_view_resume):
                pass

    elif st.session_state['page'] == 'history':
        st.header("Screening History")
        sessions = get_screening_sessions(st.session_state['user_id'])
        if not sessions:
            st.info("No past screening sessions found. Please run a screening from the Home page.")
        else:
            for session in sessions:
                session_id, job_desc, ranked_resumes, created_at = session
                with st.expander(f"Session {session_id[:8]} - {created_at.strftime('%Y-%m-%d %H:%M:%S')}"):
                    st.subheader("Job Description")
                    st.markdown(job_desc)
                    st.subheader("Ranked Resumes")
                    for i, candidate in enumerate(ranked_resumes):
                        score_percentage = round(candidate["score"] * 100)
                        st.write(f"**{i + 1}. {candidate['filename']} (Score: {score_percentage}%)**")
                        st.markdown(candidate['explanation'])

                        if 'file_path' in candidate and os.path.exists(candidate['file_path']):
                            with open(candidate['file_path'], 'rb') as f:
                                file_content = f.read()

                            st.button(f"View Preview", key=f"preview_history_{session_id}_{i}",
                                      on_click=set_view_resume, args=(file_content, candidate['filename']))

                            st.download_button(
                                label=f"Download {candidate['filename']}",
                                data=file_content,
                                file_name=candidate["filename"],
                                mime="application/octet-stream",
                                key=f"download_{session_id}_{i}"
                            )
                        else:
                            st.info("File not found.")

                        st.markdown("---")


if __name__ == "__main__":
    main()