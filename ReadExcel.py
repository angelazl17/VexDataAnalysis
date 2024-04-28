import pandas as pd
import xlrd
# from EventApi import getVexAllTeam,getTeamId
import json

def readVexDetail():
 
    # read by default 1st sheet of an excel file
    dataframe1 = pd.read_excel('./data/VexDetail.xlsx')

    dataframe1 = dataframe1[dataframe1['grade'] =="Middle School"]

    dataframe1 = dataframe1[["tsRanking","teamNumber","teamName","eventRegion","locCountry","trueskill","ccwm","opr","dpr"]]

    dataframe1 = dataframe1.sort_values(by=['tsRanking'], ascending=True)
    dataframe1['MiddleSchoolRank'] = dataframe1.reset_index().index+1

    dataframe1.to_csv("./data/msTeamAll.csv", sep=',', encoding='utf-8')
 
    print(dataframe1)
    return dataframe1

def createGoodCCWMTeamList():
    df = pd.read_excel('./data/2023DivisionskillAward-clean.xlsx')
    df=df.query("ccwm>5 and (champion >0 | finalists >0 | excellence>0 |skillaward>0)" )
    #df=df.query("(ccwm>5 ) | (champion >0 | finalists >0 | excellence>0 |skillaward>0) ")
    #df=df.query("champion >0 | finalists >0 | excellence>0 |skillaward>0")
    #df[(df.ccwm >=5) & ((df.champion >0)|(df.finalists >0)|(df.excellence))]
    df = df.sort_values(by=['teamNumber'], ascending=True)
    print(len(df.index))
    df.to_csv("./data/2023TeamCCWM5.csv", sep='\t', encoding='utf-8')

def readWorldTeamInfo():
    workbook = xlrd.open_workbook('./data/RE-VRC-22-9726-Teams-2023-04-08.xls', ignore_workbook_corruption=True)
    dataframe1 = pd.read_excel(workbook)
    return dataframe1

def readWorldDivisionTeamInfo():
    
    dataframe1 = pd.read_csv('./data/vrc-technology-division-team-list-worlds-2023-clean.csv')
    return dataframe1

def joinWorldDivisionTeamAndDetail():
    dfTeam = readWorldDivisionTeamInfo()
    dfDetail = readVexDetail()
    df_cd = pd.merge(dfTeam, dfDetail, how='left', left_on = 'Team', right_on = 'teamNumber')
    #df_cd = df_cd.sort_values(by=['MiddleSchoolRank'], ascending=True)
    #df_cd.to_csv("./data/2023DivisionTeamDetail.csv", sep='\t', encoding='utf-8')
    df_skill = pd.read_csv('./data/2023DivisionTeamID.csv')
    print(df_cd)
    print(df_skill)
    df_full=pd.merge(df_cd, df_skill, how='left', left_on = 'Team', right_on = 'TeamNumber')
    df_full.to_excel("./data/2023DivisionTeamDetailSkill.xlsx")
    df_full.to_csv("./data/2023DivisionTeamDetailSkill.csv", sep='\t', encoding='utf-8')
    return df_full

def addDivisionSkil():
    df_division=pd.read_csv('./data/2023DivisionTeamDetail.csv',index_col=False)
    df_skill = pd.read_csv('./data/2023DivisionTeamID_skill.csv')
    df_full=pd.merge(df_division, df_skill, how='left', left_on = 'Team', right_on = 'teamNumber')
    df_full.to_csv("./data/2023DivisionTeamDetailSkill.csv", sep='\t', encoding='utf-8')
    return df_full

def joinWorldTeamAndDetail(dfTeam,dfDetail):
    df_cd = pd.merge(dfTeam, dfDetail, how='left', left_on = 'Team', right_on = 'teamNumber')
    df_cd = df_cd.sort_values(by=['MiddleSchoolRank'], ascending=True)
    
    df_cd.to_csv("./data/2023TeamDetail.csv", sep='\t', encoding='utf-8')
    return df_cd

def getAllTeamId(token):
    allMiddleTeams=getVexAllTeam(token)
    jsonStr= json.dumps(allMiddleTeams)
    #df = pd.DataFrame.from_dict(dict, orient="index")
    #df = pd.read_json(allMiddleTeams)
    #df.to_csv("./data/allMSTeamWithID.csv", sep='\t', encoding='utf-8')
    df = pd.read_json(jsonStr)
    df.to_csv("./data/VexTeamRegister.csv", sep='\t', encoding='utf-8')
    return df

def updateTeamMoreInfo(token):
    dfDetail = readVexDetail()
    dfTeam= readWorldTeamInfo()
    
    dfWorld=joinWorldTeamAndDetail(dfTeam,dfDetail)
    dfWorld = dfWorld[["TeamId","teamName","MiddleSchoolRank","Organization","City","State","tsRanking","eventRegion","locCountry","trueskill","ccwm","opr","dpr"]]
    dfWorld['id'] =""
    df = dfWorld.reset_index()  # make sure indexes pair with number of rows

    for index, row in df.iterrows():
        teamNumber=row["teamNumber"]
        id=getTeamId(teamNumber,token)
        df.loc[index,["id"]]=[id]
        
    df.to_csv("./data/2023TeamDetail.csv", sep='\t', encoding='utf-8')


def addDivisionMOreDetail():
    # df_division=pd.read_csv('./data/2024DivisionTeamID.csv',index_col=False)
    df_division=pd.read_csv('./data/engineer_2024.csv',index_col=False)
    df_teamDetail = pd.read_csv('./data/msTeamAll.csv')
    print(df_division)
    print(df_teamDetail)
    df_full=pd.merge(df_division, df_teamDetail, how='left',left_on = 'Team', right_on = 'teamNumber')
    df_full.to_csv("./data/2024DivisionTeamDetail.csv", sep='\t', encoding='utf-8')


def main():
    token="eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIzIiwianRpIjoiYWQxMmYxOTBjZDk0ZmYyMGNmNDExY2YwZjU4NGM5MjM4NWE0ZGFjZDhhOTUxMTQ3NGU0MDU0YjMyZTNjMzhjNTA5M2FkZWFhZjA5YTI0ODEiLCJpYXQiOjE2Nzk3OTk2NTYuNjM3MDk2OSwibmJmIjoxNjc5Nzk5NjU2LjYzNzEsImV4cCI6MjYyNjU3NDQ1Ni42MzI2NjYxLCJzdWIiOiIxMTM1ODIiLCJzY29wZXMiOltdfQ.kejczJPbOzEOPC8ua2C1TrZJR1HKs7XU6-LiHQNTSlKxMWW3kXHTIYLk7K_6SK_NxVoPIU_RREy3teEy195xJCiYdd2JWjuz8pH-nM0CB7P7nx9-AoHFa_vNjnM03qpbxqe4QpeBtw0NiF0Srkxq028Rjl_cwU72SVxNUJUg2ug3BB8Zgfpu9VlSi7K1QSmKNy6hYVEgbOk3O6oc5XiEG70Z_wzVLpn1I1aiPxeEBLMbkMkUD1ZG3Y1XLb0JOsESeCOG6lJaXfnYbpf_j4WewBDwONhgcj9Qsp9uanIihneC3iIZDXR5X8wCF035QuHSEBfPneb8z710odCGqc4A38JUR8s80O42Xr6vx9WCTo9dfZLnE5R2n6DRP4ePu7f09hHsj8lof_vzlfc4LlXDsZ1ZJB1GCOJjNB8glheq8ofnl34JX-wkhVJEsvbdjoUk7xU6iPMquJnjNOxXj9sNOZQJDRg0VDejOltZFpoKhuIzv1kYITgLW29bcpztHIFsLkw4Mo0gozs-D6zDH1gawogGgQ7btT4xbGMPAHZyuUnGa0k-w3odvfny7pBh_WOV1kpzQ45sBsiIB7uMfkT8e7k5zd5rcwdV2rXJS4HHABHp6F4Iwe9a9k29PUTGG0yZniNol7NzJ0yP2diRkwg9iMUdmoG4-jI6X1VBnmWUkzM"
    #joinWorldDivisionTeamAndDetail()
    #addDivisionSkil()
    #createGoodCCWMTeamList()
    # readVexDetail()
    addDivisionMOreDetail()


main()

 