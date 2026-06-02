import httpx, os
from dotenv import load_dotenv
from openai import OpenAI
import anthropic
from google import genai

load_dotenv()
# Get author's basic information
def search_author(name):
    response = httpx.get('https://api.semanticscholar.org/graph/v1/author/search', headers={'x-api-key': os.environ['SEMANTICS_SCHOLAR_API_KEY']}, params={'query': name, 'fields': 'name,authorId,affiliations,paperCount,citationCount,hIndex', 'limit': 5})
    if response.status_code != 200:
        print(response.text)
        return None
    return response.json().get('data')

# Get the author's papers
def get_papers(authorid):
    r = httpx.get(f'https://api.semanticscholar.org/graph/v1/author/{authorid}', params={'fields':'papers.title,papers.year,papers.abstract,papers.citationCount,papers.authors,papers.fieldsOfStudy,papers.openAccessPdf,papers.venue'})
    if r.status_code != 200:
        print(r.text)
        return None
    papers = r.json().get('papers')
    return [i for i in papers if i.get('abstract')]

# Compute the author's top 5 cited papers and abstract, each year's papers, and coauthor'ss frequency
def compute(papers):
    top_5_cited = sorted(papers, key=lambda x: x.get('citationCount'), reverse=True)[:5]
    by_year = {}
    coauthor = {}
    for i in papers:
        if i.get('year') in by_year:
            by_year[i.get('year')].append(i)
        else:
            by_year[i.get('year')] = [i]
        for j in i.get('authors', []):
            if (j.get('authorId'), j.get('name')) in coauthor:
                coauthor[(j.get('authorId'), j.get('name'))] += 1
            else:
                coauthor[(j.get('authorId'), j.get('name'))] = 1
    return top_5_cited, by_year, coauthor


# Build prompt for llm
def prompt(author, top5, by_year, coauthor, user_interest, language):
    prompt = f"""
        You are an academic research advisor helping PhD applicants evaluate potential supervisors.
        Analyze the following professor's research profile and assess how well they match the applicant's interests.

        ### Professor Basic Information
        {str(author)}

        ### Top 5 Most Cited Papers
        The abstract is the most important field for understanding research direction.
        citationCount reflects academic influence.
        {str(top5)}

        ### Research Fields Over Time
        Papers grouped by year. Use fieldsOfStudy to identify how research focus has shifted.
        {str(by_year)}

        ### Core Collaborators
        The number next to each name is how many papers they co-authored with this professor.
        {str(coauthor)}

        ### Applicant's Research Interests
        {user_interest}

        Based on all the above, please answer the following four questions in {language}.
        Write one full paragraph per question. Use a professional but readable tone.

        1. What is this professor's core research direction and academic style?
        2. Has their research focus shifted over time? If so, in what direction?
        3. What are the specific overlaps between the applicant's interests and this professor's work?
        4. Overall, is this professor worth reaching out to? Give a clear recommendation.
        """
    return prompt


# Models are set to newest models by default
def llm_process(provider, prompt):
    match provider:
        case 'openai':
            client = OpenAI()
            response = client.responses.create(
                model="gpt-5.5",
                input=prompt
            )
            return response.output_text
        case 'anthropic':
            client = anthropic.Anthropic()
            message = client.messages.create(
                model="claude-opus-4-7",
                max_tokens=1000,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
            )
            return message.content[0].text
        case 'deepseek':
            client = OpenAI(
                api_key=os.environ.get('DEEPSEEK_API_KEY'),
                base_url="https://api.deepseek.com")

            response = client.chat.completions.create(
                model="deepseek-v4-pro",
                messages=[
                    {"role": "user", "content": prompt},
                ],
                stream=False,
                reasoning_effort="high",
                extra_body={"thinking": {"type": "enabled"}}
            )

            return response.choices[0].message.content
        case 'gemini':
            client = genai.Client()

            response = client.models.generate_content(
                model="gemini-3.1-pro",
                contents=prompt,
            )

            return response.text