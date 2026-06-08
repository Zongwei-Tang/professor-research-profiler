# Professor Research Profiler

A Streamlit app for prospective PhD applicants to evaluate potential supervisors. Enter a
professor's name and your research interests; it pulls their publication record from
[Semantic Scholar](https://www.semanticscholar.org/) and uses an LLM to assess the fit.

🔗 **Live demo:** https://prof-research-profiler.streamlit.app/

## Features

- Search a professor and pick the right person from the candidate list.
- Builds a quick profile: top-cited papers, output by year, and frequent collaborators.
- LLM analysis of their research direction, how their focus shifted, overlaps with your
  interests, and whether to reach out.
- Choose your provider: Anthropic, OpenAI, DeepSeek, or Gemini.
- Per-user history: past analyses are saved and shown in the sidebar.
- Paper cache: fetched papers are stored in Turso so repeat lookups are instant.

## Running locally

Requires [uv](https://docs.astral.sh/uv/).

```bash
uv sync                          # install dependencies
cp .env.example .env             # then fill in your API keys
uv run streamlit run app.py
```

You need a Semantic Scholar key, a [Turso](https://turso.tech/) database URL and token,
plus the key for whichever LLM provider you use.
