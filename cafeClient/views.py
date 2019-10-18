# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import json
import time
import random
import base64
import datetime
import numpy as np
from cafeClient.AI import *
from cafeClient.utils import *
from django.db.models import Q
from cafeClient.models import *
from multiprocessing import Process
from django.shortcuts import render
from django.http import JsonResponse
from cafeClient.HslCommunication import *
from django.views.decorators.csrf import csrf_exempt
# Create your views here.

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# siemens = SiemensS7Net(SiemensPLCS.S1200, '192.168.1.100')


@csrf_exempt
def queryAllOrder(request):
    '''
        查询所有订单，用来显示报表界面的数据和制图页面的数据
        splineSeries：曲线图数据格式
        pieSeries：饼图数据格式
        columnSeries：柱状图数据格式
    '''

    param = json.loads(request.body)

    orders = modOrder.objects.filter(Q(Uname__icontains=param['姓名'], Gender__icontains=param['性别'], Phone__icontains=param['电话'], Taste__icontains=param['口味'],
                                       Stime__icontains=param['接单时间'], Etime__icontains=param['完成时间'], Number__icontains=param['订单号'], Status__icontains=param['订单状态']))

    orderList = orderToJson(orders)
    clears = list(modClear.objects.all().values_list(
        'time', flat=True).distinct())
    try:
        clear = str(clears[-1])
    except:
        clear = [str(datetime.datetime.now())[:-7]]
    return JsonResponse({'orders': orderList, 'clear': clear})


@csrf_exempt
def rangeClick(request):
    taste1, taste2 = [], []
    splineTaste1, splineTaste2, pie = [], [], []
    param = json.loads(request.body)
    start = datetime.datetime.strptime(
        param['start'], '%Y-%m-%d')+datetime.timedelta(hours=8)
    stop = datetime.datetime.strptime(
        param['stop'], '%Y-%m-%d')+datetime.timedelta(hours=23)

    dateList = list(set(list(map(lambda obj: str(obj)[:10],
                                 modOrder.objects.filter(Q(Etime__gte=start, Etime__lte=stop)).values_list('Stime', flat=True)))))
    if len(modOrder.objects.all()) == 0:
        date = str(datetime.datetime.now())[:7]+'-01 08:00:00'
        for i in np.arange(int(time.mktime(time.strptime(date, '%Y-%m-%d %H:%M:%S')))*1000, time.time()*1000, 24*60*60*1000):
            splineTaste1.append([i, random.randint(0, 50)])
            splineTaste2.append([i, random.randint(0, 50)])
        pie = [{'name': '浓咖啡', 'y': random.randint(0, 100), 'color': 'blue'}, {
            'name': '清咖啡', 'y': random.randint(0, 100), 'color': 'red'}]
    else:
        if len(dateList) != 0:
            for date in dateList:
                timestamp = int(time.mktime(
                    time.strptime(date, '%Y-%m-%d'))*1000)
                timeDate = datetime.datetime.strptime(date, '%Y-%m-%d')
                t1 = len(modOrder.objects.filter(
                    Q(Taste='浓咖啡', Etime__gte=timeDate, Etime__lte=timeDate+datetime.timedelta(hours=24))))
                t2 = len(modOrder.objects.filter(
                    Q(Taste='清咖啡', Etime__gte=timeDate, Etime__lte=timeDate+datetime.timedelta(hours=24))))
                splineTaste1.append([timestamp, t1])
                splineTaste2.append([timestamp, t2])
                taste1 = len(modOrder.objects.filter(
                    Q(Taste='浓咖啡', Etime__gte=timeDate, Etime__lte=timeDate+datetime.timedelta(hours=24))))
                taste2 = len(modOrder.objects.filter(
                    Q(Taste='清咖啡', Etime__gte=timeDate, Etime__lte=timeDate+datetime.timedelta(hours=24))))
                pie = [{'name': '浓咖啡', 'y': taste1, 'color': 'blue'},
                       {'name': '清咖啡', 'y': taste2, 'color': 'red'}]
        else:
            pie, splineTaste1, splineTaste2 = [], [], []

    series = [{'type': 'column', 'name': '浓咖啡', 'color': 'blue', 'data': splineTaste1}, {
        'type': 'column', 'color': 'red', 'name': '清咖啡', 'data': splineTaste2}, {
        'type': 'pie', 'data': pie, 'center': [150, 85], 'size':200}]
    return JsonResponse({'spline': series})


@csrf_exempt
def addOrder(request):
    '''
        添加新订单，订单默认状态均为进行中
    '''
    params = json.loads(request.body)
    order = modOrder()
    order.Status = '进行中'
    order.Uname = params['name']
    order.Taste = params['taste']
    order.Phone = params['phone']
    order.Number = str(time.time())[:10]
    order.Gender = changeGender(params['gender'])
    order.Stime = datetime.datetime.now()
    order.Etime = datetime.datetime.now()
    order.save()
    return JsonResponse({'ok': 'ok'})


@csrf_exempt
def failOrder(request):
    try:
        key = json.loads(request.body)['key']
        order = modOrder.objects.get(id=key)
        order.Status = '失败'
        order.Etime = datetime.datetime.now()
        order.save()
    except:
        pass
    return JsonResponse({'ok': 'ok'})


proid = ''


@csrf_exempt
def intelligenceModel(request):
    """
        智能模式开启语音和视频进程
    """
    global proid
    switch = json.loads(request.body)['checked']
    if switch:
        recordP = Process(target=recordProcess)
        recordP.start()
        proid = str(recordP.pid)
    else:
        cmd = 'taskkill /pid ' + str(proid) + ' /f'
        try:
            os.system(cmd)
        except:
            pass
        if os.path.exists(BASE_DIR+'/startRecord.txt'):
            os.remove(BASE_DIR+'/startRecord.txt')
        if os.path.exists(BASE_DIR+'/name.txt'):
            os.remove(BASE_DIR+'/name.txt')
        if os.path.exists(BASE_DIR+'/user.txt'):
            os.remove(BASE_DIR + "/user.txt")
        if os.path.exists(BASE_DIR+'/unknown.txt'):
            os.remove(BASE_DIR + "/unknown.txt")
    return JsonResponse({'ok': 'ok'})


@csrf_exempt
def AIState(request):
    person = ''
    if os.path.exists(BASE_DIR + '/user.txt') and os.path.exists(BASE_DIR+'/unknown.txt'):
        with open(BASE_DIR+'/user.txt', "r") as f:
            person = f.readline()
    return JsonResponse({'person': person, 'record': os.path.exists(BASE_DIR+'/startRecord.txt')})


@csrf_exempt
def deleteTempFile(request):
    """
        放弃注册删除图片
    """
    global newPic
    try:
        os.remove(BASE_DIR+'/faces/%s' % newPic)
    except:
        pass
    if os.path.exists(BASE_DIR+'/startRecord.txt'):
        os.remove(BASE_DIR+'/startRecord.txt')
    if os.path.exists(BASE_DIR+'/name.txt'):
        os.remove(BASE_DIR+'/name.txt')
    if os.path.exists(BASE_DIR+'/user.txt'):
        os.remove(BASE_DIR + "/user.txt")
    if os.path.exists(BASE_DIR+'/unknown.txt'):
        os.remove(BASE_DIR + "/unknown.txt")
    return JsonResponse({'res': 'ok'})


@csrf_exempt
def addUser(request):
    """ 
        用户注册函数
    """
    param = json.loads(request.body)
    res = 'ok'
    userNums = User.objects.filter(Q(phone=param['userParam']['phone']))
    # if len(userNums) == 0:
    user = User()
    user.name = param['userParam']['name']
    user.gender = param['userParam']['gender']
    user.phone = param['userParam']['phone']
    user.save()
    with open(BASE_DIR + "/user.txt", "w") as f:
        f.write(param['userParam']['name']+param['userParam']['phone'][-4:])
        f.close()
    TTS('%s%s您好,欢迎光临，请问您是要喝咖啡吗?' %
        (param['userParam']['name'], param['userParam']['gender']), BASE_DIR + "/wav/known/%s%s.wav" % (param['userParam']['name'], param['userParam']['phone'][-4:]))
    """     res = 'ok'
    else:
        res = 'err' """
    os.remove(BASE_DIR+'/unknown.txt')
    with open(BASE_DIR + "/register.txt", "w") as f:
        f.write('register')
    return JsonResponse({'ok': res})


newPic = ''


@csrf_exempt
def photograph(request):
    """ 
        页面点击拍照按钮
    """
    global newPic
    param = json.loads(request.body)
    newPic = '%s%s.png' % (param["name"], param["phone"][-4:])
    imgdata = base64.b64decode(param['data'][22:])
    file = open(BASE_DIR+'/faces/'+newPic, 'wb')
    file.write(imgdata)
    file.close()
    return JsonResponse({'ok': 'ok'})


@csrf_exempt
def calcFaceEncoding(request):
    condings = loadKnowFace()
    return JsonResponse({'condings': condings})


@csrf_exempt
def savePerson(request):
    param = json.loads(request.body)
    person = param['person']
    with open(BASE_DIR + "/name.txt", "w") as f:
        f.write(person)
    with open(BASE_DIR + "/user.txt", "w") as f:
        f.write(person)
    return JsonResponse({'res': 'ok'})


@csrf_exempt
def searchOrder(request):
    '''
        订单模糊查询功能
    '''
    params = json.loads(request.body)
    orders = []
    if params['key'] == '姓名':
        orders = modOrder.objects.filter(Q(Uname__icontains=params['val']))
    elif params['key'] == '性别':
        orders = modOrder.objects.filter(Q(Gender__icontains=params['val']))
    elif params['key'] == '电话':
        orders = modOrder.objects.filter(Q(Phone__icontains=params['val']))
    elif params['key'] == '口味':
        orders = modOrder.objects.filter(Q(Taste__icontains=params['val']))
    elif params['key'] == '接单时间':
        orders = modOrder.objects.filter(Q(Stime__icontains=params['val']))
    elif params['key'] == '完成时间':
        orders = modOrder.objects.filter(Q(Etime__icontains=params['val']))
    elif params['key'] == '订单号':
        orders = modOrder.objects.filter(Q(Number__icontains=params['val']))
    elif params['key'] == '订单状态':
        orders = modOrder.objects.filter(Q(Status__icontains=params['val']))
    else:
        pass
    orderList = orderToJson(orders)
    return JsonResponse({'data': orderList})


@csrf_exempt
def logClear(request):
    '''
        记录清理时间
    '''
    clear = modClear()
    clear.time = datetime.datetime.now()
    clear.save()
    clears = list(modClear.objects.all().values_list(
        'time', flat=True).distinct())
    return JsonResponse({'clear': clears[-1]})


start, preM130, preRepos = 1, 0, [0, 0, 0, 0, 0]


@csrf_exempt
def loopDB(request):
    global start, preM130, preRepos
    param = json.loads(request.body)
    ing = modOrder.objects.filter(
        Q(Status='进行中', Stime__gte=datetime.datetime.now().date())).order_by('Stime')
    finList = orderToJson(modOrder.objects.filter(
        Q(Status='待取走', Stime__gte=datetime.datetime.now().date())).order_by('Stime'))
    ingList = orderToJson(ing)
    try:
        for i in range(5):
            errList = modOrder.objects.filter(Q(Pos=(i+1))).order_by('Etime')
            if len(errList) >= 2:
                for err in errList[1:]:
                    err.Pos = 0
                    err.Status = '进行中'
                    err.save()
            if preRepos[i] == 1 and param['rcv']['repos'][i] == 0:
                try:
                    order = modOrder.objects.get(Pos=int(i+1))
                    order.Etime = datetime.datetime.now()
                    order.Status = '成功'
                    order.Pos = -1
                    order.save()
                except:
                    pass
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
                """ checkSigWrite(siemens, True)
                tasteWrite(siemens, True, 1) """
            if ing[0].Taste == '浓咖啡':
                start = 0
                """ checkSigWrite(siemens, True)
                tasteWrite(siemens, True, 2) """
        if len(ing) == 0 or int(param['rcv']['cafeFin']) == 1:
            """ checkSigWrite(siemens, False)
            tasteWrite(siemens, False) """
            start = 1

        if param['rcv']['m130'] != 0 and preM130 != param['rcv']['m130']:
            try:
                preM130 = int(param['rcv']['m130'])
                preRepos = param['rcv']['repos']
                order = modOrder.objects.get(id=ing[0].id)
                order.Etime = datetime.datetime.now()
                order.Status = '待取走'
                order.Pos = int(param['rcv']['m130'])
                order.save()
            except:
                pass

        if param['rcv']['m131'] != 0:
            try:
                order = modOrder.objects.get(Pos=int(param['rcv']['m131']))
                order.Etime = datetime.datetime.now()
                order.Status = '成功'
                order.Pos = -1
                order.save()
            except:
                pass

    except:
        pass
    return JsonResponse({'ing': ingList, 'fin': finList})


@csrf_exempt
def PLCON(request):
    param = json.loads(request.body)
    # siemens.WriteBool(param['addr'], 1)
    return JsonResponse({'ok': 'ok'})


@csrf_exempt
def PLCOFF(request):
    param = json.loads(request.body)
    # siemens.WriteBool(param['addr'], 0)
    return JsonResponse({'ok': 'ok'})


rcv = {}


@csrf_exempt
def logRcv(request):
    global rcv
    rcv = json.loads(request.body)['rcv']
    return JsonResponse({'ok': 'ok'})


@csrf_exempt
def addCheck(request):
    ing = modOrder.objects.filter(
        Q(Status='进行中', Stime__gte=datetime.datetime.now().date())).order_by('Stime')
    succ = orderToJson(modOrder.objects.filter(
        Q(Status='成功', Stime__gte=datetime.datetime.now().date())).order_by('Etime'))
    ingList = orderToJson(ing)
    lessOrder = []
    if len(ingList) == 0:
        lessOrder = succ[:3]
    else:
        lessOrder = ingList[-3:]
    return JsonResponse({'rcv': rcv, 'less': lessOrder})
