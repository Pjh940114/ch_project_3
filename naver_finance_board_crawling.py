from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import requests
import time
import csv
from bs4 import BeautifulSoup

# 네이버 증권 -> 테마
url = 'https://finance.naver.com/sise/theme.naver'
browser = webdriver.Chrome()
browser.get(url)

# 초기화
def init(theme):
    global url
    browser.get(url)
    elem = browser.find_element(By.LINK_TEXT, theme)
    elem.click()
    time.sleep(1)

# 크롤링 및 파일 저장
def board_crawling(theme, rank_n, pages, endyear):
    
    elem = browser.find_element(By.LINK_TEXT, theme)
    elem.click()
    time.sleep(1)

    # 주식 토론실 경로

    # 테마별 상위 range개
    for i in range(1,rank_n + 1):
        
        # 주식 토론방 경로
        board_xpath = '//*[@id="contentarea"]/div[4]/table/tbody/tr[{}]/td[11]/a/img'.format(i)
        # 주식 이름 경로
        name_xpath = '//*[@id="contentarea"]/div[4]/table/tbody/tr[{}]/td[1]/div/a'.format(i)
        
        # 종목명 (파일명)
        stockname = browser.find_element(By.XPATH, name_xpath).text
        # print(stockname.text)
            
        filename = stockname + "_종토방 데이터" + ".csv"
        f = open(filename, "w",  encoding="utf-8-sig", newline="")
        writer = csv.writer(f)

        # 파일 저장 header
        title = "날짜	제목	글쓴이	조회	공감	비공감".split("\t")
        writer.writerow(title)
        
    # 주식 토론실 클릭
        item_board = browser.find_element(By.XPATH, board_xpath)
        item_board.click()
        time.sleep(1)
        
        # range 까지의 범위 페이지 크롤링
        for page in range(1, pages + 1):
        
            board_pages = browser.find_element(By.LINK_TEXT, "{}".format(page))
            board_pages.click()
            time.sleep(1)
                
            html = browser.page_source
            soup = BeautifulSoup(html, 'html.parser')
            
            data_rows = soup.find("table", attrs = {"class" : "type2"}).find("tbody").find_all("tr")

            for row in data_rows:
                columns = row.find_all("td")
                if len(columns) <=1:
                    continue
                data = [column.get_text().strip() for column in columns]
                # print(data)
                
                if data[0][:4] == str(endyear - 1): # endyear 는 년도를 설정해서 일정 년도가 되면 크롤링을 멈춤
                    break
                
                writer.writerow(data)

            # 페이지가 10이 될 경우 다음을 누르고 크롤링 계속 이어감
            if page % 10 == 0:
                board_pages = browser.find_element(By.LINK_TEXT, "다음")
                board_pages.click()

        init(theme)  

# 테마 입력
theme = '탈모 치료 관련주'

# '탈모 치료 관련주' 상위 5개 1 ~ 20페이지 2022년도
board_crawling(theme, rank_n = 2, pages = 2, endyear = 2022)

'''
# 변수 설명
theme : 테마 명
rank_n : 상위 n개
pages : 1 ~ n 페이지
endyear : 20xx 년도 까지 조회
'''

