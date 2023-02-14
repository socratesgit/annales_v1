import os
from pathlib import Path
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

MASK_DIR = Path.cwd() / "edits"
MASK_DIR.mkdir(exist_ok=True)

PROMPT = '''
        A fisherman is fishing in a river.
        He sees a body floating down the river.
        Watercolor painting'''

mask_path = "masks/256x256-2023-02-12T18:02:02.758145-0.png"
image_path ="cropped/256x256-2023-02-12T18:02:02.758145-0.png"

response = openai.Image.create_edit(
  image=open(image_path, "rb"),
  mask=open(mask_path, "rb"),
  prompt=PROMPT,
  n=1,
  size="256x256",
)

image_url = response['data'][0]['url']

print(image_url)

