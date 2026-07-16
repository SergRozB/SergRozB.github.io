import pandas as pd;
import requests;

article = "Burmese%E2%80%93Siamese_wars"  # Wikipedia article title, spaces become underscores automatically below
project = "en.wikipedia.org"
start = "20250101"  # YYYYMMDD
end = "20260630"
url = f"https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/{project}/all-access/all-agents/{article.replace(' ', '_')}/monthly/{start}/{end}"
headers = {
    'User-Agent': 'WarWordleWebsite (serg.rozalenbreton@gmail.com)'
}

response = requests.get(url, headers=headers)
data = response.json()

# Calculate total views from the daily breakdown
print("Data:", data)
total_views = sum(item['views'] for item in data['items'])
print("Total views:", total_views)