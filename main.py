
import json
from time import sleep
from selenium import webdriver
import selenium
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

if __name__ == '__main__':
    options = webdriver.ChromeOptions()
    options.add_argument('--user-data-dir=/home/bmcgee/.config/google-chrome/Default')

    service = Service('./chromedriver')
    driver = webdriver.Chrome(service=service, options=options)
    
    driver.get('http://bandcamp.com/mandalorian44')

    viewAllButton = driver.find_element(By.CLASS_NAME, 'show-more')
    viewAllButton.click()

    body =driver.find_element(By.TAG_NAME, 'body')

    scrolling = True
    maxTimeoutTries = 5
    timeoutCounter = 0
    lastHeight = 0

    while scrolling:        
        body.send_keys(Keys.END)
        sleep(.5)

        currentHeight = driver.execute_script("return document.documentElement.scrollHeight")

        if currentHeight == lastHeight:   
            timeoutCounter += 1         
            print('Timeout counter: ' + str(timeoutCounter))            
        elif currentHeight > lastHeight:
            lastHeight = currentHeight
        else: 
            timeoutCounter = 1

        if timeoutCounter == maxTimeoutTries:
            scrolling = False
            print('Reached timeout limit, stopping scrolling')

    collection = driver.find_element(By.XPATH, '//*[@id="collection-items"]/ol')
    items = collection.find_elements(By.TAG_NAME, 'li')

    count = 0

    jsonData = {}
    jsonData['items'] = []

    for item in items:
        # Verify if the li element is the main container collection kind and not sub element
        if 'collection-item-container' in item.get_attribute('class') :
            try:
                downloadSpan = item.find_element(By.CLASS_NAME, 'redownload-item')
                downloadLink = downloadSpan.find_element(By.TAG_NAME, 'a').get_attribute('href')

                title = item.find_element(By.CLASS_NAME, 'collection-item-title').text
                artist = item.find_element(By.CLASS_NAME, 'collection-item-artist').text             

                jsonItem = {
                    'type': item.get_attribute('data-itemtype'),
                    'title': title,
                    'artist': artist[3:],                    
                    'link': downloadLink,
                }
                jsonData['items'].append(jsonItem)

                print(item.get_attribute('data-itemtype'))
                print(title)
                print(artist[3:])
                print(downloadLink)
                print(str(count))
                print()
                
                count += 1
            
            # Just in case a collection item is no longer downloadable from Bandcamp
            except selenium.common.exceptions.NoSuchElementException as e:
                print('No download link found') 

    with open('test.json', 'w') as outfile:
        json.dump(jsonData, outfile, indent=4)
