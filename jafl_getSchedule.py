#You could use a library called requests.

#import requests
import os
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from datetime import datetime


def giveMeGameRows(tag):
	return tag['class'] == 'oddrow' or tag['class'] == 'evenrow'

def formatDate(dateString, currentYear):
	# param - dateString Wednesday, August 27
	# param - currentYear 2014

	#thisYear = datetime.now().strftime('%y')
	date_object = datetime.strptime(dateString, '%A, %B %d')
	if date_object.month > 2:
		date_object = date_object.replace(year=2014)
	else:
		date_object = date_object.replace(year=int(currentYear)+1)
	#datetime.strptime(date_object, '%A, %B %d %Y').strftime('%m/%d/%y')
	return date_object
	# we are going to assume that anything before april is next year and anything after is this year for season
	# really should never matter more than january but going with april

def formatTime(timeString):
	if timeString == 'TBA':
		timeString = ''
	else:
		timeString = datetime.strptime(timeString, '%I:%M %p').strftime('%I:%M:%S %p')
	return timeString

def cleanDisplayString(displayString):
	displayString = displayString.replace('  ', ' ')\
		.replace('*','')\
		.replace(';','')\
		.strip()
	return displayStringhon
	

outputFilePath = '/Users/adidaska/Dropbox/FootballPoolProject/PythonScripts/espnSchedule2015.csv'
sampleTablePath = '/Users/adidaska/Dropbox/KIT/Python Work/sampleTable/sampleTable.html'
#pathMain = "http://www.bestbuy.com/site/olstemplatemapper.jsp?id=pcat17096&type=page&strId=xxx&ld=28.520824&lg=-81.586365&rd=25&usc=abcat0101000&nrp=100&cp=1"


getAllDiv1 = True
espnScheduleSite = 'http://espn.go.com/college-football/schedule/_/week/'
espnAllDiv1 = '/group/90'
espnScheduleSiteWeekPath = 'http://espn.go.com/college-football/schedule/_/week/1'

week = 1
indexNum = 1
requestString = espnScheduleSite + str(week)
if getAllDiv1:
	requestString += espnAllDiv1 
req = Request(requestString, headers={'User-Agent': 'Mozilla/5.0'})
webpage = urlopen(req).read().decode("utf-8")
webPageText = webpage.replace('</tr></tr>','</tr>')
webTextSoup = BeautifulSoup(webPageText, "html.parser")
finalTableText = ''
allGameData = []

# first get the number of weeks from the list of links
#weekSoup = webTextSoup.select("div.week a")
#schedule-page > form > fieldset > div.form-group.mobile > div:nth-child(2) > div > ul
#numberOfWeeks = len(weekSoup)
#currentYear = webTextSoup.select("div.mod-content h2")[0].text[:4]

# first get the number of weeks from the list of links
#weekSoup = webTextSoup.select("#schedule-page > form > fieldset > div.form-group.mobile > div:nth-child(2) > div > ul li")
numberOfWeeks = 15 
#len(weekSoup)
currentYear = webTextSoup.select("#schedule-page > header > h1")[0].text[:4]

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


	# for espn site the outer div is #content then there are 3 .mod_content divs...
	# the first div is the menu and the second is the game tables and the third is footer links
	# each day is its own table

	tableSoup = webTextSoup.select('#my-teams-table table')
	for dayTable in tableSoup:

		# row 1 = date
		# table > tr > td -> date
		date = dayTable.td.string
		# need to format the date to mm/dd/yy

		# row 2 = header class= colhead

		# row 3+ = games
		gameRowList = dayTable.find_all("tr")
		gameRowList.pop(1)
		gameRowList.pop(0)
		for rowItem in gameRowList:
			# print(rowItem.td.contents[0])
			gameInfo = rowItem.find_all('td')
			time = formatTime(gameInfo[0].string)
			homeTeam = gameInfo[1].find_all('a')[0].string
			visTeam = gameInfo[1].find_all('a')[1].string
			vs = gameInfo[1].string
			station = gameInfo[2].string
			mobile = gameInfo[3].string
			dateString = formatDate(date, currentYear).strftime('%m/%d/%y')
			displayName = cleanDisplayString(gameInfo[1].get_text())

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