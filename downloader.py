
import json
from time import sleep
import os
from selenium import webdriver
import selenium
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

if __name__ == '__main__':

    def wait_for_download(fileName):
        found = False
        maxFailCount = 50
        failCount = 1

        print('Waiting for download: ' + fileName)

        while not found:
            if failCount == maxFailCount:
                print('Max number of fails reached, moving to next item')
                print()
                return False

            if os.path.isfile('/home/bmcgee/Downloads/' + fileName):
                found = True
                print('Download Complete!')
                print()
                return True
            else:
                print('Waiting for download to complete. Try ' + str(failCount) + ' of ' + str(maxFailCount))
                failCount += 1
                sleep(.5)
        
    def check_filename(itemType, itemTitle, itemArtist):
        expectedFilename = itemArtist + ' - ' + itemTitle

        # Apparently bandcamp changes the ~ in an albums/tracks title with an _ instead when the file is downloaded
        if '~' in itemTitle:    
            expectedFilename = expectedFilename.replace('~', '_')

        # Apparently bandcamp changes the , in an albums/tracks title with an - instead when the file is downloaded
        elif ',' in itemTitle:  
            expectedFilename = expectedFilename.replace(',', '-')

        # Apparently bandcamp changes the . in an albums/tracks title with nothing instead when the file is downloaded
        elif '...' in itemTitle:  
            expectedFilename = expectedFilename.replace('...', '')

        # Apparently bandcamp changes the : in an albums/tracks title with - instead when the file is downloaded
        elif ':' in itemTitle:  
            expectedFilename = expectedFilename.replace(':', '-')

        # Apparently bandcamp changes the / in an albums/tracks title with - instead when the file is downloaded
        elif '/' in itemTitle:  
            expectedFilename = expectedFilename.replace('/', '-')

        # Apparently bandcamp removes a tailing - in filenames
        elif itemTitle[len(itemTitle) - 1] == '-':  
            expectedFilename = expectedFilename[:-1]    

        # Append .zip or .mp3 to filename depending on item type
        if itemType == 'album':
            expectedFilename = expectedFilename + '.zip'
        elif itemType == 'track':
            expectedFilename = expectedFilename + '.mp3'

        return expectedFilename
        

    def write_to_log(logFilename, message):
        with open(logFilename, 'a') as f:
            f.write(message)

    # Create logging file for any error messages
    logFilename = 'error_log.txt'
    logFile = open(logFilename, 'w')
    logFile.write('')
    logFile.close()

    # Read json downloads file
    jsonFile = open('test3.json', 'r')    
    jsonData = json.load(jsonFile)
    jsonFile.close()

    options = webdriver.ChromeOptions()
    options.add_argument('--user-data-dir=/home/bmcgee/.config/google-chrome/Default')

    service = Service('./chromedriver')
    driver = webdriver.Chrome(service=service, options=options)

    count = 1

    for item in jsonData['items']:
        driver.get(item['link'])
        downloadLink = driver.find_element(By.XPATH, '//*[@id="post-checkout-info"]/div[1]/div[2]/div[4]/span/a')

        itemType = item['type']
        itemTitle = item['title']
        itemArtist =  item['artist']
        itemLink = item['link']

        print('Downloading item ' + str(count) + ' of ' + str(len(jsonData['items'])))
        print('Type: ' + itemType)
        print('Title: ' + itemTitle)
        print('Artist: ' + itemArtist)      
        print()              

        maxFailCount = 20
        failCount = 1
        success = False

        while not success:
            try:
                downloadLink.click()
                success = True

                # Generate expected download filename from item type, title, and artist
                expectedFilename = check_filename(itemType, itemTitle, itemArtist)

                # Wait for download of expected file to complete
                success = wait_for_download(expectedFilename)

                # Record to error log if item was unable to be downloaded. 
                # Note: the correct item could have been downloaded but the expected filename 
                # and the actually downloaded file may not be the same. For example, Bandcamp 
                # could have changed the file name for some unknown reason.
                if not success:                     
                    errorString = 'Error found while downloading collection item:\n'
                    errorString += 'Type: ' + itemType + '\n'
                    errorString += 'Title: ' + itemTitle + '\n'
                    errorString += 'Artist: ' + itemArtist + '\n'
                    errorString += 'Link: ' + itemLink + '\n\n'

                    write_to_log(logFilename, errorString)
                    break
                                    
            except selenium.common.exceptions.ElementNotInteractableException as e:
                if failCount == maxFailCount:                        
                    print('Fail, max timeout reached!')
                    print()
                    break

                sleep(.5)
                failCount += 1

        count += 1


