import random
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

import time

from bs4 import BeautifulSoup
from pymongo import MongoClient           # pymongo를 임포트 하기(패키지 인스톨 먼저 해야겠죠?)

# 아래 uri를 복사해둔 uri로 수정하기
uri = "mongodb+srv://ysh062100:1234@cluster0.etvh1.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri, 27017)  # MongoDB는 27017 포트로 돌아갑니다.
db = client.dbjungle                      # 'dbjungle'라는 이름의 db를 만듭니다.

def insert_all():
    count = 0

    # Selenium WebDriver 설정
    data = webdriver.Chrome()

    # URL을 읽어서 HTML를 받아오고,
    data.get('https://www.imdb.com/chart/top/?ref_=nv_mv_250')
    time.sleep(2)  # 페이지 로드 대기

    # 스크롤 다운 (필요시 추가)
    body = data.find_element(By.TAG_NAME, "body")


    # select를 이용해서, li들을 불러오기
    movies = data.find_elements(By.CSS_SELECTOR, '#__next > main > div > div.ipc-page-content-container.ipc-page-content-container--center > section > div > div.ipc-page-grid.ipc-page-grid--bias-left > div > ul > li')
    print(len(movies))
    # movies (li들) 의 반복문을 돌리기
    for movie in movies:
        # 영화 타이틀 정보를 추출한다.
        tag_element = movie.find_element(By.CSS_SELECTOR, '.ipc-title-link-wrapper > h3')
        if not tag_element:
            continue
        title = tag_element.text.split(". ", 1)[1]
        
        # 영화 정보 URL을 추출한다.
        info_url_tag_element = movie.find_element(By.CSS_SELECTOR, '.ipc-title-link-wrapper')
        info_url = info_url_tag_element.get_attribute("href")
        
        # 영화 포스터 이미지 URL을 추출한다.
        poster_url_tag_element = movie.find_element(By.CSS_SELECTOR, '.ipc-image')
        poster_url = poster_url_tag_element.get_attribute("src")
        print(poster_url)

        # 상영 연도 가져온다.
        released_year = movie.find_element(By.CSS_SELECTOR,'.cli-title-metadata-item:nth-child(1)').text
        # 상영 연도를 정수로 변환한다.
        released_year = int(released_year)

        # 영화 상영시간 가져오기
        running_time = movie.find_element(By.CSS_SELECTOR,'.cli-title-metadata-item:nth-child(2)').text
        # 영화 상영시간 분으로 변환하기
        # 1. running_time에서 'h'와 'm'을 제거
        running_time = running_time.replace("h", "").replace("m", "")  # "2 55"로 변경
        # 2. 공백으로 나누기
        time_parts = running_time.strip().split(" ")  # "2"와 "55"로 분리
        # 3. 문자열을 숫자로 변환
        
        if len(time_parts) == 2:  # "2h 30m" 형태
            hours = int(time_parts[0])
            minutes = int(time_parts[1])
        elif 'h' in running_time:  # "2h" 형태
            hours = int(time_parts[0])
            minutes = 0

        # 4. 시간과 분을 계산
        running_time_minutes = hours * 60 + minutes

        # 영상물 등급 가져오기
        try:
            pg_level = movie.find_element(By.CSS_SELECTOR, '.cli-title-metadata-item:nth-child(3)').text
        except NoSuchElementException:
            pg_level = "N/A"

        # 좋아요 수를 임의로 만든다
        likes = random.randrange(0, 100)

        # DB에 존재하지 않는 영화인 경우만 추가한다.
        found = list(db.movies.find({'title': title}))
        if found:
            continue

        if(count<25) : temp = False
        else : temp = True

        doc = {
            'title': title,
            'running_time': running_time_minutes,
            'released_year': released_year,
            'poster_url': poster_url,
            'info_url': info_url,
            'pg_level': pg_level,
            'likes': likes,
            'temp': temp,
        }
        db.movies.insert_one(doc)
        print('완료: ', title, running_time_minutes, released_year, poster_url, info_url, pg_level, likes, temp)
        count = count + 1


if __name__ == '__main__':
    # 기존의 movies 콜렉션을 삭제하기
    db.movies.drop()

    # 영화 사이트를 scraping 해서 db 에 채우기
    insert_all()