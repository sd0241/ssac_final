import queue, os, threading
import sounddevice as sd
import soundfile as sf
import time
import speech_recognition as sr
from gtts import gTTS
import pygame
from bs4 import BeautifulSoup
import requests
import json
global tts

import playsound
import pymysql
import pandas as pd

mic = sr.Microphone()
tts = gTTS(text=mic, lang='ko')
q = queue.Queue()
recorder = False
recording = False
# pymysql.install_as_MySQLdb()
# news_data = pymysql.connect(
#     user='admin',
#     passwd='12345678',
#     host='ssac.ctsolbee3mtl.us-west-2.rds.amazonaws.com',
#     db='news_data',
#     charset='UTF8'
# )
# cursor = news_data.cursor(pymysql.cursors.DictCursor)
# sql = "SELECT time,topic,abs_news FROM 2022년05월17일;"
# cursor.execute(sql)
# result = cursor.fetchall()
# print(result)
# df = pd.DataFrame(result)
# print(df)


def complicated_record():
    with sf.SoundFile("./temp.wav", mode='w', samplerate=16000, subtype='PCM_16', channels=1) as file:
        with sd.InputStream(samplerate=16000, dtype='int16', channels=1, callback=complicated_save):
            while recording:
                file.write(q.get())


def complicated_save(indata, frames, time, status):
    q.put(indata.copy())


def start():
    global recorder
    global recording
    recording = True
    recorder = threading.Thread(target=complicated_record)
    print('start recording')
    recorder.start()


def stop():
    global recorder
    global recording
    recording = False
    recorder.join()
    print('stop recording')


def start_record():
    start()
    time.sleep(5)
    stop()



def send_api(path, method):
    API_HOST = "https://www.newssum.shop/"
    url = API_HOST + path
    # body = {
    #     "key1": "value1",
    # "key2": "value2"
    # }
    if method == 'GET':
        response = requests.get(url)
        json_data = json.loads(response.text)
        print(json_data)
    elif method == 'POST':
            response = requests.post(url)

    tts = gTTS(text=json_data, lang='ko')
    tts.save('./text.mp3')
    return tts

def send_keyword(path, method):
    API_HOST = "https://www.newssum.shop/"
    url = API_HOST + path
    # body = {
    #     "key1": "value1",
    # "key2": "value2"
    # }

    if method == 'GET':
            response = requests.get(url)
            # json_data = json.loads(response.text)
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')
            text = soup.select('body > div.post-container > div > p:nth-child(3) > span:nth-child(2)').text
            text = text.strip()
            print(text)

        # print(json_data)
    elif method == 'POST':
            response = requests.post(url)

    tts = gTTS(text=text, lang='ko')
    tts.save('./text.mp3')
    return tts

# 호출 예시
# send_api("/tts", "GET")

def sound(tts):
    from scipy.io import wavfile
    Recognizer = sr.Recognizer()
    from playsound import playsound
    while True:
        print("정치, 경제, 사회, 생활/문화 중 하나를 말씀해주세요....")
        start_record()
        with sr.AudioFile("./temp.wav") as source:
            audio = Recognizer.record(source)
            try:
                sentence = Recognizer.recognize_google(audio, language='ko')  # 스포츠
                topic = sentence.split(' ')
                print(topic, '기사 검색중...')

                if '경제' in topic:
                    print(topic, '기사 검색중...')
                    send_api('tts/경제', "GET")

                elif '정치' in topic:
                    print(topic, '기사 검색중...')
                    send_api('tts/정치','GET')

                elif '사회' in topic:
                    print(topic, '기사 검색중...')
                    send_api('tts/사회','GET')

                elif '문화' in topic:
                    print(topic, '기사 검색중...')
                    send_api('tts/문화','GET')

                elif '스포츠' in topic:
                    print(topic, '기사 검색중...')
                    send_api('tts/스포츠','GET')

                elif '연예' in topic:
                    print(topic, '기사 검색중...')
                    send_api('tts/연예','GET')

                elif '키워드' in topic:
                    print('키워드')
                    index = topic.index('키워드')
                    print(topic[index-1])
                    send_keyword(f"news?word={topic[index-1]}%20키워드","GET")

                elif '안녕' or '꺼져' or '나가' or '그만해' or '멈춰' or '잘있어' or '헤어져' or '그만' in topic:
                    break

                else:
                    print('이해하지 못했어요 다시 말씀해주세요')
            # print(json_data["0"])
            # tts = gTTS(text=response.text, lang='ko')
            # tts.save('./text.mp3')
                pygame.mixer.init(44100,-16,1,2048)
                pygame.mixer.music.load('./text.mp3')
                pygame.mixer.music.play()
                pygame.mixer.music.set_volume(0.9)
                while pygame.mixer.music.get_busy()==True:
                    continue
                pygame.mixer.quit()
                # print(abstractive_text)
                os.remove('./text.mp3')
            except:
                print("인식할 수 없었어요.")
    return audio


sound(tts=tts)
