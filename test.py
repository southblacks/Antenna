import os

import requests
import re


def Remove_file(path):
    if os.path.exists(path):
        file_list = os.listdir(path)
        for file_name in file_list:
            os.remove(path + '/' + file_name)
        file_list = os.listdir(path)
        if len(file_list) == 0:
            os.rmdir(path)
        else:
            print("删除目录出错啦")


def Return_url(url,proxies):
    # url = ('https://javplayer.me/e/2LG9JLW8?t=9702cdf205f0d2fb3ed67a09d496a7a7&poster=https%3A%2F%2Fcdn.njav.tv'
    #        '%2Fimages%2F0%2F10%2Fcjob-158%2Fthumb_h.jpg%3Ft%3D1722287601')
    headers = {
        'referer': 'https://njav.tv/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'
    }

    response = requests.get(url=url, headers=headers,proxies=proxies)
    html = response.text
    goal_str = re.findall('{&quot;stream&quot;:&quot;(.*?)/v.m3u8&quot;', html)[0]
    goal_url = goal_str.replace("\\", "")
    return goal_url


def Receive_url(id,proxies):
    url = f'https://njav.tv/zh/ajax/v/{id}/videos'
    headers = {
        'referer': 'https://njav.tv/zh/v/qbd-097',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'
    }
    response = requests.get(url=url, headers=headers,proxies=proxies)
    goal_url = response.json()['data']['watch'][0]['url']

    return goal_url


def Search_movie(name,proxies):
    name = name.lower()
    url = f'https://njav.tv/zh/v/{name}'
    headers = {
        'referer': 'https://njav.tv/zh',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'
    }
    response = requests.get(url=url, headers=headers,proxies=proxies)
    html = response.text
    id = re.findall("id: '(.*?)'", html)[0]
    return id




def Receive_m3u8(goal_url, path='./'):
    url = goal_url + '/v.m3u8'
    headers = {
        'origin': 'https://javplayer.me',
        'referer': 'https://javplayer.me/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'
    }
    response = requests.get(url=url, headers=headers)
    with open(f'{path}/v.m3u8', 'w') as f:
        f.write(response.text)
    f.close()

    with open(f'{path}/v.m3u8', 'r') as outf:
        with open(f'{path}/v.txt', 'w') as inf:
            while True:
                line = outf.readline()
                if not line:
                    break
                if line.find('.jpg') != -1:
                    inf.write(line)
        inf.close()
    outf.close()
    os.remove(f'{path}/v.m3u8')
