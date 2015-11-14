import sqlite3
import function

__author__ = 'hanyc'

srcFiles = ["./raw_data/2000_01_raw.txt", "./raw_data/2001_02_raw.txt", "./raw_data/2002_03_raw.txt", "./raw_data/2003_04_raw.txt", "./raw_data/2004_05_raw.txt", "./raw_data/2005_06_raw.txt", "./raw_data/2006_07_raw.txt", "./raw_data/2007_08_raw.txt", "./raw_data/2008_09_raw.txt", "./raw_data/2009_10_raw.txt", "./raw_data/2010_11_raw.txt", "./raw_data/2011_12_raw.txt", "./raw_data/2012_13_raw.txt", "./raw_data/2013_14_raw.txt", "./raw_data/2014_15_raw.txt"]
years = ["00_01", "01_02", "02_03", "03_04", "04_05", "05_06", "06_07", "07_08", "08_09", "09_10", "10_11", "11_12", "12_13", "13_14", "14_15"]

connection = sqlite3.connect("./db/NBAstats.db")
cursor = connection.cursor()

function.clearDB(cursor)
function.createTables(cursor)

for i in range(0, len(srcFiles)):
    infile = open(srcFiles[i])

    line = infile.readline()
    while (line):
        # I have no idea why ' character will not be consider the same
        # So I replace ' with "
        line = line.replace("\'", "\"")

        if line.split(",")[0].isdigit():
            # outfile.write(line)
            rank,player,position,age,team,games,gamesStarted,minutes,fieldGoal,fieldGoalAttempts,fieldGoalPercentage,threePoint,threePointAttempts,threePointsPercentage,twoPoint,twoPointAttempts,twoPointsPercentage,effectiveFieldGoalPercentage,freeThrow,freeThrowAttempts,freeThrowPercentage,offensiveRebounds,defensiveRebounds,totalRebounds,assists,steals,blocks,turnovers,fouls,points = line.split(",")
            # insert into playerTable if not exists
            birth = i + 2000 - int(age)
            playerId = function.ifExistPlayer(cursor, player, birth)
            if playerId == -1:
                playerId = function.rowNumOfPlayer(cursor)
                cursor.execute("INSERT INTO playerTable VALUES (?, ?, ?)", (playerId, player, birth))
            #  insert into teamTable is not exists
            teamId = function.ifExistTeam(cursor, team)
            if teamId == -1:
                teamId = function.rowNumOfTeam(cursor)
                cursor.execute("INSERT INTO teamTable VALUES (?, ?)", (teamId, team))
            # insert into statsTable
            year = years[i]
            cursor.execute("INSERT INTO stats VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (playerId,position,year,age,teamId,games,gamesStarted,minutes,fieldGoal,fieldGoalAttempts,fieldGoalPercentage,threePoint,threePointAttempts,threePointsPercentage,twoPoint,twoPointAttempts,twoPointsPercentage,effectiveFieldGoalPercentage,freeThrow,freeThrowAttempts,freeThrowPercentage,offensiveRebounds,defensiveRebounds,totalRebounds,assists,steals,blocks,turnovers,fouls,points))

        line = infile.readline()

    infile.close()

connection.commit()
cursor.close()
connection.close()

