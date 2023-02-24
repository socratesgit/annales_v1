import os
import sys
import json
import random
from datetime import datetime
from typing import List
from newsapi import NewsApiClient
from pathlib import Path

NEWS_DIR = Path.cwd() / 'data' / 'articles'
NEWS_DIR.mkdir(exist_ok=True)

TESTED_SOURCES = ['cnn','the-washington-post','fox-news','nbc-news']

newsapi = NewsApiClient(api_key=os.environ.get('NEWS_API_KEY'))

def get_source_random() -> str:
    '''
    Get a random source from the newsapi
    '''
    sources = newsapi.get_sources(
        category='general',
        language='en',
    )
    sources_ids = [source['id'] for source in sources['sources']]
    return random.choice(sources_ids)

def get_articles(num_articles : int, save : bool = False) -> List[dict]:
    '''
    Get n articles from the newsapi
    '''
    articles = newsapi.get_everything(
        #sources=get_source_random(),
        sources='the-washington-post',
        sort_by='popularity',
        page_size=num_articles,
        )

    if save:

        today = str(datetime.now().date())

        if not os.path.exists(NEWS_DIR/today):
            os.mkdir(NEWS_DIR/today)

        with open(NEWS_DIR/today/'news.json', 'w') as outfile:
            json.dump(articles['articles'], outfile)


    return articles['articles']

def get_top_headlines(num_headlines : int, save : bool = False) -> List[dict]:
    '''
    Get n top headlines from the newsapi
    '''
    source = random.choice(TESTED_SOURCES)
    top_headlines = newsapi.get_top_headlines(
        #sources=get_source_random(),
        sources=source,
        language='en',
        page_size=num_headlines,
        )

    if save:

        today = str(datetime.now().date())

        if not os.path.exists(NEWS_DIR/today):
            os.mkdir(NEWS_DIR/today)

        with open(NEWS_DIR/today/'top_headlines.json', 'w') as outfile:
            json.dump(top_headlines['articles'], outfile)

    return top_headlines['articles']
        

if __name__ == '__main__':
    #print(get_source_random())
    #print(get_articles(5, save=True))
    print(get_top_headlines(5, save=True))


#sources = newsapi.get_sources()
#
#for source in sources['sources']:
#    print(source['name'] + ' - ' + source['id'] + ' - ' + source['url'])