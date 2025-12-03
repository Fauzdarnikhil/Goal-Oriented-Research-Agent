import os
import requests

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
ARXIV_MAX_RESULTS = 4


def retrieve_sources(query: str):
    """Retrieve research context using Tavily + Arxiv"""

    documents = []
    sources = []

    # ----- 1) Tavily Web Search -----
    if TAVILY_API_KEY:
        try:
            tavily_url = "https://api.tavily.com/search"
            response = requests.post(
                tavily_url,
                json={"api_key": TAVILY_API_KEY, "query": query, "n_results": 6},
                timeout=12
            )
            data = response.json()
            for r in data.get("results", []):
                documents.append(r["content"])
                sources.append({
                    "url": r["url"],
                    "title": r.get("title", r["url"]),
                    "snippet": r["content"][:200]
                })
        except Exception as e:
            print("[Retriever] Tavily failed:", str(e))

    # ----- 2) Arxiv Scientific Papers -----
    try:
        arxiv_url = f"https://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results={ARXIV_MAX_RESULTS}"
        res = requests.get(arxiv_url, timeout=12).text

        import feedparser
        feed = feedparser.parse(res)
        for entry in feed.entries:
            documents.append(entry.summary)
            sources.append({
                "url": entry.link,
                "title": entry.title,
                "snippet": entry.summary[:200]
            })
    except Exception as e:
        print("[Retriever] Arxiv failed:", str(e))

    # ---- Final fallback (never empty) ----
    if not documents:
        documents = [f"Research query: {query}. Generate insights from global knowledge."]
        sources = []

    return {"documents": documents, "sources": sources}
