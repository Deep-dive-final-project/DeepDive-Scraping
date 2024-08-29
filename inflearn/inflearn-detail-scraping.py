import logging
import requests
import json
from bs4 import BeautifulSoup
from logging import info

logging.basicConfig(filename='inflearn-detail-scraping.log', filemode='w', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def open_file():
    with open('/data/inflearn_lecture.json', 'r') as file:
        data = json.load(file)
    info('Read file open successfully')
    return data


def get_inflearn_detail():
    def get_from_url(url: str):
        soup = BeautifulSoup(requests.get(url).text, 'html.parser')
        contents = get_from_div_list(soup)
        res = concat_string(contents)

        return res

    def get_from_div_list(soup):
        div_list = soup.find_all('div', {'class': 'css-15vm62s'})
        div_contents = [[] for _ in range(3)]

        for i, div in enumerate(div_list):
            get_from_div(i, div, div_contents)
        return div_contents

    def get_from_div(i, div, res):
        for li in div.find_all('p', {'class': 'mantine-Text-root'})[1:]:
            res[i].append(li.get_text())

    data = open_file()
    new_data = []
    for i, line in enumerate(data):
        res = get_from_url(line['lecture_url'])
        add_contents(line, res)
        new_data.append(line)
        info(f'get {i} detail page')
    info('get page details successfully')
    with open('/data/inflearn_lecture_with_detail.json', 'w') as write_file:
        json.dump(new_data, write_file, ensure_ascii=False, indent=2)
    info('save all page details successfully')

def concat_string(result):
    return list(map(lambda x: ', '.join(x), result))


def add_contents(line, res):
    line['goals'] = res[0]
    line['target'] = res[1]
    line['pre_coures'] = res[2]


if __name__ == '__main__':
    get_inflearn_detail()
