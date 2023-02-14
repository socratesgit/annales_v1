import io
from base64 import b64decode
import time
from typing import List
from PIL import Image
from openai_api import edit_image
from crop import crop_image
from mask import mask_image
from merge import merge_right, merge_bottom

MAP_DIRECTION = {
    "right" : "right_half",
    "left" : "left_half",
    "top" : "top_half",
    "bottom" : "bottom_half",
}

def image_to_bytes(image : Image) -> io.BytesIO:
    """
    Convert an image to bytes
    """
    image_bytes = io.BytesIO()
    image.save(image_bytes, format="PNG")
    image_bytes = image_bytes.getvalue()

    return image_bytes

def make_tile(image : Image, prompt : str, direction : str) -> Image:
    """
    Make a tile to the right of the image
    """ 
    direction = MAP_DIRECTION[direction]

    first_crop = crop_image(image, direction)
    first_crop_bytes = image_to_bytes(first_crop)

    first_mask = mask_image(first_crop, direction)
    first_mask_bytes = image_to_bytes(first_mask)

    first_edit = edit_image(first_crop_bytes, first_mask_bytes, prompt)

    image_dict = first_edit["data"][0]
    image_data = b64decode(image_dict["b64_json"])
    image_data = Image.open(io.BytesIO(image_data))


    second_crop = crop_image(image_data, direction)
    second_crop_bytes = image_to_bytes(second_crop)
    second_mask = mask_image(second_crop, direction)
    second_mask_bytes = image_to_bytes(second_mask)

    second_edit = edit_image(second_crop_bytes, second_mask_bytes, prompt)

    image_data = b64decode(second_edit["data"][0]["b64_json"])
    second_edit = Image.open(io.BytesIO(image_data))

    return second_edit

def expand(image : Image, prompt : str, step : int = 1, direction : str = 'left') -> List[Image.Image]:
    """
    Expand one side of the image by a given number of tiles
    """
    list_of_images = []

    for i in range(0, step):
        list_of_images.append(make_tile(image, prompt, direction))

    return list_of_images

def main(image_path : str, prompt : str, step : int = 1) -> None:
    """
    Expand an image in a given direction by a given number of tiles
    """
    image = Image.open(image_path)
    current_image = image
    for i in range(0, step):
        current_image = make_tile(current_image, prompt, "right")
        current_image.save("{0}.png".format(i))
        time.sleep(1)
    #ist_of_images = expand(image, prompt, step, direction)
    #ew_image = merge_right(image, list_of_images[0])

    #for i in range(1, len(list_of_images)):
    #    new_image = merge_right(new_image, list_of_images[i])



if __name__ == "__main__":
    main(
        "images/256x256-2023-02-12T18:02:02.758145/256x256-2023-02-12T18:02:02.758145-0.png", 
        "A cat is sitting on a table.",
    )