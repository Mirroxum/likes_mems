import vk_api
import requests
import os
import json
import urllib

 

token = '7a8d3b867a8d3b867a8d3b86a9799f887b77a8d7a8d3b86196215fca9f755d263739248'
version = '5.120'
domain = 'memepediaru'
count = 1
offset = 0

def main():
    response = requests.get('https://api.vk.com/method/wall.get', 
                            params={
                                'access_token': token,
                                'v': version,
                                'domain': domain,
                                'count': count,
                                'offset': offset,
                            }).json()
    data = response['response']['items']
    for post in data:
        for attachment in post['attachments']:
            if attachment['type'] == 'photo':
                img_url = attachment['photo']['sizes'][3]['url']
                p = requests.get(img_url)
                with open("img.jpg", "wb") as img:
                    img.write(p.content)
if __name__ == "__main__":
    main()