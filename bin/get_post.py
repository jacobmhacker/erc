import requests
import json
import sys
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

URL = sys.argv[1]

IMAGE_WIDTH=900
IMAGE_HEIGHT=900
FONT_SIZE=18
COMMENT_FONT_SIZE=FONT_SIZE * 2

# get cookie for request
a_session = requests.Session()
a_session.get("https://www.reddit.com/")
session_cookies = a_session.cookies
cookies_dictionary = session_cookies.get_dict()

# submit request for reddit post
r = requests.get(url = URL, cookies=cookies_dictionary)
r_body = r.text

# extract comments from reddit post
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
