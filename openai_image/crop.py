from typing import Tuple
from PIL import Image
from pathlib import Path

import sys

PNG_FILE = Path.cwd() / "images" / "256x256-2023-02-12T18:02:02.758145" / "256x256-2023-02-12T18:02:02.758145-0.png"
CROP_DIR = Path.cwd() / "cropped"

CROP_DIR.mkdir(exist_ok=True)

def calculate_x_y_w_h(width : float, height : float, option : str) -> Tuple[float, float, float, float]:
    if option == "top_half":
        x=0
        y=-height/2
        w=width
        h=height/2
    elif option == "bottom_half":
        x=0
        y=height/2
        w=width
        h=height+(height/2)
    elif option == "left_half":
        x=-width/2
        y=0
        w=width/2
        h=height
    elif option == "right_half":
        x=width/2
        y=0
        w=width+(width/2)
        h=height
    else:
        raise ValueError("Option not supported")
    
    return x, y, w, h

def crop_image(image : Image, option : str) -> Image:
    """
    Crop the image. Option can be top_half, bottom_half, left_half, right_half.
    """
    width, height = image.size

    x, y, w, h = calculate_x_y_w_h(width, height, option)

    #crop the image in half
    image_crop_outside = image.crop((x, y, w, h))

    return image_crop_outside

def main(image_path : Path, option : str) -> None:
    """
    Crop the image in half based on the option and save it in cropped directory
    """
    image = Image.open(image_path)

    cropped_image = crop_image(image, option)

    cropped_image.save(CROP_DIR / image_path.name)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python3 crop.py <image_path> <option>")
        sys.exit(1)
    
    image_path = Path(sys.argv[1])
    option = sys.argv[2]

    main(image_path, option)