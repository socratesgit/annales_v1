import os
import sys
import json
from datetime import datetime
from newsapi import NewsApiClient
from pathlib import Path

NEWS_DIR = Path(__file__).parent / 'articles'
NEWS_DIR.mkdir(exist_ok=True)

newsapi = NewsApiClient(api_key=os.environ.get('NEWS_API_KEY'))

def get_articles(num_articles):
    
    articles = newsapi.get_everything(
        sources='the-washington-post',
        sort_by='popularity',
        language='en',
        page_size=num_articles,
        )

    today = str(datetime.now().date())

    os.mkdir(NEWS_DIR/today)
    with open(NEWS_DIR/today/'news.json', 'w') as outfile:
        json.dump(articles['articles'], outfile)


    return articles['articles']


#sources = newsapi.get_sources()
#
#for source in sources['sources']:
#    print(source['name'] + ' - ' + source['id'] + ' - ' + source['url'])