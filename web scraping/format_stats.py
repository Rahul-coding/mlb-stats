#the order the stats are in on the website. 
batterStatsOrder = ['TEAM', 'G', 'AB', 'R', 'H', '2B', '3B', 'HR', 'RBI', 'BB', 'SO', 'SB', 'CS', 'AVG', 'OBP', 'SLG', 'OPS']
pitcherStatsOrder = ['TEAM', 'W', 'L', 'ERA', 'G', 'GS', 'CG', 'SHO', 'SV', 'SVO', 'IP', 'H', 'R', 'ER', 'HR', 'HB', 'BB', 'SO', 'WHIP', 'AVG']


#takes in the stats and converts them to a more readable format.
def convertStats(stats, isBatter):
    converted = []

    for i in range(len(stats)):
        if isBatter:
            converted.append(batterStatsOrder[i] + ": " + str(stats[i]))
        else:
            converted.append(pitcherStatsOrder[i] + ": " + str(stats[i]))

    return converted 


def boldHighestStat(stats):

    highestStats = {}

    # Find highest value for each stat type
    if(len(stats) > 1):
        for player in stats:
            playerStats = player[1]
            for stat in playerStats:
                statName, statValue = stat.split(": ")
                if statValue.replace('.', '', 1).isdigit():
                    statValue = float(statValue)
                    if statName not in highestStats:
                        highestStats[statName] = statValue
                    elif statValue > highestStats[statName]:
                        highestStats[statName] = statValue

    # Print all players
    for player in stats:
        playerName = player[0]
        playerStats = player[1]

        print(f"\n{playerName}")
        print("-" * len(playerName))

        for stat in playerStats:
            statName, statValue = stat.split(": ")
            if statValue.replace('.', '', 1).isdigit():
                statValueFloat = float(statValue)
                # Bold if this player has the highest value
                if statValueFloat == highestStats[statName]:
                    print('\033[1;3m' + stat + '\033[0m')
                else:
                    print(stat)
            else:
                print(stat)
