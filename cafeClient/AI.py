import os
import cv2
import time
import json
import wave
import random
import datetime
import threading
import http.client
import numpy as np
import urllib.parse
import urllib.request
import face_recognition
from multiprocessing import Process
from pyaudio import PyAudio, paInt16
from aliyunsdkcore.client import AcsClient
from PIL import Image, ImageDraw, ImageFont
from aliyunsdkcore.request import CommonRequest

BASE_DIR = BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))

onlyOne = True
noListen = True
AIStatus = 'sleep'
cameraOpen = False
faceTime = time.time()
wakeTime = time.time()
checkStartSTatus = False
checkStartTime = time.time()
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


def operater(left, right, operator):
    """
    万以内的加减乘除
    left:操作符左边的数
    right:操作符右边的数
    operator:操作符
    """
    if operator == "加":
        answer = str(float(left)+float(right))
        if answer.split('.')[1] == '0':
            answer = int(answer.split('.')[0])
        else:
            answer = float(answer)
        TTS('当然是等于%s啦' % answer, BASE_DIR+'/wav/calc/calc.wav')
    if operator == "减":
        answer = str(float(left)-float(right))
        if answer.split('.')[1] == '0':
            answer = int(answer.split('.')[0])
        else:
            answer = float(answer)
        TTS('当然是等于%s啦' % answer, BASE_DIR+'/wav/calc/calc.wav')
    if operator == "乘":
        answer = str(float(left)*float(right))
        if answer.split('.')[1] == '0':
            answer = int(answer.split('.')[0])
        else:
            answer = float(answer)
        TTS('当然是等于%s啦' % answer, BASE_DIR+'/wav/calc/calc.wav')
    if operator == "除":
        answer = str(float(left)/float(right))
        if answer.split('.')[1] == '0':
            answer = int(answer.split('.')[0])
        else:
            answer = float(answer)
        TTS('当然是等于%s啦' % answer, BASE_DIR+'/wav/calc/calc.wav')


def loadKnowFace():
    """
    计算已知人脸模型
    knownEncoding:返回人脸模型,key为姓名+手机后四位，value为128D特征值
    """
    knownEncoding = {}
    for face in os.listdir(BASE_DIR+'/faces'):
        faceEncode = face_recognition.face_encodings(
            face_recognition.load_image_file(BASE_DIR+'/faces/'+face))[0]
        #knownEncoding[face[:-4]] = faceEncode
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
                img.save(BASE_DIR+'/faces/%s.jpg' % pic)
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
                with open(BASE_DIR + "/faceTimeout.txt", "w") as f:
                    f.write('timeout')
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
    global checkStartTime, checkStartSTatus, AIStatus, cameraOpen, wakeTime, noListen
    save_count = 0
    save_buffer = []
    # pyaudio对象，用来处理录音的音频流
    # 音频声道单声道，采样率16000，固定
    pa = PyAudio()
    stream = pa.open(format=paInt16, channels=1, rate=16000, input=True,
                     frames_per_buffer=1500)
    print('开始录音')
    while True:
        if checkStartSTatus:
            if int(time.time()-checkStartTime) == 10:
                PlayThread(BASE_DIR+'/wav/const/等待制作.wav').start()
                checkStartSTatus = False
                cameraOpen = False
                AIStatus = 'sleep'
                noListen = True
        if AIStatus == 'wake':
            if int(time.time()-wakeTime) == 10 and noListen:
                PlayThread(BASE_DIR + "/wav/const/等待回复.wav").start()
                AIStatus = 'sleep'
                cameraOpen = False
        if os.path.exists(BASE_DIR + "/giveUp.txt"):
            os.remove(BASE_DIR + "/giveUp.txt")
            AIStatus = 'sleep'
            cameraOpen = False
        if os.path.exists(BASE_DIR + "/faceTimeout.txt"):
            os.remove(BASE_DIR + "/faceTimeout.txt")
            AIStatus = 'sleep'
            cameraOpen = False
        if os.path.exists(BASE_DIR + "/waitListen.txt"):
            os.remove(BASE_DIR + "/waitListen.txt")
            if not checkStartSTatus:
                PlayThread(BASE_DIR + "/wav/const/等待回复.wav").start()
                AIStatus = 'sleep'
                cameraOpen = False
        # 每次读取1500字节缓冲
        string_audio_data = stream.read(1500)
        # 将缓冲数据转换为ndarray
        audio_data = np.frombuffer(string_audio_data, dtype=np.short)
        np.savetxt(BASE_DIR + "/wave.txt", audio_data)
        # 计算ndarray中数值大于1500的有多少个
        large_sample_count = np.sum(audio_data > 1500)
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
                if not os.path.exists(BASE_DIR + "/cameraP.txt"):
                    STT(content)
                save_buffer = []


def TTS(text, filename):
    """  
    阿里语音合成接口
    text:要合成的文字
    filename:合成文件的路径
    """
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
        PlayThread(filename).start()
    else:
        print('The GET request failed: ' + str(body))
    conn.close()


def STT(audioContent):
    """ 
    阿里语音识别接口
    audioContent:音频字节流
    """
    global AIStatus, cameraOpen, checkStartTime, checkStartSTatus, wakeTime, noListen
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
                AIStatus = 'wake'
                PlayThread(BASE_DIR+'/wav/const/唤醒.wav').start()
                wakeTime = time.time()
                result = ''
            if AIStatus == 'sleep':
                if len(result) > 1:
                    PlayThread(BASE_DIR+'/wav/const/睡觉.wav').start()
            if AIStatus == 'wake' and len(result) != 0:
                if ('消订' in result) or ('取消' in result) or ('交订' in result) or ('订单' in result):
                    PlayThread(BASE_DIR+'/wav/const/取消订单.wav').start()
                    noListen = True
                    AIStatus = 'sleep'
                    cameraOpen = False
                    checkStartSTatus = False
                elif ('叫啥' in result or '名字' in result) and not checkStartSTatus:
                    PlayThread(random.choice([BASE_DIR+'/wav/const/小花.wav', BASE_DIR +
                                              '/wav/const/名字.wav'])).start()
                    noListen = False
                elif ('男的' in result or '女的' in result or '性别' in result) and not checkStartSTatus:
                    answer = random.choice([BASE_DIR +
                                            '/wav/const/女孩.wav', BASE_DIR+'/wav/const/我是.wav'])
                    gender = PlayThread(answer)
                    gender.start()
                    res = gender.getResult()
                    if answer == BASE_DIR+'/wav/const/我是.wav':
                        time.sleep(1)
                        if res:
                            PlayThread(BASE_DIR+'/wav/const/骗你.wav').start()
                    noListen = False
                elif ('什么' in result or '干啥' in result or '做啥' in result) and not checkStartSTatus:
                    PlayThread(BASE_DIR+'/wav/const/能做咖啡哦.wav').start()
                    noListen = False
                elif ('几点' in result) and not checkStartSTatus:
                    dt = datetime.datetime.now()
                    TTSThread('现在是北京时间:%s年%s月%s号%s点%s分%s秒' % (dt.year, dt.month, dt.day, dt.hour,
                                                              dt.minute, dt.second), BASE_DIR + "/wav/const/time.wav").start()
                    noListen = False
                elif ('周几' in result or '星期' in result) and not checkStartSTatus:
                    dt = datetime.datetime.now()
                    TTSThread('今天是:周%s哦,' % dt.weekday(), BASE_DIR +
                              "/wav/const/time.wav").start()
                    noListen = False
                elif ('几号' in result) and not checkStartSTatus:
                    dt = datetime.datetime.now()
                    TTSThread('今天是:%s年%s月%s号哦' % (dt.year, dt.month,
                                                  dt.day), BASE_DIR + "/wav/const/time.wav").start()
                    noListen = False
                elif ('几岁' in result or '多大' in result) and not checkStartSTatus:
                    PlayThread(random.choice([BASE_DIR+'/wav/const/18岁.wav', BASE_DIR +
                                              '/wav/const/没礼貌.wav', BASE_DIR+'/wav/const/年龄.wav'])).start()
                    noListen = False
                elif (('清咖' in result) or ('轻咖' in result) or ('轻卡' in result) or ('青卡' in result) or ('新卡' in result) or ('听卡' in result) or ('新咖' in result) or ('听咖' in result) or ('清卡' in result)) and cameraOpen and not checkStartSTatus:
                    PlayThread(BASE_DIR+'/wav/const/清咖啡.wav').start()
                    checkStartTime = time.time()
                    cafeType = '清咖啡'
                    checkStartSTatus = True
                    noListen = False
                elif (('农卡' in result) or ('浓卡' in result) or ('浓咖' in result) or ('农咖' in result)) and cameraOpen and not checkStartSTatus:
                    PlayThread(BASE_DIR+'/wav/const/浓咖啡.wav').start()
                    checkStartTime = time.time()
                    cafeType = '浓咖啡'
                    checkStartSTatus = True
                    noListen = False
                elif ('不要' == result or '不喝' == result or '我喝' == result or '呵呵' == result or '薄荷' == result or '如何' == result or '符合' == result) and not checkStartSTatus:
                    PlayThread(BASE_DIR+'/wav/const/讨厌.wav').start()
                    AIStatus = 'sleep'
                    noListen = False
                elif ('要' == result or '呵' == result or '喝' == result or '哥' == result or '和' == result or '河' == result or '咖' in result or '啡' in result) and not cameraOpen and not checkStartSTatus:
                    noListen = False
                    cameraOpen = True
                    cameraP = Process(target=cameraProcess)
                    cameraP.start()
                    PlayThread(BASE_DIR+'/wav/const/身份验证.wav').start()
                    with open(BASE_DIR + "/cameraP.txt", "w") as f:
                        f.write(str(cameraP.pid))
                elif ('咖' in result or '啡' in result) and cameraOpen and not checkStartSTatus:
                    PlayThread(BASE_DIR+'/wav/const/没听清.wav').start()
                    noListen = False
                elif '傻' in result and not checkStartSTatus:
                    PlayThread(BASE_DIR+'/wav/const/傻.wav').start()
                    noListen = False
                elif '瞅' in result and not checkStartSTatus:
                    PlayThread(BASE_DIR+'/wav/const/瞅你.wav').start()
                    noListen = False
                elif '好听' in result and not checkStartSTatus:
                    PlayThread(BASE_DIR+'/wav/const/开心.wav').start()
                    noListen = False
                elif '加' in result and '等' in result and not checkStartSTatus:
                    noListen = False
                    left = result[:result.index('加')]
                    right = result[result.index(
                        '加')+1:result.index('等')]
                    operater(left, right, '加')
                elif '加' in result and '等' not in result and not checkStartSTatus:
                    noListen = False
                    left = result[:result.index('加')]
                    right = result[result.index('加')+1:]
                    operater(left, right, '加')
                elif '减' in result and '等' in result and not checkStartSTatus:
                    noListen = False
                    left = result[:result.index('减')]
                    right = result[result.index(
                        '减')+1:result.index('等')]
                    operater(left, right, '减')
                elif '减' in result and '等' not in result and not checkStartSTatus:
                    noListen = False
                    left = result[:result.index('减')]
                    right = result[result.index('减')+1:]
                    operater(left, right, '减')
                elif '乘以' in result and '等' in result and not checkStartSTatus:
                    noListen = False
                    left = result[:result.index('乘以')]
                    right = result[result.index(
                        '乘以')+2:result.index('等')]
                    operater(left, right, '乘')
                elif '乘以' in result and '等' not in result and not checkStartSTatus:
                    noListen = False
                    left = result[:result.index('乘以')]
                    right = result[result.index('乘以')+2:]
                    operater(left, right, '乘')
                elif '乘' in result and '等' in result and not checkStartSTatus:
                    noListen = False
                    left = result[:result.index('乘')]
                    right = result[result.index(
                        '乘')+1:result.index('等')]
                    operater(left, right, '乘')
                elif '乘' in result and '等' not in result and not checkStartSTatus:
                    noListen = False
                    left = result[:result.index('乘')]
                    right = result[result.index('乘')+1:]
                    operater(left, right, '乘')
                elif '除以' in result and '等' in result and not checkStartSTatus:
                    noListen = False
                    left = result[:result.index('除以')]
                    right = result[result.index(
                        '除以')+2:result.index('等')]
                    operater(left, right, '除')
                elif '除以' in result and '等' not in result and not checkStartSTatus:
                    noListen = False
                    left = result[:result.index('除以')]
                    right = result[result.index('除以')+2:]
                    operater(left, right, '除')
                elif '除' in result and '等' in result and not checkStartSTatus:
                    noListen = False
                    left = result[:result.index('除')]
                    right = result[result.index(
                        '除')+1:result.index('等')]
                    operater(left, right, '除')
                elif '除' in result and '等' not in result and not checkStartSTatus:
                    noListen = False
                    left = result[:result.index('除')]
                    right = result[result.index('除')+1:]
                    operater(left, right, '除')
                else:
                    if len(result) > 1:
                        PlayThread(BASE_DIR+'/wav/const/听不懂.wav').start()
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

    def getResult(self):
        threading.Thread.join(self)
        return True


#TTS('我能帮您做咖啡呀，但是只有清咖啡和浓咖啡哦', BASE_DIR+'/wav/const/能做咖啡哦.wav')