import requests
from requests import get
from bs4 import BeautifulSoup
import string, re
import json
import pandas as pd


transcripts_raw = pd.DataFrame(columns=['number', 'title', 'raw_transcript'])
transcripts_clean = pd.DataFrame(columns=['number','title','clean_transcript'])

# seasons 1-26
for index in range(21861,22437): # 22437
    url = "https://transcripts.foreverdreaming.org/viewtopic.php?t="
    response = get(url + str(index))

    page_html = BeautifulSoup(response.content, "html.parser")

    if page_html is not None:

        try:
            title = page_html.find('div', class_='wrap').find('div', class_='post has-profile bg2 offline').find('div', class_='inner').find('div', class_='postbody').find('h3', class_='first').text
            content = page_html.find('div', class_='wrap').find('div', class_='post has-profile bg2 offline').find('div', class_='inner').find('div', class_='postbody').find('div', class_='content').text

            pattern1 = r'\b\w+:\s*' 
            pattern2 = r"[^\w\s]"

            # remove words ending in a colon, i.e. extra words that indicate when a character is speaking, e.g.: "HOMER:", "BART:", etc
            remove_speaker = re.sub(pattern1, "", content)

            # remove punctuation/line breaks, case normalize
            
            clean_transcript = " ".join(remove_speaker.strip().lower().replace('\n', ' ').split())
            clean_transcript = re.sub(pattern2, "", clean_transcript)
            
            #clean_transcript = " ".join(remove_speaker.strip().translate(str.maketrans('','',string.punctuation)).lower().replace('\n', ' ').split())

            # splitting title into episode number and episode name to be stored separately
            ep_header = title.strip().split("-",1)
            episode_num = ep_header[0].strip()
            episode_name = ep_header[1].strip()
            
            transcripts_raw.loc[len(transcripts_raw.index)] = [episode_num, episode_name, content.replace('\n', ' ')]
            transcripts_clean.loc[len(transcripts_clean.index)] = [episode_num, episode_name, clean_transcript]

        except AttributeError:
            pass

transcripts_raw.to_csv('transcripts_raw.csv')
transcripts_clean.to_csv('transcripts_clean.csv')


        
