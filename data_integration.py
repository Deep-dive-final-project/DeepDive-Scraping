import json

# def save_to_json():
#     with open('/Users/koo/PycharmProjects/DeepDive-Scraping/inflearn/data/inflearn_lecture_with_detail2.json', 'r') as file:
#         data1 = json.load(file)
#
#     for item in data1:
#         item['platform'] = 'inflearn'
#
#     with open('/Users/koo/PycharmProjects/DeepDive-Scraping/goorm/data/goorm_lecture_with_detail.json', 'r') as file:
#         data2 = json.load(file)
#
#     for item in data2:
#         item['platform'] = 'goorm'
#
#     combined_data = data1 + data2
#
#     for index, item in enumerate(combined_data):
#         item['id'] = index + 1
#
#     with open('/Users/koo/PycharmProjects/DeepDive-Scraping/data/integrated.json', 'w') as file:
#         json.dump(combined_data, file, ensure_ascii=False, indent=2)


import pandas as pd

data = pd.read_json('/Users/koo/PycharmProjects/DeepDive-Scraping/data/integrated.json')
print(data.iloc[0])
# with open('/Users/koo/PycharmProjects/DeepDive-Scraping/data/integrated.json', 'r') as read_file:
#     data = json.load(read_file)

