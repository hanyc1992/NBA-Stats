import sqlite3
import os.path
from flask import Flask, request, session, g, redirect, url_for, abort, \
    render_template, flash


class Player:
    def __init__(self, playerId, name):
        self.playerId = playerId
        self.name = name


class PlayerStats:
    def __init__(self, playerName,season,team,games,gamesStarted,minutes,fieldGoalPercentage,threePointsPercentage,freeThrowPercentage,offensiveRebounds,defensiveRebounds,totalRebounds,assists,steals,blocks,turnovers,fouls,points):
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
    # already ignore case
    for xx in items:
        if searchContent.lower() in [x.lower() for x in xx[1].split()]:
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
    season = request.args.get('season')
# constrain1
    attribute1=request.form['attribute1']
    compare1=request.form['compare1']
    stats1=request.form['stats1']
    constraint1 = " cast(stats." + attribute1 + " as REAL)" + compare1 + stats1
    constraint.append(attribute1 + " " + compare1 + " " + stats1)
    # no constraint, then use any statement that is always true
    if stats1 == "":
        constraint1 = "stats.teamId = teamTable.teamId"
        constraint.pop()
# constrain2
    attribute2=request.form['attribute2']
    compare2=request.form['compare2']
    stats2=request.form['stats2']
    constraint2 = " cast(stats." + attribute2 + " as REAL)" + compare2 + stats2
    constraint.append(attribute2 + " " + compare2 + " " + stats2)
    # no constraint, then use any statement that is always true
    if stats2 == "":
        constraint2 = "stats.teamId = teamTable.teamId"
        constraint.pop()
# constrain3
    attribute3=request.form['attribute3']
    compare3=request.form['compare3']
    stats3=request.form['stats3']
    constraint3 = " cast(stats." + attribute3 + " as REAL)" + compare3 + stats3
    constraint.append(attribute3 + " " + compare3 + " " + stats3)
    # no constraint, then use any statement that is always true
    if stats3 == "":
        constraint3 = "stats.teamId = teamTable.teamId"
        constraint.pop()

    items = g.db.execute("SELECT DISTINCT playerTable.playerId, playerTable.name FROM playerTable, teamTable, stats WHERE stats.teamId = teamTable.teamId AND stats.playerId = playerTable.playerId AND stats.year = ? AND %s AND %s AND %s" %(constraint1,constraint2,constraint3), (season,)).fetchall()
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
    playerId = request.args.get('playerId')
    playerName = request.args.get('playerName')
    items = g.db.execute("SELECT * FROM stats WHERE playerId = ?", (playerId,))
    stats = []
    for item in items:
        playerId,position,year,age,teamId,games,gamesStarted,minutes,fieldGoal,fieldGoalAttempts,fieldGoalPercentage,threePoint,threePointAttempts,threePointsPercentage,twoPoint,twoPointAttempts,twoPointsPercentage,effectiveFieldGoalPercentage,freeThrow,freeThrowAttempts,freeThrowPercentage,offensiveRebounds,defensiveRebounds,totalRebounds,assists,steals,blocks,turnovers,fouls,points = item
        teamName = g.db.execute("SELECT name FROM teamTable WHERE teamId = ?", (teamId,)).fetchall()[0][0]
        info = PlayerStats(playerName,year,teamName,games,gamesStarted,minutes,fieldGoalPercentage,threePointsPercentage,freeThrowPercentage,offensiveRebounds,defensiveRebounds,totalRebounds,assists,steals,blocks,turnovers,fouls,points)
        stats.append(info)
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
    return render_template('playerInTeam.html', players=players, page="playerInTeam")


@app.route('/searchByPlayer', methods=['GET'])
def searchByPlayer():
    items = g.db.execute('SELECT * FROM playerTable').fetchall()
    itemsa = [[]]
    itemsb = [[]]
    itemsc = [[]]
    itemsd = [[]]
    itemse = [[]]
    itemsf = [[]]
    itemsg = [[]]
    itemsh = [[]]
    itemsi = [[]]
    itemsj = [[]]
    itemsk = [[]]
    itemsl = [[]]
    itemsm = [[]]
    itemsn = [[]]
    itemso = [[]]
    itemsp = [[]]
    itemsq = [[]]
    itemsr = [[]]
    itemss = [[]]
    itemst = [[]]
    itemsu = [[]]
    itemsv = [[]]
    itemsw = [[]]
    itemsx = [[]]
    itemsy = [[]]
    itemsz = [[]]

    for item in items:
        if item[1].startswith('A'):
            if len(itemsa[-1]) < COLUMN_NUM:
                itemsa[-1].append(Player(item[0], item[1]))
            else:
                itemsa.append([(Player(item[0], item[1])),])
        elif item[1].startswith('B'):
            if len(itemsb[-1]) < COLUMN_NUM:
                itemsb[-1].append(Player(item[0], item[1]))
            else:
                itemsb.append([(Player(item[0], item[1])),])
        elif item[1].startswith('C'):
            if len(itemsc[-1]) < COLUMN_NUM:
                itemsc[-1].append(Player(item[0], item[1]))
            else:
                itemsc.append([(Player(item[0], item[1])),])
        elif item[1].startswith('D'):
            if len(itemsd[-1]) < COLUMN_NUM:
                itemsd[-1].append(Player(item[0], item[1]))
            else:
                itemsd.append([(Player(item[0], item[1])),])
        elif item[1].startswith('E'):
            if len(itemse[-1]) < COLUMN_NUM:
                itemse[-1].append(Player(item[0], item[1]))
            else:
                itemse.append([(Player(item[0], item[1])),])
        elif item[1].startswith('F'):
            if len(itemsf[-1]) < COLUMN_NUM:
                itemsf[-1].append(Player(item[0], item[1]))
            else:
                itemsf.append([(Player(item[0], item[1])),])
        elif item[1].startswith('G'):
            if len(itemsg[-1]) < COLUMN_NUM:
                itemsg[-1].append(Player(item[0], item[1]))
            else:
                itemsg.append([(Player(item[0], item[1])),])
        elif item[1].startswith('H'):
            if len(itemsh[-1]) < COLUMN_NUM:
                itemsh[-1].append(Player(item[0], item[1]))
            else:
                itemsh.append([(Player(item[0], item[1])),])
        elif item[1].startswith('I'):
            if len(itemsi[-1]) < COLUMN_NUM:
                itemsi[-1].append(Player(item[0], item[1]))
            else:
                itemsi.append([(Player(item[0], item[1])),])
        elif item[1].startswith('J'):
            if len(itemsj[-1]) < COLUMN_NUM:
                itemsj[-1].append(Player(item[0], item[1]))
            else:
                itemsj.append([(Player(item[0], item[1])),])
        elif item[1].startswith('K'):
            if len(itemsk[-1]) < COLUMN_NUM:
                itemsk[-1].append(Player(item[0], item[1]))
            else:
                itemsk.append([(Player(item[0], item[1])),])
        elif item[1].startswith('L'):
            if len(itemsl[-1]) < COLUMN_NUM:
                itemsl[-1].append(Player(item[0], item[1]))
            else:
                itemsl.append([(Player(item[0], item[1])),])
        elif item[1].startswith('M'):
            if len(itemsm[-1]) < COLUMN_NUM:
                itemsm[-1].append(Player(item[0], item[1]))
            else:
                itemsm.append([(Player(item[0], item[1])),])
        elif item[1].startswith('N'):
            if len(itemsn[-1]) < COLUMN_NUM:
                itemsn[-1].append(Player(item[0], item[1]))
            else:
                itemsn.append([(Player(item[0], item[1])),])
        elif item[1].startswith('O'):
            if len(itemso[-1]) < COLUMN_NUM:
                itemso[-1].append(Player(item[0], item[1]))
            else:
                itemso.append([(Player(item[0], item[1])),])
        elif item[1].startswith('P'):
            if len(itemsp[-1]) < COLUMN_NUM:
                itemsp[-1].append(Player(item[0], item[1]))
            else:
                itemsp.append([(Player(item[0], item[1])),])
        elif item[1].startswith('Q'):
            if len(itemsq[-1]) < COLUMN_NUM:
                itemsq[-1].append(Player(item[0], item[1]))
            else:
                itemsq.append([(Player(item[0], item[1])),])
        elif item[1].startswith('R'):
            if len(itemsr[-1]) < COLUMN_NUM:
                itemsr[-1].append(Player(item[0], item[1]))
            else:
                itemsr.append([(Player(item[0], item[1])),])
        elif item[1].startswith('S'):
            if len(itemss[-1]) < COLUMN_NUM:
                itemss[-1].append(Player(item[0], item[1]))
            else:
                itemss.append([(Player(item[0], item[1])),])
        elif item[1].startswith('T'):
            if len(itemst[-1]) < COLUMN_NUM:
                itemst[-1].append(Player(item[0], item[1]))
            else:
                itemst.append([(Player(item[0], item[1])),])
        elif item[1].startswith('U'):
            if len(itemsu[-1]) < COLUMN_NUM:
                itemsu[-1].append(Player(item[0], item[1]))
            else:
                itemsu.append([(Player(item[0], item[1])),])
        elif item[1].startswith('V'):
            if len(itemsv[-1]) < COLUMN_NUM:
                itemsv[-1].append(Player(item[0], item[1]))
            else:
                itemsv.append([(Player(item[0], item[1])),])
        elif item[1].startswith('W'):
            if len(itemsw[-1]) < COLUMN_NUM:
                itemsw[-1].append(Player(item[0], item[1]))
            else:
                itemsw.append([(Player(item[0], item[1])),])
        elif item[1].startswith('X'):
            if len(itemsx[-1]) < COLUMN_NUM:
                itemsx[-1].append(Player(item[0], item[1]))
            else:
                itemsx.append([(Player(item[0], item[1])),])
        elif item[1].startswith('Y'):
            if len(itemsy[-1]) < COLUMN_NUM:
                itemsy[-1].append(Player(item[0], item[1]))
            else:
                itemsy.append([(Player(item[0], item[1])),])
        elif item[1].startswith('Z'):
            if len(itemsz[-1]) < COLUMN_NUM:
                itemsz[-1].append(Player(item[0], item[1]))
            else:
                itemsz.append([(Player(item[0], item[1])),])

    return render_template('searchByPlayer.html', itemsa=itemsa, itemsb=itemsb, itemsc=itemsc, itemsd=itemsd,
                           itemse=itemse, itemsf=itemsf, itemsg=itemsg, itemsh=itemsh, itemsi=itemsi, itemsj=itemsj,
                           itemsk=itemsk, itemsl=itemsl, itemsm=itemsm, itemsn=itemsn, itemso=itemso, itemsp=itemsp,
                           itemsq=itemsq, itemsr=itemsr, itemss=itemss, itemst=itemst, itemsu=itemsu, itemsv=itemsv,
                           itemsw=itemsw, itemsx=itemsx, itemsy=itemsy, itemsz=itemsz, page="searchByPlayer")


if __name__ == '__main__':
    app.run(debug=True)
