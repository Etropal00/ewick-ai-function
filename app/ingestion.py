from bs4 import BeautifulSoup
import httpx

def fetch_and_clean(url: str) -> dict:
    try:
        r = httpx.get(url, timeout=15.0, follow_redirects=True)
        r.raise_for_status()
    except Exception as e:
        return {"ok": False, "error": str(e), "url": url}

    soup = BeautifulSoup(r.text, "lxml")
    # Remove nav/footer/scripts
    for tag in soup(["script","style","noscript","header","footer","svg"]):
        tag.decompose()

    title = soup.title.string.strip() if soup.title and soup.title.string else ""
    # Join paragraphs and headings
    texts = []
    for el in soup.find_all(["h1","h2","h3","p","li"]):
        txt = el.get_text(" ", strip=True)
        if txt:
            texts.append(txt)
    body = "\n".join(texts)

    return {"ok": True, "title": title, "text": body, "url": url}
