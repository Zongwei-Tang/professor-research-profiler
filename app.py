import streamlit as st
from profiler import search_author, get_papers, compute, prompt, llm_process
import db

st.set_page_config(page_title="Professor Research Profiler")
st.title("Professor Research Profiler")

if "candidates" not in st.session_state:
    st.session_state.candidates = None

conn = db.init_db()

name = st.text_input("Professor name")

if st.button("Search"):
    if name.strip():
        st.session_state.candidates = search_author(name)
    else:
        st.warning("Please enter a name first.")

if st.session_state.candidates:
    author = st.selectbox(
        "Select the professor",
        st.session_state.candidates,
        format_func=lambda a: f"{a.get('name')} — {a.get('affiliations')} ({a.get('paperCount')} papers)",
    )
    language = st.selectbox('Language', ['English', 'Chinese'])
    if db.search_professor(conn, author["authorId"], language):
        st.success("This professor has already been analyzed.")
        cached = db.get_professor(author["authorId"], conn)
        st.markdown(cached["llm_text"])
    else:
        interest = st.text_area("Your research interests")
        provider = st.selectbox("LLM provider", ["anthropic", "openai", "deepseek", "gemini"])
        if st.button("Analyze"):
            with st.spinner("Analyzing..."):
                papers = get_papers(author["authorId"])
                top5, by_year, coauthor = compute(papers)
                p = prompt(author, top5, by_year, coauthor, interest, language)
                result = llm_process(provider, p)
            st.markdown(result)
            db.save_professor(conn, author, result, language, provider)
elif st.session_state.candidates == []:
    st.info("No professors found. Try another name.")