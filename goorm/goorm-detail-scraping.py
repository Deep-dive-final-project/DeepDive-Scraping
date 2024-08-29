import logging
import time
from logging import info, error
import requests
import json

from bs4 import BeautifulSoup

from common.const import USER_AGENT

logging.basicConfig(filename='goorm-detail-scraping.log', filemode='w', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


headers = {
    'User-Agent': USER_AGENT
}

with open('/Users/koo/PycharmProjects/DeepDive-Scraping/goorm/data/goorm_lecture.json', 'r') as read_file:
    data = json.load(read_file)
    info('Read file open successfully')

result = []
for i, line in enumerate(data):
    try:
        html = requests.get(line['lecture_url'], headers=headers).text
        soup = BeautifulSoup(html, 'html.parser')
        div_box = soup.select_one('._2h9cfz._18KWF0')
        if div_box is None:
            print(html)
            print('div box is empty')
            print(i+1)
            print(line)
        infos = div_box.select('._2yM5um')
        if len(infos) > 3:
            goals = '|'.join([infos[1].text] + list(map(lambda x: x.strip(), infos[2].text.split(','))))
            target_data = infos[-1].text.split('-')
            target = []
            for t in target_data:
                if t:
                    target.append(t.strip())
            target = '|'.join(target)
            line['target'] = target
        else:
            goals = infos[-1].text
            line['target'] = ''
        line['goals'] = goals
        line['pre_course'] = ''
        info(f'get {i+1} detail page')
        result.append(line)
    except Exception as e:
        error("An error occurred", exc_info=True)
        error("[Error occur]")
        error(f"{i+1} row - {line['title']}")

info('get page details successfully')
with open('./data/goorm_lecture_with_detail.json', 'w') as write_file:
    json.dump(result, write_file, ensure_ascii=False, indent=2)
info('save all page details successfully')