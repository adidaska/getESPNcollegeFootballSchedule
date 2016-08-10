#You could use a library called requests.

#import requests
import os
import dateutil.parser
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from datetime import datetime
from dateutil import tz


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


    

outputFilePath = '/Users/adidaska/Dropbox/FootballPoolProject/PythonScripts/espnSchedule2016.csv'
sampleTablePath = '/Users/adidaska/Dropbox/KIT/Python Work/sampleTable/sampleTable.html'
#pathMain = "http://www.bestbuy.com/site/olstemplatemapper.jsp?id=pcat17096&type=page&strId=xxx&ld=28.520824&lg=-81.586365&rd=25&usc=abcat0101000&nrp=100&cp=1"


getAllDiv1 = False
espnScheduleSite = 'http://espn.go.com/college-football/schedule/_/group/80/week/'
espnAllDiv1 = '/group/90'
espnScheduleSiteWeekPath = 'http://espn.go.com/college-football/schedule/_/group/80/week/1'

week = 1
indexNum = 1
requestString = espnScheduleSite + str(week)
if getAllDiv1:
    requestString += espnAllDiv1 
req = Request(requestString, headers={'User-Agent': 'Mozilla/5.0'})
webpage = urlopen(req).read().decode("utf-8")
#this next line was added as there was an issue with the html... not sure if still needed
webPageText = webpage.replace('</tr></tr>','</tr>')
webTextSoup = BeautifulSoup(webPageText, "html.parser")
finalTableText = ''
allGameData = []

#so things we need
#year
#weeks in the season on the site



# first get the number of weeks from the list of links
#weekSoup = webTextSoup.select("#schedule-page > form > fieldset > div.form-group.mobile > div:nth-child(2) > div > ul li")
numberOfWeeks = 15 #just going to hard code this for now
#len(weekSoup)
currentYear = webTextSoup.select("#schedule-page > header > h1")[0].text[-4:]
#print(currentYear)

# loop through getting each week
while week <= numberOfWeeks:

    if(week != 1):
        requestString = espnScheduleSite + str(week)
        if getAllDiv1:
            requestString += espnAllDiv1 
        req = Request(requestString, headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urlopen(req).read().decode('utf-8')
        webPageText = webpage.replace('</tr></tr>','</tr>')
        webTextSoup = BeautifulSoup(webPageText)
        print(webTextSoup)

    # so for 2015 the site was redone. each day is a table.
    # the first row is the date and then the date is in the caption
    # each tr in the table is a game.. the th had the column headers as should

    tableSoup = webTextSoup.select('#sched-container table')
    #print(tableSoup)
    for dayTable in tableSoup:
        print(dayTable)
        date = dayTable.caption.string
        gameRowList = dayTable.find_all("tr")

        for rowItem in gameRowList:
            gameInfo = rowItem.find_all('td')

            if len(gameInfo) != 0:

                time = ''
                if gameInfo[2].get('data-date') != None:
                    print(requestString)
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
    week += 1




# # save file
for data in allGameData:
    for dataElement in data:
        finalTableText += str(dataElement)
        if data.index(dataElement) < (len(data) - 1):
            finalTableText += ','
    finalTableText += '\n'
with open (outputFilePath, 'w') as myOutfile:
    myOutfile.write(finalTableText)
print('done')