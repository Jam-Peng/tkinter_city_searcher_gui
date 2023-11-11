import requests
from bs4 import BeautifulSoup
import os

headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'}


def get_soup(url, post_data=None, get_data=None):
    soup = None
    try:
        if post_data is not None:
            res = requests.post(url, data=post_data, headers=headers)
        elif get_data is not None:
            res = requests.get(url, params=get_data, headers=headers)
        else:
            res = requests.get(url, headers=headers)

        res.encoding = 'utf-8'

        if res.status_code == requests.codes.ok:
            # print(res.status_code)
            soup = BeautifulSoup(res.text, 'lxml')
            return soup
        else:
            print('讀取網頁失敗', res.status_code)
    except Exception as err:
        print(err)
    # 失敗則回傳None
    return None


weather_icon_url = 'https://openweathermap.org/weather-conditions'

soup = get_soup(weather_icon_url)

trs = soup.find('table', class_="table table-bordered").find_all('tr')[1:]
datas = []
for tr in trs:
    data = {}
    for td in tr.find_all('td')[:2]:
        img_name = f"{td.text.split('.')[0].strip()}@2x"
        img_url = td.find('img').get('src')
        data[img_name] = img_url
    datas.append(data)

path = './icon'
if not os.path.exists(path):
    os.makedirs(path)
    for data in datas:
        for key, value in data.items():
            res = requests.get(value)
            with open(f'{path}/{key}.png', mode='wb') as f:
                f.write(res.content)
            print(f'{key} - 儲存完畢')
else:
    print('文件已存在')
