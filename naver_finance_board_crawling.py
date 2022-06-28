from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import requests
import time
import csv
import re

# 네이버 증권 -> 테마
url = 'https://finance.naver.com/sise/theme.naver?&page=1'
browser = webdriver.Chrome()
browser.maximize_window()
time.sleep(0.5)
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
    
    # 테마별 종목 이름 담는 리스트
    theme_stockname_li = []
    
    # 테마별 시가총액을 담는 리스트
    theme_stockcap_li = []
    
    # 시총 1위 기업 담는 리스트
    tmp_stock = ['', '', '', '', '', '', '', '', '', '', 0, '']
    for i in range(1,8):
        browser.find_element(By.LINK_TEXT, "{}".format(i)).click()
        time.sleep(1)
        try:
            elem = browser.find_element(By.LINK_TEXT, theme)
            if elem.text == theme:
                elem.click()
                time.sleep(1)            
        except:
            continue
    
        # 테마 클릭 후 종목이 나열되어 있는 메인화면 url
        cnt_url = browser.current_url
       
        # 시가총액 기준 클릭
        browser.find_element(By.ID, "option4").click()
        
        # 적용하기 버튼 클릭
        browser.find_element(By.XPATH,'//*[@id="contentarea"]/div[3]/form/div/div/div/a[1]/img').click()
        time.sleep(1)
        
        html = browser.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        stock_rows = soup.find("table", attrs = {"class" : "type_5"}).find("tbody").find_all("tr")
        
        # 테마 홈페이지 접속 후 시총 상위 1위 기업 추출
        for row in stock_rows:
            stock_columns = row.find_all("td")
            if len(stock_columns) <= 1:
                continue
            stock = [column.get_text().strip() for column in stock_columns]
            # print(stock[10]) # 시가총액
            
            stock[10] = re.sub(r'[^0-9]', '', stock[10])
            
            theme_stockname_li.append(stock[0])
            theme_stockcap_li.append(stock[10])
            
            if int(stock[10]) >= int(tmp_stock[10]):
                tmp_stock = stock
        
        theme_stockcap_li = list(map(int, theme_stockcap_li))
        theme_stockcap_li = {(i + 1): theme_stockcap_li[i] for i in range(0, len(theme_stockcap_li))}
        theme_stockcap_li = dict(sorted(theme_stockcap_li.items(), key=lambda x: x[1], reverse=True))
        
        # 테마 중 시가총액 상위 rank_n 개
        theme_top = list(theme_stockcap_li.keys())[:rank_n]

        # 주식 토론실 경로
        # 테마별 시가총액 상위 rank_n개
        for i in theme_top:
            
            # 주식 토론방 경로
            board_xpath = '//*[@id="contentarea"]/div[4]/table/tbody/tr[{}]/td[12]/a/img'.format(i)
            # 주식 이름 경로
            name_xpath = '//*[@id="contentarea"]/div[4]/table/tbody/tr[{}]/td[1]/div/a'.format(i)
            
            # 종목명 (파일명)
            stockname = browser.find_element(By.XPATH, name_xpath).text
            # print(stockname.text)
                
            # filename = "1_종목명_종토방 데이터.csv"
            filename = str(theme_top.index(i)+1) + "_" + stockname + "_종토방 데이터" + ".csv"
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

            browser.get(cnt_url)  

# 테마 입력
theme = '제지'

# theme 별 시가총액 상위 5개 1 ~ pages, endyear년도
board_crawling(theme, rank_n = 5, pages = 2, endyear = 2022)

'''
# 변수 설명
theme : 테마 명
rank_n : 상위 n개
pages : 1 ~ n 페이지
endyear : 20xx 년도 까지 조회
'''

