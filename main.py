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
import requests
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
wanted_seats_count = 1

date_list=["2023-12-30"]
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
WebDriverWait(driver, 10000).until(lambda d: len(d.window_handles) > 1)
window_handles = driver.window_handles
driver.switch_to.window(window_handles[1])



time.sleep(0.6)

while True:
    try:
        dialog =  WebDriverWait(driver, 0.2).until(EC.presence_of_element_located((By.CLASS_NAME, 'ui-dialog')))

        # 확인 버튼 클릭
        confirm_button = dialog.find_element(By.CLASS_NAME, 'ui-button-text')
        confirm_button.click()
    except TimeoutException:
        pass
    try:

        wait = WebDriverWait(driver, 0.5)
        date_element = wait.until(
            EC.visibility_of_element_located((By.XPATH, "//a[contains(@id, '2023-12-30')]"))
        )


        # 해당 날짜 클릭
        date_element.click()

        # 버튼을 찾아 클릭
        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#StepCtrlBtn01 > a > img"))
        )
        button.click()
    except TimeoutException:
        pass   
    try:
        try:
            dialog =  WebDriverWait(driver, 0.2).until(EC.presence_of_element_located((By.CLASS_NAME, 'ui-dialog')))

            # 확인 버튼 클릭
            confirm_button = dialog.find_element(By.CLASS_NAME, 'ui-button-text')
            confirm_button.click()
        except TimeoutException:
            pass
        select_element = driver.find_element(By.ID, "selFlashDateAll")

        # Select 객체 생성
        select_object = Select(select_element)


        # 원하는 값으로 선택 (예: "2023-12-24")
        # select_data=date_list[int(round(random.uniform(0, len(date_list)-1)))]
        select_data=date_list[0]
        select_object.select_by_value(select_data)
        
        
        select_element_time = Select(driver.find_element(By.ID, "selFlashTime"))
        select_element_time.select_by_visible_text('회차 선택')
        select_element_time.select_by_visible_text('[1회] 19시 00분')
        try:
            # 프레임이 로드되고 사용 가능할 때까지 기다린 후 자동으로 전환
            wait.until(EC.frame_to_be_available_and_switch_to_it((By.NAME, "ifrmSeatFrame")))
        except TimeoutException:
            # 위의 시도가 실패하면 메인 컨텐츠로 돌아가서 필요한 작업 수행
            pass   
        # driver.switch_to.frame("ifrmSeatFrame")
        left_be=0
        top_be=0
        seat_elements = driver.find_elements(By.XPATH, "//div[@id='divSeatArray']/div[@title]")

        found_seat = False
        for i, seat in enumerate(seat_elements):
            if '스탠딩A'in seat.get_attribute("title") or '스탠딩B'in seat.get_attribute("title"):
                print(seat.get_attribute("title"), seat.get_attribute("style"),end="\t")
                if wanted_seats_count>1:
                    parts = seat.get_attribute("style").split(';')

                    # LEFT와 TOP 값을 추출
                    left = int(parts[0].split(':')[1].strip().split("px")[0])
                    top = int(parts[1].split(':')[1].strip().split("px")[0])  
                    if abs(left-left_be)<50 and abs(left-left_be)<50:
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
                elif wanted_seats_count==1:
                    top = int(parts[1].split(':')[1].strip().split("px")[0])  
                    if top<200:
                        seat_elements[i].click()
                        # '좌석선택완료' 이미지 버튼 찾기
                        booking_button = driver.find_element(By.XPATH, "//img[@alt='좌석선택완료']")
                        found_seat = True  # 인접한 좌석을 찾음
                        # 버튼 클릭
                        booking_button.click()
                        break                    
        time.sleep(0.3)
        driver.switch_to.default_content()
        if found_seat:
            # 인접한 좌석을 찾았으므로, while 루프를 벗어나지 않고, 다음 단계로 이동
            print(select_data)
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



            mu_check=False

            try:
                mu_pay_radio_button = wait.until(EC.visibility_of_element_located((By.ID, "rdoPays22")))
                mu_pay_radio_button.click()
                # 'selBank' 드롭다운 요소를 찾습니다.
                select_element = driver.find_element(By.ID, "selBank")

                # 요소의 'disabled' 속성을 확인합니다.
                is_disabled = select_element.get_attribute("disabled")

                # 'disabled' 속성이 없거나 false일 때만 작업을 수행합니다.
                if not is_disabled or is_disabled == "false":
                    # Select 객체를 생성합니다.
                    select_object = Select(select_element)

                    # 특정 작업을 수행합니다 (예: 옵션 선택).
                    select_object.select_by_value("57")  # '농협중앙회' 선택
                    mu_check=True
                else:
                    # '토스페이' 라디오 버튼이 보이길 기다린 후 클릭
                    toss_pay_radio_button = wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@name='rdoPays'][following-sibling::img[contains(@src, 'tosspay')]]")))
                    toss_pay_radio_button.click()
            except Exception:
                toss_pay_radio_button = wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@name='rdoPays'][following-sibling::img[contains(@src, 'tosspay')]]")))
                toss_pay_radio_button.click()
                pass  
                
            while True:
                # '새로고침' 링크 찾기
                # refresh_link = wait.until(EC.visibility_of_element_located((By.XPATH, "//a[@href='javascript:initCaptcha();']")))

                # 링크 클릭
                # refresh_link.click()
                # 캡차 이미지 요소 찾기
                captcha_element = driver.find_element(By.ID, "captchaImg")

                # 캡차 이미지 요소의 스크린샷을 찍기
                captcha_element.screenshot("captcha.png")
                if os.path.exists("captcha.png"):
                    image = cv2.imread("captcha.png")

                    # 주황색의 BGR 범위 정의 (예시 범위, 필요에 따라 조절)
                    lower_orange = np.array([0, 40, 100])   # BGR
                    upper_orange = np.array([50, 150, 255]) # BGR

                    # 주황색 범위 내의 픽셀에 대한 마스크 생성
                    mask = cv2.inRange(image, lower_orange, upper_orange)

                    # 마스크 반전 (주황색이 아닌 부분을 흰색으로 만듦)
                    mask_inv = cv2.bitwise_not(mask)

                    # 흰색 배경 이미지 생성
                    white_background = np.full(image.shape, 255, dtype=np.uint8)

                    # 마스크를 흰색 배경에 적용 (주황색이 아닌 부분을 흰색으로)
                    white_background = cv2.bitwise_and(white_background, white_background, mask=mask_inv)

                    # 주황색 부분을 원본 이미지에서 추출
                    orange_part = cv2.bitwise_and(image, image, mask=mask)

                    # 흰색 배경과 주황색 부분을 결합
                    result = cv2.add(white_background, orange_part)

                    captcha_text = pytesseract.image_to_string(result)
                    print(captcha_text)
                    cv2.imwrite(captcha_text.split("\n")[0]+".jpg",result)
                    # 'captchaText' 입력 필드 찾기
                    captcha_input = driver.find_element(By.ID, "captchaText")

                    # 입력 필드에 텍스트 입력
                    captcha_input.send_keys(captcha_text)

                # 'cbxAllAgree' 체크박스가 보이길 기다린 후 클릭
                print("checkt checkbox  ",end="\t")
                time.sleep(1)
                checkbox = wait.until(EC.visibility_of_element_located((By.ID, "cbxAllAgree")))
                try:
                    if not cbx_all_agree.is_selected():
                        checkbox.click()
                except:
                    print("아 무슨에러야 ~  ",end="\t")
                    checkbox.click()
                    pass
                # wait.until(EC.element_to_be_selected((By.ID, "cbxAllAgree")))
                print("all 동의  클릭  ",end="\t")
                # 'cbxAllAgree' 체크박스 체크 여부 확인
                cbx_all_agree = driver.find_element(By.ID, "cbxAllAgree")
                is_cbx_all_agree_checked = cbx_all_agree.is_selected()

                # 'chkUserAgree' 체크박스 체크 여부 확인
                chk_user_agree = driver.find_element(By.ID, "chkUserAgree")
                is_chk_user_agree_checked = chk_user_agree.is_selected()

                # 'cbxCancelFeeAgree' 체크박스 체크 여부 확인
                cbx_cancel_fee_agree = driver.find_element(By.ID, "cbxCancelFeeAgree")
                is_cbx_cancel_fee_agree_checked = cbx_cancel_fee_agree.is_selected()

                # 'chkinfoAgree' 체크박스 체크 여부 확인
                chk_info_agree = driver.find_element(By.ID, "chkinfoAgree")
                is_chk_info_agree_checked = chk_info_agree.is_selected()

                # 체크 상태 출력
                print("모두 동의합니다:", is_cbx_all_agree_checked)
                print("개인정보 수집 및 이용 동의:", is_chk_user_agree_checked)
                print("취소수수료 및 취소기한 동의:", is_cbx_cancel_fee_agree_checked)
                print("제3자 정보제공 내용 동의:", is_chk_info_agree_checked)
                
                if not cbx_all_agree.is_selected():
                    continue
                step_ctrl_btn_panel = wait.until(
                    EC.visibility_of_element_located((By.ID, "StepCtrlBtn05"))
                )
                print("결제하기 클릭!!   ",end="\t")
                # StepCtrlBtn05가 보이길 기다린 후, '결제하기' 버튼 클릭
                step_ctrl_btn_panel = wait.until(EC.visibility_of_element_located((By.ID, "StepCtrlBtn05")))  
                next_step_button = wait.until(
                    EC.visibility_of_element_located((By.XPATH, ".//a[.//img[@alt='결제하기']]"))
                )
                next_step_button.click()

                print("결제하기 클릭!! 성공   ",end="\t")
                try:
                    # 경고창이 나타날 때까지 기다립니다.
                    WebDriverWait(driver, 10).until(EC.alert_is_present())

                    # 경고창에 대한 참조를 가져옵니다.
                    alert = driver.switch_to.alert

                    # 경고창의 텍스트를 가져옵니다.
                    alert_text = alert.text
                    print("경고창 텍스트:", alert_text)

                    # 필요한 경우 경고창을 닫습니다.
                    alert.accept()
                    time.sleep(0.5)
                    continue
                except NoAlertPresentException:
                    print("경고창이 나타나지 않았습니다.")
                    pass
                break

            if mu_check:
                dialog = WebDriverWait(driver, 1).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, "div.ui-dialog[style*='display: block']"))
                )

                # '확인' 버튼 찾기
                confirm_button = dialog.find_element(By.CSS_SELECTOR, "button.ui-button")

                # '확인' 버튼 클릭
                confirm_button.click()
                
                
                # StepCtrlBtn05가 보이길 기다린 후, '결제하기' 버튼 클릭
                step_ctrl_btn_panel = wait.until(EC.visibility_of_element_located((By.ID, "StepCtrlBtn05")))  
                # '이전단계' 버튼 찾기
                prev_step_button = driver.find_element(By.XPATH, "//div[@id='StepCtrlBtn05']//a[img[@alt='이전단계']]")

                # 버튼 클릭
                prev_step_button.click()
                
                step_ctrl_btn_panel = wait.until(EC.visibility_of_element_located((By.ID, "StepCtrlBtn04")))  
                # '이전단계' 버튼 찾기
                prev_step_button = driver.find_element(By.XPATH, "//div[@id='StepCtrlBtn04']//a[img[@alt='이전단계']]")

                # 버튼 클릭
                prev_step_button.click()

                step_ctrl_btn_panel = wait.until(EC.visibility_of_element_located((By.ID, "StepCtrlBtn03")))  
                # '이전단계' 버튼 찾기
                prev_step_button = driver.find_element(By.XPATH, "//div[@id='StepCtrlBtn03']//a[img[@alt='이전단계']]")

                # 버튼 클릭
                prev_step_button.click()
                print("태초마을",end="\t")
                continue
            else:
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
        else:
            continue
    except Exception as e:
        print("refresh man",end="\t")
        driver.refresh()
        time.sleep(1)

        continue
    
    

#다시 돌아와 ~~
# wait = WebDriverWait(driver, 10)
# step_ctrl_btn_panel = wait.until(
#     EC.visibility_of_element_located((By.ID, "StepCtrlBtn03"))
# )
# # 'StepCtrlBtn03' 내부의 '다음단계' 버튼 클릭
# next_step_button = step_ctrl_btn_panel.find_element(By.XPATH, ".//a[.//img[@alt='다음단계']]")
# next_step_button.click()
# time.sleep(10)
# step_ctrl_btn_panel = wait.until(
#     EC.visibility_of_element_located((By.ID, "StepCtrlBtn04"))
# )

# # StepCtrlBtn04가 보이길 기다린 후, '다음단계' 버튼 클릭
# step_ctrl_btn_panel = wait.until(EC.visibility_of_element_located((By.ID, "StepCtrlBtn04")))
# next_step_button = step_ctrl_btn_panel.find_element(By.XPATH, ".//a[.//img[@alt='다음단계']]")
# next_step_button.click()
# time.sleep(1)



# mu_check=False

# try:
#     mu_pay_radio_button = wait.until(EC.visibility_of_element_located((By.ID, "rdoPays22")))
#     mu_pay_radio_button.click()
#     # 'selBank' 드롭다운 요소를 찾습니다.
#     select_element = driver.find_element(By.ID, "selBank")

#     # 요소의 'disabled' 속성을 확인합니다.
#     is_disabled = select_element.get_attribute("disabled")

#     # 'disabled' 속성이 없거나 false일 때만 작업을 수행합니다.
#     if not is_disabled or is_disabled == "false":
#         # Select 객체를 생성합니다.
#         select_object = Select(select_element)

#         # 특정 작업을 수행합니다 (예: 옵션 선택).
#         select_object.select_by_value("57")  # '농협중앙회' 선택
#         mu_check=True
#     else:
#         # '토스페이' 라디오 버튼이 보이길 기다린 후 클릭
#         toss_pay_radio_button = wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@name='rdoPays'][following-sibling::img[contains(@src, 'tosspay')]]")))
#         toss_pay_radio_button.click()
# except Exception:
#     toss_pay_radio_button = wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@name='rdoPays'][following-sibling::img[contains(@src, 'tosspay')]]")))
#     toss_pay_radio_button.click()
#     pass  
    
# while True:
#     # '새로고침' 링크 찾기
#     refresh_link = wait.until(EC.visibility_of_element_located((By.XPATH, "//a[@href='javascript:initCaptcha();']")))

#     # 링크 클릭
#     refresh_link.click()
#     captcha_img = driver.find_element(By.ID, "captchaImg")
#     img_src = captcha_img.get_attribute("src")
#     response = requests.get(img_src)
#     if response.status_code == 200:
#         with open("captcha.jpg", "wb") as file:
#             file.write(response.content)
#         image = cv2.imread("captcha.jpg")

#         # 주황색의 BGR 범위 정의 (예시 범위, 필요에 따라 조절)
#         lower_orange = np.array([0, 40, 100])   # BGR
#         upper_orange = np.array([50, 150, 255]) # BGR

#         # 주황색 범위 내의 픽셀에 대한 마스크 생성
#         mask = cv2.inRange(image, lower_orange, upper_orange)

#         # 마스크 반전 (주황색이 아닌 부분을 흰색으로 만듦)
#         mask_inv = cv2.bitwise_not(mask)

#         # 흰색 배경 이미지 생성
#         white_background = np.full(image.shape, 255, dtype=np.uint8)

#         # 마스크를 흰색 배경에 적용 (주황색이 아닌 부분을 흰색으로)
#         white_background = cv2.bitwise_and(white_background, white_background, mask=mask_inv)

#         # 주황색 부분을 원본 이미지에서 추출
#         orange_part = cv2.bitwise_and(image, image, mask=mask)

#         # 흰색 배경과 주황색 부분을 결합
#         result = cv2.add(white_background, orange_part)

#         captcha_text = pytesseract.image_to_string(result)
#         print(captcha_text)
#         # 'captchaText' 입력 필드 찾기
#         captcha_input = driver.find_element(By.ID, "captchaText")

#         # 입력 필드에 텍스트 입력
#         captcha_input.send_keys(captcha_text)

#     # 'cbxAllAgree' 체크박스가 보이길 기다린 후 클릭

#     checkbox = wait.until(EC.visibility_of_element_located((By.ID, "cbxAllAgree")))
#     if not cbx_all_agree.is_selected():
#         checkbox.click()
#     # wait.until(EC.element_to_be_selected((By.ID, "cbxAllAgree")))

#     # 'cbxAllAgree' 체크박스 체크 여부 확인
#     cbx_all_agree = driver.find_element(By.ID, "cbxAllAgree")
#     is_cbx_all_agree_checked = cbx_all_agree.is_selected()

#     # 'chkUserAgree' 체크박스 체크 여부 확인
#     chk_user_agree = driver.find_element(By.ID, "chkUserAgree")
#     is_chk_user_agree_checked = chk_user_agree.is_selected()

#     # 'cbxCancelFeeAgree' 체크박스 체크 여부 확인
#     cbx_cancel_fee_agree = driver.find_element(By.ID, "cbxCancelFeeAgree")
#     is_cbx_cancel_fee_agree_checked = cbx_cancel_fee_agree.is_selected()

#     # 'chkinfoAgree' 체크박스 체크 여부 확인
#     chk_info_agree = driver.find_element(By.ID, "chkinfoAgree")
#     is_chk_info_agree_checked = chk_info_agree.is_selected()

#     # 체크 상태 출력
#     print("모두 동의합니다:", is_cbx_all_agree_checked)
#     print("개인정보 수집 및 이용 동의:", is_chk_user_agree_checked)
#     print("취소수수료 및 취소기한 동의:", is_cbx_cancel_fee_agree_checked)
#     print("제3자 정보제공 내용 동의:", is_chk_info_agree_checked)
    
#     if not cbx_all_agree.is_selected():
#         continue
#     step_ctrl_btn_panel = wait.until(
#         EC.visibility_of_element_located((By.ID, "StepCtrlBtn05"))
#     )

#     # StepCtrlBtn05가 보이길 기다린 후, '결제하기' 버튼 클릭
#     step_ctrl_btn_panel = wait.until(EC.visibility_of_element_located((By.ID, "StepCtrlBtn05")))  
#     next_step_button = wait.until(
#         EC.visibility_of_element_located((By.XPATH, ".//a[.//img[@alt='결제하기']]"))
#     )
#     next_step_button.click()


#     try:
#         # 경고창이 나타날 때까지 기다립니다.
#         WebDriverWait(driver, 10).until(EC.alert_is_present())

#         # 경고창에 대한 참조를 가져옵니다.
#         alert = driver.switch_to.alert

#         # 경고창의 텍스트를 가져옵니다.
#         alert_text = alert.text
#         print("경고창 텍스트:", alert_text)

#         # 필요한 경우 경고창을 닫습니다.
#         alert.accept()
#         time.sleep(0.5)
#     except NoAlertPresentException:
#         print("경고창이 나타나지 않았습니다.")
#         pass
#     break

# if mu_check:
#     dialog = WebDriverWait(driver, 1).until(
#         EC.visibility_of_element_located((By.CSS_SELECTOR, "div.ui-dialog[style*='display: block']"))
#     )

#     # '확인' 버튼 찾기
#     confirm_button = dialog.find_element(By.CSS_SELECTOR, "button.ui-button")

#     # '확인' 버튼 클릭
#     confirm_button.click()
    
    
#     # StepCtrlBtn05가 보이길 기다린 후, '결제하기' 버튼 클릭
#     step_ctrl_btn_panel = wait.until(EC.visibility_of_element_located((By.ID, "StepCtrlBtn05")))  
#     # '이전단계' 버튼 찾기
#     prev_step_button = driver.find_element(By.XPATH, "//div[@id='StepCtrlBtn05']//a[img[@alt='이전단계']]")

#     # 버튼 클릭
#     prev_step_button.click()
    
#     step_ctrl_btn_panel = wait.until(EC.visibility_of_element_located((By.ID, "StepCtrlBtn04")))  
#     # '이전단계' 버튼 찾기
#     prev_step_button = driver.find_element(By.XPATH, "//div[@id='StepCtrlBtn04']//a[img[@alt='이전단계']]")

#     # 버튼 클릭
#     prev_step_button.click()

#     step_ctrl_btn_panel = wait.until(EC.visibility_of_element_located((By.ID, "StepCtrlBtn03")))  
#     # '이전단계' 버튼 찾기
#     prev_step_button = driver.find_element(By.XPATH, "//div[@id='StepCtrlBtn03']//a[img[@alt='이전단계']]")

#     # 버튼 클릭
#     prev_step_button.click()
# else:
#     time.sleep(10)
#     #새창이뜬다
#     WebDriverWait(driver, wait_sec).until(lambda d: len(d.window_handles) > 2)
#     window_handles = driver.window_handles
#     driver.switch_to.window(window_handles[2])

#     # 휴대폰 번호 입력 필드 찾기
#     phone_number_input = driver.find_element(By.CSS_SELECTOR, "#__next > div.css-a9cbnn > div > main > div.e1a4cznt0.css-djdvp0 > div.css-1j804c3 > div.form-group.css-aeb6cd.e1um61b20 > div > div > input")

#     # 휴대폰 번호 입력
#     phone_number_input.send_keys("")

#     birthday_input = driver.find_element(By.CSS_SELECTOR, "#__next > div.css-a9cbnn > div > main > div.e1a4cznt0.css-djdvp0 > div.css-1j804c3 > div.form-group.css-aeb6cd.e1m33tsd0 > div > div > input")
#     birthday_input.send_keys("")
#     print("222")