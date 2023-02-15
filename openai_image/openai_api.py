import io
from base64 import b64decode
from datetime import datetime
from typing import List
from PIL import Image
import json
import os
import sys
from pathlib import Path
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

IMAGE_DIR = Path.cwd() / 'data' / 'images'
IMAGE_DIR.mkdir(exist_ok=True)

EDIT_DIR = Path.cwd() / 'data' / 'edits'
EDIT_DIR.mkdir(exist_ok=True)

SIZES = {
    "small" : '256x256',
    "medium" : '512x512',
    "large" : '1024x1024',
}

def generate_images(prompt : str, size : str = 'small', n : int = 1, save : bool = False) -> List[Image.Image]:
    """
    Generate images from a prompt
    """
    try:
        image_resp = openai.Image.create(
            prompt=prompt, 
            n=n, 
            size=SIZES[size],
            response_format="b64_json",
        )
    except openai.error.OpenAIError as e:
        print(e.http_status)
        print(e.error)

    finally:

        if save:

            prompt_dir = IMAGE_DIR / prompt[:10]
            prompt_dir.mkdir(exist_ok=True)

            list_images = []

            for index, image_dict in enumerate(image_resp["data"]):
                image_data = b64decode(image_dict["b64_json"])
                list_images.append(Image.open(io.BytesIO(image_data)))
                image_file = prompt_dir / f"{prompt[:10]}-{index}.png"
                with open(image_file, mode="wb") as png:
                    png.write(image_data)

        return list_images

def edit_image(image : io.BytesIO, mask : io.BytesIO, prompt : str, n : int = 1, size : str = 'small', save : bool = False) -> List[Image.Image]:
    """
    Edit an image with a mask
    """
    try:
        image_resp = openai.Image.create_edit(
            image=image,
            mask=mask,
            prompt=prompt,
            n=n,
            size=SIZES[size],
            response_format="b64_json",
        )

    except openai.error.OpenAIError as e:
        print(e.http_status)
        print(e.error)

    finally:

        if save:

            prompt_dir = EDIT_DIR / prompt[:10]
            prompt_dir.mkdir(exist_ok=True)

            list_images = []

            for index, image_dict in enumerate(image_resp["data"]):
                    image_data = b64decode(image_dict["b64_json"])
                    list_images.append(Image.open(io.BytesIO(image_data)))
                    image_file = prompt_dir / f"{prompt[:10]}-{index}.png"
                    with open(image_file, mode="wb") as png:
                        png.write(image_data)

        return list_images

def generate_text(prompt : str, n : int = 1) -> dict:
    """
    Generate text from a prompt
    """
    try:
        text_resp = openai.Completion.create(
            model="davinci",
            prompt=prompt,
            max_tokens=1000,
            n=n,
            temperature=0.7,
        )

    except openai.error.OpenAIError as e:
        print(e.http_status)
        print(e.error)

    finally:

        return text_resp

def edit_text(input : str, instruction : str) -> dict:
    """
    Edit text
    """
    try:
        text_resp = openai.Edit.create(
            model="text-davinci-edit-001",
            input=input,
            instruction=instruction,
        )

    except openai.error.OpenAIError as e:
        print(e.http_status)
        print(e.error)

    finally:

        return text_resp
    



if __name__ == "__main__":
    input='''
    Tom Brady's future is about to get awkward. The Washington Post.
Tom Brady sounds less like he's taken his last snap and more like he's uncertain where his next one will be. Yahoo Sports.
Tom Brady Fan Veronika Rajek Is Pumped For W
    '''
    instruction = '''
    comment on this piece of news as if you were a pagan Roman historian of the imperial era
    '''

    text_resp = edit_text(input, instruction)
    

    print(text_resp)

