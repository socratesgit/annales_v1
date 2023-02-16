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

def generator_next_compliant_headline():
    '''
    Generator that yields the next headline that is compliant with OpenAI's policies.
    '''
    top_headlines = news.get_top_headlines(20)
    for headline in top_headlines:
        yield headline['title']
        #is_compliant = openai_api.is_compliant(headline['title'])
        #if is_compliant:
        #    yield headline

def current_index_and_image(dir : Path):
    '''
    Get the current index and image path for a given directory.
    '''
    current_index = 0
    current_image_path = None
    for file in dir.iterdir():
        #if file is png 
        if file.suffix == ".png":
            #split file name on _ and get first element
            index = int(file.name.split("_")[0])
            if index > current_index or current_index == 0:
                current_index = index
                current_image_path = file
    return current_index, current_image_path

def generate_next_feed_line():
    #prompt = decorate_prompt(random.choice(PROMPTS))
    prompts = news.get_top_headlines(20)
    current_index, _ = current_index_and_image(CENTER_DIR)
    try:

        prompt = create_caption(prompts.pop())
        while not openai_api.is_compliant(prompt):
            if prompts:
                prompt = create_caption(prompts.pop())
            else:
                prompts = news.get_top_headlines(20)

        print(f"Generating center image for {prompt}")
        center_image = openai_api.generate_images(
                                                prompt=prompt,
                                                #prompt=next(prompt),
                                                size='small',
                                                n=1
                                                ).pop()
        center_image.save(CENTER_DIR / f"{current_index + 1}_{prompt}.png")
        print("Generated center image")
    except Exception as e:
        print(e)
        return
    else:
        try:
            print("Generating left and right images")
            left_image = outpaint.make_tile(center_image, 
                                                prompt=prompt, 
                                                direction="right")
            left_image.save(LEFT_DIR / f"{current_index + 1}_{prompt}.png")
            right_image = outpaint.make_tile(center_image, 
                                             prompt=prompt, 
                                             direction="left")
            right_image.save(RIGHT_DIR / f"{current_index + 1}_{prompt}.png")
            print("Generated left and right images")
        except Exception as e:
            print(e)
            return

def generate_next_feed_top():

    dir_list_reverse = DIR_LIST[::-1]
    for dir in dir_list_reverse:
        
        current_index, current_image_path = current_index_and_image(dir)

        if current_image_path:
            print(f"Making tile for {current_image_path.name}")
            try:
                prompt = random.choice(PROMPTS)
                current_image = Image.open(current_image_path)
                next_image = outpaint.make_tile(current_image, prompt, "top")
                next_image.save(dir / f"{current_index + 1}_{prompt}.png")
            except Exception as e:
                print(e)
        else:
            print("No current feed image found")
        
            
def upload_feed():

    insta_bot = bot.InstaBot()
    dir_list_reverse = DIR_LIST[::-1]
    for dir in dir_list_reverse:

        _, current_image = current_index_and_image(dir)
            
        if current_image:

            print("uploading " + dir.name + " - " + current_image.name)
            try:
                insta_bot.upload_photo(path=current_image, 
                                        caption=current_image.name.split("_")[1]
                                        )
                print("uploaded  " + dir.name + " - " + current_image.name)
                time.sleep((random.random() + 1) * 10)
            except Exception as e:
                print(e)
                pass


if __name__ == "__main__":
    generate_next_feed_line()
    #upload_feed()