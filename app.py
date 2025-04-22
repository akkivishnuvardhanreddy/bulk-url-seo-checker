import os
from flask import Flask, request, render_template
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def get_seo_data(url):
    try:
        response = requests.get(url, timeout=10)
        status = response.status_code
        soup = BeautifulSoup(response.text, 'html.parser')

        title = soup.title.string.strip() if soup.title else "N/A"
        description = soup.find("meta", attrs={"name": "description"})
        description = description["content"].strip() if description else "N/A"

        canonical = soup.find("link", rel="canonical")
        canonical = canonical["href"].strip() if canonical else "N/A"

        h1 = soup.find("h1")
        h1 = h1.text.strip() if h1 else "N/A"

        # Basic robots meta check
        meta_robots = soup.find("meta", attrs={"name": "robots"})
        if meta_robots and "noindex" in meta_robots.get("content", "").lower():
            indexability = "Noindex"
        else:
            indexability = "Indexable"

        return {
            "url": url,
            "status": status,
            "title": title,
            "description": description,
            "canonical": canonical,
            "h1": h1,
            "indexability": indexability
        }

    except Exception as e:
        return {
            "url": url,
            "status": "Error",
            "title": "Error",
            "description": str(e),
            "canonical": "N/A",
            "h1": "N/A",
            "indexability": "Unknown"
        }

@app.route('/', methods=['GET', 'POST'])
def index():
    results = []
    if request.method == 'POST':
        urls_text = request.form['urls']
        urls = [url.strip() for url in urls_text.splitlines() if url.strip()]
        for url in urls:
            if not url.startswith("http"):
                url = "http://" + url
            results.append(get_seo_data(url))
    return render_template('index.html', results=results)

if __name__ == '__main__':
    # For Render.com - use dynamic port
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
