import io
from base64 import b64decode
import os
import time
from typing import List
from PIL import Image
from . import openai_api, crop, mask

MAP_DIRECTION = {
    "right" : "right-half",
    "left" : "left-half",
    "top" : "top-half",
    "bottom" : "bottom-half",
}

def image_to_bytes(image : Image.Image) -> io.BytesIO:
    """
    Convert an image to bytes
    """
    image_bytes = io.BytesIO()
    image.save(image_bytes, format="PNG")
    image_bytes = image_bytes.getvalue()

    return image_bytes

def make_tile(image : Image.Image, prompt : str, direction : str, size : str) -> Image.Image:
    """
    Make a tile to the right of the image
    """ 
    direction = MAP_DIRECTION[direction]

    first_crop = crop.crop_image(image, direction)
    first_crop_bytes = image_to_bytes(first_crop)

    first_mask = mask.mask_image(first_crop, direction)
    first_mask_bytes = image_to_bytes(first_mask)

    first_edit = openai_api.edit_image(
        image=first_crop_bytes, 
        mask=first_mask_bytes, 
        prompt=prompt,
        n=1,
        size=size,
        ).pop()


    second_crop = crop.crop_image(first_edit, direction)
    second_crop_bytes = image_to_bytes(second_crop)
    second_mask = mask.mask_image(second_crop, direction)
    second_mask_bytes = image_to_bytes(second_mask)

    second_edit = openai_api.edit_image(
        image=second_crop_bytes, 
        mask=second_mask_bytes, 
        prompt=prompt,
        n=1,
        size=size
        ).pop()

    return second_edit

def expand(image : Image.Image, prompt : str, step : int = 1, direction : str = 'left') -> List[Image.Image]:
    """
    Expand one side of the image by a given number of tiles
    """
    list_of_images = []

    for i in range(0, step):
        list_of_images.append(make_tile(image, prompt, direction))

    return list_of_images

def tasselate_left(
                   image_left : Image.Image, 
                   image_center : Image.Image,
                   image_top : Image.Image, 
                   prompt : str,
                   size : str) -> Image.Image:
    
    t_r_left_image = crop.crop_image(image_left, "top-right-corner")
    t_l_center_image = crop.crop_image(image_center, "top-left-corner")     
    t_r_left_image_masked = mask.mask_image(t_r_left_image, "bottom-right-corner")
    t_l_center_image_masked = mask.mask_image(t_l_center_image, "bottom-left-corner")
    t1_to_be = t_r_left_image_masked.copy()
    t1_to_be.paste(t_l_center_image_masked, (0,0), t_l_center_image_masked)
    b_l_top_center_image = crop.crop_image(image_top, "bottom-left-corner")
    b_l_top_center_image_masked = mask.mask_image(b_l_top_center_image, "bottom-half")
    t1_to_be.paste(b_l_top_center_image_masked, (0,0), b_l_top_center_image_masked)

    t1_to_be_masked = mask.mask_image(t1_to_be, "top-left-corner")

    t1_to_be_bytes = image_to_bytes(t1_to_be)
    t1_to_be_masked_bytes = image_to_bytes(t1_to_be_masked)

    
    t1 = openai_api.edit_image(
        image=t1_to_be_bytes, 
        mask=t1_to_be_masked_bytes, 
        prompt=prompt,
        n=1,
        size=size
    ).pop()

    half_left_t1 = crop.crop_image(t1, "left-half")
    half_left_t1_masked = mask.mask_image(half_left_t1, "left-half")
    t2_to_be = crop.crop_image(image_left, "top-half")
    t2_to_be.paste(half_left_t1_masked, (0,0), half_left_t1_masked)
    t2_to_be_masked = mask.mask_image(t2_to_be, "top-left-corner")

    t2_to_be_bytes = image_to_bytes(t2_to_be)
    t2_to_be_masked_bytes = image_to_bytes(t2_to_be_masked)

    t2 = openai_api.edit_image(
        image=t2_to_be_bytes,
        mask=t2_to_be_masked_bytes,
        prompt=prompt,
        n=1,
        size=size
    ).pop()

    left_half_image_top = crop.crop_image(image_top, "left-half")
    left_half_image_top_masked = mask.mask_image(left_half_image_top, "left-half")
    t3_to_be = crop.crop_image(t1, "top-half")
    t3_to_be.paste(left_half_image_top, (0,0), left_half_image_top_masked)
    t3_to_be_masked = mask.mask_image(t3_to_be, "top-left-corner")

    t3_to_be_bytes = image_to_bytes(t3_to_be)
    t3_to_be_masked_bytes = image_to_bytes(t3_to_be_masked)

    t3 = openai_api.edit_image(
        image=t3_to_be_bytes,
        mask=t3_to_be_masked_bytes,
        prompt=prompt,
        n=1,
        size=size
    ).pop()
    

    left_half_t3 = crop.crop_image(t3, "left-half")
    left_half_t3_masked = mask.mask_image(left_half_t3, "bottom-half")
    t4_to_be = crop.crop_image(t2, "top-half")
    t4_to_be.paste(left_half_t3_masked, (0,0), left_half_t3_masked)
    t4_to_be_masked = mask.mask_image(t4_to_be, "top-left-corner")

    t4_to_be_bytes = image_to_bytes(t4_to_be)
    t4_to_be_masked_bytes = image_to_bytes(t4_to_be_masked)

    t4 = openai_api.edit_image(
        image=t4_to_be_bytes,
        mask=t4_to_be_masked_bytes,
        prompt=prompt,
        n=1,
        size=size
    ).pop()

    return t4

def tasselate_right(
                   image_right : Image.Image, 
                   image_center : Image.Image,
                   image_top : Image.Image, 
                   prompt : str,
                   size : str) -> Image.Image:
    
    t_l_right_image = crop.crop_image(image_right, "top-left-corner")
    t_r_center_image = crop.crop_image(image_center, "top-right-corner")
    t_l_right_image_masked = mask.mask_image(t_l_right_image, "bottom-left-corner")
    t_r_center_image_masked = mask.mask_image(t_r_center_image, "bottom-right-corner")
    t1_to_be = t_r_center_image_masked.copy()
    t1_to_be.paste(t_l_right_image_masked, (0,0), t_l_right_image_masked)
    b_r_top_center_image = crop.crop_image(image_top, "bottom-right-corner")
    b_r_top_center_image_masked = mask.mask_image(b_r_top_center_image, "bottom-half")
    t1_to_be.paste(b_r_top_center_image_masked, (0,0), b_r_top_center_image_masked)

    t1_to_be_masked = mask.mask_image(t1_to_be, "top-right-corner")

    t1_to_be_bytes = image_to_bytes(t1_to_be)
    t1_to_be_masked_bytes = image_to_bytes(t1_to_be_masked)

    t1 = openai_api.edit_image(
        image=t1_to_be_bytes,
        mask=t1_to_be_masked_bytes,
        prompt=prompt,
        n=1,
        size=size
    ).pop()

    half_right_t1 = crop.crop_image(t1, "right-half")
    half_right_t1_masked = mask.mask_image(half_right_t1, "right-half")
    t2_to_be = crop.crop_image(image_right, "top-half")
    t2_to_be.paste(half_right_t1_masked, (0,0), half_right_t1_masked)
    t2_to_be_masked = mask.mask_image(t2_to_be, "top-right-corner")

    t2_to_be_bytes = image_to_bytes(t2_to_be)
    t2_to_be_masked_bytes = image_to_bytes(t2_to_be_masked)

    t2 = openai_api.edit_image(
        image=t2_to_be_bytes,
        mask=t2_to_be_masked_bytes,
        prompt=prompt,
        n=1,
        size=size
    ).pop()

    half_right_image_top = crop.crop_image(image_top, "right-half")
    half_right_image_top_masked = mask.mask_image(half_right_image_top, "right-half")
    t3_to_be = crop.crop_image(t1, "top-half")
    t3_to_be.paste(half_right_image_top_masked, (0,0), half_right_image_top_masked)
    t3_to_be_masked = mask.mask_image(t3_to_be, "top-right-corner")

    t3_to_be_bytes = image_to_bytes(t3_to_be)
    t3_to_be_masked_bytes = image_to_bytes(t3_to_be_masked)

    t3 = openai_api.edit_image(
        image=t3_to_be_bytes,
        mask=t3_to_be_masked_bytes,
        prompt=prompt,
        n=1,
        size=size
    ).pop()

    half_right_t3 = crop.crop_image(t3, "right-half")
    half_right_t3_masked = mask.mask_image(half_right_t3, "right-half")
    t4_to_be = crop.crop_image(t2, "top-half")
    t4_to_be.paste(half_right_t3_masked, (0,0), half_right_t3_masked)
    t4_to_be_masked = mask.mask_image(t4_to_be, "top-right-corner") 

    t4_to_be_bytes = image_to_bytes(t4_to_be)
    t4_to_be_masked_bytes = image_to_bytes(t4_to_be_masked)

    t4 = openai_api.edit_image(
        image=t4_to_be_bytes,
        mask=t4_to_be_masked_bytes,
        prompt=prompt,
        n=1,
        size=size
    ).pop()

    return t4



 

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

    prompt = "a cat with a hat on a mat"

    image_center = Image.open("../feed/center/6_1853471379446242757.jpg")
    image_right = Image.open("../feed/right/6_1853471379446242757.jpg")
    image_left = Image.open("../feed/left/6_1853471379446242757.jpg")
    image_top = Image.open("../feed/center/7_1241827218317012271.jpg")

    print(image_center.size)




