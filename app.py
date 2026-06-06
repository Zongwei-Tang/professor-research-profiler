import streamlit as st
from profiler import search_author, get_papers, compute, prompt, llm_process
import db

st.set_page_config(page_title="Professor Research Profiler")
st.title("Professor Research Profiler")

def analyze_one(conn, author, provider, interest, language, user_id):
    papers = db.get_papers_cache(conn, author["authorId"])
    if papers is None:
        papers = get_papers(author["authorId"])
        if papers is None:
            st.error("Failed to fetch papers for the selected professor.")
            st.stop()
        if papers == []:
            st.warning("No papers with abstracts found for this professor.")
            st.stop()
        db.save_papers(conn, author, papers)
    top5, by_year, coauthor = compute(papers)
    p = prompt(author, top5, by_year, coauthor, interest, language)
    result = llm_process(provider, p)
    if result is None:
        st.error("Failed to get analysis from the LLM provider.")
        st.stop()
    st.session_state.from_history, st.session_state.result, st.session_state.author_id = False, result, author['authorId']
    db.save_analysis(conn, user_id, author['authorId'], author['name'], st.session_state.result, interest, language, provider)

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
                st.write(f"Interest: {i['interest']}")
                st.markdown(i['analysis_text'])

    name = st.text_input("Professor name")

    if st.button("Search"):
        if name.strip():
            candidates = search_author(name)
            if candidates is None:
                st.error("Error occurred while searching for the professor. Please try again later.")
                st.stop()
            st.session_state.candidates = candidates
            st.session_state.result = None
            st.session_state.from_history = False
            st.session_state.author_id = None
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
                    st.session_state.result, st.session_state.from_history, st.session_state.author_id = result, True, author['authorId']
                else:
                    analyze_one(conn, author, provider, interest, language, user_id)
        if st.session_state.get('from_history'):
            if st.button('Rerun'):
                analyze_one(conn, author, provider, interest, language, user_id)
        if st.session_state.get('result') and st.session_state.author_id == author['authorId']:
            st.markdown(st.session_state.result)
    elif st.session_state.candidates == []:
        st.info("No professors found. Try another name.")