from moviepy.video import *
from moviepy.editor import *

from TikTokApi import TikTokApi
import numpy as np
import urllib
import cv2

from re import sub
from math import floor

import yaml

config = yaml.safe_load(open('config.yaml').read())

if not config['tiktok_cookies']:
    raise Exception('Missing TikTok Cookies\nPlease check config.yaml')
api = TikTokApi(custom_verify_fp=config['tiktok_cookies'])

if not config['width']:
    raise Exception('Missing image width\nPlease check config.yaml')
resolution = (config['width'],config['width'])

def url_to_image(url):
	resp = urllib.request.urlopen(url)
	image = np.asarray(bytearray(resp.read()), dtype="uint8")
	image = cv2.imdecode(image, cv2.IMREAD_COLOR)
	return image

def get_user_info(account):
    global api
    user = api.user(username=account)
    for video in user.videos(count=1):
        return video.as_dict

def grab(user):
    global resolution
    infomation = get_user_info(user)

    pfp = url_to_image(infomation["author"]["avatarLarger"])
    cv2.imwrite(f"profiles/{user}_picture.png", pfp)
    pfp = ImageClip(f"profiles/{user}_picture.png",duration=1).fx(vfx.resize,width=resolution[0]*0.5)

    userid = infomation["author"]["uniqueId"]
    username = sub(r'[^A-Za-z0-9 ,.!?:;()\[\]/\"\'#{}+=_%~@£$<>|&\n-]+', '', infomation["author"]["nickname"])
    bio = sub(r'[^A-Za-z0-9 ,.!?:;()\[\]/\"\'#{}+=_%~@£$<>|&\n-]+', '', infomation["author"]["signature"])

    if infomation["authorStats"]["followerCount"] <= 999 or infomation["authorStats"]["heartCount"] <= 999:
        aspect = 0.2
    else:
        aspect = 0.3

    idText = TextClip(txt=userid, fontsize=100, color='white').set_duration(1).fx(vfx.resize,width=resolution[0]*0.3)
    nameText = TextClip(txt=username, fontsize=100, color='white').set_duration(1).fx(vfx.resize,width=resolution[0]*0.5)
    bioText = TextClip(txt=bio, fontsize=100, color='white').set_duration(1).fx(vfx.resize,width=resolution[0]*0.7)
    followersText = TextClip(txt=f'{"{:,}".format(infomation["authorStats"]["followerCount"])}' , fontsize=100, color='white').set_duration(1).fx(
        vfx.resize,width=aspect*resolution[0])
    likesText = TextClip(txt=f'{"{:,}".format(infomation["authorStats"]["heartCount"])}', fontsize=100, color='white').set_duration(1).fx(
        vfx.resize,height=followersText.h)

    heart = ImageClip("assets/heart.png",duration=1).fx(vfx.resize,height=followersText.h*0.6)
    follower = ImageClip("assets/follow.png",duration=1).fx(vfx.resize,height=likesText.h*0.6)

    resolution = (resolution[0],floor(idText.h+pfp.h+nameText.h+bioText.h+followersText.h+likesText.h*0.2+heart.h)+10)
    profile = CompositeVideoClip(
        [
            idText.set_position(("center","top")),
            pfp.set_position(("center",idText.h)),
            nameText.set_position(("center",idText.h+pfp.h)),

            bioText.set_position(("center",idText.h+pfp.h+nameText.h)),

            followersText.set_position(("center",idText.h+pfp.h+nameText.h+bioText.h)),
            follower.set_position((resolution[0]/2-followersText.w/2-follower.w*1.2,idText.h+pfp.h+nameText.h+bioText.h+followersText.h*0.2)),
            
            likesText.set_position(("center",idText.h+pfp.h+nameText.h+bioText.h+followersText.h)),
            heart.set_position((resolution[0]/2-likesText.w/2-heart.w*1.2,idText.h+pfp.h+nameText.h+bioText.h+followersText.h+likesText.h*0.2))
        ],
        resolution
        )

    profile = profile.on_color(size= resolution,color=(0,0,0),col_opacity=0.3)
    profile.save_frame(f"profiles/{user}_profile.png")
    print(f"Profile grabbed at profiles/{user}_profile.png")

while True:
    user = input("Enter account name\n>>>")
    grab(user)