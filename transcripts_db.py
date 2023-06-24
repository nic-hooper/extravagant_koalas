import requests
from requests import get
from bs4 import BeautifulSoup
from pymongo import MongoClient
import string, re

url = "https://webscraper.io/test-sites/tables/tables-semantically-correct"

connection_string = "mongodb+srv://test1:testpassword123@cluster0.pfezsmf.mongodb.net/?retryWrites=true&w=majority"

cluster = MongoClient(connection_string)


db = cluster["theSimpsons"]
collection = db["episodes"]


# seasons 1-26
for index in range(21861,22437):
    url = "https://transcripts.foreverdreaming.org/viewtopic.php?t="
    response = get(url + str(index))

    page_html = BeautifulSoup(response.content, "html.parser")


    if page_html is not None:

        try:
            title = page_html.find('div', class_='wrap').find('div', class_='post has-profile bg2 offline').find('div', class_='inner').find('div', class_='postbody').find('h3', class_='first').text
            content = page_html.find('div', class_='wrap').find('div', class_='post has-profile bg2 offline').find('div', class_='inner').find('div', class_='postbody').find('div', class_='content').text

            pattern = r'\b\w+:\s*'

            # remove words ending in a colon, i.e. extra words that indicate when a character is speaking, e.g.: "HOMER:...", "BART:", etc
            remove_speaker = re.sub(pattern, "", content)

            # remove punctuation/line breaks, case normalize
            clean_transcript = " ".join(remove_speaker.strip().translate(str.maketrans('','',string.punctuation)).lower().replace('\n', ' ').split())

            #remove extra space from title
            clean_title = title.strip()
            
            # add to mongo collection
            collection.insert_one({"title":clean_title, "transcript":clean_transcript})
        except AttributeError:
            pass

        
