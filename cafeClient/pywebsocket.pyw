import os
import sys
import time
import json
import django
import random
import asyncio
import websockets
from utils import *
from django.db.models import Q
from HslCommunication import *


#siemens = SiemensS7Net(SiemensPLCS.S1200, "192.168.1.100")

BASE_DIR = BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))


sys.path.append(BASE_DIR)
os.environ['DJANGO_SETTINGS_MODULE'] = 'cafeServer.settings'
django.setup()

equipments = [
    {'title': '1号机状态', 'data': [
        {'desc': '1号机上电完成', 'status': random.randint(0, 1)},
        {'desc': '1号机关机', 'status': random.randint(0, 1)},
        {'desc': '1号机准备完成', 'status': random.randint(0, 1)},
        {'desc': '1号机工作中', 'status': random.randint(0, 1)},
        {'desc': '1号机工作完成', 'status': random.randint(0, 1)},
        {'desc': '1号机缺水', 'status': random.randint(0, 1)},
        {'desc': '1号机缺料', 'status': random.randint(0, 1)},
        {'desc': '1号机渣满', 'status': random.randint(0, 1)},
        {'desc': '1号机开门', 'status': random.randint(0, 1)},
        {'desc': '无杯到1号机', 'status': random.randint(0, 1)},
        {'desc': '1号机料台检测', 'status': random.randint(0, 1)},
        {'desc': '1号机不能下单', 'status': random.randint(0, 1)},
    ]},
    {'title': '2号机状态', 'data': [
        {'desc': '2号机上电完成', 'status': random.randint(0, 1)},
        {'desc': '2号机关机', 'status': random.randint(0, 1)},
        {'desc': '2号机准备完成', 'status': random.randint(0, 1)},
        {'desc': '2号机工作中', 'status': random.randint(0, 1)},
        {'desc': '2号机工作完成', 'status': random.randint(0, 1)},
        {'desc': '2号机缺水', 'status': random.randint(0, 1)},
        {'desc': '2号机缺料', 'status': random.randint(0, 1)},
        {'desc': '2号机渣满', 'status': random.randint(0, 1)},
        {'desc': '2号机开门', 'status': random.randint(0, 1)},
        {'desc': '无杯到2号机', 'status': random.randint(0, 1)},
        {'desc': '2号机料台检测', 'status': random.randint(0, 1)},
        {'desc': '2号机不能下单', 'status': random.randint(0, 1)}
    ]},
    {'title': '机器人状态', 'data': [
        {'desc': '机器人故障', 'status': random.randint(0, 1)},
        {'desc': '机器人电池报警', 'status': random.randint(0, 1)},
        {'desc': '机器人忙碌', 'status': random.randint(0, 1)},
        {'desc': '仓位1', 'status': random.randint(0, 1)},
        {'desc': '仓位2', 'status': random.randint(0, 1)},
        {'desc': '仓位3', 'status': random.randint(0, 1)},
        {'desc': '仓位4', 'status': random.randint(0, 1)},
        {'desc': '仓位5', 'status': random.randint(0, 1)},
    ]},
    {'title': '其他状态', 'data': [
        {'desc': '制作完成', 'status': random.randint(0, 1)},
        {'desc': '缺盖报警', 'status': random.randint(0, 1)},
        {'desc': '无盖报警', 'status': random.randint(0, 1)},
        {'desc': '标签异常', 'status': random.randint(0, 1)},
        {'desc': '通知贴签', 'status': random.randint(0, 1)},
        {'desc': '整站未完成', 'status': random.randint(0, 1)},
        {'desc': '缺杯报警', 'status': random.randint(0, 1)},
        {'desc': '杯无报警', 'status': random.randint(0, 1)},
    ]},
]

start, preRes7 = 1, 0


async def PLCServer(websocket, path):
    from cafeClient.models import User, modOrder
    global start, preRes7
    async for message in websocket:
        while True:
            await asyncio.sleep(1)
            ing = modOrder.objects.filter(
                Q(Status='进行中', Stime__gte=datetime.datetime.now().date())).order_by('Stime')
            finList = orderToJson(modOrder.objects.filter(
                Q(Status='待取走', Stime__gte=datetime.datetime.now().date())).order_by('Stime'))
            ingList = orderToJson(ing)
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

            if len(ing) != 0 and start == 1:
                order = modOrder.objects.get(id=ing[0].id)
                with open(BASE_DIR+'\order.txt', 'w') as file:
                    file.write('**********订单信息***********\n')
                    file.write('口味:'+order.Taste+'\n')
                    file.write('单号:'+order.Number+'\n')
                    file.write('手机:'+order.Phone+'\n')
                    file.write('时间:'+str(datetime.datetime.now())[:19]+'\n')
                    file.write('*****************************')
                if ing[0].Taste == '清咖啡':
                    start = 0
                    print('制作清咖啡')
                    """ checkSigWrite(siemens, True)
                    tasteWrite(siemens, True, 1) """
                if ing[0].Taste == '浓咖啡':
                    start = 0
                    print('制作浓咖啡')
                    """ checkSigWrite(siemens, True)
                    tasteWrite(siemens, True, 2) """
            # if len(ing) == 0 or cafeFin == 1:
            if len(ing) == 0:
                """ checkSigWrite(siemens, False)
                tasteWrite(siemens, False) """
                start = 1

            """ if res7 != 0 and preRes7 != res7:
                try:
                    preRes7 = res7
                    order = modOrder.objects.get(id=ing[0].id)
                    order.Etime = datetime.datetime.now()
                    order.Status = '待取走'
                    order.Pos = res7
                    order.save()
                except:
                    pass

            if res8 != 0:
                try:
                    order = modOrder.objects.get(Pos=res8)
                    order.Etime = datetime.datetime.now()
                    order.Status = '成功'
                    order.Pos = -1
                    order.save()
                except:
                    pass """

            await websocket.send(json.dumps({'repos': [0, 0, 0, 0, 0], 'aError': 0, 'bError': 0, 'coverLess': 0, 'cupLess': 0, 'cafe1Material': 0, 'cafe2Material': 0, 'robotErr': 0, 'cafe1Rubbish': 0, 'cafe2Rubbish': 0, 'cupNo': 0, 'coverNo': 0, 'tagErr': 0, 'guangMu': 0, 'equipment': equipments, 'cafeFin': 0, 'm130': 0, 'm131': 0, 'ing': ingList, 'fin': finList, 'cafe1Fin': 0, 'cafe2Fin': 0}))


start_server = websockets.serve(PLCServer, '127.0.0.1', 8765)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
