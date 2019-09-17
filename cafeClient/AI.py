import os
import cv2
import time
import json
import wave
import psutil
import random
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
lastPerson = ''
isCancle = False
AIStatus = 'sleep'
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


def play(audio, CHUNK=1024):
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
    data = wf.readframes(CHUNK)
    while data != b'':
        stream.write(data)
        data = wf.readframes(CHUNK)
    stream.stop_stream()
    stream.close()
    p.terminate()


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
        knownEncoding[face[:-4]] = faceEncode
    return knownEncoding


def cameraProcess():
    """
    人脸识别的进程函数
    """
    global onlyOne, lastPerson
    face_locations = []
    face_encodings = []
    process_this_frame = True
    # 首次运行，加载已知人脸特征值
    knowFace = loadKnowFace()
    # 开启默认摄像头
    video_capture = cv2.VideoCapture(0)
    width = video_capture.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
    while True:
        # 前端注册完成信号，重新计算人脸特征值
        if os.path.exists(BASE_DIR + "/register.txt"):
            os.remove(BASE_DIR + "/register.txt")
            knowFace = loadKnowFace()
        # ret摄像头设否开启，False关闭 True开启
        # frame每帧视频数据，ndarray格式
        ret, frame = video_capture.read()
        # 黄线包裹区域
        cv2.rectangle(frame, (int(width*0.25), 0),
                      (int(width*0.75), int(height)), (0, 255, 255))
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
            # 检测当前帧中是否存在人脸，将人脸数写入personNum.txt文件，语音识别时需要用到
            face_locations = face_recognition.face_locations(
                rgb_small_frame)
            with open(BASE_DIR + "/personNum.txt", "w") as f:
                f.write(str(len(face_locations)))
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
                    name = list(knowFace.keys())[
                        best_match_index]
                    # lastPerson默认是空，当认识一个人时把lastPerson赋值为认识的这个人，当俩次认识的不是一个人时，重启问候语音
                    if lastPerson != name:
                        onlyOne = True
                    lastPerson = name
                    # 生成一个文件known.txt文件，内容为known，代表认识这个人
                    with open(BASE_DIR + "/known.txt", "w") as f:
                        f.write('known')
                    # 当认识的这个人在黄线区域内时开启问候语音，将姓名写入name.txt文件，供问候语音使用
                    if len(face_locations) > 0 and face_locations[0][1]*4 < int(width*0.75) and face_locations[0][3]*4 > int(width*0.25) and onlyOne:
                        onlyOne = False
                        with open(BASE_DIR+'/name.txt', 'w') as f:
                            f.write(name)
                            f.close()
                    face_names.append(name[:-4])
                else:
                    # 不认识与认识的处理逻辑相反
                    with open(BASE_DIR + "/known.txt", "w") as f:
                        f.write('unknown')
                    if len(face_locations) > 0 and face_locations[0][1]*4 < int(width*0.75) and face_locations[0][3]*4 > int(width*0.25) and onlyOne:
                        onlyOne = False
                        with open(BASE_DIR+'/name.txt', 'w') as f:
                            f.write('unknown')
                            f.close()
                    face_names.append('unknown')
        process_this_frame = not process_this_frame
        # 用方框将人脸区域画出，并在左下角显示姓名
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4
            img_PIL = Image.fromarray(
                cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            font = ImageFont.truetype('simsun.ttc', 40)
            draw = ImageDraw.Draw(img_PIL)
            draw.text((left, bottom), name,
                      font=font, fill=(255, 255, 255))
            frame = cv2.cvtColor(np.asarray(img_PIL), cv2.COLOR_RGB2BGR)
            cv2.rectangle(frame, (left, top),
                          (right, bottom), (255, 255, 255), 2)
        cv2.imshow('FaceRecognition', frame)
        # 键盘摁下q键，关闭进程，删除临时文件，关闭摄像头和窗口
        if key == ord('q'):
            if os.path.exists(BASE_DIR+'/name.txt'):
                os.remove(BASE_DIR+'/name.txt')
            if os.path.exists(BASE_DIR+'/known.txt'):
                os.remove(BASE_DIR+'/known.txt')
            if os.path.exists(BASE_DIR+'/personNum.txt'):
                os.remove(BASE_DIR+'/personNum.txt')
            if os.path.exists(BASE_DIR+'/welcome.txt'):
                os.remove(BASE_DIR+'/welcome.txt')
            with open(BASE_DIR+'/recordP.txt', 'r') as f:
                pid = f.readline()
                f.close()
                os.remove(BASE_DIR+'/recordP.txt')
                cmd = 'taskkill /pid ' + str(pid) + ' /f'
                try:
                    os.system(cmd)
                except Exception as e:
                    print(e)
            with open(BASE_DIR+'/cameraP.txt', 'r') as f:
                pid = f.readline()
                f.close()
                os.remove(BASE_DIR+'/cameraP.txt')
                cmd = 'taskkill /pid ' + str(pid) + ' /f'
                try:
                    os.system(cmd)
                except Exception as e:
                    print(e)
            break
    video_capture.release()
    cv2.destroyAllWindows()


def recordProcess():
    """  
    录音进程
    """
    save_count = 0
    save_buffer = []
    # pyaudio对象，用来处理录音的音频流
    # 音频声道单声道，采样率16000，固定
    pa = PyAudio()
    stream = pa.open(format=paInt16, channels=1, rate=16000, input=True,
                     frames_per_buffer=1500)
    print('开始录音')
    while True:
        # 每次读取1500字节缓冲
        string_audio_data = stream.read(1500)
        # 将缓冲数据转换为ndarray
        audio_data = np.frombuffer(string_audio_data, dtype=np.short)
        np.savetxt(BASE_DIR + "/wave.txt", audio_data)
        # 计算ndarray中数值大于1500的有多少个
        large_sample_count = np.sum(audio_data > 1500)
        # 大于1500的有20个以上时，保存这段录音，时长5秒
        if large_sample_count > 20:
            start = time.time()
            save_count = 5
        else:
            save_count -= 1

        if save_count < 0:
            end = time.time()
            save_count = 0

        if save_count > 0:
            save_buffer.append(string_audio_data)
        else:
            # 将保存的缓冲数据拼接成一句完整的话，调用语音识别接口
            if len(save_buffer) > 0:
                content = b''
                for buf in save_buffer:
                    content = content + buf
                STT(content)
                save_buffer = []


def getGender(path):
    """  
    人脸信息识别，此处主要识别性别
    path:人脸图片路径
    """
    boundary = '----------%s' % hex(int(time.time() * 1000))
    data = []
    data.append('--%s' % boundary)
    data.append('Content-Disposition: form-data; name="%s"\r\n' %
                'api_key')
    data.append('_J5zX52Zc7kmvxjz3WWEgG6QHLXWJF-K')
    data.append('--%s' % boundary)
    data.append('Content-Disposition: form-data; name="%s"\r\n' %
                'api_secret')
    data.append('Z5XX_2af1a7pTBLGeBxBMORJlsK1jC8r')
    data.append('--%s' % boundary)
    fr = open(path, 'rb')
    data.append('Content-Disposition: form-data; name="%s"; filename=" "' %
                'image_file')
    data.append('Content-Type: %s\r\n' % 'application/octet-stream')
    data.append(fr.read())
    fr.close()
    data.append('--%s' % boundary)
    data.append('Content-Disposition: form-data; name="%s"\r\n' %
                'return_landmark')
    data.append('1')
    data.append('--%s' % boundary)
    data.append('Content-Disposition: form-data; name="%s"\r\n' %
                'return_attributes')
    data.append(
        'gender,age,smiling,headpose,facequality,blur,eyestatus,emotion,ethnicity,beauty,mouthstatus,eyegaze,skinstatus')
    data.append('--%s--\r\n' % boundary)

    for i, d in enumerate(data):
        if isinstance(d, str):
            data[i] = d.encode('utf-8')
    http_body = b'\r\n'.join(data)
    req = urllib.request.Request(
        url='https://api-cn.faceplusplus.com/facepp/v3/detect', data=http_body)
    req.add_header(
        'Content-Type', 'multipart/form-data; boundary=%s' % boundary)
    resp = urllib.request.urlopen(req, timeout=5)
    qrcont = resp.read()
    res = json.loads(qrcont.decode('utf-8'))
    return res


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
                 (getToken('LTAI4ycWN34khiO2', 'TazGS3zeb5eeBc2ZEmBUGuCAVo1t9e'), textUrlencode, random.choice(voices)))
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
    global AIStatus, isCancle
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
            arr1, arr2 = ['清', '青', '轻', '请', '冰', '新',
                          '情', '听', '停', '金', '京', '经'], ['农', '浓', '本', '能', '檬', '侬']
            # 热词唤醒，唤醒后状态改为wake，是否取消改为False
            if ('花' in result) or ('华' in result):
                AIStatus = 'wake'
                isCancle = False
                play(BASE_DIR+'/wav/const/唤醒.wav')
            if os.path.exists(BASE_DIR+'/known.txt'):
                with open(BASE_DIR+'/known.txt', 'r') as f:
                    name = f.readline()
                    f.close()
                    os.remove(BASE_DIR+'/known.txt')
                    # 判断是否认识这个人，如果认识则默认为唤醒状态
                    if name == 'known':
                        AIStatus = 'wake'
                        if os.path.exists(BASE_DIR + "/welcome.txt"):
                            isCancle = False
                            os.remove(BASE_DIR + "/welcome.txt")
                    else:
                        # 如果不认识，首先判断镜头中是否有人，如果没人则忽略周围声音，如果有人，则回复不认识的语音
                        with open(BASE_DIR + "/personNum.txt", "r") as f:
                            persons = int(f.readline())
                            f.close()
                            os.remove(BASE_DIR + "/personNum.txt")
                            if persons != 0:
                                play(BASE_DIR+'/wav/const/不认识.wav')
                            else:
                                AIStatus = 'sleep'
                    # 如果是唤醒状态，并且认识这个人，这个人也没有说取消订单字样，则进行后续逻辑
                    # 如果有听到取消订单则状态改为sleep，是否取消改为True
                    if AIStatus == 'wake' and name == 'known' and not isCancle:
                        if ('消订' in result) or ('取消' in result) or ('交订' in result) or ('订单' in result):
                            play(BASE_DIR+'/wav/const/取消订单.wav')
                            AIStatus = 'sleep'
                            isCancle = True
                        elif ('咖' in result and result[result.index('咖')-1] in arr1) or ('客' in result and result[result.index('客')-1] in arr1) or ('卡' in result and result[result.index('卡')-1] in arr1):
                            play(BASE_DIR+'/wav/const/清咖啡.wav')
                        elif ('咖' in result and result[result.index('咖')-1] in arr2) or ('客' in result and result[result.index('客')-1] in arr2) or ('卡' in result and result[result.index('卡')-1] in arr2):
                            play(BASE_DIR+'/wav/const/浓咖啡.wav')
                        elif '咖啡' in result:
                            play(BASE_DIR+'/wav/const/没听清.wav')
                        elif '傻' in result:
                            play(BASE_DIR+'/wav/const/傻.wav')
                        elif '瞅' in result or '丑' in result:
                            play(BASE_DIR+'/wav/const/瞅你.wav')
                        elif '加' in result and '等' in result:
                            left = result[:result.index('加')]
                            right = result[result.index(
                                '加')+1:result.index('等')]
                            operater(left, right, '加')
                        elif '加' in result and '等' not in result:
                            left = result[:result.index('加')]
                            right = result[result.index('加')+1:]
                            operater(left, right, '加')
                        elif '减' in result and '等' in result:
                            left = result[:result.index('减')]
                            right = result[result.index(
                                '减')+1:result.index('等')]
                            operater(left, right, '减')
                        elif '减' in result and '等' not in result:
                            left = result[:result.index('减')]
                            right = result[result.index('减')+1:]
                            operater(left, right, '减')
                        elif '乘以' in result and '等' in result:
                            left = result[:result.index('乘以')]
                            right = result[result.index(
                                '乘以')+2:result.index('等')]
                            operater(left, right, '乘')
                        elif '乘以' in result and '等' not in result:
                            left = result[:result.index('乘以')]
                            right = result[result.index('乘以')+2:]
                            operater(left, right, '乘')
                        elif '乘' in result and '等' in result:
                            left = result[:result.index('乘')]
                            right = result[result.index(
                                '乘')+1:result.index('等')]
                            operater(left, right, '乘')
                        elif '乘' in result and '等' not in result:
                            left = result[:result.index('乘')]
                            right = result[result.index('乘')+1:]
                            operater(left, right, '乘')
                        elif '除以' in result and '等' in result:
                            left = result[:result.index('除以')]
                            right = result[result.index(
                                '除以')+2:result.index('等')]
                            operater(left, right, '除')
                        elif '除以' in result and '等' not in result:
                            left = result[:result.index('除以')]
                            right = result[result.index('除以')+2:]
                            operater(left, right, '除')
                        elif '除' in result and '等' in result:
                            left = result[:result.index('除')]
                            right = result[result.index(
                                '除')+1:result.index('等')]
                            operater(left, right, '除')
                        elif '除' in result and '等' not in result:
                            left = result[:result.index('除')]
                            right = result[result.index('除')+1:]
                            operater(left, right, '除')
                        else:
                            pass
        else:
            print('Recognizer failed!')
    except ValueError:
        print('The response is not json format string')
    conn.close()


class GenderThread (threading.Thread):
    """  
    获取性别线程
    """

    def __init__(self, path):
        threading.Thread.__init__(self)
        self.path = path

    def run(self):
        self.res = getGender(self.path)

    def getResult(self):
        threading.Thread.join(self)
        try:
            return self.res
        except:
            return None
