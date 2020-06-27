#!/usr/bin/python3 

"""
@author FANG
@date 2020.6.25
"""
from urllib import request, parse, error
import ssl, json, os, re

def debug(*args):
    #print(*args)
    pass

"""
Communicate with riot backend server
"""
def postReq(url, what):
    debug("[*]", 'POST', url)
    try:
        return request.urlopen(
            request.Request(url, headers={
            "Accept": "*/*",
            "Content-Type": "application/json"
            }, data=what.encode("utf-8"))
        ).read().decode("utf-8")
    except error.URLError as e:
        debug("[-]", e)
    except error.HTTPError as e:
        debug("[-]", e)

def getReg(url):
    debug("[*]", 'GET', url)
    try:
        return request.urlopen(
            request.Request(url, headers={
            "Accept": "*/*",
            "Content-Type": "application/json"
            })
        ).read().decode("utf-8")
    except error.URLError as e:
        debug("[-]", e)
    except error.HTTPError as e:
        debug("[-]", e)

class LobbyManager:
    def __init__(self, gamePath):
        self.info = self.loadLockFile(gamePath)
        self.url = "https://127.0.0.1:" + self.info["port"]
        self.url_lobby = self.url + "/lol-lobby/v2/lobby"
        self.url_summoner = self.url + "/lol-summoner/v1/current-summoner"

        # Create an OpenerDirector with support for Basic HTTP Authentication
        auth_handler = request.HTTPBasicAuthHandler()
        auth_handler.add_password(realm="RiotRemoting", # realm is sent by server
                                  uri=self.url,
                                  user='riot',
                                  passwd=self.info["token"])
        # install it globally so it can be used with urlopen.
        request.install_opener(request.build_opener(auth_handler))

        # cancel ssl check
        #context = ssl._create_unverified_context()
        ssl._create_default_https_context = ssl._create_unverified_context

    def getSummonerInfo(self):
        # Get Summoner information
        reply = getReg(self.url_summoner)
        if reply:
            debug("[+]", "(getSummonerInfo)", json.dumps(json.loads(reply), indent=4))
        else:
            debug("[-]", "(getSummonerInfo)", "An error occurred.")
        return reply

    def __createLobby(self, jsn):
        return postReq(self.url_lobby, jsn);

    def createLobbyByQueueId(self, queueId):
        debug("[*]", "queueId=", queueId)
        reply = self.__createLobby(json.dumps({
            "queueId": queueId
        }));
        if reply:
            debug("[+]", "(createLobbyByQueueId)", json.dumps(json.loads(reply), indent=4))
        else:
            debug("[-]", "(createLobbyByQueueId)", "An error occurred.")
        return reply

    def create5V5Practice(self, lobbyName="test_lobby", teamSize=5):
        reply = self.__createLobby(json.dumps({
            "customGameLobby": {
                "configuration": {
                    "gameMode": "PRACTICETOOL",
                    "gameMutator": "",
                    "gameServerRegion": "",
                    "mapId": 11,
                    "mutators": {
                        "id": 1
                    },
                    "spectatorPolicy": "AllAllowed",
                    "teamSize": teamSize
                },
                "lobbyName": lobbyName,
                "lobbyPassword": None
            },
            "isCustom": True
        }))
        if reply:
            debug("[+]", "(create5V5Practice)", json.dumps(json.loads(reply), indent=4))
        else:
            debug("[-]", "(create5V5Practice)", "An error occurred.")
        return reply

    def loadLockFile(self, gamePath):
        lockFilePath = os.path.join(gamePath, "lockfile")
        if not os.path.exists(lockFilePath):
            raise Exception("Game is not running!")
        with open(lockFilePath, "r", encoding="utf-8") as lockFile:
            s = lockFile.read()
            m = re.match(r'(.*):(.*):(.*):(.*):(.*)', s)
            if m:
                info = {
                    "name": m[1],
                    "uid": m[2],
                    "port": m[3],
                    "token": m[4],
                    "protocol": m[5]
                }
                debug("[+]", "(loadLockFile)", json.dumps(info, indent=4))
                return info
        raise Exception("Unable to read lockfile!")

    def findGamePathByProcess(self):
        pass # not implemented yet

"""
http://static.developer.riotgames.com/docs/lol
http://static.developer.riotgames.com/docs/lol/queues.json
"""
normal_modes = {
    0: "5V5 训练模式", # 这是自定义的编号
    420: "排位赛 单排/双排",
    430: "匹配模式 自选",
    440: "排位赛 灵活排位",
    450: "极地大乱斗 嚎哭深渊",
    830: "人机 召唤师峡谷 入门",
    840: "人机 召唤师峡谷 新手",
    850: "人机 召唤师峡谷 一般",
    1090: "云顶之弈 匹配",
    1100: "云顶之弈 排位",
    2000: "新手教程 一",
    2010: "新手教程 二",
    2020: "新手教程 三"
}
# 目前这些模式都无法使用，使用 * 标注的是隐藏模式
special_modes = {
    460: "扭曲丛林 自选",
    470: "排位赛 扭曲丛林 灵活排位",
    480: "?1", #*
    490: "?2", #*
    500: "?3", #*
    510: "?4", #*
    600: "红月决",
    610: "暗星",
    620: "?5", #*
    630: "?6", #*
    700: "冠军杯赛 征召",
    800: "人机 扭曲丛林 一般",
    810: "人机 扭曲丛林 入门",
    820: "人机 扭曲丛林 新手",
    860: "人机 嚎哭深渊 极地大乱斗", #*
    870: "?7", #*
    880: "?8", #*
    890: "?9", #*
    900: "无限火力 召唤师峡谷",
    910: "飞升争夺战",
    920: "魄罗大乱斗",
    930: "极地大乱斗 召唤师峡谷", #*
    940: "水晶围城 召唤师峡谷",
    950: "末日审判 投票 召唤师峡谷",
    960: "末日审判 标准 召唤师峡谷",
    970: "?10", #*
    980: "星际守护者入侵 普通",
    990: "星际守护者入侵 狂袭",
    1000: "超频行动",
    1010: "冰雪无限火力",
    1020: "克隆大乱斗",
    1030: "奥德赛:淬炼 入门|一星",
    1040: "奥德赛:淬炼 学员|二星",
    1050: "奥德赛:淬炼 组员|三星",
    1060: "奥德赛:淬炼 船长|四星",
    1070: "奥德赛:淬炼 狂袭|五星",
    1080: "?11", #*
    1110: "云顶之弈 教学",
    1200: "极限闪击",
    1210: "?12" #*
}

def main():
    print("＋＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＋")
    print("｜　　　英雄联盟　　开房系统　　　｜")
    print("｜　　　－－－－－－－－－－　　　｜")
    print("｜　　　　　版本：v1.0　　　　　　｜")
    print("｜　　　　　作者：FANG　　　　　　｜")
    print("｜　　　　　日期：2020.6　　　　　｜")
    print("｜　　　　　　　　　　　　　　　　｜")
    print("｜　　　　　　使用须知　　　　　　｜")
    print("｜　　　－－－－－－－－－－　　　｜")
    print("｜先启动英雄联盟客户端，再运行本　｜")
    print("｜程序。注意修改脚本中的游戏路径，｜")
    print("｜　　　　否则无法正常使用！　　　｜")
    print("＋＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＋")
    print()
    # 注意修改这一行游戏路径
    lol = LobbyManager("Q:\\英雄联盟\\LeagueClient")

    print("请选择一个游戏模式（输入 q 退出）：\n")
    print("============ 常规模式 ============")
    for k in normal_modes:
        print(k, "\t\t", normal_modes[k])
    print("\n==== 特殊模式（可能无法创建） =====")
    for k in special_modes:
        print(k, "\t\t", special_modes[k])

    lol.getSummonerInfo()
    while True:
        print('> ', end='')
        mode = input()
        if mode == 'q':
            break
        else:
            mode = int(mode)
            if mode == 0:
                lol.create5V5Practice()
            else:
                lol.createLobbyByQueueId(mode)

if __name__ == '__main__':
    main()
