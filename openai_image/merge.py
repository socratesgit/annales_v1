from datetime import datetime
from typing import List
from PIL import Image
from pathlib import Path
import sys

MERGE_DIR = Path.cwd() / 'data' / 'merged'

MERGE_DIR.mkdir(exist_ok=True)

def merge_in_place(image1 : Image.Image, image2 : Image.Image) -> Image.Image:
    """
    Paste one image on top of another image in place.
    """
    width1, height1 = image1.size
    width2, height2 = image2.size

    image1.paste(image2, (0,0))

    return image1


def merge_right(image1 : Image.Image, image2 : Image.Image) -> Image.Image:
    """
    Merge two images together. The first image is on the left, the second image is on the right.
    """

    width1, height1 = image1.size
    width2, height2 = image2.size

    new_image = Image.new('RGB',(width1+width2, height1), (250,250,250))

    new_image.paste(image1, (0,0))
    new_image.paste(image2, (width1,0))

    return new_image

def merge_bottom(image1 : Image.Image, image2 : Image.Image) -> Image.Image:
    """
    Merge two images together. The first image is on the top, the second image is on the bottom.
    """
    width1, height1 = image1.size
    width2, height2 = image2.size

    new_image = Image.new('RGB',(width1, height1+height2), (250,250,250))

    new_image.paste(image1, (0,0))
    new_image.paste(image2, (0,height1))

    return new_image

def merge_left_list(image_list : List[Image.Image]) -> Image.Image:
    """
    Merge a list of images together. The first image is on the left, the second image is on the right.
    """
    width, height = image_list[0].size

    new_image = Image.new('RGB',(len(image_list)*width, height), (250,250,250))

    for i in range(len(image_list)):
        new_image.paste(image_list[i], (i*width,0))

    return new_image

def merge_top_list(image_list : List[Image.Image]) -> Image.Image:
    """
    Merge a list of images together. The first image is on the top, the second image is on the bottom.
    """
    width, height = image_list[0].size

    new_image = Image.new('RGB',(width, len(image_list)*height), (250,250,250))

    for i in range(len(image_list)):
        new_image.paste(image_list[i], (0,i*height))

    return new_image

OPTIONS = {
    'right': merge_right,
    'bottom': merge_bottom,
    'in-place': merge_in_place,
}

def main(image1_path : str, image2_path : str, merge_type : str = 'right') -> None:
    """
    Merge two images together
    """
    image1 = Image.open(image1_path)
    image2 = Image.open(image2_path)

    new_image = OPTIONS[merge_type](image1, image2)

    new_image.save(MERGE_DIR/f"merged_{datetime.now()}.png")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python merge.py <image1> <image2> <merge_type>")
        sys.exit(1)

    main(sys.argv[1], sys.argv[2], sys.argv[3])

