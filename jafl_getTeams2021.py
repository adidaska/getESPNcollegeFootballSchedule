#You could use a library called requests.
#python3

from datetime import datetime
from urllib.request import Request, urlopen

import dateutil.parser
from bs4 import BeautifulSoup

from dateutil import tz

baseFilePath = 'results/'
baseFileName = 'espn2022'
outputFileNameSchedule = 'Sched'
outputFilePath = baseFilePath + baseFileName + outputFileNameSchedule + '.csv'
outputFileNameTeams = baseFilePath + baseFileName + 'Teams' + '.csv'
getAllDiv1 = False
espnScheduleSite = 'http://espn.go.com/college-football/schedule/_/group/80/week/'
espnAllDiv1 = '/group/90'
espnScheduleSiteWeekPath = 'http://espn.go.com/college-football/schedule/_/group/80/week/1'
week = 1
indexNum = 1
requestString = espnScheduleSite + str(week)

def giveMeGameRows(tag):
    return tag['class'] == 'oddrow' or tag['class'] == 'evenrow'

def formatDate(dateString, currentYear):
    # param - dateString Wednesday, August 27
    # param - currentYear 2014

    #thisYear = datetime.now().strftime('%y')
    # date_object = datetime.strptime(dateString, '%A, %B %d')
    # if date_object.month > 2:
    #     date_object = date_object.replace(year=2015)
    # else:
    #     date_object = date_object.replace(year=int(currentYear)+1)
    #datetime.strptime(date_object, '%A, %B %d %Y').strftime('%m/%d/%y')
    date_object = dateutil.parser.parse(dateString)

    return date_object
    # we are going to assume that anything before april is next year and anything after is this year for season
    # really should never matter more than january but going with april

def formatTime(timeString):
    #need in the format 03:30:00 PM.. incoming 2015-08-29T19:30Z
    if timeString == 'TBA':
        timeString = ''
    else:
        #timeString = datetime.strptime(timeString, '%I:%M %p').strftime('%I:%M:%S %p')
        to_zone = tz.gettz('America/New_York')
        timeString = dateutil.parser.parse(timeString).astimezone(to_zone).strftime('%I:%M:%S %p')
    return timeString

def cleanDisplayString(displayString):
    displayString = displayString.replace('  ', ' ')\
        .replace('*','')\
        .replace(';','')\
        .strip()
    return displayString

def getTeamName(teamNameSoup):
    teamName = ''
    teamNameTag = teamNameSoup.find(True, {'class': 'team-name'})
    if teamNameTag == None:
        teamName = 'Unknown'
    elif teamNameTag.name == 'a':
        teamName = teamNameTag.find('span').string
    elif teamNameTag.name == 'span':
        teamName = teamNameTag.find('span').string
    return teamName



def convertToLocalTime():
    # METHOD 1: Hardcode zones:
    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz('America/New_York')

    # METHOD 2: Auto-detect zones:
    #from_zone = tz.tzutc()
    #to_zone = tz.tzlocal()

    # utc = datetime.utcnow()
    utc = datetime.strptime('2011-01-21 02:37:21', '%Y-%m-%d %H:%M:%S')

    # Tell the datetime object that it's in UTC time zone since
    # datetime objects are 'naive' by default
    utc = utc.replace(tzinfo=from_zone)

    # Convert time zone
    return utc.astimezone(to_zone)

def addTeamData(logoId, teamAbbr, collegeName, teamName):
    # need to grab the team name, team id, team abbr, college name
    teamNamesData = [teamAbbr, collegeName, teamName, logoId]
    # see if the data is already in the dataset so no dupes
    # if not then add
    allTeamNames.append(teamNamesData)
    #
    # team1abbr = gameInfo[0].abbr.string
    # team1college = getTeamName(gameInfo[0])
    # team1id = gameInfo[0].a.get('href').split('/')[5]
    # team2abbr = gameInfo[0].abbr.string
    # team2name = getTeamName(gameInfo[0])
    # team2id = gameInfo[0].a.get('href').split('/')[5]


# Define the gameData structure
# IndexNum
# Week
# VisitingTeam
# HomeTeam
# GameDate
# GameTime
# DisplayValue
# InPool
# PointSpread
# GameId
# vs - from website
# station - from website
# mobile - from website
allGameData = []
gameData = ['IndexNum', 'Week', 'VisitorName', 'HomeTeam', 'GameDate', 'GameTime', 'DisplayValue', 'InPool', 'PointSpread', 'GameId', 'VS', 'Station', 'Mobile']
allGameData.append(gameData)

allTeamNames = []
teamNamesData = ['TeamID', 'CollegeName', 'TeamName', 'LogoID']
allTeamNames.append(teamNamesData)




if getAllDiv1:
    requestString += espnAllDiv1
req = Request(requestString, headers={'User-Agent': 'Mozilla/5.0'})
webpage = urlopen(req).read().decode("utf-8")
#this next line was added as there was an issue with the html... not sure if still needed
webPageText = webpage.replace('</tr></tr>','</tr>')
webTextSoup = BeautifulSoup(webPageText, "html.parser")
finalTableText = ''
# allGameData = []
#print(webTextSoup)
numberOfWeeks = 15 #just going to hard code this for now

#currentYear = webTextSoup.select("#schedule-page > header > h1")[0].text[-4:]
currentYear = webTextSoup.select("#schedule-page .automated-header > h1")[0].text[-4:]
print(currentYear)
# loop through getting each week
while week <= numberOfWeeks:

    if(week != 1):
        requestString = espnScheduleSite + str(week)
        if getAllDiv1:
            requestString += espnAllDiv1
        req = Request(requestString, headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urlopen(req).read().decode('utf-8')
        webPageText = webpage.replace('</tr></tr>','</tr>')
        webTextSoup = BeautifulSoup(webPageText, "html.parser")

    tableSoup = webTextSoup.select('#sched-container')
    print('currently getting games for week ' + str(week))

    datesElementsSoup = webTextSoup.find_all('h2', class_='table-caption')
    datesElements = []
    for x in datesElementsSoup:
        datesElements.append(x.string + ', ' + currentYear)


    tableSoup = webTextSoup.find_all('table', class_='schedule')
    index = 0

    for dayTable in tableSoup:

        date = datesElements[index]
        print(index)

        gameRowList = dayTable.find_all("tr")


        for rowItem in gameRowList:
            gameInfo = rowItem.find_all('td')

            if len(gameInfo) != 0:
                #print(gameInfo)

                time = ''
                if gameInfo[2].get('data-date') != None:
                    time = formatTime(gameInfo[2].get('data-date'))
                homeTeam = getTeamName(gameInfo[1])
                visTeam = getTeamName(gameInfo[0])
                vs = '' #gameInfo[1].string
                station = '' #gameInfo[3].string
                mobile = '' #gameInfo[3].string
                dateString = formatDate(date, currentYear).strftime('%m/%d/%y')
                displayName = '' #cleanDisplayString(visTeam + ' at ' + homeTeam)
                gameData = [indexNum, week, visTeam, homeTeam, dateString, time, displayName, 'No', '', '', vs, station, mobile]
                allGameData.append(gameData)

                if visTeam != 'TBD':
                    team1name = gameInfo[0].abbr.get('title')
                    team1abbr = gameInfo[0].abbr.string
                    team1college = visTeam
                    team1id = gameInfo[0].a.get('href').split('/')[5]
                    addTeamData(team1id, team1abbr, team1college, team1name)

                if homeTeam != 'TBD':
                    team2name = gameInfo[1].abbr.get('title')
                    team2abbr = gameInfo[1].abbr.string
                    team2college = homeTeam
                    team2id = gameInfo[1].a.get('href').split('/')[5]
                    addTeamData(team2id, team2abbr, team2college, team2name)

                indexNum += 1
        index += 1
    week += 1

loopVar = 1
print(len(allGameData))
uniqueTeamNames = set(tuple(i) for i in allTeamNames)


# game replacement data is to change the team names to line up with the team names in the database
gameReplacementData = {
    # 'St.': 'State',
    # 'W.': 'Western',
    # 'C.': 'Central',
    # 'VMI': 'Virginia Military',
    # 'UC-Davis': 'UC Davis',
    # #'The Citadel': 'Citadel',
    # 'Tenn.': 'Tennessee',
    # # 'Saint Francis (PA.)': 'St. Francis (PA)',
    # 'Saint Augustine': 'St. Augustine',
    # 'SMU': 'Southern Methodist',
    # 'Sam Hou. State': 'Sam Houston State',
    # 'S.F. Austin': 'Stephen F. Austin',
    # 'Ole Miss': 'Mississippi',
    # #"Hawai'i": 'Hawaii',
    # 'Texas A&M;': 'Texas A&M',
    # 'North Carolina A&T;': 'North Carolina A&T',
    # 'Florida A&M;': 'Florida A&M',
    # 'Alabama A&M;': 'Alabama A&M',
    # 'BYU': 'Brigham Young',
    # 'Florida Intl': 'Florida International',
    # 'UL Monroe': 'Lousiana-Monroe',
    # #'UConn': 'Connecticut',
    # 'Prairie View': 'Prairie View A&M',
    # 'Central Connecticut': 'Central Connecticut State',
    # 'Southern': 'Southern University',
    # 'UMass': 'Massachusetts',
    # # 'UT Martin': 'Tennessee-Martin',
    # 'Grambling': 'Grambling State',
    # 'UT San Antonio': 'Texas-San Antonio',
    # 'Miami': 'Miami (FL)',
    # #'Lousiana-Monroe': 'Louisiana-Monroe',
    # 'Southern Mississippi': 'Southern Miss',
    # 'McNeese': 'McNeese State',
    # # 'NC State': 'North Carolina State',
    # 'Louisiana': 'Louisiana-Lafayette'

}

while loopVar < len(allGameData):
    # loop through allGameData for the k value and if found then replace
    currentGameData = allGameData[loopVar]
    for k, v in gameReplacementData.items():
        if k == currentGameData[2]:
            print('replacement made ' + k)
            currentGameData[2] = v
        elif k == currentGameData[3]:
            currentGameData[3] = v
            print('replacement made ' + k)

    #print(allGameData[loopVar])
    loopVar += 1





# # save file
for data in teamNamesData:
    for dataElement in data:
        finalTableText += str(dataElement)
        if data.index(dataElement) < (len(data) - 1):
            finalTableText += ','
    finalTableText += '\n'

for data in uniqueTeamNames:
    for dataElement in data:
        finalTableText += str(dataElement)
        if data.index(dataElement) < (len(data) - 1):
            finalTableText += ','
    finalTableText += '\n'

with open (outputFileNameTeams, 'w') as myOutfile:
    myOutfile.write(finalTableText)
print('the export has finished with ' + str(len(teamNamesData)) + ' games')





# so we need to find if the names match the team names we have in the db
# first we can use a list of known replacements
# then we need to find what names on the schedule do not have a match in the db
#
# gameReplacementData = {
#     'St.': 'State',
#     'W.': 'Western',
#     'C.': 'Central',
#     'VMI': 'Virginia Military',
#     'UC-Davis': 'UC Davis',
#     'The Citadel': 'Citadel',
#     'Tenn.': 'Tennessee',
#     'Saint Francis (PA.)': 'St. Francis (PA)',
#     'Saint Augustine': 'St. Augustine',
#     'SMU': 'Southern Methodist',
#     'Sam Hou. State': 'Sam Houston State',
#     'S.F. Austin': 'Stephen F. Austin',
#     'Ole Miss': 'Mississippi'
# }
#
# for gameData in allGameData.items():
#     # loop through allGameData for the k value and if found then replace
#     for data in gameData:
#         print(data.index(2))
#         print(data.index(3))

# To get the team names we have a few things to do.. we need the name, ID for the logo, a short ID (for summary screens) and the names match to the schedule
# on the espn site they dont list D I-AA on the teams page... but on the standings there is a second tab that shows them
# https://www.espn.com/college-football/standings
#https://site.web.api.espn.com/apis/v2/sports/football/college-football/standings?region=us&lang=en&contentorigin=espn&group=81&level=3&sort=leaguewinpercent%3Adesc%2Cvsconf_wins%3Adesc%2Cvsconf_gamesbehind%3Aasc%2Cvsconf_playoffseed%3Aasc%2Cwins%3Adesc%2Closses%3Adesc%2Cplayoffseed%3Aasc%2Calpha%3Aasc
#https://site.web.api.espn.com/apis/v2/sports/football/college-football/standings?region=us&lang=en&contentorigin=espn&group=80&level=3&sort=leaguewinpercent%3Adesc%2Cvsconf_wins%3Adesc%2Cvsconf_gamesbehind%3Aasc%2Cvsconf_playoffseed%3Aasc%2Cwins%3Adesc%2Closses%3Adesc%2Cplayoffseed%3Aasc%2Calpha%3Aasc
#actually can get from the schedule.. team name, abbr, id...
# so need to build the team names as we go through the schedule


