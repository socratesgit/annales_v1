from instagrapi import Client
from instagrapi.types import Usertag, Location
from PIL import Image
import time
import os

class InstaBot:
    def __init__(self):
        self.cl = Client()
        self.email = os.environ.get("INSTA_EMAIL")
        self.password = os.environ.get("INSTA_PASSWORD")
        self.username = os.environ.get("INSTA_USERNAME")
        #self.user = self.cl.user_info_by_username(self.username)
        self.location = Location(name="Milan, Italy", lat=45.4642, lng=9.1927)
        #self.usertags = [Usertag(user_id=self.user.pk, position=[0.5, 0.5])]
        try:
            self.cl.login(self.email, self.password, relogin=False)
        except Exception as e:
            print(e)
            print("Logging in again after 100 seconds")
            time.sleep(100)
            for i in range(10):
                print(f"{i}th attempt")
                try:
                    self.cl.login(self.email, self.password, relogin=False)
                except Exception as e:
                    print(e)
                    print("Logging in again after 100 seconds")
                    time.sleep(100)
                else:
                    break

    
    def upload_photo(self, path, caption):
        self.cl.photo_upload(
            path, 
            caption, 
            location=self.location,
            #usertags=[Usertag(user_id=user.pk, position=[0.5, 0.5])],
        )
    
    def print_info(self):
        print(self.cl.user_info_by_username(self.username))


if __name__ == "__main__":
    bot = InstaBot()
    bot.upload_photo("test.png", "test")
