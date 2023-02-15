from base64 import b64decode
import random
import time
from PIL import Image
from openai_image import openai_api, outpaint, merge
from news import news
from instagram_bot import bot
from pathlib import Path

FEED_DIR = Path.cwd() / 'feed'

FEED_DIR.mkdir(exist_ok=True)

RIGHT_DIR = Path.cwd() / 'feed' / 'right'
CENTER_DIR = Path.cwd() / 'feed' / 'center'
LEFT_DIR = Path.cwd() / 'feed' / 'left'

RIGHT_DIR.mkdir(exist_ok=True)
CENTER_DIR.mkdir(exist_ok=True)
LEFT_DIR.mkdir(exist_ok=True)

DIR_LIST = [RIGHT_DIR, CENTER_DIR, LEFT_DIR]

PROMPT = [
    "Tesla might have revealed the Cybertruck frame in a new video about the automaker’s robots.\n more…\nThe post Did Tesla leak the Cybertruck frame with this robot? appeared first on Electrek.",
    "As AI hype hits a fever pitch, CNBC's Brandon Gomez and Fahiemah Al-Ali kick off a conversation around the widespread interest in the technology with Paper c...",
    "Doge, Floki and SHIB are up, while BONK is flat after Musk declares his dog Floki is an amazing CEO of Twitter and “better than that other guy.”",
    "Egg prices have surged 70% in January on an annual basis. Egg prices have been on the rise over the past year due to inflation and continued outbreaks of bird flu.",
    "Stocks making the biggest moves midday: Roblox, Airbnb, Barclays, Silvergate Capital & more - CNBC",
    "The U.S. economy is expected to grow at a 4.5% annual rate in the fourth quarter, according to the Atlanta Fed's GDPNow forecast released on Wednesday.",
]

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

def feed_seed():

    articles = news.get_top_headlines(10)
    first_image_created = False
    
    for index,article in enumerate(articles):
        print(f"Making tile for {article['description']}")
        if not first_image_created:
            print(f"Making tile for {article['description']}")
            try:
                image = openai_api.generate_images(
                                                    prompt=article["title"],
                                                    size='small',
                                                    n=1
                                                    ).pop()
                image.save(f"{index}_{article['title']}.png")
                first_image_created = True
                continue
            except Exception as e:
                continue
        
        try:
            image = outpaint.make_tile(image, article["title"], "left")
            image.save(f"{index}_{article['title']}.png")
        except Exception as e:
            continue

def generate_next_feed():
    current_index = 0
    current_image = None
    for dir in DIR_LIST:
        for file in dir.iterdir():
            #if file is png 
            if file.suffix == ".png":
                #split file name on _ and get first element
                index = int(file.name.split("_")[0])
                if index > current_index:
                    current_index = index
                    current_image = file
    if current_image:
        print(f"Making tile for {current_image.name}")
        try:
            prompt = random.choice(PROMPT)
            image = outpaint.make_tile(image, prompt, "top")
            image.save(f"{index}_{prompt}.png")
        except Exception as e:
            pass
        
            
def upload_feed():
    dir_list_reverse = DIR_LIST[::-1]
    for dir in dir_list_reverse:
        for file in dir.iterdir():
            #if file is png 
            if file.suffix == ".png":
                #split file name on _ and get first element
                index = int(file.name.split("_")[0])
                if index > current_index:
                    current_index = index
                    current_image = file
    if current_image:
        print("uploading feed")
        try:
            bot.upload_photo(path=current_image, caption=current_image.name.split("_")[1])
            print("uploaded feed")
            time.sleep(60)
        except Exception as e:
            pass


if __name__ == "__main__":
    upload_feed()
