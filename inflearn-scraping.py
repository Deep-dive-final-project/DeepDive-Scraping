from typing import Any

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from const.xpaths import *
from const.page import *
from const.inflearn_const import TIME_OUT_CNT, INITIAL_WAITING_TIME, PAGE_WAITING_TIME, MAX_PAGE_NUM
from formatter import *
import pandas as pd
import time
import logging
from logging import info

logging.basicConfig(filename='app.log', filemode='w', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

driver = webdriver.Chrome()


def get_inflearn_lecture():
    """
    전체 페이지를 순회한다.
    각각의 페이지를 조회 및 저장한다.

    :return: None
    """
    result_df = pd.DataFrame()
    page_number = 1
    lecture_id = 1
    while page_number < MAX_PAGE_NUM:
        info(f'page number : {page_number}')
        page_courses, lecture_id = process_page(page_number, lecture_id)
        result_df = concat_page(page_courses, result_df)
        page_number += 1
    save_result(result_df)
    driver.quit()


def process_page(page_number: int, start_lecture_id: int) -> tuple[list[dict], int]:
    """
    페이지 하나를 처리한다

    :param page_number: 처리할 페이지 번호
    :param start_lecture_id: 행값의 시작 id
    :return: 페이지에 있는 강의들, 마지막 행값 id
    """
    page_courses = page_init(page_number)
    last_lecture_id = start_lecture_id
    for section_id in range(1, 3):
        last_lecture_id = process_section(section_id, page_courses, last_lecture_id)
    return page_courses, last_lecture_id


def page_init(page_number: int) -> list[Any]:
    """
    새로운 페이지 처리가 시작될 때 초기화 작업을 수행한다
    :param page_number:
    :param start_id:
    :return:
    """
    courses = []  # lecture를 저장할 list 생성
    driver.get(get_page_format(INFLEARN_URL, page_number=page_number))  # 새로운 page로 이동
    time.sleep(INITIAL_WAITING_TIME + PAGE_WAITING_TIME)  # 이동 중 delay

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    return courses


def process_section(section_id: int, page_courses: list[dict], lecture_id: int):
    """
    page의 section을 처리한다

    :param section_id: 처리할 section id
    :param page_courses: 처리한 lecture를 저장할 list
    :param lecture_id: lecture 시작 id
    :return: lecture를 저장한 list를 반환
    """
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, get_xpath(LI_LIST_XPATH, section_id=section_id)))
    )

    li_elements = driver.find_elements(By.XPATH, get_xpath(LI_ITEM_XPATH, section_id=section_id))
    for item_id, li in enumerate(li_elements):
        get_item(li, section_id, item_id, page_courses, lecture_id)
        lecture_id += 1
    time.sleep(1)
    return lecture_id


def concat_page(courses: list[dict], df: pd.DataFrame) -> pd.DataFrame:
    """
    조회한 lecture list를 dataframe에 합친다

    :param courses: 합칠 lecture list
    :param df: 합쳐질 lecture dataframe
    :return: 합쳐진 lecture dataframe을 반환
    """
    global PAGE_WAITING_TIME
    PAGE_WAITING_TIME = 0.5  # 늘어난 대기 시간을 초기화
    ndf = pd.DataFrame(courses)
    concat_df = pd.concat([df, ndf], ignore_index=True)
    return concat_df


def get_item(li, section_id: int, item_id: int, page_courses: list[dict], lecture_id: int) -> list[dict]:
    """
    하나의 lecture를 처리하여 page_courses list에 추가한다
    :param li: 처리할 li tag
    :param section_id: li tag가 속하는 section id
    :param item_id: li의 item id
    :param page_courses: 결과를 저장할 list
    :param lecture_id: lecture id
    :return:
    """

    def append_course(row_id, title, img_url, instructor, price, rating, lecture_url):
        course_info = {
            'id': row_id,
            'title': title,
            'image_url': img_url,
            'instructor': instructor,
            'price': price,
            'rating': rating,
            'lecture_url': lecture_url
        }
        page_courses.append(course_info)

    def item_exception_handling():
        global PAGE_WAITING_TIME, TIME_OUT_CNT, INITIAL_WAITING_TIME
        PAGE_WAITING_TIME += 1
        TIME_OUT_CNT += 1
        if TIME_OUT_CNT > 3:
            INITIAL_WAITING_TIME += 1
            TIME_OUT_CNT = 0

    def get_title():
        return li.find_element(By.XPATH, get_xpath(TITLE_XPATH, section_id=section_id, item_id=item_id + 1)).text

    def get_img_url():
        img_tag = li.find_element(By.TAG_NAME, 'img')
        return img_tag.get_attribute('src')

    def get_instructor():
        return li.find_element(By.XPATH, get_xpath(INSTRUCTOR_XPATH, section_id=section_id, item_id=item_id + 1)).text

    def get_price():
        prices = li.find_elements(By.XPATH, get_xpath(PRICE_XPATH, section_id=section_id, item_id=item_id + 1))
        price = '0'
        if len(prices) > 1:
            price = prices[-1].text
        if len(prices) == 1 and prices[0] != '무료':
            price = prices[0].text
        return 0 if price in ('무료', '') else int(''.join(price.rstrip('원').split(',')))

    def get_rating():
        try:
            rating = li.find_element(By.XPATH, get_xpath(RATING_XPATH, section_id=section_id, item_id=item_id + 1)).text
        except Exception:
            rating = 0
        return float(rating)

    try:
        a_tag = li.find_element(By.TAG_NAME, 'a')
        lecture_url = a_tag.get_attribute('href')
        instructor = get_instructor()
        img_url = get_img_url()
        title = get_title()
        price = get_price()
        rating = get_rating()
        append_course(lecture_id, title, img_url, instructor, price, rating, lecture_url)

    except Exception as e:
        info('[Error occur] - {section_id}:{item_id}')
        info(e)
        item_exception_handling()


def save_result(df: pd.DataFrame):
    df.to_csv('db/inflearn_lecture.csv', index=False, encoding='utf-8')
    df.to_json('db/inflearn_lecture.json', index=False, orient='records', force_ascii=False)
    info(f'total dataframe length : {len(df)}')
    info("save successfully")


if __name__ == '__main__':
    get_inflearn_lecture()
