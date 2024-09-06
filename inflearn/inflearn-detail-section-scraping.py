import json
import requests
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
}

with open('./data/inflearn_lecture_with_detail2.json') as file:
    data = json.load(file)

section_datas = []
entire_data_length = len(data)

section_id = 1
percent = 0

for d in data:
    url = d['lecture_url']
    page = requests.get(url, headers=headers).text
    soup = BeautifulSoup(page, 'html.parser')
    curriculum_body = soup.select_one('.mantine-Group-root.mantine-pr1x6c').next_sibling
    sections = curriculum_body.select('.mantine-Accordion-item.mantine-18e13oy')  # 섹션들

    for section in sections:
        line = {}
        section_name = section.select_one('.mantine-Text-root.mantine-5jtosh').text
        containers = section.select_one('.mantine-1avyp1d')
        sub_sections = containers.select('.mantine-Group-root.mantine-1rraes2')
        sub_section_list = []
        for ss in sub_sections:
            a_tag = ss.select_one('.mantine-Text-root.css-1081t4c.mantine-ltpwr3')
            p_tag = None
            if not a_tag:
                p_tag = ss.select_one('.mantine-Text-root.mantine-tsx071')
            sub_section_list.append(a_tag.text if a_tag else p_tag.text)
        line['section_id'] = section_id
        line['name'] = section_name
        line['sub_section'] = '|'.join(sub_section_list)
        line['lecture_id'] = d['id']
        section_datas.append(line)
        section_id += 1
        prev_percent = percent
        percent = int(section_id * 100 / entire_data_length)
        if percent > prev_percent:
            print(f'[{percent}/100] : ' + '=' * percent)
    with open('/Users/koo/PycharmProjects/DeepDive-Scraping/inflearn/data/inflearn_lecture_sections.json', 'w') as write_file:
        json.dump(section_datas, write_file, ensure_ascii=False, indent=2)

