import streamlit as st
from profiler import search_author, get_papers, compute, prompt, llm_process
import db

st.set_page_config(page_title="Professor Research Profiler")
st.title("Professor Research Profiler")

if "candidates" not in st.session_state:
    st.session_state.candidates = None

username = st.text_input("Your username")

conn = db.init_db()

if username.strip():
    user_id = db.create_get_user(conn, username)

    with st.sidebar:
        st.header(f'History: {username}')
        history = db.get_user_analysis_history(conn, user_id)
        for i in history:
            with st.expander(f"{i['author_name']} --{i['time']}"):
                st.markdown(i['analysis_text'])

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
        interest = st.text_area("Your research interests")
        provider = st.selectbox("LLM provider", ["anthropic", "openai", "deepseek", "gemini"])
        if st.button("Analyze"):
            with st.spinner("Analyzing..."):
                result = db.get_one_history(conn, user_id, author['authorId'], interest, language, provider)
                if result:
                    st.markdown(result)
                else:
                    papers = db.get_papers_cache(conn, author["authorId"])
                    if papers is None:
                        papers = get_papers(author["authorId"])
                        db.save_papers(conn, author, papers)
                    top5, by_year, coauthor = compute(papers)
                    p = prompt(author, top5, by_year, coauthor, interest, language)
                    result = llm_process(provider, p)
                    st.markdown(result)
                    db.save_analysis(conn, user_id, author['authorId'], author['name'], result, interest, language, provider)
    elif st.session_state.candidates == []:
        st.info("No professors found. Try another name.")