import re
import os
import sys
import cv2
import time
import json
import wave
import socket
import struct
import django
import random
import datetime
import requests
import threading
import http.client
import numpy as np
import urllib.parse
import urllib.request
import face_recognition
from django.db.models import Q
from multiprocessing import Process
from pyaudio import PyAudio, paInt16
from aliyunsdkcore.client import AcsClient
from PIL import Image, ImageDraw, ImageFont
from aliyunsdkcore.request import CommonRequest

sys.path.append('D://work/cafeBack')
os.environ['DJANGO_SETTINGS_MODULE'] = 'cafeServer.settings'
django.setup()

BASE_DIR = BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))

cafeType = ''  # 咖啡种类
onlyOne = True  # 确保临时文件生成一次
wakaran = False  # 听不懂
speaking = False  # 是否正在说话
wakaranTimes = 0  # 听不懂的次数
AIStatus = 'sleep'  # 默认睡眠状态
cameraOpen = False  # 是否经过身份识别
specialTime = False  # 特别耗时的
faceTime = time.time()  # 画面中出现人脸的时间
wakeTime = time.time()  # 默认的唤醒时间
wakeTime2 = time.time()  # 听不懂的唤醒时间
checkStartTime = time.time()  # 确认做咖啡的时间，默认当前系统时间
checkStartStatus = False  # 是否确认做咖啡，默认为False
voices = ['Xiaoyun', 'Xiaomeng', 'Ruoxi', 'Siqi', 'Sijia', 'Aiqi', 'Aijia', 'Ninger', 'Ruilin', 'Amei', 'Xiaoxue',
          'Siyue', 'Aixia', 'Aimei', 'Aiyu', 'Aiyue', 'Aijing', 'Xiaomei', 'Yina', 'Sijing', 'Sitong', 'Xiaobei', 'Aibao']


def getToken(key, secret):
    client = AcsClient(key, secret, 'cn-shanghai')
    request = CommonRequest()
    request.set_method('POST')
    request.set_domain('nls-meta.cn-shanghai.aliyuncs.com')
    request.set_version('2019-02-28')
    request.set_action_name('CreateToken')
    response = client.do_action_with_exception(request)
    return json.loads(response)['Token']['Id']


def sock_client_image(filepath):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('192.168.0.114', 9999))
    except socket.error as msg:
        print(msg)
        print(sys.exit(1))
    fhead = struct.pack(b'128sq', bytes(os.path.basename(
        filepath), encoding='utf-8'), os.stat(filepath).st_size)
    s.send(fhead)

    fp = open(filepath, 'rb')
    while True:
        data = fp.read(1024)
        if not data:
            break
        s.send(data)
    s.close()


def play(audio):
    """
    语音播放
    audio:要播放的文件地址
    """
    wf = wave.open(audio, 'rb')
    p = PyAudio()
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)
    data = wf.readframes(1024)
    while data != b'':
        stream.write(data)
        data = wf.readframes(1024)
    stream.stop_stream()
    stream.close()
    p.terminate()


def loadKnowFace():
    """
    计算已知人脸模型
    knownEncoding:返回人脸模型,key为姓名+手机后四位，value为128D特征值
    """
    knownEncoding = {}
    for face in os.listdir(BASE_DIR+'/faces'):
        faceEncode = face_recognition.face_encodings(
            face_recognition.load_image_file(BASE_DIR+'/faces/'+face))[0]
        knownEncoding[face[:-4]] = faceEncode.tolist()
    return knownEncoding


def cameraProcess():
    """
    人脸识别的进程函数
    """
    global onlyOne, faceTime
    face_locations = []
    face_encodings = []
    process_this_frame = True
    # 首次运行，加载已知人脸特征值
    knowFace = loadKnowFace()
    # 开启默认摄像头
    video_capture = cv2.VideoCapture(0)
    while True:
        # ret摄像头设否开启，False关闭 True开启
        # frame每帧视频数据，ndarray格式
        ret, frame = video_capture.read()
        if ret and os.path.exists(BASE_DIR+'/loadCamera.txt'):
            os.remove(BASE_DIR+'/loadCamera.txt')
        # 键盘点击监听
        key = cv2.waitKey(1)
        # 重置视频帧大小，提高处理效率？
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        # 视频去噪，此处貌似是图片灰化处理
        rgb_small_frame = small_frame[:, :, ::-1]
        # 前端点击拍照后根据person.txt文件更新视频帧，主要信息为姓名和手机号后四位
        # img为Image对象，因opencv不支持中文，此处需要转换处理
        if os.path.exists(BASE_DIR + "/person.txt"):
            with open(BASE_DIR + "/person.txt", "r") as f:
                pic = f.readline()
                f.close()
                os.remove(BASE_DIR + "/person.txt")
                img = Image.fromarray(
                    cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                img.save(BASE_DIR+'/faces/%s.png' % pic)
                #sock_client_image(BASE_DIR+'/faces/%s.png' % pic)
                #os.remove(BASE_DIR+'/faces/%s.png' % pic)
        # 逐帧处理
        if process_this_frame:
            # 检测当前帧中是否存在人脸
            face_locations = face_recognition.face_locations(
                rgb_small_frame)
            if len(face_locations) == 0 and time.time()-faceTime > 5:
                if os.path.exists(BASE_DIR+'/name.txt'):
                    os.remove(BASE_DIR+'/name.txt')
                if os.path.exists(BASE_DIR+'/cameraP.txt'):
                    os.remove(BASE_DIR+'/cameraP.txt')
                with open(BASE_DIR + "/toSleep.txt", "w") as f:
                    f.write('toSleep')
                break
            # 根据人脸数计算每张脸的特征值
            face_encodings = face_recognition.face_encodings(
                rgb_small_frame, face_locations)
            face_names = []
            # 循环每个人脸特征值和已知人脸特征值对比
            for face_encoding in face_encodings:
                matches = face_recognition.compare_faces(
                    list(knowFace.values()), face_encoding)
                name = 'unknown'
                # 计算俩个特征值之间的欧式距离
                face_distances = face_recognition.face_distance(
                    list(knowFace.values()), face_encoding)
                # 计算欧式距离中最小值的索引
                best_match_index = np.argmin(face_distances)
                # 如果找到匹配的人脸，找出这个人的姓名
                if matches[best_match_index]:
                    faceTime = time.time()
                    name = list(knowFace.keys())[
                        best_match_index]
                    if onlyOne:
                        onlyOne = False
                        with open(BASE_DIR+'/name.txt', 'w') as f:
                            f.write(name)
                            f.close()
                        with open(BASE_DIR + "/user.txt", "w") as f:
                            f.write(name)
                            f.close()
                    face_names.append(name[:-4])
                else:
                    faceTime = time.time()
                    if onlyOne:
                        onlyOne = False
                        with open(BASE_DIR+'/name.txt', 'w') as f:
                            f.write('unknown')
                            f.close()
                    face_names.append('unknown')
        process_this_frame = not process_this_frame
        cv2.imshow('FaceRecognition', frame)
        if key == ord('q'):
            if os.path.exists(BASE_DIR+'/name.txt'):
                os.remove(BASE_DIR+'/name.txt')
            if os.path.exists(BASE_DIR+'/cameraP.txt'):
                os.remove(BASE_DIR+'/cameraP.txt')
            break
    video_capture.release()
    cv2.destroyAllWindows()


def recordProcess():
    """
    录音进程
    """
    from cafeClient.models import User, modOrder
    global checkStartTime, AIStatus, wakeTime, cafeType, checkStartStatus, wakeTime2, wakaran, wakaranTimes, specialTime, speaking
    save_count = 0
    save_buffer = []
    # pyaudio对象，用来处理录音的音频流
    # 音频声道单声道，采样率16000，固定
    pa = PyAudio()
    stream = pa.open(format=paInt16, channels=1, rate=16000, input=True,
                     frames_per_buffer=1500)
    with open(BASE_DIR + "/startRecord.txt", "w") as f:
        f.write('startRecord')
    while True:
        if AIStatus == 'wake':
            if int(time.time()-checkStartTime) == 10 and checkStartStatus:
                play(BASE_DIR+'/wav/const/等待制作.wav')
                if os.path.exists(BASE_DIR + "/user.txt"):
                    with open(BASE_DIR + "/user.txt", "r") as f:
                        userInfo = f.readline()
                        f.close()
                        os.remove(BASE_DIR + "/user.txt")
                        name = userInfo[:-4]
                        phone = userInfo[-4:]
                        user = User.objects.get(
                            Q(phone__icontains=phone, name=name))
                        order = modOrder()
                        order.Status = '进行中'
                        order.Uname = name
                        order.Taste = cafeType
                        order.Phone = user.phone
                        order.Number = str(time.time())[:10]
                        order.Gender = user.gender
                        order.Stime = datetime.datetime.now()
                        order.Etime = datetime.datetime.now()
                        order.save()
                checkStartStatus = False
                AIStatus = 'sleep'
            watiTime = 60 if specialTime else 15
            if int(time.time()-wakeTime) == watiTime and not os.path.exists(BASE_DIR+'/cameraP.txt'):
                specialTime = False
                play(BASE_DIR+'/wav/const/超时.wav')
                AIStatus = 'sleep'
            if int(time.time()-wakeTime2) == 1 and wakaran:
                play(BASE_DIR+'/wav/const/听不懂.wav')
                wakaran = False
            if wakaranTimes == 3:
                play(BASE_DIR+'/wav/const/主动再见.wav')
                wakaranTimes = 0
                AIStatus = 'sleep'
        if os.path.exists(BASE_DIR + "/toSleep.txt"):
            os.remove(BASE_DIR + "/toSleep.txt")
            AIStatus = 'sleep'
        # 每次读取1500字节缓冲
        string_audio_data = stream.read(1500)
        # 将缓冲数据转换为ndarray
        audio_data = np.frombuffer(string_audio_data, dtype=np.short)
        # 计算ndarray中数值大于1500的有多少个
        large_sample_count = np.sum(audio_data > 1000)
        # 大于1500的有20个以上时，保存这段录音，时长5秒
        if large_sample_count > 20:
            save_count = 5
        else:
            save_count -= 1

        if save_count < 0:
            save_count = 0

        if save_count > 0:
            save_buffer.append(string_audio_data)
        else:
            # 将保存的缓冲数据拼接成一句完整的话，调用语音识别接口
            if len(save_buffer) > 0:
                content = b''
                for buf in save_buffer:
                    content = content + buf
                if not speaking and len(content) <= 72000 and not os.path.exists(BASE_DIR+'/cameraP.txt') and not os.path.exists(BASE_DIR+'/play.txt'):
                    STT(content)
                save_buffer = []


def TTS(text, filename):
    """
    阿里语音合成接口
    text:要合成的文字
    filename:合成文件的路径
    """
    global speaking
    textUrlencode = text
    textUrlencode = urllib.parse.quote_plus(textUrlencode)
    textUrlencode = textUrlencode.replace("+", "%20")
    textUrlencode = textUrlencode.replace("*", "%2A")
    textUrlencode = textUrlencode.replace("%7E", "~")
    host = 'nls-gateway.cn-shanghai.aliyuncs.com'
    conn = http.client.HTTPSConnection(host)
    conn.request(method='GET', url='https://nls-gateway.cn-shanghai.aliyuncs.com/stream/v1/tts?appkey=F5KOFmsQkJYT5bfB&token=%s&text=%s&format=wav&sample_rate=16000&voice=%s' %
                 (getToken('LTAI4ycWN34khiO2', 'TazGS3zeb5eeBc2ZEmBUGuCAVo1t9e'), textUrlencode, voices[-1]))
    response = conn.getresponse()
    contentType = response.getheader('Content-Type')
    body = response.read()
    if 'audio/mpeg' == contentType:
        with open(filename, mode='wb') as f:
            f.write(body)
        play(filename)
    else:
        print('The GET request failed: ' + str(body))
    conn.close()


def STT(audioContent):
    """
    阿里语音识别接口
    audioContent:音频字节流
    """
    global AIStatus, checkStartTime, wakeTime, cafeType, checkStartStatus, wakeTime2, wakaran, cameraOpen, wakaranTimes, specialTime, speaking
    host = 'nls-gateway.cn-shanghai.aliyuncs.com'
    httpHeaders = {
        'X-NLS-Token': getToken('LTAI4ycWN34khiO2', 'TazGS3zeb5eeBc2ZEmBUGuCAVo1t9e'),
        'Content-type': 'application/octet-stream',
        'Content-Length': len(audioContent)
    }
    conn = http.client.HTTPConnection(host)
    conn.request(method='POST', url='http://nls-gateway.cn-shanghai.aliyuncs.com/stream/v1/asr?appkey=iD6WHk9lXQLupV45&format=pcm&sample_rate=16000&enable_punctuation_prediction=false&enable_inverse_text_normalization=true',
                 body=audioContent, headers=httpHeaders)
    response = conn.getresponse()
    body = response.read()
    try:
        body = json.loads(body)
        status = body['status']
        if status == 20000000:
            result = body['result']
            # 识别成功后续逻辑
            print('Recognize result: ' + result)
            # 热词唤醒，唤醒后状态改为wake，是否取消改为False
            if ('花' in result) or ('华' in result):
                speaking = True
                play(BASE_DIR+'/wav/const/唤醒.wav')
                speaking = False
                AIStatus = 'wake'
                wakeTime = time.time()
            if AIStatus == 'wake':
                if ('消订' in result) or ('取消' in result) or ('交订' in result) or ('订单' in result):
                    speaking = True
                    play(BASE_DIR+'/wav/const/取消订单.wav')
                    speaking = False
                    AIStatus = 'sleep'
                    wakeTime = time.time()
                    checkStartStatus = False
                elif ('叫啥' in result or '名字' in result) and not checkStartStatus:
                    speaking = True
                    play(random.choice([BASE_DIR+'/wav/const/小花.wav', BASE_DIR +
                                        '/wav/const/名字.wav']))
                    speaking = False
                    wakeTime = time.time()
                elif ('男的' in result or '女的' in result or '性别' in result) and not checkStartStatus:
                    answer = random.choice([BASE_DIR +
                                            '/wav/const/女孩.wav', BASE_DIR+'/wav/const/我是.wav'])
                    speaking = True
                    play(answer)
                    speaking = False
                    if answer == BASE_DIR+'/wav/const/我是.wav':
                        time.sleep(1)
                        if res:
                            speaking = True
                            play(BASE_DIR+'/wav/const/骗你.wav')
                            speaking = False
                    wakeTime = time.time()
                elif ('什么' in result or '干啥' in result or '做啥' in result) and not checkStartStatus:
                    speaking = True
                    play(BASE_DIR+'/wav/const/能做咖啡哦.wav')
                    speaking = False
                    wakeTime = time.time()
                elif ('再见' in result or '拜拜' in result) and not checkStartStatus:
                    speaking = True
                    play(BASE_DIR+'/wav/const/byebye.wav')
                    speaking = False
                    AIStatus = 'sleep'
                elif ('几点' in result) and not checkStartStatus:
                    speaking = True
                    dt = datetime.datetime.now()
                    TTS('现在是北京时间:%s年%s月%s号%s点%s分%s秒' % (dt.year, dt.month, dt.day, dt.hour,
                                                        dt.minute, dt.second), BASE_DIR + "/wav/const/time.wav")
                    wakeTime = time.time()
                    specialTime = True
                    speaking = False
                elif ('周几' in result or '星期' in result) and not checkStartStatus:
                    speaking = True
                    dt = datetime.datetime.now()
                    TTS('今天是:周%s哦,' % (dt.weekday()+1 if dt.weekday()+1 != 7 else '日'), BASE_DIR +
                        "/wav/const/time.wav")
                    wakeTime = time.time()
                    specialTime = True
                    speaking = False
                elif ('几号' in result) and not checkStartStatus:
                    speaking = True
                    dt = datetime.datetime.now()
                    TTS('今天是:%s年%s月%s号哦' % (dt.year, dt.month,
                                            dt.day), BASE_DIR + "/wav/const/time.wav")
                    wakeTime = time.time()
                    specialTime = True
                    speaking = False
                elif ('天气' in result or '少度' in result or '几度' in result or '温度' in result) and not checkStartStatus:
                    speaking = True
                    city = requests.get('http://pv.sohu.com/cityjson').text
                    cname = city[city.index('cname')+9:-7]
                    weather = requests.get(
                        'https://restapi.amap.com/v3/weather/weatherInfo?city=%s&key=373fd53572f1b0dbf5158592c2c2370b' % cname).text
                    res = json.loads(weather)['lives'][0]
                    TTS('今日%s:天气%s,气温%s度,湿度%s,%s风%s级,' % (res['province'], res['weather'], res['temperature'],
                                                          res['humidity'], res['winddirection'], res['windpower']), BASE_DIR+'/wav/const/天气.wav')
                    wakeTime = time.time()
                    specialTime = True
                    speaking = False
                elif ('几岁' in result or '多大' in result) and not checkStartStatus:
                    speaking = True
                    play(random.choice([BASE_DIR+'/wav/const/18岁.wav', BASE_DIR +
                                        '/wav/const/没礼貌.wav', BASE_DIR+'/wav/const/年龄.wav']))
                    speaking = False
                    wakeTime = time.time()
                elif '傻' in result and not checkStartStatus:
                    speaking = True
                    play(BASE_DIR+'/wav/const/傻.wav')
                    speaking = False
                    wakeTime = time.time()
                elif (('清咖' in result) or ('轻咖' in result) or ('轻卡' in result) or ('青卡' in result) or ('新卡' in result) or ('听卡' in result) or ('新咖' in result) or ('听咖' in result) or ('清卡' in result) or ('星咖' in result)) and cameraOpen and not checkStartStatus:
                    speaking = True
                    play(BASE_DIR+'/wav/const/清咖啡.wav')
                    speaking = False
                    checkStartStatus = True
                    cameraOpen = False
                    checkStartTime = time.time()
                    wakeTime = time.time()
                    cafeType = '清咖啡'
                elif (('农卡' in result) or ('浓卡' in result) or ('浓咖' in result) or ('农咖' in result) or ('能咖' in result) or ('侬咖' in result)) and cameraOpen and not checkStartStatus:
                    speaking = True
                    play(BASE_DIR+'/wav/const/浓咖啡.wav')
                    speaking = False
                    checkStartStatus = True
                    cameraOpen = False
                    checkStartTime = time.time()
                    wakeTime = time.time()
                    cafeType = '浓咖啡'
                elif ('不要' == result or '不喝' == result or '我喝' == result or '呵呵' == result or '薄荷' == result or '如何' == result or '符合' == result) and not checkStartStatus:
                    speaking = True
                    play(BASE_DIR+'/wav/const/讨厌.wav')
                    speaking = False
                    AIStatus = 'sleep'
                    wakeTime = time.time()
                elif ('要' in result or '呵' in result or '对' in result or '喝' in result or '哥' in result or '和' in result or '河' in result or '对' in result or '是' in result or '杯' in result or '咖' in result or '啡' in result) and not checkStartStatus:
                    speaking = True
                    play(BASE_DIR+'/wav/const/身份验证.wav')
                    cameraP = Process(target=cameraProcess)
                    cameraP.start()
                    cameraOpen = True
                    with open(BASE_DIR + "/cameraP.txt", "w") as f:
                        f.write(str(cameraP.pid))
                        speaking = False
                    with open(BASE_DIR + "/loadCamera.txt", "w") as f:
                        f.write('loadCamera')
                    wakeTime = time.time()
                    specialTime = True
                elif '咖啡' == result and not checkStartStatus:
                    speaking = True
                    play(BASE_DIR+'/wav/const/没听清.wav')
                    speaking = False
                    wakeTime = time.time()
                elif '瞅' in result and not checkStartStatus:
                    speaking = True
                    play(BASE_DIR+'/wav/const/瞅你.wav')
                    speaking = False
                    wakeTime = time.time()
                elif ('你好' == result or '您好' == result) and not checkStartStatus:
                    speaking = True
                    play(BASE_DIR+'/wav/const/你好.wav')
                    speaking = False
                    wakeTime = time.time()
                elif '好听' in result and not checkStartStatus:
                    speaking = True
                    play(BASE_DIR+'/wav/const/开心.wav')
                    speaking = False
                    wakeTime = time.time()
                elif len(result) > 1 and '花' not in result and '华' not in result and not checkStartStatus:
                    wakaran = True
                    wakaranTimes += 1
                    wakeTime = time.time()
                    wakeTime2 = time.time()
                else:
                    pass
        else:
            print('Recognizer failed!')
    except ValueError:
        print('The response is not json format string')
    conn.close()


class TTSThread (threading.Thread):
    def __init__(self, text, path):
        threading.Thread.__init__(self)
        self.text = text
        self.path = path

    def run(self):
        TTS(self.text, self.path)


class PlayThread (threading.Thread):
    def __init__(self, audio):
        threading.Thread.__init__(self)
        self.audio = audio

    def run(self):
        """
        语音播放
        audio:要播放的文件地址
        """
        with open(BASE_DIR+'/play.txt', 'w') as f:
            f.write('playing')
        wf = wave.open(self.audio, 'rb')
        p = PyAudio()
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)
        data = wf.readframes(1024)
        while data != b'':
            stream.write(data)
            data = wf.readframes(1024)
        stream.stop_stream()
        stream.close()
        p.terminate()
        if os.path.exists(BASE_DIR + "/play.txt"):
            os.remove(BASE_DIR + "/play.txt")

    def getResult(self):
        threading.Thread.join(self)
        return True


#TTS('小花不能回答这个问题，再见', BASE_DIR+'/wav/const/主动再见.wav')
