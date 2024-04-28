#pip install beautifulsoup4
#pip install requests

from bs4 import BeautifulSoup
import requests
import pandas as pd


def getUrlContent(link):
    r= requests.get(link)
    print(r.status_code)
    soup = BeautifulSoup(r.text,features="lxml")
    
    
    return soup

def findHtmlTable(soup):
    
    tags=soup.find_all(True)
    for tag in tags:
        if(tag is None):
            print('  There was no entry')
        else:
            if(tag.name!="script"):
                print(tag.name)
                #findHtmlTable(tag)
     

def main():
    body=getUrlContent("https://www.robotevents.com/robot-competitions/vex-robotics-competition/RE-VRC-22-9726.html#teams")
    findHtmlTable(body)


main()


