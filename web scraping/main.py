import requests
from bs4 import BeautifulSoup
import time
import format_stats



#takes in the cells of the table and returns the stats as a list of strings.
def getStats(cells):
   return [cell.get_text(strip=True) for cell in cells]

#gets the player names and whether they are batters or pitchers from the user.
def getInputs():
    playerNames= input('Enter player(s) seperated by a comma: ').title()
    isBatter = input('Is each player a batter? (y/n/u) seperated by a comma: ').strip().lower()
    players = [name.strip() for name in playerNames.split(',')]
    isBatter = [player.strip() for player in isBatter.split(',')]
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
    allPlayerStats = []
    for player in players:
        isBatterFlag = isBatter[players.index(player)].lower()
        if isBatterFlag == 'y':
            row, isBatterFlag = checkBatters(players.index(player))
        elif isBatterFlag == 'n':
            row, isBatterFlag = checkPitchers(player)
        else:
            result = checkBatters(players.index(player))
            row, isBatterFlag = result if result[0] is not None else checkPitchers(player)

        if row:
            cells = row.find_all('td')
            stats = getStats(cells)
            convertedStats = format_stats.convertStats(stats, isBatterFlag)
            allPlayerStats.append((player, convertedStats, isBatterFlag))
        else:
            print(f'{player} not found.')
    #only bold the highest stat if all players are the same type and there is more than one player. If there is a mix of batters and pitchers, just print the stats without bolding.
    allBatters = all(player[2] == True for player in allPlayerStats)
    allPitchers = all(player[2] == False for player in allPlayerStats)
    print(allBatters)
    print(allPitchers)
    if(len(allPlayerStats) > 1 and (allBatters or allPitchers)):
        format_stats.boldHighestStat(allPlayerStats)
    else:
        for player in allPlayerStats:
            print(player[0].title())
            print("-" * len(player[0]))
            for stat in player[1]:
                print(stat)
main(areBatters)