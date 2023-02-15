from base64 import b64decode
from PIL import Image
from openai_image import openai_api, outpaint, merge
from news import news
from pathlib import Path

FEED_DIR = Path.cwd() / 'feed'

FEED_DIR.mkdir(exist_ok=True)

RIGHT_DIR = Path.cwd() / 'feed' / 'right'
CENTER_DIR = Path.cwd() / 'feed' / 'center'
LEFT_DIR = Path.cwd() / 'feed' / 'left'

RIGHT_DIR.mkdir(exist_ok=True)
CENTER_DIR.mkdir(exist_ok=True)
LEFT_DIR.mkdir(exist_ok=True)

PROMPT_DECORATOR = "Comment on the following piece of news as if you were a Roman pagan historian of the imperial era:\n"

def decorate_prompt(prompt):
    return PROMPT_DECORATOR + "\"" + prompt + "\"" + "\n"

def create_feed():
    articles = news.get_top_headlines(10)

    first_image_created = False

    list_images = []

    for index,article in enumerate(articles):
        if index > 4:
            break
        prompt = create_caption(article)
        if not first_image_created: 
            print(f"Making tile for {article['description']}")
            try:
                image = openai_api.generate_images(
                                                    prompt=prompt,
                                                    size='small',
                                                    n=1
                                                    ).pop()
                list_images.append(image)
                first_image_created = True
            except Exception as e:
                continue
                
        else:
            print(f"Making tile for {article['description']}")
            try:
                prompt = article["title"]
                image = outpaint.make_tile(image, prompt, "left")
                list_images.append(image)
            except Exception as e:
                continue
        
        image.save(f"outpaint-{index}.png")
    
    
def create_caption(article):
    header = f"{article['title']} - {article['source']['name']}\n"
    body = f"{article['description']}"
    return header + body
    #decorated_prompt = decorate_prompt(header + body)
    #text = openai_api.generate_text(decorated_prompt, 1)
    #return text['choices'][0]['text']

def generate_feed():
    articles = news.get_top_headlines(3)
    for article in articles:
        image = openai_api.generate_images(
                                            prompt=article["title"],
                                            size='small',
                                            n=1
                                            ).pop()
        image.save(f"feed/{article['title']}.png")
    


if __name__ == "__main__":
    generate_feed()
