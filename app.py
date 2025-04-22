import os
import csv
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

# Function to parse CSV file and extract URLs
def parse_csv(file):
    urls = []
    try:
        csv_file = file.stream.read().decode("utf-8")
        reader = csv.reader(csv_file.splitlines())
        for row in reader:
            if row and row[0]:
                urls.append(row[0].strip())  # Assuming URLs are in the first column
    except Exception as e:
        print(f"Error reading CSV: {e}")
    return urls

@app.route('/', methods=['GET', 'POST'])
def index():
    results = []
    if request.method == 'POST':
        urls_text = request.form['urls']
        if urls_text:
            urls = [url.strip() for url in urls_text.splitlines() if url.strip()]
        elif 'csv_file' in request.files:
            csv_file = request.files['csv_file']
            if csv_file:
                urls = parse_csv(csv_file)
        else:
            urls = []
        
        for url in urls:
            if not url.startswith("http"):
                url = "http://" + url
            results.append(get_seo_data(url))
    
    return render_template('index.html', results=results)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
