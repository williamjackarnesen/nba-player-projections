import requests
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time, pickle
from selenium.webdriver.support.ui import Select
import time
from selenium.common.exceptions import NoSuchElementException        


#FUNCTIONS FOR SCRAPING THE BOX SCORES

#function to get the locations of each element in the webpage
def get_xpaths():
    
    #table with away team box scores
    xpath_table_away = '/html/body/div[1]/div[2]/div[4]/section[2]/div[2]/div[2]/div/table/tbody'
    
    #table with home team box scores
    xpath_table_home = '/html/body/div[1]/div[2]/div[4]/section[3]/div[2]/div[2]/div/table/tbody'
    
    #location of dropdown menu
    xpath_dropdown = '/html/body/div[1]/div[2]/div[4]/section[1]/div/form/div[1]/label/div/select'
    
    #names of the teams
    xpath_away_name = '/html/body/div[1]/div[2]/div[4]/section[2]/div[1]/h1/span'
    xpath_home_name = '/html/body/div[1]/div[2]/div[4]/section[3]/div[1]/h1/span'
    
    return xpath_table_away, xpath_table_home, xpath_dropdown, xpath_away_name, xpath_home_name


#initialize the player dictionary
def initialize_player_dict(table, away_name, home_name):
    player_dict = {}
    
    #away team comes first since the table is listed first
    curr_team = away_name
    
    for row in table:
        
        #make sure the row actually contains a player name
        check = re.search('[0-9]|DNP|TOTALS|^.$',row)
        
        #if you hit a row called "TOTALS", it means the away table has ended
        check_tot = re.search('TOTALS',row)
        
        #if so, switch teams
        if check_tot is not None:
            curr_team = home_name
            
        #else, initialize the dictionary entry
        if check is None:
            player_dict[row] = {'team': curr_team,'min': 0, 'fgm': 0, 'fga': 0, 'fgX': 0, "X3pm": 0,
                               "X3pa": 0, 'X3pX': 0,"ftm": 0, 'fta': 0, "ftX": 0, "orb": 0,
                               "drb": 0, "reb": 0, "ast": 0, "stl": 0, "blk": 0,
                               "tov": 0, "pf": 0, "pts": 0, "plusminus": 0}
    return player_dict

#adding a new entry to the table in case the scraper misses it the first time
def add_new_player_dict_row(player_dict, player):
    
    player_dict[player] = {'team': team_name,'min': 0, 'fgm': 0, 'fga': 0, 'fgX': 0, "X3pm": 0,
                               "X3pa": 0, 'X3pX': 0,"ftm": 0, 'fta': 0, "ftX": 0, "orb": 0,
                               "drb": 0, "reb": 0, "ast": 0, "stl": 0, "blk": 0,
                               "tov": 0, "pf": 0, "pts": 0, "plusminus": 0}
    return player_dict

#once you have a table location, pull the table data
def populate_player_dict(player_dict, table,stats):
    
    for row in table:
        
        #make sure the row actually has a player name in it
        check = re.search('[0-9]|DNP|TOTALS|^.$',row)
        
        #check if it is a stat row
        check_num = re.search('[0-9]',row)
        
        #if it has a player name, save the player name
        if check is None:
            curr_player = row
            
        #if it is a stat row, pull the stats
        if check_num is not None: 
            
            #tease out each individual stat
            new_rows = row.split(' ')
            
            #make sure that the row is not missing data
            if len(new_rows) == len(stats):
                
                #add the data to the row
                for i, entry in enumerate(new_rows):
                    category = stats[i]
                    
                    #make sure the player is in the set already (this is an error-checking line)
                    if curr_player not in player_dict:
                        print(curr_player)
                        player_dict = add_new_player_dict_row(player_dict, player, name)
                        
                    #add the data
                    else:
                        curr_team = player_dict[curr_player]['team']
                        player_dict[curr_player][category] = entry
    return player_dict

#this merely lists the stats available in each table
def get_stat_categories():
    trad_stats = ['min','fgm','fga','fgX','X3pm','X3pa','X3pX','ftm','fta',
                 'ftX','orb','drb','reb','ast','stl','blk','tov','pf',
                 'pts','plusminus']
    adv_stats = ['min','offrtg','defrtg','netrtg','astX','ast_to','ast_rat',
                'orbX','drbX','rebX','to_rat','efgX','tsX','usgX','pace',
                'pie']
    track_stats = ['min','spd','dist','orbc','drbc','rbc','tchs','sast','ftast',
                  'pass','ast','cfgm','cfga','cfgX','ufgm', 'ufga',
                  'ufgX','fgX','dfgm','dfga','dfgX']
    hustle_stats = ['min','screen_ast','screen_ast_pts','deflections','off_loose',
                   'def_loose','loose_tot','charges_drawn','contested_2',
                   'contested_3','contested_tot','off_boxouts','def_boxouts',
                   'tot_boxouts']
    return trad_stats, adv_stats, track_stats, hustle_stats

#this returns the raw table information
def get_tables(xpath_table_away, xpath_table_home):
    time.sleep(1)
    table_away = driver.find_element_by_xpath(xpath_table_away).text
    table_home = driver.find_element_by_xpath(xpath_table_home).text

    table = table_away + "break1" + table_home
    table = re.split('\n|^[0-9]\s|break1',table)
        
    return table
    
#this calls the dropdown menu (dropdown_word controls which elemnt of dropdown menu to click)
def new_tab(dropdown_word, stat_name, xpath_table_away, 
            xpath_table_home, xpath_dropdown, player_dict):
    
    #use try in case the menu doesn't render in time 
    try:
        dropdown=Select(driver.find_element_by_xpath(xpath_dropdown))
        dropdown.select_by_visible_text(dropdown_word)
    
    #if it doesn't, catch the error and try again after three seconds
    except NoSuchElementException:
        time.sleep(3)
        try:
            dropdown=Select(driver.find_element_by_xpath(xpath_dropdown))
            dropdown.select_by_visible_text(dropdown_word)
        except:
            pass
    time.sleep(1)
    
    #call the raw table information
    new_table = get_tables(xpath_table_away, xpath_table_home)
    
    #add the new information to the dictioanry
    player_dict = populate_player_dict(player_dict, new_table, stat_name)
    return player_dict

#this gets the team names by location
def get_names(xpath_away_name, xpath_home_name):
    away_name = driver.find_element_by_xpath(xpath_away_name).text
    home_name = driver.find_element_by_xpath(xpath_home_name).text
    
    return away_name, home_name

#this gets the score and margin of victory
def get_scores_and_margins(player_dict,home_name,away_name):
    
    #initialize scores
    home_score = 0
    away_score = 0
    
    #player's team is already stored in the dictionary from above
    for player in player_dict:
        if player_dict[player]['team']==home_name:
            home_score += int(player_dict[player]['pts'])
        else:
            away_score += int(player_dict[player]['pts'])
    
    #get the margin of victory
    away_margin = away_score-home_score
    home_margin = home_score-away_score
    
    #append margin of victory to each player (needed for calculating on-off plus-minus)
    for player in player_dict:
        if player_dict[player]['team']==home_name:
            player_dict[player]['margin']=home_margin
        else:
            player_dict[player]['margin']=away_margin
    
    #record the winner in the scores dictionary
    winner = away_name
    loser = home_name
    
    #importantly, there are no ties so this works
    if home_score > away_score:
        winner = home_name
        loser = away_name
    
    return player_dict, winner, loser
        
#pull all the data for a given game url    
def pull_game(gameid, scores):
    
    #get xpath locations
    xpath_table_away, xpath_table_home, xpath_dropdown, xpath_away_name, xpath_home_name = get_xpaths()

    #get team names
    away_name, home_name = get_names(xpath_away_name, xpath_home_name)
    time.sleep(1.5)
    
    #get the list of stats on each page
    trad_stats, adv_stats, track_stats, hustle_stats = get_stat_categories()
    
    #initialize player dictionary
    trad_table = get_tables(xpath_table_away, xpath_table_home)
    player_dict = initialize_player_dict(trad_table, away_name, home_name)
        
    #get traditional stats
    player_dict = populate_player_dict(player_dict, trad_table,trad_stats)

    #get advanced stats (hustle is not available for long enough)
    player_dict = new_tab("Advanced",adv_stats, xpath_table_away, xpath_table_home, xpath_dropdown, player_dict)
    time.sleep(0.5)
    
    #get player tracking stats
    player_dict = new_tab("Player Tracking",track_stats, xpath_table_away, xpath_table_home, xpath_dropdown, player_dict)
    time.sleep(0.5)
    
    #get winner of game
    player_dict, winner, loser =  get_scores_and_margins(player_dict,home_name,away_name)

    #need to store the winners
    scores[gameid] = {'winner': winner, 'loser': loser}
    
    #write winner to csv
    player_df = pd.DataFrame(player_dict) 
    player_df = player_df.transpose()
    
    #get correct location to write to
    year = str(int(re.search('1[0-9]',gameid).group(0))+1)
    write_address = "box_scores_new/"+"20"+year+"/"+gameid+".csv"
    
    #write to location
    player_df.to_csv(write_address)  

    return gameid

#gets all the urls for regular season
def get_url_list_regular():
    url_stub='https://www.nba.com/game/002'
    max_games_dict = get_max_games()
    url_list = []
    
    #generates the correct url strings for pulling
    for year in range(2014,2020):
        max_num = max_games_dict[year]
        for i in range(max_num):
            day_str = str(i+1)
            if i < 999:
                day_str =  "0" + day_str 
            if i < 99:
                day_str = "0" + day_str
            if i < 9:
                day_str = "0" + day_str
            year_str = str(year - 2001)
            url_new = url_stub+year_str+"0"+day_str+"/box-score#box-score"
            url_list.append(url_new)
    return url_list

#get number of games in the season
def get_max_games():
    max_games = {}
    for year in range(2014,2021):
        max_games[year] = 1230
    max_games[2012] = 990
    max_games[2020] = 973
    return max_games
    
#get the url stubs for playoff games
def get_playoff_directory_by_year(year):
    year_start = str(year-1)
    year_end = str(year-2000)
    url_start = 'https://www.nba.com/stats/teams/boxscores-traditional/?Season=' 
    url_end = '&SeasonType=Playoffs'
    full_url = url_start + year_start + "-" + year_end + url_end
    return full_url

#pull the playoff links (no consistent pattern unlike regular season)
def get_playoff_links_given_year(url,url_list=[]):
    #navigate to the url
    driver.get(url)
    time.sleep(3)
    
    #get the dropdown menu and click on it
    xpath_dropdown_playoffs = '/html/body/main/div/div/div[2]/div/div/nba-stat-table/div[3]/div/div/select'
    try:
        dropdown=Select(driver.find_element_by_xpath(xpath_dropdown_playoffs))
        dropdown.select_by_visible_text('All')
    except NoSuchElementException:
        time.sleep(3)
        dropdown=Select(driver.find_element_by_xpath(xpath_dropdown_playoffs))
        dropdown.select_by_visible_text('All')
        
    #get all links from the page
    links = driver.find_elements_by_xpath("//*[@href]")
    
    #make sure each link has a url for a box-score page
    for elem in links:
        link = (elem.get_attribute("href"))
        check = re.search('/stats/game/[0-9]',link)
        
        #add it to the list if it is a box-score URL
        if check is not None:
            link = link + "/box-score"
            link = link.replace('/stats',"")
            url_list.append(link)
    return url_list

#adding all the urls for each year 
def get_all_playoff_links():
    playoff_url_list = []
    for year in range(2014,2021):
        year_url = get_playoff_directory_by_year(year)
        new_playoff_games = get_playoff_links_given_year(year_url)
        playoff_url_list.append(new_playoff_games)
        time.sleep(3)
    return playoff_url_list

#after it has been written, pulling it from a csv and cleaning it
def import_url_list():
    url_list_base = pd.read_csv("nbaurls.csv", encoding="latin1").values
    url_list = []
    for row in url_list_base:
        url = row[0]
        if url not in url_list:
            url_list.append(url)
    return url_list


