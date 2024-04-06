# Importing the required libraries

from email import header
import requests
import os 
import ffmpeg
from concurrent.futures import ThreadPoolExecutor
from time import sleep

URLs = ['https://www.reddit.com/r/Unexplained/comments/wwjap5/ghost_dog_video/',
   'https://www.reddit.com/r/teenagersbuthot/comments/w81zmn/heres_a_little_dog_video_to_brighten_your_day/',
   'https://www.reddit.com/r/Awww/comments/w5156z/cutest_dog_video_ive_come_across_today/']

def main():
    with ThreadPoolExecutor(max_workers = 3) as executor:
        executor.map(extract_av_url, URLs)

    #url = input("Enter Reddit URL :")[:-1]+".json" # Adding .json at the end of the URL.

def extract_av_url(url):
    url = url[:-1]+".json"
    headers = {"User-agent":"Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Mobile Safari/537.36"}
    r = requests.get(url, headers=headers)
    data = r.json()[0]
    video_url = data['data']['children'][0]['data']['secure_media']['reddit_video']['fallback_url']
    audio_url = "https://v.redd.it/"+video_url.split("/")[3]+"/DASH_audio.mp4"
    
    with open('video.mp4', 'wb') as f:
        video_stream = requests.get(video_url, stream=True)
        f.write(video_stream.content)

    with open('audio.mp3', 'wb') as f:
        audio_stream = requests.get(audio_url, stream=True)
        f.write(audio_stream.content)
    
    file_index = int(input("Enter file number index which you want to save as:"))
    # Please make sure ffpmeg is installed in the system otherwise error - 'ffmpeg' is not recognized as an internal or external command, operable program or batch file. will come.
    os.system(f"ffmpeg -i video.mp4 -i audio.mp3 -c copy output_{file_index}.mp4") 

if __name__ == '__main__':
    main()



