from requests import get
from bs4 import BeautifulSoup
import pandas as pd

# empty dataframe to store episode id, director list, and writer list
episode_data = pd.DataFrame(columns=['ep_id', 'description', 'directors', 'writers'])

# loop to iterate over seasons
for season in range(1,27):

    url = "https://www.imdb.com/title/tt0096697/episodes?season="
    response = get(url + str(season))

    page_html = BeautifulSoup(response.content, "html.parser")
    list = page_html.find('div', class_ = 'list detail eplist').findAll('strong')

    season_num = season
    ep_num = 1

# loop to iterate over episodes in season
    for item in list:
        # creating ep_id to match format in transcripts dataframe
        ep_id = "{:02d}".format(season)+"x"+"{:02d}".format(ep_num)
        
        # constructing url and request to access each episode's page
        url = item.find('a').get('href')
        ep_url = "https://www.imdb.com" + url + "?ref_=ttep_ep" + str(ep_num)
        ep_response = get(ep_url, headers={"User-Agent":"Mozilla/5.0"})

        ep_html = BeautifulSoup(ep_response.content,"html.parser")

        # grabbing description
        description = ep_html.find('span', attrs = {"data-testid":"plot-xl"}).text

        # selecting container with director and writer info
        info = ep_html.find('div', class_ = "sc-acac9414-3 hKIseD").find('ul').findAll('li', attrs={"data-testid":"title-pc-principal-credit"})

        director_list = []
        writers_list = []

        # iterating through directors and writers lists
        directors = info[0].find('ul').findAll('a')
        for i in directors:
            director_list.append(i.text)

        writers = info[1].find('ul').findAll('a')
        for i in writers:
            writers_list.append(i.text)

        
        # adding data to dataframe
        episode_data.loc[len(episode_data.index)] = [ep_id, description, ', '.join(director_list), ', '.join(writers_list)]

        # counter
        print("Added: " + ep_id)

        ep_num +=1

# create csv
episode_data.to_csv('episode_data.csv')