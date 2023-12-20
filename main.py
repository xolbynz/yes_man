from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoAlertPresentException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
import random
import pytesseract
import time
import re
import os
import glob
from datetime import datetime
import cv2 
import numpy as np
import time
import pytesseract
import threading
wait_sec = 1
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
# 예매할 자리 수 (최대 2매)
wanted_seats_count = 2

date_list=["2023-12-23","2023-12-24","2023-12-25","2023-12-30","2023-12-31"]
options = Options()
options.add_argument('--disable-cache')  # 캐시 비활성화
options.add_argument('--incognito')     # 시크릿 모드에서 캐시 최소화

driver = webdriver.Chrome(options=options)

driver.get('https://www.yes24.com/Templates/FTLogin.aspx?ReturnURL=http://ticket.yes24.com/New/Perf/Detail/DetailSpecial.aspx&&ReturnParams=IdPerf=47823')
input("로그인 한 후에는 'y'를 입력하고 Enter 누르세요.")
# driver.get('http://ticket.yes24.com/Perf/47709')

close_button = WebDriverWait(driver, 30).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, "#mainForm > div.renew-wrap.rw2 > div > div.rn-05 > a.rn-bb03"))
)
#mainForm > div.renew-wrap.rw2 > div > div.rn-05 > a.rn-bb03
# 버튼 클릭
close_button.click()
WebDriverWait(driver, 30).until(lambda d: len(d.window_handles) > 1)
window_handles = driver.window_handles
driver.switch_to.window(window_handles[1])


wait = WebDriverWait(driver, 10)
date_element = wait.until(
    EC.visibility_of_element_located((By.XPATH, "//a[contains(@id, '2023-12-29')]"))
)


# 해당 날짜 클릭
date_element.click()

# 버튼을 찾아 클릭
button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, "#StepCtrlBtn01 > a > img"))
)
button.click()

time.sleep(0.6)
while True:
    
    try:
        select_element = driver.find_element(By.ID, "selFlashDateAll")

        # Select 객체 생성
        select_object = Select(select_element)

        time.sleep(0.1)
        # 원하는 값으로 선택 (예: "2023-12-24")
        select_data=date_list[int(round(random.uniform(0, 4)))]
        select_object.select_by_value(select_data)
        try:
            # 프레임이 로드되고 사용 가능할 때까지 기다린 후 자동으로 전환
            wait.until(EC.frame_to_be_available_and_switch_to_it((By.NAME, "ifrmSeatFrame")))
        except TimeoutException:
            # 위의 시도가 실패하면 메인 컨텐츠로 돌아가서 필요한 작업 수행
            continue
        # driver.switch_to.frame("ifrmSeatFrame")
        left_be=0
        top_be=0
        seat_elements = driver.find_elements(By.XPATH, "//div[@id='divSeatArray']/div[@title]")

        found_seat = False
        for i, seat in enumerate(seat_elements):
            if seat.get_attribute("title"):
                print(seat.get_attribute("title"), seat.get_attribute("style"))
                parts = seat.get_attribute("style").split(';')

                # LEFT와 TOP 값을 추출
                left = int(parts[0].split(':')[1].strip().split("px")[0])
                top = int(parts[1].split(':')[1].strip().split("px")[0])  
                if top_be==top and abs(left-left_be)<15:
                    seat_elements[i-1].click()
                    seat_elements[i].click()
                    found_seat = True  # 인접한 좌석을 찾음
                    # '좌석선택완료' 이미지 버튼 찾기
                    booking_button = driver.find_element(By.XPATH, "//img[@alt='좌석선택완료']")

                    # 버튼 클릭
                    booking_button.click()
                    break
                else:
                    left_be=left
                    top_be=top
        time.sleep(0.3)
        driver.switch_to.default_content()
        if found_seat:
            # 인접한 좌석을 찾았으므로, while 루프를 벗어나지 않고, 다음 단계로 이동
            print(select_data)
            break
        else:
            continue
    except Exception as e:
        driver.refresh()
        continue
#다시 돌아와 ~~
wait = WebDriverWait(driver, 10)
step_ctrl_btn_panel = wait.until(
    EC.visibility_of_element_located((By.ID, "StepCtrlBtn03"))
)
# 'StepCtrlBtn03' 내부의 '다음단계' 버튼 클릭
next_step_button = step_ctrl_btn_panel.find_element(By.XPATH, ".//a[.//img[@alt='다음단계']]")
next_step_button.click()
time.sleep(10)
step_ctrl_btn_panel = wait.until(
    EC.visibility_of_element_located((By.ID, "StepCtrlBtn04"))
)

# StepCtrlBtn04가 보이길 기다린 후, '다음단계' 버튼 클릭
step_ctrl_btn_panel = wait.until(EC.visibility_of_element_located((By.ID, "StepCtrlBtn04")))
next_step_button = step_ctrl_btn_panel.find_element(By.XPATH, ".//a[.//img[@alt='다음단계']]")
next_step_button.click()
time.sleep(1)



# '토스페이' 라디오 버튼이 보이길 기다린 후 클릭
toss_pay_radio_button = wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@name='rdoPays'][following-sibling::img[contains(@src, 'tosspay')]]")))
toss_pay_radio_button.click()


# 'cbxAllAgree' 체크박스가 보이길 기다린 후 클릭
checkbox = wait.until(EC.visibility_of_element_located((By.ID, "cbxAllAgree")))
checkbox.click()

step_ctrl_btn_panel = wait.until(
    EC.visibility_of_element_located((By.ID, "StepCtrlBtn05"))
)

# StepCtrlBtn05가 보이길 기다린 후, '결제하기' 버튼 클릭
step_ctrl_btn_panel = wait.until(EC.visibility_of_element_located((By.ID, "StepCtrlBtn05")))
next_step_button = step_ctrl_btn_panel.find_element(By.XPATH, ".//a[.//img[@alt='결제하기']]")
next_step_button.click()


time.sleep(10)
#새창이뜬다
WebDriverWait(driver, wait_sec).until(lambda d: len(d.window_handles) > 2)
window_handles = driver.window_handles
driver.switch_to.window(window_handles[2])

# 휴대폰 번호 입력 필드 찾기
phone_number_input = driver.find_element(By.CSS_SELECTOR, "#__next > div.css-a9cbnn > div > main > div.e1a4cznt0.css-djdvp0 > div.css-1j804c3 > div.form-group.css-aeb6cd.e1um61b20 > div > div > input")

# 휴대폰 번호 입력
phone_number_input.send_keys("")

birthday_input = driver.find_element(By.CSS_SELECTOR, "#__next > div.css-a9cbnn > div > main > div.e1a4cznt0.css-djdvp0 > div.css-1j804c3 > div.form-group.css-aeb6cd.e1m33tsd0 > div > div > input")
birthday_input.send_keys("")
print("222")