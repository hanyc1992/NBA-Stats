import sqlite3
import os.path
import re
from flask import Flask, request, session, g, redirect, url_for, abort, \
    render_template, flash


class Player:
    def __init__(self, playerId, name):
        self.playerId = playerId
        self.name = name


class PlayerStats:
    def __init__(self, exist,playerName,season,team,games,gamesStarted,minutes,fieldGoalPercentage,threePointsPercentage,freeThrowPercentage,offensiveRebounds,defensiveRebounds,totalRebounds,assists,steals,blocks,turnovers,fouls,points):
        self.exist = exist
        self.playerName = playerName
        self.season = season
        self.team = team
        self.games = games
        self.gamesStarted = gamesStarted
        self.minutes = minutes
        self.fieldGoalPercentage = fieldGoalPercentage
        self.threePointsPercentage = threePointsPercentage
        self.freeThrowPercentage = freeThrowPercentage
        self.offensiveRebounds = offensiveRebounds
        self.defensiveRebounds = defensiveRebounds
        self.totalRebounds = totalRebounds
        self.assists = assists
        self.steals = steals
        self.blocks = blocks
        self.turnovers = turnovers
        self.fouls = fouls
        self.points = points


# configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "NBAstats.db")
COLUMN_NUM = 4

app = Flask(__name__)
app.config.from_object(__name__)


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    g.db.close()


def dbToDisplaySeason(db):
    """ reformat season for better display """
    first, second = db.split('_')
    result = "20"+first+" - "+second
    return result


@app.route('/')
def welcomePage():
    return render_template('welcomePage.html')


@app.route('/searchHandler', methods=['POST'])
def searchHandler():
    searchContent=request.form['searchContent']

    items = g.db.execute("SELECT DISTINCT * FROM playerTable").fetchall()
    itemsFilter = []
    itemelse = []
    # already ignore case
    for xx in items:
        if (searchContent.lower() in [x.lower() for x in xx[1].split()]) or (searchContent.lower() == xx[1].lower()) or re.compile(searchContent.lower()).search(xx[1].lower()) != None:
            itemsFilter.append(xx)

    players = [[]]
    for item in itemsFilter:
        if len(players[-1]) < COLUMN_NUM:
            players[-1].append(Player(item[0], item[1]))
        else:
            players.append([(Player(item[0], item[1])),])

    return render_template('searchHandler.html', players=players, playerNum=len(itemsFilter), searchContent=searchContent, page="searchHandler")


@app.route('/filterResult', methods=['POST'])
def filterResult():
    constraint = []
    # constraintexe = []
    season = request.args.get('season')
    n =int(request.form['nval'])
    execution = "SELECT DISTINCT playerTable.playerId, playerTable.name FROM playerTable, teamTable, stats WHERE stats.teamId = teamTable.teamId AND stats.playerId = playerTable.playerId AND stats.year = \"%s\"" % season
    # execution += "AND stats.playerId = playerTable.playerId"
    for i in range(1,n+1):
        attribute=request.form['attribute'+str(i)]
        compare=request.form['compare'+str(i)]
        stats=request.form['stats'+str(i)]
        
        # no constraint, then use any statement that is always true
        if stats != "":
            # constraintexe.append(" cast(stats." + attribute + " as REAL)" + compare + stats)
            execution = execution+" AND cast(stats." + attribute + " as REAL)" + compare + stats
            constraint.append(attribute + " " + compare + " " + stats)
        else:
            # constraintexe.append("stats.teamId = teamTable.teamId")
            execution = execution+" AND stats.teamId = teamTable.teamId"

    items = g.db.execute(execution).fetchall()
    players = [[]]
    for item in items:
        if len(players[-1]) < COLUMN_NUM:
            players[-1].append(Player(item[0], item[1]))
        else:
            players.append([(Player(item[0], item[1])),])

    return render_template('filterResult.html', players=players, constraint=constraint, playerNum=len(items), page="filterResult")


@app.route('/filterPlayer', methods=['GET'])
def filterPlayer():
    season = request.args.get('season')
    return render_template('filterPlayer.html', seasonDisplay=dbToDisplaySeason(season), season=season, page="filterPlayer")


@app.route('/playerStats', methods=['GET'])
def playerStats():
    years = ["00_01","01_02","02_03","03_04","04_05","05_06","06_07","07_08","08_09","09_10","10_11","11_12","12_13","13_14","14_15"]
    index = 0

    playerId = request.args.get('playerId')
    playerName = request.args.get('playerName')
    stats = []
    empty = PlayerStats(0,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None)
    for count in range(0,len(years)):
        stats.append(empty)

    items = g.db.execute("SELECT * FROM stats WHERE playerId = ?", (playerId,))
    for item in items:
        playerId,position,year,age,teamId,games,gamesStarted,minutes,fieldGoal,fieldGoalAttempts,fieldGoalPercentage,threePoint,threePointAttempts,threePointsPercentage,twoPoint,twoPointAttempts,twoPointsPercentage,effectiveFieldGoalPercentage,freeThrow,freeThrowAttempts,freeThrowPercentage,offensiveRebounds,defensiveRebounds,totalRebounds,assists,steals,blocks,turnovers,fouls,points = item
        teamName = g.db.execute("SELECT name FROM teamTable WHERE teamId = ?", (teamId,)).fetchall()[0][0]
        info = PlayerStats(1,playerName,year,teamName,games,gamesStarted,minutes,fieldGoalPercentage,threePointsPercentage,freeThrowPercentage,offensiveRebounds,defensiveRebounds,totalRebounds,assists,steals,blocks,turnovers,fouls,points)
        # stats.append(info)
        stats[years.index(year)] = info



    return render_template('playerStats.html', stats=stats, playerName=playerName, page="playerStats")


@app.route('/searchByTeam', methods=['GET'])
def searchByTeam():
    season = request.args.get('season')
    items = g.db.execute("SELECT DISTINCT teamTable.name FROM teamTable, stats WHERE stats.teamId = teamTable.teamId AND stats.year = ?" , (season,)).fetchall()
    teams = [[]]
    for item in items:
        if item[0] != "TOT":
            if len(teams[-1]) < COLUMN_NUM:
                teams[-1].append(item[0])
            else:
                teams.append([item[0],])
    return render_template('searchByTeam.html', teams=teams, seasonDisplay=dbToDisplaySeason(season), season=season, page="searchByTeam")


@app.route('/playerInTeam', methods=['GET'])
def playerInTeam():
    season = request.args.get('season')
    team = request.args.get('team')
    items = g.db.execute("SELECT DISTINCT playerTable.playerId, playerTable.name FROM playerTable, teamTable, stats WHERE stats.teamId = teamTable.teamId AND stats.playerId = playerTable.playerId AND stats.year = ? AND teamTable.name = ?" , (season, team)).fetchall()
    players = [[]]
    for item in items:
        if len(players[-1]) < COLUMN_NUM:
            players[-1].append(Player(item[0], item[1]))
        else:
            players.append([(Player(item[0], item[1])),])
    return render_template('playerInTeam.html', players=players, page="playerInTeam", team=team, season=dbToDisplaySeason(season))


@app.route('/searchByPlayer', methods=['GET'])
def searchByPlayer():
    items = g.db.execute('SELECT * FROM playerTable').fetchall()
    item_list = []
    for i in range(26):
        item_list.append([[]]);


    for item in items:
        iname = item[1]
        init_num = ord(iname[0])-ord('A')
        if len(item_list[init_num][-1]) < COLUMN_NUM:
            item_list[init_num][-1].append(Player(item[0], item[1]))
        else:
            item_list[init_num].append([(Player(item[0], item[1])),])

    return render_template('searchByPlayer.html', itemsa=item_list[0], itemsb=item_list[1], itemsc=item_list[2], itemsd=item_list[3],
                           itemse=item_list[4], itemsf=item_list[5], itemsg=item_list[6], itemsh=item_list[7], itemsi=item_list[8], itemsj=item_list[9],
                           itemsk=item_list[10], itemsl=item_list[11], itemsm=item_list[12], itemsn=item_list[13], itemso=item_list[14], itemsp=item_list[15],
                           itemsq=item_list[16], itemsr=item_list[17], itemss=item_list[18], itemst=item_list[19], itemsu=item_list[20], itemsv=item_list[21],
                           itemsw=item_list[22], itemsx=item_list[23], itemsy=item_list[24], itemsz=item_list[25], page="searchByPlayer")


if __name__ == '__main__':
    app.run(debug=True)
