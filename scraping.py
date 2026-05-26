import requests
from bs4 import BeautifulSoup
import time

#the order the stats are in on the website. 
batterStatsOrder = ['TEAM', 'G', 'AB', 'R', 'H', '2B', '3B', 'HR', 'RBI', 'BB', 'SO', 'SB', 'CS', 'AVG', 'OBP', 'SLG', 'OPS']
pitcherStatsOrder = ['TEAM', 'W', 'L', 'ERA', 'G', 'GS', 'CG', 'SHO', 'SV', 'SVO', 'IP', 'H', 'R', 'ER', 'HR', 'HB', 'BB', 'SO', 'WHIP', 'AVG']


#takes in the stats and converts them to a more readable format.
def convertStats(stats, isBatter):
    converted = []
    for i in range(len(stats)):
        if(isBatter):
            converted.append(batterStatsOrder[i] + ": " +  '\033[3m'+str(stats[i])+'\033[0m')
        else:
            converted.append(pitcherStatsOrder[i] + ': ' + '\033[3m'+str(stats[i])+'\033[0m')
    return converted 

#takes in the cells of the table and returns the stats as a list of strings.
def getStats(cells):
   return [cell.get_text(strip=True) for cell in cells]

#gets the player names and whether they are batters or pitchers from the user.
def getInputs():
    playerNames= input('Enter player(s) seperated by a comma: ').title()
    isBatter = input('Is each player a batter? (y/n/u) seperated by a comma: ').strip().lower()
    players = [name.strip() for name in playerNames.split(',')]
    isBatter = [batter.strip() for batter in isBatter.split(',')]
    return players, isBatter

players, areBatters = getInputs()
 
#checks the batters page. If the player is not found and its is unnkown if the player is a btter or pitcher check pitchers. Otherwise, return None
def checkBatters(player, isBatter='y',page=1):
    print('Checking batters page: ', page)
    URL = 'https://www.mlb.com/stats/?page=' + str(page)
    r = requests.get(URL)
    time.sleep(1)

    soup = BeautifulSoup(r.content, 'html.parser')
    playerTag = soup.find('a', attrs={'aria-label': players[player]})
    row = None
    
    if playerTag:
        row = playerTag.find_parent('tr')
        if(row):
            isBatter = True
            return row, isBatter
    else:
        if(int(page) > 23):
            page = 1
            if(isBatter == 'u'):
                print('Checking pitchers...')
                checkPitchers(1)
                return None, None
        else:
            page += 1
            return checkBatters(player, isBatter, page)
    

#check if the player is a pitcher.
def checkPitchers(playerName, page=1):
    print('Checking pitchers page: ', page)
    URL = 'https://www.mlb.com/stats/pitching?page=' + str(page)
    r = requests.get(URL)
    time.sleep(1)
    soup = BeautifulSoup(r.content, 'html.parser')
    playerTag = soup.find('a', attrs={'aria-label': playerName})
    row = None
    if playerTag:
        row = playerTag.find_parent('tr')
        if(row):
            isBatter= False
            return row, isBatter
    else:
        if(page > 23):
            print('Player not found ):')
            return None, None
        page += 1
        return checkPitchers(playerName, page)

#main function that checks if the player is a batter or pitcher and then gets the stats and prints them in a readable format. If the player is not found, it will print a message saying so.
def main(isBatter):
    for index, player in enumerate(players):
        isBatterFlag = isBatter[index].lower()
        if isBatterFlag == 'y':
            row, isBatterFlag = checkBatters(index)
        elif isBatterFlag == 'n':
            row, isBatterFlag = checkPitchers(players[index])
        else:
            result = checkBatters(index)
            row, isBatterFlag = result if result[0] is not None else checkPitchers(players[index])

        if row:
            cells = row.find_all('td')
            stats = getStats(cells)
            convertedStats = convertStats(stats, isBatterFlag)
            print(f"\nSTATS FOR {players[index].upper()}:")
            print('\n'.join(convertedStats),'\n')
        else:
            print(f"Player {players[index]} not found.")
main(areBatters)