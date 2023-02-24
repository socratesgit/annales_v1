import os
import random
import time
from PIL import Image
from openai_image import openai_api, outpaint
from news import news
from instagram_bot import bot
from pathlib import Path

DATA_DIR = Path.cwd() / 'data'

DATA_DIR.mkdir(exist_ok=True)

FEED_DIR = Path.cwd() / 'feed'

FEED_DIR.mkdir(exist_ok=True)

RIGHT_DIR = Path.cwd() / 'feed' / 'right'
CENTER_DIR = Path.cwd() / 'feed' / 'center'
LEFT_DIR = Path.cwd() / 'feed' / 'left'

RIGHT_DIR.mkdir(exist_ok=True)
CENTER_DIR.mkdir(exist_ok=True)
LEFT_DIR.mkdir(exist_ok=True)

DIR_LIST = [RIGHT_DIR, CENTER_DIR, LEFT_DIR]

PROMPTS = [
    "Tesla might have revealed the Cybertruck frame in a new video about the automaker’s robots.\n more…\nThe post Did Tesla leak the Cybertruck frame with this robot? appeared first on Electrek.",
    "As AI hype hits a fever pitch, CNBC's Brandon Gomez and Fahiemah Al-Ali kick off a conversation around the widespread interest in the technology with Paper c...",
    "Doge, Floki and SHIB are up, while BONK is flat after Musk declares his dog Floki is an amazing CEO of Twitter and “better than that other guy.”",
    "Egg prices have surged 70% in January on an annual basis. Egg prices have been on the rise over the past year due to inflation and continued outbreaks of bird flu.",
    "Stocks making the biggest moves midday: Roblox, Airbnb, Barclays, Silvergate Capital & more - CNBC",
    "The U.S. economy is expected to grow at a 4.5% annual rate in the fourth quarter, according to the Atlanta Fed's GDPNow forecast released on Wednesday.",
]

AESTHETICS = open("aesthetics.txt", "r").read().splitlines()
ART_MOVEMENTS = open("art_movements.txt", "r").read().splitlines()

PROMPT_DECORATOR = "in the style of "



def decorate_prompt(prompt : str) -> str:
    '''
    Decorate the prompt with the prompt decorator.
    '''
    return PROMPT_DECORATOR + random.choice(AESTHETICS) + ": \n\"" + prompt + "\"" + "\n"

def create_caption(article : dict) -> str:
    '''
    Create a caption for an article.
    '''
    header = f"{article['title']} - {article['source']['name']}\n"
    body = f"{article['description']}"
    return header + body
    #decorated_prompt = decorate_prompt(header + body)
    #text = openai_api.generate_text(decorated_prompt, 1)
    #return text['choices'][0]['text']

def current_index_and_image(dir : Path):
    '''
    Get the current index and image path for a given directory.
    '''
    current_index = 0
    current_image_path = None
    for file in dir.iterdir():
        #if file is png 
        if file.suffix == ".jpg":
            #split file name on _ and get first element
            index = int(file.name.split("_")[0])
            if index > current_index or current_index == 0:
                current_index = index
                current_image_path = file
    return current_index, current_image_path

def generate_next_feed_line(prompt : str, size : str):
    '''
    Generate the next feed line. Horizontal coherence only!
    '''

    current_index, _ = current_index_and_image(CENTER_DIR)
    prompt_hash = hash(prompt)
    try:

        print(f"Generating center image for {prompt}")
        center_image = openai_api.generate_images(
                                                prompt=prompt,
                                                size=size,
                                                n=1
                                                ).pop()
        center_image.save(CENTER_DIR / f"{current_index + 1}_{prompt_hash}.jpg")
        print("Generated center image")
    except Exception as e:
        print(e)
        return
    else:
        try:
            print("Generating left and right images")
            left_image = outpaint.make_tile(center_image, 
                                                prompt=prompt, 
                                                direction="right",
                                                size=size)
            left_image.save(LEFT_DIR / f"{current_index + 1}_{prompt_hash}.jpg")
            right_image = outpaint.make_tile(center_image, 
                                             prompt=prompt, 
                                             direction="left",
                                             size=size)
            right_image.save(RIGHT_DIR / f"{current_index + 1}_{prompt_hash}.jpg")
            print("Generated left and right images")
        except Exception as e:
            print(e)
            for dir in DIR_LIST:
                for file in dir.iterdir():
                    if file.name.split("_")[0] == str(current_index + 1):
                        file.unlink()


def generate_next_feed_top(prompt : str, size : str):
    '''
    Generate the next feed line. Vertical coherence only!
    '''
    prompt_hash = hash(prompt)
    dir_list_reverse = DIR_LIST[::-1]
    for dir in dir_list_reverse:
        
        current_index, current_image_path = current_index_and_image(dir)

        if current_image_path:
            print(f"Making tile for {current_image_path.name}")
            try:
                current_image = Image.open(current_image_path)
                next_image = outpaint.make_tile(current_image, prompt, "top", size)
                next_image.save(dir / f"{current_index + 1}_{prompt_hash}.jpg")
            except Exception as e:
                print(e)
                for file in dir.iterdir():
                    if file.name.split("_")[0] == str(current_index + 1):
                        file.unlink()
        else:
            print("No current feed image found")


def generate_next_feed_tasselate(prompt : str, size : str):
    '''
    Generate the next feed line. Vertical and horizontal coherence.
    '''
    prompt_hash = hash(prompt)
    center_current_index, center_image_name = current_index_and_image(CENTER_DIR)
    left_current_index, left_image_name = current_index_and_image(LEFT_DIR)
    right_current_index, right_image_name = current_index_and_image(RIGHT_DIR)

    if center_image_name and left_image_name and right_image_name:
        print(f"Making tasselate for {center_image_name.name}")
        print(f"with prompt: {prompt}")
        try:
            center_image = Image.open(center_image_name)
            #something has to be fixed...
            left_image = Image.open(right_image_name)
            right_image = Image.open(left_image_name)
            
            next_center_image = outpaint.make_tile(center_image, prompt, "top", size)
            next_left_image = outpaint.tasselate_left(left_image, center_image, next_center_image, prompt, size)
            next_right_image = outpaint.tasselate_right(right_image, center_image, next_center_image, prompt, size)

            next_center_image.save(CENTER_DIR / f"{center_current_index + 1}_{prompt_hash}.jpg")
            next_left_image.save(RIGHT_DIR / f"{left_current_index + 1}_{prompt_hash}.jpg")
            next_right_image.save(LEFT_DIR / f"{right_current_index + 1}_{prompt_hash}.jpg")

        except Exception as e:
            print(e)
            for dir in DIR_LIST:
                for file in dir.iterdir():
                    if file.name.split("_")[0] == str(center_current_index + 1):
                        file.unlink()


def upload_feed(caption : str):
    '''
    Upload the feed to instagram.
    '''
    insta_bot = bot.InstaBot()

    dir_list_reverse = DIR_LIST[::-1]

    for dir in dir_list_reverse:

        _, current_image = current_index_and_image(dir)
            
        if current_image:

            print("uploading " + dir.name + " - " + current_image.name)
            try:
                insta_bot.upload_photo(path=current_image, 
                                        caption=caption
                                        )
                print("uploaded  " + dir.name + " - " + current_image.name)
                time.sleep((random.random() + 1) * 10)
            except Exception as e:
                print(e)
                pass

def test():
    articles = news.get_top_headlines(10)
    if not articles:
        print("No articles found")
        exit(1)
    prompt_selected = None
    article_selected = None
    while True:
        article = articles.pop()
        if openai_api.is_compliant(article["title"] + " - " + article["description"]):
            prompt_selected = article["title"] + " - " + article["description"]
            article_selected = article
            break
    if not prompt_selected:
        print("No compliant articles found")
        exit(1)

    generate_next_feed_line(
        prompt=decorate_prompt(prompt_selected),
        size="large"
    )
    upload_feed(
        caption= create_caption(article_selected)
    )
    
    while True:
        article = articles.pop()
        if openai_api.is_compliant(article["title"] + " - " + article["description"]):
            prompt_selected = article["title"] + " - " + article["description"]
            article_selected = article
            break
    if not prompt_selected:
        print("No compliant articles found")
        exit(1)

    generate_next_feed_tasselate(
        prompt=decorate_prompt(prompt_selected),
        size="large"
    )
    upload_feed(
        caption= create_caption(article_selected)
    )

if __name__ == "__main__": 
    
    articles = news.get_top_headlines(10)

    if not articles:
        print("No articles found")
        exit(1)

    prompt_selected = None
    article_selected = None

    while True:
        article = articles.pop()
        if openai_api.is_compliant(article["description"]):
            prompt_selected = article["description"]
            article_selected = article
            break

    if not prompt_selected:
        print("No compliant articles found")
        exit(1)

    generate_next_feed_line(
        prompt=decorate_prompt(prompt_selected),
        size="large"
    )
    upload_feed(
        caption=create_caption(article_selected)
    )

    
    