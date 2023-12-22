#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import os
import time
import datetime as dt

today = dt.datetime.today().date()


# In[2]:


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup as bs

driver = webdriver.Chrome()
dk_url = f'https://sportsbook.draftkings.com/leagues/football/nfl?category=player-stats&subcategory=pass-yards'
driver.get(dk_url)
driver.maximize_window()
wait = WebDriverWait(driver, 10)

buttons = {
    'Pass_Yards'    : 'subcategory_Pass Yards',
    'Pass_TDs'      : 'subcategory_Pass TDs',
    'Rush_Yards'    : 'subcategory_Rush Yards',
    'Rush_TDs'      : 'subcategory_Rush TDs',
    'Rec_Yards'     : 'subcategory_Rec Yards',
    'Rec_TDs'       : 'subcategory_Rec TDs',
    'Receptions'    : 'subcategory_Receptions',
    'Ints'          : 'subcategory_QB INTs'
}

pages = {}
for key, value in buttons.items(): 
    try:
        primary_button = wait.until(EC.element_to_be_clickable((By.ID, value)))
        side_buttons = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME,'side-arrow-icon')))
        try:
            primary_button.click()     
            time.sleep(2)
            pages[key] = driver.page_source
        except:
            if len(side_buttons) > 2:
                side_buttons[2].click()
            else:
                side_buttons.click()
            time.sleep(2)
            primary_button.click()
            pages[key] = driver.page_source
    except:
        continue

driver.close()


# In[3]:


stats_list = []
for key, value in pages.items():
    doc = bs(value, 'html.parser')
    cards = doc.find_all('div', class_ = 'sportsbook-event-accordion__wrapper expanded')
    for i in range(len(cards)):
        player = cards[i].find('a').text
        stat = key
        value = cards[i].find('div', class_ = 'sportsbook-outcome-cell__label-line-container').text.split()[1]
        #over_odds = cards[i].find('span', class_ = 'sportsbook-odds american default-color').text
        #under_odds = cards[i].find_all('span', class_ = 'sportsbook-odds american default-color')[1].text
        stats = {'Player': player, 'Stat': stat, 'Value': value, 'Date': today}
        stats_list.append(stats)
betting = pd.DataFrame(stats_list)


# In[4]:


driver = webdriver.Chrome()
espn_url = f'https://fantasy.espn.com/football/livedraftresults'
driver.get(espn_url)
driver.maximize_window()
wait = WebDriverWait(driver, 10)

pages = {}
for i in range(3) :  
    time.sleep(3)
    pages['page ' + str(i + 1)] = driver.page_source
    primary_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@class='Button Button--default Button--icon-noLabel Pagination__Button Pagination__Button--next']")))
    primary_button.click()

driver.close()


# In[5]:


draft_info = []
for key, value in pages.items():
    doc = bs(value, 'html.parser')
    for i in range(50):
        player = doc.find_all('a', class_ = 'AnchorLink link clr-link pointer')[i].text
        team = doc.find_all('span', class_ = 'playerinfo__playerteam')[i].text
        pos = doc.find_all('span', class_ = 'playerinfo__playerpos ttu')[i].text
        adp = doc.find_all('div', attrs = {'class': 'jsx-2810852873 table--cell sortedAscending adp tar sortable'})[i].text        
        info = {'Player': player, 'Team': team, 'Position': pos, 'ADP': adp}
        draft_info.append(info)

adp = pd.DataFrame(draft_info)
adp['Date'] = today
adp_types = {'Player':        object,
             'Date':          'datetime64[ns]',
             'Team':          object,
             'Position':      object,
             'ADP':           float}
adp = adp.astype(adp_types)
adp.reset_index(inplace=True)
adp['Position Rank'] = adp.groupby('Position')['ADP'].rank(axis = 0)
adp['Overall Rank'] = adp['ADP'].rank(axis = 0)


# In[6]:


betting = betting.pivot(index = ['Player', 'Date'], columns = ['Stat'], values = 'Value').fillna(0)
betting.reset_index(inplace = True)
types = {'Player':        object,
         'Date':          'datetime64[ns]',
         'Ints':          float,
         'Pass_TDs':      float,
         'Pass_Yards':    float,
         'Rec_TDs':       float,
         'Rec_Yards':     float,
         'Receptions':    float,
         'Rush_TDs':      float,
         'Rush_Yards':    float}

for key, value in types.items():
    try:
        betting[key] = betting[key].astype(value)
    except:
        continue


# In[7]:


driver = webdriver.Chrome()
players_url = f'https://fantasy.espn.com/football/players/projections'
driver.get(players_url)
driver.maximize_window()
wait = WebDriverWait(driver, 10)
time.sleep(5)
slider = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@class='Button Button--filter player--filters__projections-button']")))
slider.click()

players_pages = {}
for i in range(3) :
    time.sleep(2)
    players_pages['page ' + str(i + 1)] = driver.page_source
    primary_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@class='Button Button--default Button--icon-noLabel Pagination__Button Pagination__Button--next']")))
    primary_button.click()

driver.close()


# In[8]:


player_info = []
for key, value in players_pages.items():
    doc = bs(value, 'html.parser')
    for i in range(50):
        player = doc.find_all('a', class_ = 'AnchorLink link clr-link pointer')[i].text
        team = doc.find_all('span', class_ = 'playerinfo__playerteam')[i].text
        pos = doc.find_all('span', class_ = 'playerinfo__playerpos ttu')[i].text
        pass_tds = doc.find_all('div', attrs = {'class': 'jsx-2810852873 table--cell stat-td tar sortable',
                                                'title': 'TD Pass'})[i].text 
        pass_yards = doc.find_all('div', attrs = {'class': 'jsx-2810852873 table--cell stat-yds tar sortable',
                                                  'title': 'Passing Yards'})[i].text
        ints = doc.find_all('div', attrs = {'class': 'jsx-2810852873 table--cell stat-int tar sortable',
                                                  'title': 'Interceptions Thrown'})[i].text
        rush_yards = doc.find_all('div', attrs = {'class': 'jsx-2810852873 table--cell stat-yds tar sortable',
                                                 'title': 'Rushing Yards'})[i].text
        rush_tds = doc.find_all('div', attrs = {'class': 'jsx-2810852873 table--cell stat-td tar sortable',
                                                 'title': 'TD Rush'})[i].text
        recs = doc.find_all('div', attrs = {'class': 'jsx-2810852873 table--cell stat-rec tar sortable',
                                                 'title': 'Each reception'})[i].text
        rec_yards = doc.find_all('div', attrs = {'class': 'jsx-2810852873 table--cell stat-yds tar sortable',
                                                 'title': 'Receiving Yards'})[i].text
        rec_tds = doc.find_all('div', attrs = {'class': 'jsx-2810852873 table--cell stat-td tar sortable',
                                                 'title': 'TD Reception'})[i].text
        info = {'Player': player, 'Team': team, 'Position': pos, 'Pass_TDs': pass_tds, 'Pass_Yards': pass_yards, 'Ints': ints,
                'Rush_Yards': rush_yards, 'Rush_TDs': rush_tds, 'Receptions': recs, 'Rec_Yards': rec_yards, 'Rec_TDs': rec_tds, 'Date': today}
        player_info.append(info)
        
espn_projections = pd.DataFrame(player_info)


# In[9]:


espn_types = {'Player':        object,
              'Team':          object,
              'Date':          'datetime64[ns]',
              'Ints':          float,
              'Pass_TDs':      float,
              'Pass_Yards':    float,
              'Rec_TDs':       float,
              'Rec_Yards':     float,
              'Receptions':    float,
              'Rush_TDs':      float,
              'Rush_Yards':    float}
espn_projections = espn_projections.astype(espn_types)

update_cols = ['Pass_TDs', 'Pass_Yards', 'Ints', 'Rec_TDs', 
               'Rec_Yards', 'Receptions','Rush_TDs', 'Rush_Yards']
updated_proj = betting.merge(espn_projections, on = ['Player', 'Date'], suffixes = ('_vegas', '_espn'))
for col in update_cols:
    updated_proj[col] = updated_proj.apply(lambda row: row[f"{col}_espn"] if row[f"{col}_vegas"] == 0 else row[f"{col}_vegas"], axis = 1)
    updated_proj.drop([f"{col}_vegas", f"{col}_espn"], axis = 1, inplace = True)

#L1 -> Ken's League
#L2 -> League with HS friends
updated_proj['Vegas_Projections_L1'] = (updated_proj['Ints'] * -2) + (updated_proj['Pass_TDs'] * 6) + (updated_proj['Pass_Yards'] * 0.04) + (updated_proj['Rec_TDs'] * 6) + (updated_proj['Rec_Yards'] * 0.1) + (updated_proj['Receptions'] * 0.5) + (updated_proj['Rush_TDs'] * 6) + (updated_proj['Rush_Yards'] * 0.1)
updated_proj['Vegas_Projections_L2'] = (updated_proj['Ints'] * -2) + (updated_proj['Pass_TDs'] * 4) + (updated_proj['Pass_Yards'] * 0.04) + (updated_proj['Rec_TDs'] * 6) + (updated_proj['Rec_Yards'] * 0.1) + (updated_proj['Receptions'] * 1) + (updated_proj['Rush_TDs'] * 6) + (updated_proj['Rush_Yards'] * 0.1)
espn_projections['ESPN_Projections_L1'] = (espn_projections['Ints'] * -2) + (espn_projections['Pass_TDs'] * 6) + (espn_projections['Pass_Yards'] * 0.04) + (espn_projections['Rec_TDs'] * 6) + (espn_projections['Rec_Yards'] * 0.1) + (espn_projections['Receptions'] * 0.5) + (espn_projections['Rush_TDs'] * 6) + (espn_projections['Rush_Yards'] * 0.1)
espn_projections['ESPN_Projections_L2'] = (espn_projections['Ints'] * -2) + (espn_projections['Pass_TDs'] * 4) + (espn_projections['Pass_Yards'] * 0.04) + (espn_projections['Rec_TDs'] * 6) + (espn_projections['Rec_Yards'] * 0.1) + (espn_projections['Receptions'] * 1) + (espn_projections['Rush_TDs'] * 6) + (espn_projections['Rush_Yards'] * 0.1)


# In[10]:


espn_projections['Player'] = espn_projections['Player'].astype(str)
updated_proj['Player'] = updated_proj['Player'].astype(str)

total_projections = espn_projections.merge(updated_proj, how = 'left', on = ['Player', 'Team', 'Position', 'Date'], suffixes = ('_espn', '_dk'))


# In[11]:


from sqlalchemy import create_engine
import getpass

password = getpass.getpass()
engine = create_engine(f'postgresql+psycopg2://postgres:{password}\
@localhost:5432/postgres')
conn = engine.connect()

total_projections.columns = total_projections.columns.str.lower()
adp.columns = adp.columns.str.lower()

total_projections.to_sql('nfl_projections',
                        engine,
                        if_exists = 'append',
                        index = False)
adp.to_sql('nfl_adp',
            engine,
            if_exists = 'append',
            index = False)

conn.close()

