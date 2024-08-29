import logging

from common.const import USER_AGENT
from const.page import GOORM_URL
from const.goorm_const import CATEGORIES, PAGE_NUM, PAGE_DETAIL_PREFIX_URL, SAVED_CSV_PATH, IMG_SAVED_PATH, \
    SAVED_JSON_PATH
from formatter import get_page_format, get_saved_format
from bs4 import BeautifulSoup
import requests
import base64
import pandas as pd
from logging import info

logging.basicConfig(filename='goorm-scraping.log', filemode='w', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def preprocess_price(price: str):
    """
    1. 무료 -> 0
    2. 맨 앞에 ₩ 지우기
    3. 22,000 -> 22000 : , 지우기
    4. int형 변환
    """
    ret = '0' if price == '무료' else price[1:]
    return int(ret.replace(',', ''))


def save_img(img, id: int):
    saved_path = get_saved_format(IMG_SAVED_PATH, id=id)
    if img.startswith('data:image/png;base64'):
        header, encoded = img.split(",", 1)
        image_data = base64.b64decode(encoded)
        with open(saved_path, 'wb') as file:
            file.write(image_data)
    else:
        img = requests.get(card.select_one('._3PxZMG._1bYAeB')['data-src'])
        with open(saved_path, 'wb') as f:
            f.write(img.content)
    return saved_path


courses = []
row_id = 1
headers = {
    'User-Agent': USER_AGENT
}
for page_num in range(1, PAGE_NUM):
    page_url = get_page_format(GOORM_URL, category=CATEGORIES[0], page_num=page_num)
    html = requests.get(page_url, headers=headers).text
    soup = BeautifulSoup(html, 'html.parser')
    cards = soup.select('.card')
    for card in cards:
        img_source_path = card.select_one('._3PxZMG._1bYAeB')['data-src']
        img_path = save_img(img_source_path, row_id)

        try:
            course = {
                'id': row_id,
                'title': card.select_one('.card-title').text,
                'image_url': img_path,
                'instructor': card.select_one('._2q_4L7').text,
                'price': preprocess_price(card.select_one('._1zPZlD').text),
                'rating': float(card.select_one('._2KWt9f').text),
                'lecture_url': PAGE_DETAIL_PREFIX_URL + card.parent['href']
            }
            courses.append(course)
            info(f'{row_id} saved')
        except Exception:
            info('[Exception occur]')
            info(row_id)
            info(card.select_one('.card-title').text)

        row_id += 1

print('search complete')
df = pd.DataFrame(courses)

df.to_csv(SAVED_CSV_PATH, index=False, encoding='utf-8')
df.to_json(SAVED_JSON_PATH, index=False, orient='records', force_ascii=False)
print('save complete')
