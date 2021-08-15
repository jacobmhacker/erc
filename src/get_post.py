import requests
import json

URL = "https://www.reddit.com/r/AskReddit/comments/p4r8u9/what_is_old_but_that_people_still_use/"

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

for comment_key in models_json.keys():
    comment_json = models_json[comment_key]
    comment_dict = {}
    comment_dict['id'] = comment_json['id']
    comment_dict['author'] = comment_json['author']
    comment_dict['parentId'] = comment_json['parentId']
    comment_dict['score'] = comment_json['score']
    media_json = comment_json['media']
    rtc_json = media_json['richtextContent']
    document_json = rtc_json['document']
    c_arr = document_json[0]
    c_json = c_arr['c']
    e_arr = c_json[0]
    comment_dict['text'] = e_arr['t']
    comments_arr.append(comment_dict)

# output comment array

print(comments_arr)
