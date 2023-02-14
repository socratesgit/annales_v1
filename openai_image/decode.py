import json
from base64 import b64decode
from pathlib import Path

DATA_DIR = Path.cwd() / "responses"
JSON_FILE = DATA_DIR / "256x256-2023-02-12T18:02:02.758145.json"
IMAGE_DIR = Path.cwd() / "images" / JSON_FILE.stem

IMAGE_DIR.mkdir(parents=True, exist_ok=True)

with open(JSON_FILE, mode="r", encoding="utf-8") as file:
    image_resp = json.load(file)

for index, image_dict in enumerate(image_resp["data"]):
    image_data = b64decode(image_dict["b64_json"])
    image_file = IMAGE_DIR / f"{JSON_FILE.stem}-{index}.png"
    with open(image_file, mode="wb") as png:
        png.write(image_data)
