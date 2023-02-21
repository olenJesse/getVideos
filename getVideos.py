import os
import sqlite3
import traceback
from tkinter import messagebox
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def myAlert(myText: str, myTitle: str):
	messagebox.showerror(myTitle, myText)

def myLog(myText: str):
	print(f'{datetime.strftime(datetime.now(), "%H:%M:%S")} {myText}')

def myError(driver):
	if type(driver) == webdriver.firefox.webdriver.WebDriver:
		driver.quit()
	driver = None
	myAlert(traceback.format_exc(), 'Error')

def main():
	try:
		driver = None
		thisName = 'other'
		bookmarksFolderName = 'videos'
		getRecentVideos = 10
		firefoxProfile = r'C:\Users\Jesse\AppData\Roaming\Mozilla\Firefox\Profiles\7yr6lvv1.default-release'
		firefoxBinary = r'C:\Program Files\Mozilla Firefox\firefox.exe'
		oldContent = 'oldContent.txt'
		newContent = 'index.html'
		webdriverTimeout = 30
		myLog('start')
		theDatabase = 'file:' + firefoxProfile + '\places.sqlite?mode=ro'													  
		myLog(f'open database: {theDatabase}')
		with sqlite3.connect(theDatabase, uri=True) as conn:
			c = conn.cursor()
			theQuery = 'SELECT url FROM moz_places WHERE id IN (SELECT fk FROM moz_bookmarks WHERE parent = (SELECT id FROM moz_bookmarks WHERE (type = 2 AND parent = 2 AND title = "' + bookmarksFolderName + '")))'
			myLog(f'execute query: {theQuery}')
			c.execute(theQuery)
			myBookmarks = c.fetchall()
		countBookmarks = len(myBookmarks)
		myLog(f'{countBookmarks} bookmarks retrieved')
		if countBookmarks > 0:
			try:
				with open(oldContent, 'r', encoding='utf-8') as tempFile:
					oldData = tempFile.read()
			except FileNotFoundError:
				oldData = ''
			oldRows = oldData.split('\n')
			lastOldRow = len(oldRows)
			newData = ''
			tempData = ''
			options = webdriver.FirefoxOptions()
			options.add_argument('-headless')
			options.binary_location = firefoxBinary
			driver = webdriver.Firefox(options=options)
			for tempBookmark in myBookmarks:
				driver.get(tempBookmark[0])
				roska = WebDriverWait(driver, webdriverTimeout).until(EC.presence_of_element_located((By.TAG_NAME, 'button')))
				if driver.current_url.find('consent') > 0:
					myLog('consent window handling')
					theButtons = driver.find_elements(By.TAG_NAME, 'button')
					doExit = False
					for tempButton in theButtons:
						tempChildren = tempButton.find_elements(By.XPATH, './*')
						for tempChild in tempChildren:
							if tempChild.get_attribute('innerHTML').strip().lower() == 'reject all':
								tempButton.click()
								doExit = True
								break
						if doExit:
							myLog('consent window handled')
							break
					if not doExit:
						myLog('consent window handling failed')
						input()
				roska = WebDriverWait(driver, webdriverTimeout).until(EC.presence_of_element_located((By.ID, 'details')))
				tempTitle = driver.title.replace(' - YouTube', '')
				tempBoxes = driver.find_elements(By.ID, 'dismissible')
				tempCnt = 0
				foundCnt = 0
				newCount = 0
				for tempBox in tempBoxes:
					tempText = tempBox.get_attribute('innerText').lower()
					if not ' waiting' in tempText and not ' watching' in tempText:
						tempCnt += 1
						tempVideo = tempBox.find_element(By.ID, 'video-title-link')
						tempName = tempVideo.get_attribute('title').replace(' - ' + tempTitle, '')
						tempLink = tempVideo.get_attribute('href')
						thisRow = tempTitle + '\t' + tempName + '\t' + tempLink
						newData += ('\n' if newData != '' else '') + thisRow
						didFind = False
						if oldData != '':
							for oRow in range(lastOldRow):
								oldCols = oldRows[oRow].split('\t')
								if oldCols[1] == tempName or oldCols[2] == tempLink:
									didFind = True
									foundCnt += 1
									break
						if not didFind:
							tempData += ('\n' if tempData != '' else '') + thisRow
						if tempCnt >= getRecentVideos:
							break
				newCount = tempCnt - foundCnt
				myLog(f'{tempTitle}, new videos: {newCount}')
			driver.quit()
			driver = None
			tempRows = tempData.split('\n')
			lastTempRow = len(tempRows) - 1
			tempContent = '<html><head><title>'
			if lastTempRow >= 0:
				if lastTempRow >= 1:
					tempContent += '(' + str(lastTempRow + 1) + ') New ' + thisName + ' videos</title><style>'
				else:
					tempContent += '(1) New ' + thisName + ' video</title><style>'
				tempContent += 'body{background-color:#75d864;}'	
				tempContent += 'td{vertical-align:text-top;padding-right:10px;}'
				tempContent += 'button{background-color:#75d864;border:none;padding:5px;}'
				tempContent += 'span{font-size:14px;color:blue;text-decoration:underline;cursor:pointer;}'
				tempContent += 'span:hover{font-weight:bold;}'
				tempContent += 'input[type=checkbox]{display:none;}'
				tempContent += 'input[type=checkbox]:checked+span{color:red;}'
				tempContent += '</style></head><body>'
				tempContent += '<h1><u>New videos:</u></h1><table>'
				theAddress = 'https://www.youtube.com/'
				for tempRow in range(lastTempRow + 1):
					tempVals = tempRows[tempRow].split('\t')
					videoId = tempVals[2].replace(theAddress + 'watch?v=', '')
					if theAddress + 'shorts/' in videoId:
						tempContent += '<tr><td><b>' + tempVals[0] + '</b></td><td><form action="' + videoId + '" method="get" target="_blank"><button><label><input type="checkbox"><span>' + tempVals[1] + '</span></input></label></button></form></td></tr>'
					else:
						tempContent += '<tr><td><b>' + tempVals[0] + '</b></td><td><form action="' + theAddress + 'watch' + '" method="get" target="_blank"><button name="v" value="' + videoId + '"><label><input type="checkbox"><span>' + tempVals[1] + '</span></input></label></button></form></td></tr>'
				tempContent += '</table>'
			else:
				tempContent += 'No new ' + thisName + ' videos</title><style>body{background-color:gray;}</style></head><body><h2>No new ' + thisName + ' videos.</h2>'
			tempContent += '</body></html>'
			writeContent = tempContent.replace('><', '>\n<').replace('}', '}\n')
			with open(oldContent, 'w', encoding='utf-8') as tempFile:
				tempFile.write(newData)
			with open(newContent, 'w', encoding='utf-8') as tempFile:
				tempFile.write(writeContent)
			os.startfile(newContent)
		myLog('end')
	except:
		myError(driver)

main()