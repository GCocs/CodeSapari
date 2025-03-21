from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

# Selenium WebDriver 설정
browser = webdriver.Chrome()

# IMDb Top 250 페이지 열기
browser.get("https://www.imdb.com/chart/top/?ref_=nv_mv_250")
time.sleep(2)  # 페이지 로드 대기

# 스크롤 다운 (필요시 추가)
body = browser.find_element(By.TAG_NAME, "body")
for _ in range(53):  # 스크롤 53번 내리기
    body.send_keys(Keys.PAGE_DOWN)
    time.sleep(0.2)

# 영화 데이터 추출 (BeautifulSoup 대신 Selenium 메서드 사용)
movies = browser.find_elements(By.CSS_SELECTOR, '#__next > main > div > div.ipc-page-content-container.ipc-page-content-container--center > section > div > div.ipc-page-grid.ipc-page-grid--bias-left > div > ul > li')

for movie in movies:
    try:
        # 영화 제목
        title_element = movie.find_element(By.CSS_SELECTOR, '.ipc-title__text')
        title = title_element.text if title_element else "N/A"
    except:
        title = "N/A"
    print(f"Title: {title}")

    try:
        # 영화 개봉 연도
        released_year_element = movie.find_element(By.CSS_SELECTOR, '.cli-title-metadata > span:nth-child(1)')
        released_year = released_year_element.text if released_year_element else "N/A"
    except:
        released_year = "N/A"
    print(f"Released Year: {released_year}")

    try:
        # 영화 상영 시간
        running_time_element = movie.find_element(By.CSS_SELECTOR, '.cli-title-metadata > span:nth-child(2)')
        running_time = running_time_element.text if running_time_element else "N/A"
    except:
        running_time = "N/A"
    print(f"Running Time: {running_time}")

    try:
        # 영상물 등급
        pg_level_element = movie.find_element(By.CSS_SELECTOR, '.cli-title-metadata > span:nth-child(3)')
        pg_level = pg_level_element.text if pg_level_element else "N/A"
    except:
        pg_level = "N/A"
    print(f"PG Level: {pg_level}")
    print("---------------")

# 브라우저 종료
browser.quit()