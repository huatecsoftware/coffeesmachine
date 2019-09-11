import os
import time
import json
import asyncio
from AI import *
import websockets
from utils import *
from HslCommunication import *

#siemens = SiemensS7Net(SiemensPLCS.S1200, "192.168.1.100")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

equipments = [
    {'desc': '1号机上电完成', 'status': 1},
    {'desc': '1号机关机', 'status': 0},
    {'desc': '1号机准备完成', 'status': 1},
    {'desc': '1号机工作中', 'status': 0},
    {'desc': '1号机工作完成', 'status': 0},
    {'desc': '1号机缺水', 'status': 0},
    {'desc': '1号机缺料', 'status': 0},
    {'desc': '1号机渣满', 'status': 0},
    {'desc': '1号机开门', 'status': 0},
    {'desc': '2号机上电完成', 'status': 1},
    {'desc': '2号机关机', 'status': 0},
    {'desc': '2号机准备完成', 'status': 1},
    {'desc': '2号机工作中', 'status': 0},
    {'desc': '2号机工作完成', 'status': 0},
    {'desc': '2号机缺水', 'status': 0},
    {'desc': '2号机缺料', 'status': 0},
    {'desc': '2号机渣满', 'status': 0},
    {'desc': '2号机开门', 'status': 0},
    {'desc': '制作完成', 'status': 0},
    {'desc': '机器人故障', 'status': 0},
    {'desc': '机器人电池报警', 'status': 0},
    {'desc': '机器人忙碌', 'status': 0},
    {'desc': '缺盖报警', 'status': 0},
    {'desc': '无盖报警', 'status': 0},
    {'desc': '标签异常', 'status': 0},
    {'desc': '通知贴签', 'status': 0},
    {'desc': '仓位1', 'status': 1},
    {'desc': '仓位2', 'status': 0},
    {'desc': '仓位3', 'status': 1},
    {'desc': '仓位4', 'status': 0},
    {'desc': '仓位5', 'status': 0},
    {'desc': '整站未完成', 'status': 0},
    {'desc': '1号机料台检测', 'status': 0},
    {'desc': '2号机料台检测', 'status': 0},
    {'desc': '无杯到1号机', 'status': 0},
    {'desc': '无杯到2号机', 'status': 0},
    {'desc': '缺杯报警', 'status': 0},
    {'desc': '杯无报警', 'status': 0},
    #{'desc': '进入光幕', 'status': guangMu},
    #{'desc': '准备入库', 'status': playing},
    {'desc': '1号机不能下单', 'status': 0},
    {'desc': '2号机不能下单', 'status': 0},
]


async def PLCServer(websocket, path):
    async for message in websocket:
        while True:
            await asyncio.sleep(0.5)
            """ totalPoint = siemens.Read('M124', 8)
            if totalPoint.IsSuccess:
                res1 = '{:08b}'.format(totalPoint.Content[0])
                res2 = '{:08b}'.format(totalPoint.Content[1])
                res3 = '{:08b}'.format(totalPoint.Content[2])
                res4 = '{:08b}'.format(totalPoint.Content[3])
                res5 = '{:08b}'.format(totalPoint.Content[4])
                res6 = '{:08b}'.format(totalPoint.Content[5])
                res7 = totalPoint.Content[6]
                res8 = totalPoint.Content[7]
                (cafe1Power, cafe1Off, cafe1Fin, cafe1Working, cafe1Worked, cafe1Water, cafe1Material, cafe1Rubbish, cafe1Door, cafe2Power, cafe2Off, cafe2Fin, cafe2Working, cafe2Worked, cafe2Water, cafe2Material, cafe2Rubbish, cafe2Door, cafeFin, robotErr, robotPower,
                    robotBusy, coverLess, coverNo, tagErr, tagNotice, repo1, repo2, repo3, repo4, repo5, platformIng, cafe1Plat, cafe2Plat, robotNoA, robotNoB, cupLess, cupNo, guangMu, playing, equipments, repos, aError, bError) = plcAnalysis(res1, res2, res3, res4, res5, res6) """
            await websocket.send(json.dumps({'repos': [0, 0, 0, 0, 0], 'aError': 0, 'bError': 0, 'coverLess': 0, 'cupLess': 0, 'cafe1Material': 0, 'cafe2Material': 0, 'robotErr': 1, 'cafe1Rubbish': 0, 'cafe2Rubbish': 0, 'cupNo': 0, 'coverNo': 0, 'tagErr': 0, 'guangMu': 0, 'equipment': equipments, 'cafeFin': 0, 'm130': 0, 'm131': 0, 'cafe1Fin': 0, 'cafe2Fin': 0}))

onlyOnce = True


async def AI(websocket, path):
    global onlyOnce
    async for message in websocket:
        while True:
            person = ''
            if os.path.exists(BASE_DIR + '/name.txt'):
                with open(BASE_DIR+'/name.txt', "r") as f:
                    person = f.readline()
                    f.close()
                    if person != 'unknown':
                        os.remove(BASE_DIR + "/name.txt")
                        knowList = list(
                            map(lambda obj: obj[:-4], os.listdir(BASE_DIR + "/wav/known")))
                        if person in knowList:
                            play(BASE_DIR + "/wav/known/%s.wav" % person)
                        else:
                            gr = GenderThread(
                                BASE_DIR + "/faces/%s.jpg" % person)
                            gr.start()
                            faceStatus = gr.getResult()
                            gender = '先生' if faceStatus['faces'][0]['attributes']['gender']['value'] == 'Male' else '女士'
                            TTS('%s%s您好，欢迎光临，要来杯咖啡么' %
                                (person[:-4], gender), BASE_DIR + "/wav/known/%s.wav" % person)
                    else:
                        if onlyOnce:
                            onlyOnce = False
                            play(BASE_DIR+'/wav/const/不认识.wav')
            else:
                onlyOnce = True
            await asyncio.sleep(1)
            await websocket.send(json.dumps({'person': person}))

start_server = websockets.serve(PLCServer, '127.0.0.1', 8765)
asyncio.get_event_loop().run_until_complete(start_server)
ai_server = websockets.serve(AI, '127.0.0.1', 8899)
asyncio.get_event_loop().run_until_complete(ai_server)
asyncio.get_event_loop().run_forever()
