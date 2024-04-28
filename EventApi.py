import requests
import pandas as pd
import json
import time


season="181"

def getEventApiJsonResult(url, token):
    keepTry=True
    while(keepTry):
        try:
            headers = {"Authorization": "Bearer " + token}
            
            auth_response = requests.get(url, headers=headers)
            result=auth_response.json()
            keepTry=False
            return result
        except:
            print("getEventApiJsonResult error, try again")
            time.sleep(3)
            keepTry=True
    

def getTeamId(teamNumber, tokenvalue):
    api_url = "https://www.robotevents.com/api/v2/teams?number%5B%5D={teamNumber}&myTeams=false"
    api_url = api_url.replace("{teamNumber}",teamNumber)
    print(api_url)
    
    #api_url = "https://www.robotevents.com/api/v2/teams?myTeams=false"
    headers = {"Authorization": "Bearer " + tokenvalue}
    
    auth_response = requests.get(api_url, headers=headers)
    #auth_response = requests.get(api_url,  headers=headers)
    result=auth_response.json()
    teamResult=result["data"][0]
    print(teamResult["id"])
    return teamResult["id"]

#get team id from teamNumber list, teamNumber List length<=15
def getTeamsId(token, teamNumberList):
    api_url = "https://www.robotevents.com/api/v2/teams?"
    teamNumberQuery="number%5B%5D={teamNumber}"
    teamQuery=""
 
        
    for i in range(len(teamNumberList)):
            
            if(i==0):
                teamQuery=teamNumberQuery.replace("{teamNumber}",teamNumberList[i])
            else:
                teamQuery= teamQuery+"&"+teamNumberQuery.replace("{teamNumber}",teamNumberList[i])
    #program=1 means VRC
    url=api_url+teamQuery+"&registered=true&program%5B%5D=1&myTeams=false"
    print(url)    
     
    result=getEventApiJsonResult(url,token)
    jsonStr= json.dumps(result["data"])
    df = pd.read_json(jsonStr)
    df = df[["id","number"]]
    df.columns=["TeamId","TeamNumber"]
    #df.to_csv("./data/2023DivisionTeamID.csv", sep='\t', encoding='utf-8')
    
    return df

def getDivisionTeamIds(token):
    dataframe1 = pd.read_csv('./data/2024_math_team_clean.csv')
    teamList=dataframe1["Team"].to_list()
    teamTotal = len(teamList)
    groupSize=10
    group=1
    if(teamTotal%groupSize==0):
        group=(int)(teamTotal/groupSize)
    else:
        group=int(teamTotal/groupSize)+1
    
    print("total="+str(teamTotal)+", group="+str(group))
    teamSubListArray=[]
    for j in range(group) :
        teamSubList=[]
        for i in range (groupSize):
            if(j*groupSize+i>=teamTotal):
                break
            teamSubList.append(teamList[j*groupSize+i])
        
        teamSubListArray.append(teamSubList)
    

    teamIdDfArray=[]
    for index, teamSub in enumerate(teamSubListArray):
        print(teamSub)
        df=getTeamsId(token, teamSub)
        dfDetail=getTeamsDetailInfo(token,df)
        teamIdDfArray.append(dfDetail)
        time.sleep(3)
        

    dfDivision=pd.concat(teamIdDfArray,ignore_index=True)
    print(dfDivision)
            

       
    dfDivision.to_csv("./data/2024DivisionTeamID.csv", sep=',', encoding='utf-8')

def getTeamsDetailInfo(token, dfTeamIds):
    #dfTeams = getTeamsId(token, teamNumberList)
    dfTeams =dfTeamIds
    dfTeams['Max_Driver_Skill'] ="N/A"
    dfTeams['Max_Programming_Skill'] ="N/A"
    df = dfTeams.reset_index()  # make sure indexes pair with number of rows

    for index, row in df.iterrows():
        teamId=row["TeamId"]
        skillDataframe=getTeamSkill(token,str(teamId))
        if(skillDataframe is None):
            df.loc[index,["Max_Driver_Skill"]]=["N/A"]
            df.loc[index,["Max_Programming_Skill"]]=["N/A"]
        else:
            driverSkill=getTeamSkillHighetScore(skillDataframe,"driver")
            programmingSkill=getTeamSkillHighetScore(skillDataframe,"programming")
            df.loc[index,["Max_Driver_Skill"]]=[driverSkill]
            df.loc[index,["Max_Programming_Skill"]]=[programmingSkill]
        awardJson=getTeamAwardJson(token,str(teamId))
        df.loc[index,["Total_Awards"]]=[awardJson["TotalAwards"]]
        df.loc[index,["count_champion"]]=[awardJson["count_TournamentChampion"]]
        df.loc[index,["count_finalists"]]=[awardJson["count_TournamentFinalists"]]
        df.loc[index,["count_excellence"]]=[awardJson["count_Excellence"]]
        df.loc[index,["count_skillChampion"]]=[awardJson["count_SkillChampion"]]
        df.loc[index,["count_design"]]=[awardJson["count_Design"]]
        df.loc[index,["count_judge"]]=[awardJson["count_Judge"]]
    df = df[["TeamId","TeamNumber","Max_Driver_Skill","Max_Programming_Skill","Total_Awards","count_champion","count_finalists","count_excellence","count_skillChampion","count_design","count_judge"]]

    print(df)
    return df



def getTeamSkillHighetScore(skillDataframe,type):
    df=skillDataframe
    dflen=len(df.to_dict("records"))
    if dflen==0 :
        return "N/A"
    else:
        dfType = df[df['type'] ==type]
        if len(dfType.to_dict("records")) ==0:
            return "N/A"
        else:
            return dfType['score'].max()

def getTeamInfo(token,teamId):
    api_url = "https://www.robotevents.com/api/v2/teams/{teamId}"
    api_url = api_url.replace("{teamId}",teamId)
    print(api_url)
    result=getEventApiJsonResult(api_url,token)
    teamNumber=result["number"]
    city=result["location"]["city"]
    data = {}
    data['TeamId'] = teamId
    data['TeamNumber'] = result["number"]
    data['TeamName'] = result["team_name"]
    data['City'] = result["location"]["city"]
    data['Region'] = result["location"]["region"]
    data['Country'] = result["location"]["country"]
    # data = {'TeamId':teamId,
    #     'TeamNumber':result["number"],
    #     'TeamName':result["team_name"],
    #     'City':result["location"]["city"],
    #     'Region':result["location"]["region"],
    #     'Country':result["location"]["country"]}
    print(data)
    # df = pd.DataFrame(data)
    # print(df) 
    

def getTeamSkill(token,teamNumber) :
    # api_url = "https://www.robotevents.com/api/v2/teams/{teamNumber}/skills?season%5B%5D=173"
    
    api_url = "https://www.robotevents.com/api/v2/teams/{teamNumber}/skills?season%5B%5D={season}"
    api_url = api_url.replace("{season}",season)
    api_url = api_url.replace("{teamNumber}",teamNumber)
    print(api_url)
   
    result=getEventApiJsonResult(api_url,token)

    if not result["data"]:
        print("No Skill")
        return None
    
    df = df = pd.json_normalize(result["data"])
    df = df[["id","event.id","team.id","team.name","type","score"]]
    print(df)
    return df

def getTeamAward(token,teamNumber) :
    #api_url = "https://www.robotevents.com/api/v2/teams/{teamNumber}/awards?season%5B%5D=173"
    
    api_url = "https://www.robotevents.com/api/v2/teams/{teamNumber}/awards?season%5B%5D={season}"
    api_url = api_url.replace("{season}",season)
    api_url = api_url.replace("{teamNumber}",teamNumber)
    print(api_url)
   
    result=getEventApiJsonResult(api_url,token)
    meta=result["meta"]
    total=meta["total"]
    if total== 0:
        print("No Award")
        return None
    
    df = df = pd.json_normalize(result["data"])
    

    df = df[["event.id","title","qualifications"]]
    print(df)
    return df

def getTeamAwardJson(token,teamId):
    df=getTeamAward(token,teamId)
    if(df is None):
        data = {}
        data['TeamId'] = teamId
        data['TotalAwards']=0
        data['count_TournamentChampion'] = 0
        data['count_TournamentFinalists']=0
        data['count_Excellence'] = 0
        data['count_SkillChampion']=0
        data['count_Design']=0
        data['count_Judge']=0
        json_data = json.dumps(data)
    else:

        data = {}
        data['TeamId'] = teamId
        data['TotalAwards']=len(df)
        countChampion= len(df[df['title'].str.contains("Tournament Champions")])
        data['count_TournamentChampion'] = countChampion
        countFinalists= len(df[df['title'].str.contains("Tournament Finalists")])
        data['count_TournamentFinalists'] = countFinalists
        countExcellence= len(df[df['title'].str.contains("Excellence Award")])
        data['count_Excellence'] = countExcellence
        countSkills= len(df[df['title'].str.contains("Skills Champion")])
        data['count_SkillChampion'] = countSkills
        countDesign= len(df[df['title'].str.contains("Design Award")])
        data['count_Design'] = countDesign
        countJudge= len(df[df['title'].str.contains("Judge Award")])
        data['count_Judge'] = countJudge
        json_data = json.dumps(data)
    print(json_data)
    return data

def getVexProgram(token):
    api_url = "https://www.robotevents.com/api/v2/programs"
    result=getEventApiJsonResult(api_url,token)
    print(result)


def getVexAllTeam(token):
    api_url = "https://www.robotevents.com/api/v2/teams?registered=true&type%5B%5D=Middle%20School&myTeams=false"
    
    json=getEventApiJsonResult(api_url,token)
    print(json["data"])
    return json["data"]

def main():
    token="eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIzIiwianRpIjoiYWQxMmYxOTBjZDk0ZmYyMGNmNDExY2YwZjU4NGM5MjM4NWE0ZGFjZDhhOTUxMTQ3NGU0MDU0YjMyZTNjMzhjNTA5M2FkZWFhZjA5YTI0ODEiLCJpYXQiOjE2Nzk3OTk2NTYuNjM3MDk2OSwibmJmIjoxNjc5Nzk5NjU2LjYzNzEsImV4cCI6MjYyNjU3NDQ1Ni42MzI2NjYxLCJzdWIiOiIxMTM1ODIiLCJzY29wZXMiOltdfQ.kejczJPbOzEOPC8ua2C1TrZJR1HKs7XU6-LiHQNTSlKxMWW3kXHTIYLk7K_6SK_NxVoPIU_RREy3teEy195xJCiYdd2JWjuz8pH-nM0CB7P7nx9-AoHFa_vNjnM03qpbxqe4QpeBtw0NiF0Srkxq028Rjl_cwU72SVxNUJUg2ug3BB8Zgfpu9VlSi7K1QSmKNy6hYVEgbOk3O6oc5XiEG70Z_wzVLpn1I1aiPxeEBLMbkMkUD1ZG3Y1XLb0JOsESeCOG6lJaXfnYbpf_j4WewBDwONhgcj9Qsp9uanIihneC3iIZDXR5X8wCF035QuHSEBfPneb8z710odCGqc4A38JUR8s80O42Xr6vx9WCTo9dfZLnE5R2n6DRP4ePu7f09hHsj8lof_vzlfc4LlXDsZ1ZJB1GCOJjNB8glheq8ofnl34JX-wkhVJEsvbdjoUk7xU6iPMquJnjNOxXj9sNOZQJDRg0VDejOltZFpoKhuIzv1kYITgLW29bcpztHIFsLkw4Mo0gozs-D6zDH1gawogGgQ7btT4xbGMPAHZyuUnGa0k-w3odvfny7pBh_WOV1kpzQ45sBsiIB7uMfkT8e7k5zd5rcwdV2rXJS4HHABHp6F4Iwe9a9k29PUTGG0yZniNol7NzJ0yP2diRkwg9iMUdmoG4-jI6X1VBnmWUkzM"
    
    # getTeamId("2668A",token)
    #getVexProgram(token)
    #getVexAllTeam(token)
    teamNumberList=["78759D","78759J","2668A","70709X","151T","2158Z"]
    
    df=getTeamsId(token,teamNumberList)
    print(df)
    #getTeamSkill(token,"131545")
    #driverSkill=getTeamSkillHighetScore(token,"131545","driver")
    #print(driverSkill)
    #getTeamsDetailInfo(token,df)
    # getTeamAwardJson(token,"130100")
    #getTeamAwardJson(token,"138967")
    # getTeamAward(token,"128470")
    # getTeamAward(token,"138967")
    #getTeamAward(token,"139812")
    #getTeamAwardJson(token,"139812")
    getDivisionTeamIds(token)
    # getTeamInfo(token,"130100")
   
main()