import requests
import json
import sys
import os
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from gtts import gTTS

URL = sys.argv[1]

IMAGE_WIDTH=900
IMAGE_HEIGHT=900
FONT_SIZE=18
COMMENT_FONT_SIZE=FONT_SIZE * 2

# get cookie for request
print("Getting cookie from Reddit")

a_session = requests.Session()
a_session.get("https://www.reddit.com/")
session_cookies = a_session.cookies
cookies_dictionary = session_cookies.get_dict()

# submit request for reddit post
print("Requesting Reddit post")

r = requests.get(url = URL, cookies=cookies_dictionary)
r_body = r.text

# extract comments from reddit post
print("Extracting comments")

comments_start = r_body.find("<script id=\"data\">")
comments_end = r_body.find("</script>", comments_start)
comments_body = r_body[comments_start:comments_end]

json_start = comments_body.find("{")
json_body = comments_body[json_start:-1]

response_json = json.loads(json_body)

features_json = response_json['features']
comments_json = features_json['comments']
models_json = comments_json['models']

# convert comments to json array
print("Parsing comments")

comments_arr = []
error_count = 0

for comment_key in models_json.keys():
    try:
        comment_json = models_json[comment_key]
        comment_dict = {}
        comment_dict['id'] = comment_json['id']
        comment_dict['author'] = comment_json['author']
        comment_dict['score'] = comment_json['score']
        media_json = comment_json['media']
        rtc_json = media_json['richtextContent']
        document_json = rtc_json['document']
        c_arr = document_json[0]
        c_json = c_arr['c']
        e_arr = c_json[0]
        comment_dict['text'] = e_arr['t']
        if comment_json['parentId'] == None:
            comments_arr.append(comment_dict)
    except:
        error_count = error_count + 1

font = ImageFont.truetype("res/Consolas.ttf", FONT_SIZE)
comment_font = ImageFont.truetype("res/Consolas.ttf", COMMENT_FONT_SIZE)

for comment in comments_arr:
    print("Rendering image for comment " + comment['id'])

    img = Image.new(mode="RGB", size = (IMAGE_WIDTH, IMAGE_HEIGHT), color = (8, 8, 8))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("res/Consolas.ttf", FONT_SIZE)
    draw.text((10, 10), "u/" + comment['author'] + "@effortless.reddit.curator:~/r/ask_reddit$", (20, 200, 20), font=font)
    draw.text((10, IMAGE_HEIGHT - 30), "\"up votes\": " + str(comment['score']), (20, 200, 20), font=font)
    tokens = comment['text'].split(' ')
    x = 10
    y = 40 + COMMENT_FONT_SIZE
    for token in tokens:
        if x > IMAGE_WIDTH * 0.6:
            x = 10
            y = y + COMMENT_FONT_SIZE
        if x == 10:
            draw.text((x, y), ">", (170, 170, 170), font=comment_font)
            x = x + COMMENT_FONT_SIZE * 0.55 * 2
        draw.text((x, y), token, (170, 170, 170), font=comment_font)
        x = x + (len(token) + 1) * COMMENT_FONT_SIZE * 0.55
            
    file_name = "data/img_" + comment['id'] + ".png"
    img.save(file_name)

    print("Dubbing audio for comment " + comment['id'])

    audio_name = "data/audio_" + comment['id'] + ".mp3"
    comment_audio = gTTS(text=comment['text'], lang='en', tld='ca', slow=False)
    comment_audio.save(audio_name)

    print("Generating video for comment " + comment['id'])

    video_name = "data/video_" + comment['id'] + ".mp4"

    os.system('ffmpeg -loop 1 -i ' + file_name + ' -i ' + audio_name + ' -c:v libx264 -tune stillimage -c:a aac -b:a 192k -pix_fmt yuv420p -shortest ' + video_name + ' > /dev/null 2>&1')
    os.system('echo file ' + video_name[5:] + ' >> data/vid_list.txt')

    print("Clearing image and audio files for comment " + comment['id'])
    os.system('rm ' + file_name + ' ' + audio_name)

print("Concatenating videos")
os.system('ffmpeg -f concat -i data/vid_list.txt -c copy final_video.mp4 > /dev/null 2>&1')

print("Removing intermediate videos")
os.system('rm -f data/vid*')
os.system('rm -r data')
