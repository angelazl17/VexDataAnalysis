import os

def cleanDivisionTeamInfo():
     divisionFile = './data/vrc-ms-technology-division-team-list-vex-worlds-2023.csv'
     resultFile = './data/vrc-technology-division-team-list-worlds-2023-clean.csv'

     fwp = open(resultFile, "w", encoding='utf-8')
     with open(divisionFile, encoding='utf-8') as fpp:
        line = fpp.readline()
        while line:
            
            x = line.split(",")
            newline=x[0]+'\n'
            print(newline)

            fwp.write(newline)
            line = fpp.readline()
cleanDivisionTeamInfo()