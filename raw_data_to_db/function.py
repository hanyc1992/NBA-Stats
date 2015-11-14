__author__ = 'hanyc'

def clearDB(cursor):
    cursor.execute("DROP TABLE IF EXISTS playerTable")
    cursor.execute("DROP TABLE IF EXISTS teamTable")
    cursor.execute("DROP TABLE IF EXISTS stats")

def createTables(cursor):
    # using name and birth because of duplication of names
    cursor.execute("CREATE TABLE IF NOT EXISTS playerTable (playerId INTEGER PRIMARY KEY , name TEXT, birth INTEGER);")
    cursor.execute("CREATE TABLE IF NOT EXISTS teamTable (teamId INTEGER PRIMARY KEY , name TEXT);")
    cursor.execute("""CREATE TABLE IF NOT EXISTS stats (playerId INTEGER, position TEXT, year TEXT, age INTEGER, teamId INTEGER,
                  games INTEGER, gamesStarted INTEGER, minutes REAL, fieldGoal REAL,fieldGoalAttempts REAL,fieldGoalPercentage REAL,
                  threePoint REAL, threePointAttempts REAL, threePointsPercentage REAL, twoPoint REAL, twoPointAttempts REAL,
                  twoPointsPercentage REAL, effectiveFieldGoalPercentage REAL, freeThrow REAL,freeThrowAttempts REAL,
                  freeThrowPercentage REAL, offensiveRebounds REAL, defensiveRebounds REAL, totalRebounds REAL, assists REAL,
                  steals REAL, blocks REAL, turnovers REAL, fouls REAL, points REAL)""")

# return type is int, can use as:
#       num = rowNumOfPlayer(cursor)
def rowNumOfPlayer(cursor):
    return cursor.execute("SELECT Count(*) FROM playerTable").fetchone()[0]

def rowNumOfTeam(cursor):
    return cursor.execute("SELECT Count(*) FROM teamTable").fetchone()[0]


# if exists, return the corresponding id
# if not, return -1
# return type is int, can use as:
#       id = ifExistPlayer(cursor, "Yao Ming")
def ifExistPlayer(cursor, queryName, birth):
    try:
        return cursor.execute("SELECT * FROM playerTable WHERE name = ? AND birth = ?", (queryName, birth)).fetchone()[0]
    except:
        return -1

def ifExistTeam(cursor, queryName):
    try:
        return cursor.execute("SELECT * FROM teamTable WHERE name = ?", (queryName,)).fetchone()[0]
    except:
        return -1