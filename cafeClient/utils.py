import time
import datetime
import numpy as np


def orderToJson(orders):
    '''
        将订单对象转换为JSON格式
    '''
    models = []
    for order in orders:
        a_order = {}
        a_order['key'] = order.id
        a_order['Taste'] = order.Taste
        a_order['Stime'] = str(order.Stime)[:19]
        a_order['Etime'] = '' if order.Status == '进行中' else str(order.Etime)[
            :19]
        a_order['Uname'] = order.Uname
        a_order['Gender'] = order.Gender
        a_order['Phone'] = order.Phone
        a_order['Status'] = order.Status
        a_order['Number'] = order.Number
        a_order['Pos'] = order.Pos
        models.append(a_order)
    return models


def changeGender(gender):
    '''
        性别转换函数
    '''
    if gender == '先生' or gender == '男':
        return '男'
    else:
        return '女'


def drillChange(cafes):
    '''
        数据钻取功能中数据格式的转换
    '''

    def selectData(item):
        if item == 1:
            return janData
        elif item == 2:
            return febData
        elif item == 3:
            return marData
        elif item == 4:
            return aprData
        elif item == 5:
            return mayData
        elif item == 6:
            return junData
        elif item == 7:
            return julData
        elif item == 8:
            return augData
        elif item == 9:
            return sepData
        elif item == 10:
            return octData
        elif item == 11:
            return novData
        else:
            return decData

    def calcData(item):
        if item == 1:
            return janCount
        elif item == 2:
            return febCount
        elif item == 3:
            return marCount
        elif item == 4:
            return aprCount
        elif item == 5:
            return mayCount
        elif item == 6:
            return junCount
        elif item == 7:
            return julCount
        elif item == 8:
            return augCount
        elif item == 9:
            return sepCount
        elif item == 10:
            return octCount
        elif item == 11:
            return novCount
        else:
            return decCount

    def runNian(year):
        if int(year) % 4 == 0:
            return year+'-2-29 23:59:59'
        else:
            return year+'-2-28 23:59:59'

    janCount = 0
    febCount = 0
    marCount = 0
    aprCount = 0
    mayCount = 0
    junCount = 0
    julCount = 0
    augCount = 0
    sepCount = 0
    octCount = 0
    novCount = 0
    decCount = 0

    pie = []
    drillPie = []

    janData = []
    febData = []
    marData = []
    aprData = []
    mayData = []
    junData = []
    julData = []
    augData = []
    sepData = []
    octData = []
    novData = []
    decData = []

    try:
        year = time.strftime('%Y-%m-%d %H:%M:%S',
                             time.localtime(cafes[0]['name']/1000))[:4]
    except:
        year = datetime.datetime.now().strftime('%Y-%m-%d')[:4]

    yuanDan = int(time.mktime(time.strptime(
        year+'-1-1 00:00:00', "%Y-%m-%d %H:%M:%S"))*1000)
    january = int(time.mktime(time.strptime(
        year+'-1-31 23:59:59', "%Y-%m-%d %H:%M:%S"))*1000)
    february = int(time.mktime(time.strptime(
        runNian(year), "%Y-%m-%d %H:%M:%S"))*1000)
    march = int(time.mktime(time.strptime(
        year+'-3-31 23:59:59', "%Y-%m-%d %H:%M:%S"))*1000)
    april = int(time.mktime(time.strptime(
        year+'-4-30 23:59:59', "%Y-%m-%d %H:%M:%S"))*1000)
    may = int(time.mktime(time.strptime(
        year+'-5-31 23:59:59', "%Y-%m-%d %H:%M:%S"))*1000)
    june = int(time.mktime(time.strptime(
        year+'-6-30 23:59:59', "%Y-%m-%d %H:%M:%S"))*1000)
    july = int(time.mktime(time.strptime(
        year+'-7-31 23:59:59', "%Y-%m-%d %H:%M:%S"))*1000)
    august = int(time.mktime(time.strptime(
        year+'-8-31 23:59:59', "%Y-%m-%d %H:%M:%S"))*1000)
    september = int(time.mktime(time.strptime(
        year+'-9-30 23:59:59', "%Y-%m-%d %H:%M:%S"))*1000)
    october = int(time.mktime(time.strptime(
        year+'-10-31 23:59:59', "%Y-%m-%d %H:%M:%S"))*1000)
    november = int(time.mktime(time.strptime(
        year+'-11-30 23:59:59', "%Y-%m-%d %H:%M:%S"))*1000)
    december = int(time.mktime(time.strptime(
        year+'-12-31 23:59:59', "%Y-%m-%d %H:%M:%S"))*1000)

    for cafe in cafes:
        if cafe['name'] >= yuanDan and cafe['name'] <= january:
            janCount = janCount + cafe['y']
            janData.append([cafe['name'], cafe['y']])
        elif cafe['name'] > january and cafe['name'] <= february:
            febCount = febCount + cafe['y']
            febData.append([cafe['name'], cafe['y']])
        elif cafe['name'] > february and cafe['name'] <= march:
            marCount = marCount + cafe['y']
            marData.append([cafe['name'], cafe['y']])
        elif cafe['name'] > march and cafe['name'] <= april:
            aprCount = aprCount + cafe['y']
            aprData.append([cafe['name'], cafe['y']])
        elif cafe['name'] > april and cafe['name'] <= may:
            mayCount = mayCount + cafe['y']
            mayData.append([cafe['name'], cafe['y']])
        elif cafe['name'] > may and cafe['name'] <= june:
            junCount = junCount + cafe['y']
            junData.append([cafe['name'], cafe['y']])
        elif cafe['name'] > june and cafe['name'] <= july:
            julCount = julCount + cafe['y']
            julData.append([cafe['name'], cafe['y']])
        elif cafe['name'] > july and cafe['name'] <= august:
            augCount = augCount + cafe['y']
            augData.append([cafe['name'], cafe['y']])
        elif cafe['name'] > august and cafe['name'] <= september:
            sepCount = sepCount + cafe['y']
            sepData.append([cafe['name'], cafe['y']])
        elif cafe['name'] > september and cafe['name'] <= october:
            octCount = octCount + cafe['y']
            octData.append([cafe['name'], cafe['y']])
        elif cafe['name'] > october and cafe['name'] <= november:
            novCount = novCount + cafe['y']
            novData.append([cafe['name'], cafe['y']])
        elif cafe['name'] > november and cafe['name'] <= december:
            decCount = decCount + cafe['y']
            decData.append([cafe['name'], cafe['y']])
        else:
            pass

    for month in np.arange(1, 13):
        pie.append({'name': str(month), 'y': calcData(month),
                    'drilldown': str(month)})
        drillPie.append({'name': str(month), 'id': str(month), 'data': selectData(
            month), 'colorByPoint': True})

    return (pie, drillPie, year)


def plcAnalysis(*args):
    cafe1Power = int(args[0][-1])
    cafe1Off = int(args[0][-2])
    cafe1Fin = int(args[0][-3])
    cafe1Working = int(args[0][-4])
    cafe1Worked = int(args[0][-5])
    cafe1Water = int(args[0][-6])
    cafe1Material = int(args[0][-7])
    cafe1Rubbish = int(args[0][-8])

    cafe1Door = int(args[1][-1])
    cafe2Power = int(args[1][-2])
    cafe2Off = int(args[1][-4])
    cafe2Fin = int(args[1][-5])
    cafe2Working = int(args[1][-6])
    cafe2Worked = int(args[1][-7])
    cafe2Water = int(args[1][-8])

    cafe2Material = int(args[2][-1])
    cafe2Rubbish = int(args[2][-2])
    cafe2Door = int(args[2][-3])
    cafeFin = int(args[2][-4])
    robotErr = int(args[2][-5])
    robotPower = int(args[2][-6])
    robotBusy = int(args[2][-7])

    coverLess = int(args[3][-1])
    coverNo = int(args[3][-2])
    tagErr = int(args[3][-3])
    tagNotice = int(args[3][-4])
    repo1 = int(args[3][-5])
    repo2 = int(args[3][-6])
    repo3 = int(args[3][-7])
    repo4 = int(args[3][-8])

    repo5 = int(args[4][-1])
    platformIng = int(args[4][-2])
    cafe1Plat = int(args[4][-3])
    cafe2Plat = int(args[4][-4])
    robotNoA = int(args[4][-5])
    robotNoB = int(args[4][-6])
    cupLess = int(args[4][-7])
    cupNo = int(args[4][-8])

    guangMu = int(args[5][-1])
    playing = int(args[5][-2])
    aError = int(args[5][-3])
    bError = int(args[5][-4])

    equipments = [
        {'desc': '1号机上电完成', 'status': cafe1Power},
        {'desc': '1号机关机', 'status': cafe1Off},
        {'desc': '1号机准备完成', 'status': cafe1Fin},
        {'desc': '1号机工作中', 'status': cafe1Working},
        {'desc': '1号机工作完成', 'status': cafe1Worked},
        {'desc': '1号机缺水', 'status': cafe1Water},
        {'desc': '1号机缺料', 'status': cafe1Material},
        {'desc': '1号机渣满', 'status': cafe1Rubbish},
        {'desc': '1号机开门', 'status': cafe1Door},
        {'desc': '2号机上电完成', 'status': cafe2Power},
        {'desc': '2号机关机', 'status': cafe2Off},
        {'desc': '2号机准备完成', 'status': cafe2Fin},
        {'desc': '2号机工作中', 'status': cafe2Working},
        {'desc': '2号机工作完成', 'status': cafe2Worked},
        {'desc': '2号机缺水', 'status': cafe2Water},
        {'desc': '2号机缺料', 'status': cafe2Material},
        {'desc': '2号机渣满', 'status': cafe2Rubbish},
        {'desc': '2号机开门', 'status': cafe2Door},
        {'desc': '制作完成', 'status': cafeFin},
        {'desc': '机器人故障', 'status': robotErr},
        {'desc': '机器人电池报警', 'status': robotPower},
        {'desc': '机器人忙碌', 'status': robotBusy},
        {'desc': '缺盖报警', 'status': coverLess},
        {'desc': '无盖报警', 'status': coverNo},
        {'desc': '标签异常', 'status': tagErr},
        {'desc': '通知贴签', 'status': tagNotice},
        {'desc': '仓位1', 'status': repo1},
        {'desc': '仓位2', 'status': repo2},
        {'desc': '仓位3', 'status': repo3},
        {'desc': '仓位4', 'status': repo4},
        {'desc': '仓位5', 'status': repo5},
        {'desc': '整站未完成', 'status': platformIng},
        {'desc': '1号机料台检测', 'status': cafe1Plat},
        {'desc': '2号机料台检测', 'status': cafe2Plat},
        {'desc': '无杯到1号机', 'status': robotNoA},
        {'desc': '无杯到2号机', 'status': robotNoB},
        {'desc': '缺杯报警', 'status': cupLess},
        {'desc': '杯无报警', 'status': cupNo},
        # {'desc': '进入光幕', 'status': guangMu},
        # {'desc': '准备入库', 'status': playing},
        {'desc': '1号机不能下单', 'status': aError},
        {'desc': '2号机不能下单', 'status': bError},
    ]

    repos = [repo1, repo2, repo3, repo4, repo5]

    return (cafe1Power, cafe1Off, cafe1Fin, cafe1Working, cafe1Worked, cafe1Water, cafe1Material, cafe1Rubbish, cafe1Door, cafe2Power, cafe2Off, cafe2Fin, cafe2Working, cafe2Worked, cafe2Water, cafe2Material, cafe2Rubbish, cafe2Door, cafeFin, robotErr, robotPower, robotBusy, coverLess, coverNo, tagErr, tagNotice, repo1, repo2, repo3, repo4, repo5, platformIng, cafe1Plat, cafe2Plat, robotNoA, robotNoB, cupLess, cupNo, guangMu, playing, equipments, repos, aError, bError)


def checkSigWrite(siemens, flag):
    if flag:
        while True:
            siemens.WriteBool('M30.3', 1)
            m3031 = siemens.ReadBool('M30.3')
            if m3031.IsSuccess:
                if m3031.Content:
                    break
                else:
                    continue
            else:
                continue
    else:
        while True:
            siemens.WriteBool('M30.3', 0)
            m303 = siemens.ReadBool('M30.3')
            if m303.IsSuccess:
                if m303.Content == False:
                    break
                else:
                    continue
            else:
                continue


def tasteWrite(siemens, *args):
    if args[0]:
        if args[1] == 1:
            while True:
                siemens.WriteBool('M30.1', 1)
                m301 = siemens.ReadBool('M30.1')
                if m301.IsSuccess:
                    if m301.Content:
                        break
                    else:
                        continue
                else:
                    continue
        else:
            while True:
                siemens.WriteBool('M30.2', 1)
                m302 = siemens.ReadBool('M30.2')
                if m302.IsSuccess:
                    if m302.Content:
                        break
                    else:
                        continue
                else:
                    continue
    else:
        while True:
            siemens.WriteBool('M30.1', 0)
            m301 = siemens.ReadBool('M30.1')
            if m301.IsSuccess:
                if m301.Content == False:
                    break
                else:
                    continue
            else:
                continue
        while True:
            siemens.WriteBool('M30.2', 0)
            m302 = siemens.ReadBool('M30.2')
            if m302.IsSuccess:
                if m302.Content == False:
                    break
                else:
                    continue
            else:
                continue
