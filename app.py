import streamlit as st
from profiler import search_author, get_papers, compute, prompt, llm_process

st.set_page_config(page_title="Professor Research Profiler")
st.title("Professor Research Profiler")

if "candidates" not in st.session_state:
    st.session_state.candidates = None

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
    interest = st.text_area("Your research interests")
    provider = st.selectbox("LLM provider", ["anthropic", "openai", "deepseek", "gemini"])
    language = st.selectbox('Language', ['English', 'Chinese'])
    if st.button("Analyze"):
        with st.spinner("Analyzing..."):
            papers = get_papers(author["authorId"])
            top5, by_year, coauthor = compute(papers)
            p = prompt(author, top5, by_year, coauthor, interest, language)
            result = llm_process(provider, p)
        st.markdown(result)
elif st.session_state.candidates == []:
    st.info("No professors found. Try another name.")