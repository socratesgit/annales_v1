from typing import Tuple
from PIL import Image, ImageDraw
from pathlib import Path
import sys

MASK_DIR = Path.cwd() / "masks"
MASK_DIR.mkdir(exist_ok=True)

def calculate_x_y_width_height(width : float, height : float, option : str) -> Tuple[float, float, float, float]:
    if option == "top_half":
        x=0
        y=0
        width=width
        height=height/2
    elif option == "bottom_half":
        x=0
        y=height/2
        width=width
        height=height
    elif option == "left_half":
        x=0
        y=0
        width=width/2
        height=height
    elif option == "right_half":
        x=width/2
        y=0
        width=width
        height=height
    else:
        raise ValueError("Option not supported")
    
    return x, y, width, height

def mask_image(image : Image, option : str) -> Image:
    """
    Mask the image. Option can be top_half, bottom_half, left_half, right_half.
    """
    width, height = image.size

    #mask the image in half
    image_mask = Image.new('L', (width, height), color=255)
    draw = ImageDraw.Draw(image_mask)
    x, y, width, height = calculate_x_y_width_height(width, height, option)
    draw.rectangle((x, y, width, height), fill=0)
    image.putalpha(image_mask)

    return image

def main(image_path : Path, option : str) -> None:
    """
    Main function
    """
    image = Image.open(image_path)
    mask = mask_image(image, option)
    image.putalpha(mask)
    image.save(MASK_DIR / image_path.name)

if __name__ == "__main__":
    if(len(sys.argv) != 3):
        print("Usage: python mask.py <image_path> <option>")
        print("Options: top_half, bottom_half, left_half, right_half")
        sys.exit(1)
    
    image_path = Path(sys.argv[1])
    option = sys.argv[2]

    main(image_path, option)