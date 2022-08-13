#You could use a library called requests.

#import requests
import os
import dateutil.parser
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from datetime import datetime
from dateutil import tz

baseFilePath = 'results/'
baseFileName = 'espn2022'
outputFileNameSchedule = 'SchedA'
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
    findTheTeam = teamNameSoup.find_all('span', 'Table__Team')
    teamNameTag = teamNameSoup.find('.Table__Team')
    # print(findTheTeam)
    if findTheTeam == None:
        teamName = 'Unknown'
    elif len(findTheTeam) > 0:
        teamName = findTheTeam[0].get_text()
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




if getAllDiv1:
    requestString += espnAllDiv1
req = Request(requestString, headers={'User-Agent': 'Mozilla/5.0'})
webpage = urlopen(req).read().decode("utf-8")
#this next line was added as there was an issue with the html... not sure if still needed
webPageText = webpage.replace('</tr></tr>','</tr>')
webTextSoup = BeautifulSoup(webPageText, "html.parser")
finalTableText = ''
# allGameData = []

numberOfWeeks = 15 #just going to hard code this for now
# print(webTextSoup.select(".ScheduleTables"))
currentYear = 2022 #webTextSoup.select("#schedule-page header > h1")[0].text[-4:]

# loop through getting each week
while week <= numberOfWeeks:

    if(week != 1):
        requestString = espnScheduleSite + str(week)
        if getAllDiv1:
            requestString += espnAllDiv1
        req = Request(requestString, headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urlopen(req).read().decode('utf-8')
        #webPageText = webpage.replace('</tr></tr>','</tr>')
        webTextSoup = BeautifulSoup(webpage, "html.parser")

    #2022 - new site intro.. each week on page..
    #overall new structure. days are individual tables. class"mt3" contains week. within that are ScheduleTables for the days. each has the the date at the top. game rows are within the table
    #so get the overall div. then the list of ScheduleTables. loop through each and grab the date then loop through the game table

    tableSoup = webTextSoup.select('#mt3')
    print('currently getting games for week ' + str(week))

    #get the daytables

    #old way to get dates
    # datesElementsSoup = webTextSoup.find_all('h2', class_='table-caption')
    # datesElements = []
    # for x in datesElementsSoup:
    #     datesElements.append(x.string + ', ' + currentYear)


    tableSoup = webTextSoup.find_all(class_='ScheduleTables')
    dayTablesInWeek = len(tableSoup)
    print(str(dayTablesInWeek) + ' in week ' + str(week))

    for dayTable in tableSoup:

        date = dayTable.select('.Table__Title')[0].string
        print(date)

        gameRowList = dayTable.find_all("tr")

        for rowItem in gameRowList:
            gameInfo = rowItem.find_all('td')
            # print(gameInfo)

            if len(gameInfo) != 0:
                print(getTeamName(gameInfo[1]) + ' @ ' + getTeamName(gameInfo[0]))
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
                indexNum += 1
        # index += 1
    week += 1

loopVar = 1
print(len(allGameData))

gameReplacementData = {
    # 'St.': 'State',
    # 'W.': 'Western',
    # 'C.': 'Central',
    # 'VMI': 'Virginia Military',
    # 'UC-Davis': 'UC Davis',
    # 'The Citadel': 'Citadel',
    # 'Tenn.': 'Tennessee',
    # 'Saint Francis (PA.)': 'St. Francis (PA)',
    # 'Saint Augustine': 'St. Augustine',
    # 'SMU': 'Southern Methodist',
    # 'Sam Hou. State': 'Sam Houston State',
    # 'S.F. Austin': 'Stephen F. Austin',
    # 'Ole Miss': 'Mississippi',
    "Hawai'i": 'Hawaii',
    'Texas A&M;': 'Texas A&M',
    'North Carolina A&T;': 'North Carolina A&T',
    'Florida A&M;': 'Florida A&M',
    'Alabama A&M;': 'Alabama A&M',
    # 'BYU': 'Brigham Young',
    # 'Florida Intl': 'Florida International',
    # 'UL Monroe': 'Lousiana-Monroe',
    # 'UConn': 'Connecticut',
    'Prairie View': 'Prairie View A&M',
    # 'Central Connecticut': 'Central Connecticut State',
    # 'Southern': 'Southern University',
    # 'UMass': 'Massachusetts',
    # 'UT Martin': 'Tennessee-Martin',
    # 'Grambling': 'Grambling State',
    # 'UT San Antonio': 'Texas-San Antonio',
    # 'Miami': 'Miami (FL)',
    # 'Lousiana-Monroe': 'Louisiana-Monroe',
    # 'Southern Mississippi': 'Southern Miss',
    # 'McNeese': 'McNeese State',
    # 'NC State': 'North Carolina State',
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
for data in allGameData:
    for dataElement in data:
        finalTableText += str(dataElement)
        if data.index(dataElement) < (len(data) - 1):
            finalTableText += ','
    finalTableText += '\n'
with open (outputFilePath, 'w') as myOutfile:
    myOutfile.write(finalTableText)
print('the export has finished with ' + str(len(allGameData)) + ' games')



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
