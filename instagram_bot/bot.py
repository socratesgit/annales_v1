from instagrapi import Client
from instagrapi.types import Usertag, Location
import time
import os

email = os.environ.get("INSTA_EMAIL")
password = os.environ.get("INSTA_PASSWORD")
username = os.environ.get("INSTA_USERNAME")

cl = Client()
cl.login(email, password)

user = cl.user_info_by_username(username)

location = Location(name="Milan, Italy", lat=45.4642, lng=9.1927)
usertags = [Usertag(user_id=user.pk, position=[0.5, 0.5])]


#cl.photo_upload(
#                "photo.png", 
#                "caption",
#                location=Location(name="Milan, Italy", lat=45.4642, lng=9.1927),
#                usertags=[Usertag(user_id=user.pk, position=[0.5, 0.5])],
#                )

def upload_photo(path, caption):
    return cl.photo_upload(
                path, 
                caption, 
                location=location, 
                usertags=usertags
        )

