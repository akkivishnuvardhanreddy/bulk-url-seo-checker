from flask import Flask, request, render_template
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    if request.method == "POST":
        urls = request.form.get("urls", "").splitlines()
        for url in urls:
            try:
                res = requests.get(url, timeout=10)
                soup = BeautifulSoup(res.text, "html.parser")
                title = soup.title.string if soup.title else "No Title"
                meta = soup.find("meta", attrs={"name": "description"})
                desc = meta["content"] if meta else "No Meta Description"
                canonical = soup.find("link", rel="canonical")
                canon = canonical["href"] if canonical else "No Canonical"
                h1 = soup.find("h1").text.strip() if soup.find("h1") else "No H1"
                results.append({
                    "url": url,
                    "status": res.status_code,
                    "title": title,
                    "description": desc,
                    "canonical": canon,
                    "h1": h1
                })
            except Exception as e:
                results.append({
                    "url": url,
                    "status": "Error",
                    "title": str(e),
                    "description": "-",
                    "canonical": "-",
                    "h1": "-"
                })
    return render_template("index.html", results=results)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
