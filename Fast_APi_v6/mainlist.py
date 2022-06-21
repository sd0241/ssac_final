from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import List
from starlette.middleware.cors import CORSMiddleware
from backend.news.database import SessionLocal
from backend.news.models import News, Topic
from generate import Generate
import requests
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
import json
import re
import pandas as pd
import pymysql
from datetime import datetime
from typing import Optional
app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")

# ----------API 정의------------
@app.get("/")
def read_NEWS(request:Request):
    context = {}
    news = SessionLocal.query(News).all()
    context["news"] = news
    context["request"] = request

    return templates.TemplateResponse("main.html", context)

# @app.get("/news",response_class=HTMLResponse)
# def read_NEWS(request:Request):
#     context = {}
#     news = SessionLocal.query(News).all()
#     context["news"] = news
#     context["request"] = request
#
#     return templates.TemplateResponse("main.html", context)

@app.get("/news/{topic}", response_class= HTMLResponse)
def read_NEWS(request:Request, topic: str):
    # context_Root = []
    context = {}
    news = SessionLocal.query(News).filter(News.topic == topic).all()

    for i in range(-3,0):
        # context = {}
        j = i * -1
        context[f'time_{j}'] = news[i].time
        context[f'media_{j}'] = news[i].media
        context[f'topic_{j}'] = news[i].topic
        context[f'title_{j}'] = news[i].title
        context[f'news_{j}'] = news[i].news
        context[f'abs_news_{j}'] = news[i].abs_news
        context[f'url_{j}'] = news[i].url

    context['topic'] = news[i].topic
    context['request'] = request
    return templates.TemplateResponse("news_topic.html", context)

@app.get("/url",response_class=HTMLResponse)
def url(url:str, request:Request, aid:Optional[str]=None):
    if aid:
        url = url + '&aid=' + aid
    url = url
    # if aid is not None :
    #     print(aid)
    #     url = url + '&aid=' + aid
    # else:
    #     url = url
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"}
    model_url = '/home/ec2-user/ssac/test_code1/kobart'
    if 'entertain' in url:
        print(url)
        req = requests.get(url, headers=headers)
        soup = BeautifulSoup(req.text, "html.parser")
        # 뉴스 본문 가져오기
        text = soup.select("#articeBody")
        print(text)
        text = ''.join(str(text))
        print(text)
        # 본문의 html태그제거
        pattern1 = '<[^>]*>'
        pattern2 = '\n'
        pattern3 = '\t'
        text = re.sub(pattern=pattern1, repl='', string=text)
        text = re.sub(pattern=pattern2, repl='', string=text)
        text = re.sub(pattern=pattern3, repl='', string=text)
        print(text)
        # 기사 작성 시간 가져오기
        time_ = soup.select_one('#content > div.end_ct > div > div.article_info > span> em').text
        time_ = time_.replace('오전', 'AM').replace('오후', 'PM')
        title = soup.find(class_='end_tit').text

        # 언론사 가져오기
        media = soup.find(class_='link_news').text.split()[0]

    elif 'sports' in url:
        req = requests.get(url, headers=headers)
        soup = BeautifulSoup(req.text, 'html.parser')
        time_ = soup.find(class_='info').text.split('최종수정')[1].split('기사원문')[0].strip()  # time
        time_ = time_.replace('오전', 'AM').replace('오후', 'PM')
        title = soup.find(class_='title').text
        text = soup.find(id='newsEndContents').text.split('기사제공')[0].strip('\n')
        media = soup.select_one('#pressLogo > a > img')['alt']
    else:
        req = requests.get(url, headers=headers)
        soup = BeautifulSoup(req.text, 'html.parser')
        title = soup.select_one('div.media_end_head_title > h2').text
        text = soup.find(id='dic_area').text
        media = soup.select_one('div.media_end_head_top > a > img')['title']
        time_ = soup.select_one('span.media_end_head_info_datestamp_time').text
        time_ = time_.replace('오전', 'AM').replace('오후', 'PM')
    text = re.sub('[^0-9a-zA-Zㄱ-ㅎ가-힣.,/()]', ' ', text)
    text = text[:2200]
    fin_text = []
    # fin_text = list(text.split('\n')[0])
    fin_text.append(text.split('\n')[0])
    print(fin_text)
    generate = Generate(model_url)
    result = pd.DataFrame(fin_text, columns=['document']).reset_index(drop=True)

    abstractive_text = generate.input_generate(result, 'document')
    abstractive_text = abstractive_text['generate_text'][0]

    context = {}

    context['time'] = time_
    context['media'] = media
    context['title'] = title
    context['url'] = url
    context['news'] = text
    context['abs_news'] = abstractive_text

    context['request'] = request
    return templates.TemplateResponse("url_search.html", context)



@app.get("/tts/{topic}")
def tts(topic: str):
    pymysql.install_as_MySQLdb()
    news_data = pymysql.connect(
        user='newssum',
        passwd='qkrrkddls',
        host='ssac.ctsolbee3mtl.us-west-2.rds.amazonaws.com',
        db='news_data',
        charset='UTF8'
    )
    cursor = news_data.cursor(pymysql.cursors.DictCursor)
    sql = "SELECT time,topic,abs_news FROM {date};"
    tt = str(datetime.today().strftime('%Y{}%m{}%d{}').format(*'년월일'))
    cursor.execute(sql.format(date = tt))
    result = cursor.fetchall()
    print(result)
    df = pd.DataFrame(result)[-18:]
    # news = SessionLocal.query(News).filter(News.topic == topic).all()
    # for new in news:
    #     df['time'] = new.time
    #     df['media'] = new.media
    #     df['topic'] = new.topic
    #     df['title'] = new.title
    #     df['news'] = new.news
    #     df['abs_news'] = new.abs_news
    #
    # df['request'] = request
    if '경제' in topic:
        #                     print(df[1][df[0] == '경제'])
        abstractive_text = "첫번째 기사입니다. " + df['abs_news'][df['topic'] == '경제'].reset_index(drop=True)[0] \
                           + "두번째 기사입니다. " + df['abs_news'][df['topic'] == '경제'].reset_index(drop=True)[1] \
                           + "세번째 기사입니다. " + df['abs_news'][df['topic'] == '경제'].reset_index(drop=True)[2]
    elif '정치' in topic:
        #                     print(df[1][df[0] == '정치'])
        abstractive_text = "첫번째 기사입니다. " + df['abs_news'][df['topic'] == '정치'].reset_index(drop=True)[0] \
                           + "두번째 기사입니다. " + df['abs_news'][df['topic'] == '정치'].reset_index(drop=True)[1] \
                           + "세번째 기사입니다. " + df['abs_news'][df['topic'] == '정치'].reset_index(drop=True)[2]
    elif '사회' in topic:
        #                     print(df[1][df[0] == '사회'])
        abstractive_text = "첫번째 기사입니다. " + df['abs_news'][df['topic'] == '사회'].reset_index(drop=True)[0] \
                           + "두번째 기사입니다. " + df['abs_news'][df['topic'] == '사회'].reset_index(drop=True)[1] \
                           + "세번째 기사입니다. " + df['abs_news'][df['topic'] == '사회'].reset_index(drop=True)[2]
    elif '문화' in topic:
        #                     print(df[1][df[0] == '생활/문화'])
        abstractive_text = "첫번째 기사입니다. " + df['abs_news'][df['topic'] == '문화'].reset_index(drop=True)[0] \
                           + "두번째 기사입니다. " + df['abs_news'][df['topic'] == '문화'].reset_index(drop=True)[
                               1] \
                           + "세번째 기사입니다. " + df['abs_news'][df['topic'] == '문화'].reset_index(drop=True)[
                              2]
    elif '스포츠' in topic:
        #                     print(df[1][df[0] == '생활/문화'])
        abstractive_text = "첫번째 기사입니다. " + df['abs_news'][df['topic'] == '스포츠'].reset_index(drop=True)[0] \
                           + "두번째 기사입니다. " + df['abs_news'][df['topic'] == '스포츠'].reset_index(drop=True)[
                               1] \
                           + "세번째 기사입니다. " + df['abs_news'][df['topic'] == '스포츠'].reset_index(drop=True)[
                               2]
    elif '연예' in topic:
        #                     print(df[1][df[0] == '생활/문화'])
        abstractive_text = "첫번째 기사입니다. " + df['abs_news'][df['topic'] == '연예'].reset_index(drop=True)[0] \
                           + "두번째 기사입니다. " + df['abs_news'][df['topic'] == '연예'].reset_index(drop=True)[
                               1] \
                           + "세번째 기사입니다. " + df['abs_news'][df['topic'] == '연예'].reset_index(drop=True)[
                               2]

    # elif '키워드' in topic:
    #     chrome_options = webdriver.ChromeOptions()
    #     chrome_options.add_argument('--headless')
    #     chrome_options.add_argument('--no-sandbox')
    #     chrome_options.add_argument('--disable-dev-shm-usage')
    #
    #     driver = webdriver.Chrome(executable_path='/usr/bin/chromedriver',
    #                               chrome_options=chrome_options)
    #     keyword = topic.split(' ')
    #     index = keyword.index('키워드')
    #     url = 'https://search.naver.com/search.naver?where=news&sm=tab_jum&query={}'.format(
    #         keyword[index - 1])
    #     model_url = '/home/ec2-user/ssac/test_code1/etri_et5'
    #     driver.get(url)
    #     time.sleep(1)  # 대기시간 변경 가능
    #     a = driver.find_elements(By.CSS_SELECTOR, 'a.info')
    #     for i in a:
    #         if i.text == '네이버뉴스':
    #             # 위에서 생성한 css selector list 하나씩 클릭하여 본문 url얻기
    #             i.click()
    #
    #     # 현재탭에 접근
    #     driver.switch_to.window(driver.window_handles[1])
    #     time.sleep(3)  # 대기시간 변경 가능
    #     url = driver.current_url
    #     headers = {
    #         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"}
    #     req = requests.get(url, headers=headers)
    #     html = req.text
    #     soup = BeautifulSoup(html, 'html.parser')
    #     _id = ['dic_area', 'newsEndContents', 'articeBody']
    #     # text = soup.find(id= '{dic_area}').text
    #     for i in _id:
    #         try:
    #             text = soup.find(id='{}'.format(i)).text
    #         except:
    #             continue
    #
    #     string = text.strip()
    #     text = re.sub('[^0-9a-zA-Zㄱ-ㅎ가-힣]', ' ', string)
    #
    #     # req = requests.get(url,headers=headers)
    #     # html = req.text
    #     # soup = BeautifulSoup(html, 'html.parser')
    #     # text = soup.find(id= 'dic_area').text
    #
    #     # 현재 탭 닫기
    #     driver.close()
    #
    #     # 다시처음 탭으로 돌아가기(매우 중요!!!)
    #     driver.switch_to.window(driver.window_handles[0])
    #     fin_text = []
    #     # fin_text = list(text.split('\n')[0])
    #     fin_text.append(text.split('\n')[0])
    #
    #     generate = Generate(model_url)
    #     result = pd.DataFrame(fin_text, columns=['document'])
    #
    #     abstractive_text = generate.input_generate(result, 'document')
    #     abstractive_text = abstractive_text.generate_text
    #     print(abstractive_text.generate_text)
    #     print()
    #     print(result.document)
    #     print()
    #     print(url)

    return abstractive_text

@app.get("/news",response_class=HTMLResponse)
def keyword(word:str, request:Request):
    import time
    if '키워드' in word:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')

        driver = webdriver.Chrome(executable_path='/usr/bin/chromedriver',
                                  chrome_options=chrome_options)
        # driver = webdriver.Chrome('./chromedriver',
        #                           chrome_options=chrome_options)
        driver.implicitly_wait(1)
        keyword = word.split(' ')
        index = keyword.index('키워드')
        url = 'https://search.naver.com/search.naver?where=news&sm=tab_jum&query={}'.format(
            keyword[index - 1])
        model_url = '/home/ec2-user/ssac/test_code1/kobart'
        driver.get(url)
        time.sleep(1)  # 대기시간 변경 가능
        a = driver.find_elements(By.CSS_SELECTOR, 'a.info')
        for i in a:
            if i.text == '네이버뉴스':
                # 위에서 생성한 css selector list 하나씩 클릭하여 본문 url얻기
                i.click()

                break

        # 현재탭에 접근
        driver.switch_to.window(driver.window_handles[1])
        time.sleep(1)  # 대기시간 변경 가능
        url = driver.current_url
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"}

        if url.find('entertain') != -1:
            req = requests.get(url, headers=headers)
            soup = BeautifulSoup(req.text, "html.parser")
            # 뉴스 본문 가져오기

            text = soup.select("#articeBody")
            text = ''.join(str(text))
            # 본문의 html태그제거
            pattern1 = '<[^>]*>'
            pattern2 = '\n'
            pattern3 = '\t'
            text = re.sub(pattern=pattern1, repl='', string=text)
            text = re.sub(pattern=pattern2, repl='', string=text)
            text = re.sub(pattern=pattern3, repl='', string=text)
            text = text.replace('\xa0', '')
            # 기사 작성 시간 가져오기
            time_ = soup.select_one('#content > div.end_ct > div > div.article_info > span > em').text
            time_ = time_.replace('오전', 'AM').replace('오후', 'PM')
            title = soup.find(class_='end_tit').text

            # 언론사 가져오기
            media = soup.find(class_='link_news').text.split()[0]
            url = url

        elif url.find('sports') != -1:
            req = requests.get(url, headers=headers)
            soup = BeautifulSoup(req.text, 'html.parser')
            time_ = soup.find(class_='info').text.split('최종수정')[1].split('기사원문')[0].strip()  # time
            time_ = time_.replace('오전', 'AM').replace('오후', 'PM')
            title = soup.find(class_='title').text
            text = soup.find(id='newsEndContents').text.split('기사제공')[0].strip('\n')
            pattern1 = '<[^>]*>'
            pattern2 = '\n'
            pattern3 = '\t'
            text = re.sub(pattern=pattern1, repl='', string=text)
            text = re.sub(pattern=pattern2, repl='', string=text)
            text = re.sub(pattern=pattern3, repl='', string=text)
            text  = text.replace('\xa0','')
            media = soup.select_one('#pressLogo > a > img')['alt']
            url = url
        else:
            req = requests.get(url, headers=headers)
            soup = BeautifulSoup(req.text, 'html.parser')
            title = soup.select_one('div.media_end_head_title > h2').text
            text = soup.find(id='dic_area').text
            pattern1 = '<[^>]*>'
            pattern2 = '\n'
            pattern3 = '\t'
            text = re.sub(pattern=pattern1, repl='', string=text)
            text = re.sub(pattern=pattern2, repl='', string=text)
            text = re.sub(pattern=pattern3, repl='', string=text)
            text = text.replace('\xa0', '')
            media = soup.select_one('div.media_end_head_top > a > img')['title']
            time_ = soup.select_one('span.media_end_head_info_datestamp_time').text
            time_ = time_.replace('오전', 'AM').replace('오후', 'PM')
            url = url
        # 현재 탭 닫기
        driver.close()
        text = re.sub('[^0-9a-zA-Zㄱ-ㅎ가-힣.,/()]', ' ', text)
        text = text[:2200]
        # 다시처음 탭으로 돌아가기(매우 중요!!!)
        driver.switch_to.window(driver.window_handles[0])
        fin_text = []
        # fin_text = list(text.split('\n')[0])
        fin_text.append(text.split('\n')[0])
        print(fin_text)
        generate = Generate(model_url)
        result = pd.DataFrame(fin_text, columns=['document']).reset_index(drop=True)

        abstractive_text = generate.input_generate(result, 'document')
        abstractive_text = abstractive_text['generate_text'][0]

        context = {}

        context['time'] = time_
        context['media'] = media
        context['title'] = title
        context['url'] = url
        context['news'] = text
        context['abs_news'] = abstractive_text
        print(abstractive_text)
        print(type(abstractive_text))

        context['request'] = request
    return templates.TemplateResponse("news_search.html", context)

@app.get("/{url}", response_class= HTMLResponse)
def read_NEWS_one(request:Request, url: str):
    news = SessionLocal.query(News).filter(News.url.contains(url)).all()
    context = {}
    context['time'] = news[0].time
    context['media'] = news[0].media
    context['title'] = news[0].title
    context['url'] = news[0].url
    # context['news'] = news[0].news
    context['abs_news'] = news[0].abs_news
    context['url'] = news[0].url
    context['request'] = request
    return templates.TemplateResponse("news_search.html", context)



@app.post("/news")
def create_news(time: int, media: str, topic:str, title:str, news:str, abs_news:str):

    new = News()
    new.topic = topic
    new.time = time
    new.media = media
    new.title = title
    new.news = news
    new.abs_news = abs_news

    session.add(new)
    session.commit()

    return f"{topic} created..."

@app.put("/news")
def update_news(topics: List[Topic]):

    for i in topics:
        News = SessionLocal.query(News).filter(News.topic == i.topic).first()
        News.topic = i.topic
        News.time = i.time

    #users[0].name

    return f"{News[0].topic} updated..."

@app.delete("/News")
def delete_News(NEWS:str):
    New = SessionLocal.query(News).filter(News.topic == News).delete()
    SessionLocal.commit()

    return New