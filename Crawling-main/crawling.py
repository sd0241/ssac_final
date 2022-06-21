from os import link
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
import schedule
import torch
from sqlalchemy import create_engine
import sqlalchemy
import requests
import pymysql
import numpy as np
from datetime import datetime, timedelta
from generate import Generate
from selenium import webdriver

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--incognito")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-setuid-sandbox")
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
driver = webdriver.Chrome('./chromedriver', options=chrome_options)  # 옵션 적용


class Topic:
    def __init__(self):
        # model = torch.load('./test_code1/etri_et5/model.pt',map_location=torch.device('cpu'))
        model_url = './test_code1/kobart'
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"}
        self.generate = Generate(model_url)

    def main_page(self, url, topic):
        # 모듈 import
        import re
        import numpy as np
        from datetime import datetime
        # 정치면 메인 페이지 요청 -> html로 파싱
        req = requests.get(url, headers=self.headers)
        target = BeautifulSoup(req.content, 'html.parser')
        url_main = 'https://news.naver.com/'
        total = {}
        link = {}
        if topic == '정치':
            select = target.select('div.cluster_foot_inner > a')
        else:
            select = target.select('div.cluster_head_inner > a')
        for idx, tag in enumerate(select):
            each_url = url_main + tag['href']  # 각 헤드라인 서브 페이지 링크
            try:
                news_num = int(re.match('[0-9]+', tag.text).group())  # 관련 기사 갯수
            except:
                news_num = np.nan
            # 헤드라인 서브 페이지 요청 -> html로 파싱
            try:
                sub_req = requests.get(each_url, headers=self.headers)
                page = BeautifulSoup(sub_req.content, 'html.parser')
                # 헤드라인 서브 페이지에서 가장 첫번째 기사 제목 (편의상 넣음 꼭 필요한 것은 아님)
                topic = page.select('div > ul > li > dl > dt')[1].text.strip()
                # link 딕셔너리에 헤드라인 서브 페이지 링크, 관련 기사 건수, 첫번째 기사 제목
                link[idx] = {'head_link': each_url, '관련기사': news_num, 'topic': topic}
                # 헤드라인 서브 페이지 별로 언론사 리스트 추출
                np_list = page.select('span.writing')
            except IndexError:
                pass
            counter = {}
            try:
                for np_name in np_list:
                    # 동영상 기사를 취급하는 언론사 제외해야 될 코드
                    if np_name.text not in ['조선일보', '중앙일보', '경향신문', '한겨레', '한국일보', '동아일보']:
                        if np_name.text not in counter:
                            counter[np_name.text] = 0
                        counter[np_name.text] += 1
                    else:
                        pass
            except UnboundLocalError:
                pass
            total[idx] = counter  # key: index / value : 언론사 별 기사
        df1 = pd.DataFrame.from_dict(link, orient='index')  # 링크, 관련기사 수, topic 있는 dataframe
        df2 = pd.DataFrame.from_dict(total, orient='index')  # 각 언론사별 기사 갯수 있는 dataframe
        # merge
        df3 = pd.merge(df1.reset_index(), df2.reset_index(), on='index', how='outer').drop('index', axis=1)
        df3 = df3.sort_values(by='관련기사', ascending=False)
        df3 = df3.iloc[:3, :3]
        return df3
    
    def sport_contents(self,url):
        req = requests.get(url, headers=self.headers)
        html = req.text
        soup = BeautifulSoup(html, 'html.parser')
        try:
            time = soup.find(class_='info').text.split('최종수정')[1].split('기사원문')[0].strip()  # time
            time = time.replace('오전', 'AM').replace('오후', 'PM')
            time = datetime.strptime(time, '%Y.%m.%d. %p %I:%M')  # datetime 으로 파싱
            title = soup.find(class_='title').text
            text = soup.find(id='newsEndContents').text.split('기사제공')[0].strip('\n')
            text = re.sub('[^0-9a-zA-Zㄱ-ㅎ가-힣.,/()]', ' ', text)
            text = text[:2000]
            media = soup.select_one('#pressLogo > a > img')['alt']
            #url = url
            return time, media, title, text
        except AttributeError:
            pass
    def sport_news(self, url):

        time_li = [];
        time_list = [];
        media_li = [];
        title_li = [];
        document_li = [];
        topic_li = [];
        url_li = [];

        req = requests.get(url, headers=self.headers)
        html = req.text
        soup = BeautifulSoup(html, 'html.parser')
        contents = soup.find_all(class_='today_item')
        # url2 = soup.select('#content > div > div.today_section.type_no_da > ul > li:nth-child(1) > a')
        # for i in url2:
        # href = i.attrs['href']
        topic = soup.select_one('#content > div > div.today_section.type_no_da > h3').text.split(' ')[1]
        for content in contents[:4]:
            link = url + content.find(class_='link_today')['href'][1:]

            time, media_name, title, text = self.sport_contents(link)

            time_li.append(time)
            time_list.append(time)  # 순서정렬용
            media_li.append(media_name)  # media
            title_li.append(title)  # title
            document_li.append(text)
            topic_li.append(topic)
            url_li.append(link)
        df = pd.DataFrame(
            {'time_list': time_list, 'time': time_li, 'media': media_li, 'title': title_li, 'document': document_li,
             'topic': topic_li,'url' : url_li})
        df.sort_values(by='time_list', ascending=False, inplace=True)  # (시간 기준) 최신 순으로 정렬
        df.drop(['time_list'], axis=1, inplace=True)  # 필요없는 컬럼 삭제
        df.reset_index(drop=True, inplace=True)
        df = df.iloc[:3]
        return df

    def enter_news(self, url):
        driver.get(url)

        # 연예 뉴스 페이지
        star = driver.find_elements_by_xpath('//*[@id="left_cont"]/div[9]/div[2]/div/ul/li')

        url_list = []
        press_list = []
        title_list = []

        for thing in star:
            for i in range(len(star)):
                url_link = star[i].find_element_by_tag_name('a').get_attribute('href')
                press = star[i].find_element_by_class_name('press').text
                title = star[i].find_element_by_class_name('title').text

                url_list.append(url_link)
                press_list.append(press)
                title_list.append(title)
            break

            # ConnectionError방지
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"}
        content_list = []
        time_list = []
        topic_list = []
        req = requests.get(url, headers=headers)
        html = req.text
        soup = BeautifulSoup(html, 'html.parser')
        for i in url_list:
            original_html = requests.get(i, headers=headers)
            html = BeautifulSoup(original_html.text, "html.parser")

            # 뉴스 본문 가져오기
            content = html.select("#articeBody")
            content = ''.join(str(content))

            # 본문의 html태그제거
            pattern1 = '<[^>]*>'
            pattern2 = '\n'
            pattern3 = '\t'
            # final_df.document = final_df.document.apply(lambda x: re.sub('\n', '', x))
            # final_df.document = final_df.document.apply(lambda x: re.sub('\t', '', x))
            content = re.sub(pattern=pattern1, repl='', string=content)
            content = re.sub(pattern=pattern2, repl='', string=content)
            content = re.sub(pattern=pattern3, repl='', string=content)
            content = re.sub('[^0-9a-zA-Zㄱ-ㅎ가-힣.,/()]', ' ', content)
            content = content[:2000]
            # 기사 작성 시간 가져오기
            time = html.select_one('#content > div.end_ct > div > div.article_info > span > em').text
            time = time.replace('오전', 'AM').replace('오후', 'PM')
            time = datetime.strptime(time, '%Y.%m.%d. %p %I:%M')  # datetime 으로 파싱
            topic = soup.select_one('#header > div > div.snb_wrap > h1 > a.logo_enter').text[-2:]

            time_list.append(time)
            content_list.append(content)
            topic_list.append(topic)
        df = pd.DataFrame({"time": time_list, "media": press_list, "title": title_list, "document": content_list,
                           "topic": topic_list, 'url' : url_list})
        df.reset_index(drop=True, inplace=True)
        df = df.iloc[:3]
        return df

    def choice_url(self, url, topic):
        global selected_url
        df3 = self.main_page(url, topic)
        selected_url = df3['head_link']
        selected_url = selected_url.reset_index()
        selected_url.drop('index', axis=1, inplace=True)
        selected_url = selected_url['head_link']
        return selected_url
    
    def iserror(self, x):
        try:
            if x.split('\n')[3]:            
                return x.split('\n')[3].replace(',','')
        except IndexError:
            return 'error'
    
    
    # 선택된 헤드라인 페이지에서 신문사별로 링크 따오기
    def choice_link(self, url, topic):
        press_link = []
        press_name = []
        selected_link = self.choice_url(url, topic)
        for selected_url in selected_link:
            driver.get(selected_url)
            temp = driver.find_elements_by_css_selector('div > ul > li > dl ')
            mx = 0
            for i in range(len(temp)):
                try:
                    if temp[i].text.split('\n')[3]:
                        if eval(temp[i].text.split('\n')[3]).replace(',','') > mx:
                            mx = eval(temp[i].text.split('\n')[3]).replace(',','')
                            url = temp[i].find_element_by_tag_name('a').get_attribute('href')
                except:
                    if self.iserror(temp[i].text) == 'error':
                        if mx == 0:
                            url= temp[0].find_element_by_tag_name('a').get_attribute('href')
                    else:
                        continue
            link = url
            req = requests.get(selected_url, headers=self.headers)
            target = BeautifulSoup(req.content, 'html.parser')
            tag = target.select('div > ul > li > dl')
            press = tag[0].select_one('dd > span.writing').text
            # link = tag[0].select_one('dt > a')['href']
            press_link.append(link)
            press_name.append(press)
        print(press_link)  # 확인용
        total_links = {press_name[0]: press_link[0], press_name[1]: press_link[1], press_name[2]: press_link[2]}
        return total_links

    def naver_news_crawling(self, url):
        try:
            req = requests.get(url, headers=self.headers)
            html = req.text
            soup = BeautifulSoup(html, 'html.parser')
            title = soup.select_one('div.media_end_head_title > h2').text
            text = soup.find(id='dic_area').text
            text = re.sub('[^0-9a-zA-Zㄱ-ㅎ가-힣.,/()]', ' ', text)
            text = text[:2000]
            media_name = soup.select_one('div.media_end_head_top > a > img')['title']
            time = soup.select_one('span.media_end_head_info_datestamp_time').text
            time = time.replace('오전', 'AM').replace('오후', 'PM')
            time = datetime.strptime(time, '%Y.%m.%d. %p %I:%M')
            time = time.strftime('%Y-%m-%d %H:%M:%S')
            topic = soup.select_one('#_LNB > ul > li.Nlist_item._LNB_ITEM.is_active > a>span').text
            url = url
            return time, media_name, title, text, topic, url
        except AttributeError:
            pass

class Crawling(Topic):
    def __init__(self):
        super().__init__()

    def make_df(self, topic):
        pymysql.install_as_MySQLdb()
        if topic == '모두':
            tp = {'경제': 'https://news.naver.com/main/main.naver?mode=LSD&mid=shm&sid1=101',
                  '정치': 'https://news.naver.com/main/main.naver?mode=LSD&mid=shm&sid1=100',
                  '사회': "https://news.naver.com/main/main.naver?mode=LSD&mid=shm&sid1=102",
                  '생활/문화': 'https://news.naver.com/main/main.naver?mode=LSD&mid=shm&sid1=103',
                  '스포츠':  "https://sports.news.naver.com/",
                  '연예': "https://entertain.naver.com/home"}
            time = []
            media = []
            head = []
            body = []
            topic1 =[]
            url_li = []
            for a, b in tp.items():
                topic = a
                url = b
                if a == '스포츠':
                    df = super().sport_news(b)
                elif a == '연예':
                    df2 = super().enter_news(b)
                else:
                    final_links = super().choice_link(url, topic)

                    for name, link in final_links.items():
                        t, media_name, title, text, topic, url = self.naver_news_crawling(link)
                        time.append(t)
                        media.append(media_name)
                        head.append(title)
                        body.append(text)
                        topic1.append(topic)
                        url_li.append(url)

                final_df = pd.DataFrame(
                    {'time': time, 'media': media, 'title': head, 'document': body, 'topic': topic1, 'url' : url_li})
                final_df.document = final_df.document.apply(lambda x: re.sub('\n', '', x))
                final_df.document = final_df.document.apply(lambda x: re.sub('\t', '', x))
            final_df = pd.concat([final_df,df,df2],axis=0)
            final_df['topic'] = np.where(final_df['topic']=='생활/문화','문화',final_df['topic'])
            final_df.drop_duplicates(inplace=True)
            final_df = self.generate.input_generate(final_df, 'document')
        else:
            return print('"경제", "정치", "사회", "생활/문화" 중에 골라주세요')
            final_links = super().choice_link(url, topic)
        # time = []
        # media = []
        # head = []
        # body = []
        # zz = []
        # for name, link in final_links.items():
        #     t, media_name, title, text,topic1 = self.naver_news_crawling(link)
        #     time.append(t);
        #     media.append(media_name)
        #     head.append(title);
        #     body.append(text)
        #     # zz.append(topic1)
        # final_df = pd.DataFrame({'time': time, 'media': media, 'title': head, 'document': body})
        # final_df.document = final_df.document.apply(lambda x: re.sub('\n', '', x))
        # final_df.document = final_df.document.apply(lambda x: re.sub('\t', '', x))
        # final_df = self.generate.input_generate(final_df, 'document')
        return final_df


def tosql():
    from sqlalchemy import create_engine
    import sqlalchemy
    import pymysql
    pymysql.install_as_MySQLdb()
    import MySQLdb
    # crawl = Crawling()
    # final_df = crawl.make_df(topic)
    tt = str(datetime.today().strftime('%Y{}%m{}%d{}').format(*'년월일'))
    conn = pymysql.connect(host='??.ctsolbee3mtl.us-west-2.rds.amazonaws.com',
                           user='user',
                           password='password',
                           db='news_data',
                           charset='utf8')
    sql = '''
    CREATE TABLE {date} (
            time datetime,
            media text,
            topic text,
            title text,
            news text,
            abs_news text,
            url text
            );
            '''
    with conn:
        with conn.cursor() as cur:
            cur.execute(sql.format(date=tt))
            conn.commit()
        # for topic in ["경제", "정치", "사회", "생활/문화"]:
        #     for i in range(3):
        #         tt.append(topic)
        # final_df['topic'] = a
        # final_df.to_csv('./df_all.csv')

    # time = []
    # media = []
    # head = []
    # body = []
    # zz = []
    # for name, link in final_links.items():
    #     t, media_name, title, text,topic1 = self.naver_news_crawling(link)
    #     time.append(t);
    #     media.append(media_name)
    #     head.append(title);
    #     body.append(text)
    #     # zz.append(topic1)
    # final_df = pd.DataFrame({'time': time, 'media': media, 'title': head, 'document': body})
    # final_df.document = final_df.document.apply(lambda x: re.sub('\n', '', x))
    # final_df.document = final_df.document.apply(lambda x: re.sub('\t', '', x))
    # final_df = self.generate.input_generate(final_df, 'document')
    return tt


def return_abstract(topic):
    from sqlalchemy import create_engine
    import pymysql
    pymysql.install_as_MySQLdb()
    crawl = Crawling()
    final_df = crawl.make_df(topic)
    tt = str(datetime.today().strftime('%Y{}%m{}%d{}').format(*'년월일'))
    try:
        abstractive_text = "첫번째 기사입니다. " + final_df['generate_text'][0] \
                       + "두번째 기사입니다. " + final_df['generate_text'][1] \
                       + "세번째 기사입니다. " + final_df['generate_text'][2]

        engine = create_engine(
            "mysql+mysqldb://newssum:" + "qkrrkddls" + "@ssac.ctsolbee3mtl.us-west-2.rds.amazonaws.com/news_data",
            encoding='utf-8', echo=False)
        df = final_df[['time', 'media', 'topic', 'title', 'document', 'generate_text', 'url']]
        df.columns = ['time', 'media', 'topic', 'title', 'news', 'abs_news', 'url']
        df.to_sql(name='{table}'.format(table=tt), con=engine, if_exists='append', index=False)
        print(abstractive_text)
    except NameError or IndexError:
        pass
    return abstractive_text
def del_table():
    tb = datetime.today() - timedelta(weeks=1)
    del_tb = tb.strftime('%Y{}%m{}%d{}').format(*'년월일')
    conn = pymysql.connect(host='ssac.ctsolbee3mtl.us-west-2.rds.amazonaws.com',
                           user='newssum',
                           password='qkrrkddls',
                           db='news_data',
                           charset='utf8')
    sql = '''
    "DROP TABLE IF EXISTS {del_tb}
    '''
    
    with conn:
        with conn.cursor() as cur:
            cur.execute(sql.format(del_tb = del_tb))
            conn.commit()


schedule.every(1).day.do(tosql)

########## For test ################
schedule.every(1).hour.do(return_abstract, '모두')
#####################################
schedule.every(1).day.do(del_table)

while True:
    if __name__ == "__main__":
        schedule.run_pending()
        time.sleep(1)
