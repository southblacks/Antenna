import os
import threading
import time

import test
import queue
import requests
import re

proxies = {

}
###改成你自己的cookie 自行从https://njav.tv/zh上获取
cookie = '_ga=GA1.1.1577869706.1722549271; dom3ic8zudi28v8lr6fgphwffqoz0j6c=e60405cc-fb72-4754-97da-18eb1f6b64b3%3A2%3A1; _ga_VZGC2QQBZ8=GS1.1.1722668540.5.1.1722668549.0.0.0; __PPU_puid=7399296917985452147; UGVyc2lzdFN0b3JhZ2U=%7B%22CAIFRQ%22%3A%22ACgQOgAAAAAAAAAB%22%2C%22CAIFRT%22%3A%22ACgQOgAAAABmsFxQ%22%7D; locale=zh; session=F69uxAalO4tQB1pJkdkCUst8GSySw0gIWFmOtzVi; bnState_2031042={"impressions":3,"delayStarted":0}; x-token=7e7451de566c755867b6d8922ea5b549'
def Get_url(name):
    url = test.Return_url(test.Receive_url(test.Search_movie(name,proxies=proxies),proxies=proxies),proxies=proxies)
    return url


def Get_m3u8(url, path='./'):
    test.Receive_m3u8(url, path)


def response_content(url,proxies):
    headers = {
        'cookie': cookie,
        'origin': 'https://javplayer.me',
        'referer': 'https://javplayer.me/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'
    }

    ##修改代理
    try:
        response = requests.get(url=url, headers=headers, proxies=proxies)
    except Exception as e:
        try:
            response = requests.get(url=url, headers=headers, proxies=proxies, timeout=5)
        except Exception as e:
            pass
    return response.content


def Request_mp4(url_queue: queue, content_queue: queue, name_queue: queue):
    i = 0
    while True:
        if url_queue.empty():
            i = i + 1
            time.sleep(1)
            if i == 3:
                break
            else:
                continue
        url = url_queue.get(timeout=3)
        content = response_content(url,proxies)
        name = re.findall('/720/(.*?).jpg', url)[0]
        content_queue.put(content)
        name_queue.put(name)
    print("一个request结束")
    url_queue.task_done()


def download_mp4(content_queue: queue, name_queue: queue, path='./'):
    while True:
        try:
            content = content_queue.get(timeout=3)
            name = name_queue.get(timeout=3)
            with open(f'{path}/{name}.mp4', 'wb') as f:
                f.write(content)
            f.close()
            print(f"successfully download{name}.mp4")
            content_queue.task_done()
            name_queue.task_done()
        except queue.Empty:
            print('一个下载进程结束')
            break


if __name__ == '__main__':
    path = 'AV/'
    if not os.path.exists(path):
        os.mkdir(path)
    name = str(input("请输入番号："))
    name.lower()
    path = 'AV/' + name
    if not os.path.exists(path):
        os.mkdir(path)
    url = Get_url(name)
    print(url)
    test.Remove_file(path)
    if not os.path.exists(path):
        os.mkdir(path)
    Get_m3u8(url, path=path)

    url_queue = queue.Queue()
    content_queue = queue.Queue()
    name_queue = queue.Queue()

    req_thread = []
    dow_thread = []

    for i in range(7):
        t = threading.Thread(target=Request_mp4, args=(url_queue, content_queue, name_queue))
        req_thread.append(t)
        t.start()

    for i in range(5):
        t = threading.Thread(target=download_mp4, args=(content_queue, name_queue, f'{path}'))
        dow_thread.append(t)
        t.start()

    with open(f"{path}/v.txt", 'r') as out:
        while True:
            line = out.readline()
            if not line:
                print(line)
                break
            line = line.replace('\n', '')
            goal = url + '/' + line
            url_queue.put(goal)
    out.close()
    print('url获取结束')

    print('下载开始了')
    for i in dow_thread:
        i.join()


    print("下载完成")

    print('开始合并')

    with open(f'{path}/{name}.mp4', 'ab') as outfile:
        with open(f'{path}/v.txt', 'r') as f:
            while True:
                line = f.readline()
                if not line:
                    break
                line = line.replace('\n', '')
                strname = line[:-4]
                try:
                    with open(f'{path}/{strname}.mp4', 'rb') as infile:
                        outfile.write(infile.read())
                    infile.close()
                    os.remove(f'{path}/{strname}.mp4')
                except Exception:
                    pass
        f.close()
    outfile.close()

    filelist = os.listdir(path)
    filelist.remove(f'{name}.mp4')
    print(filelist)

    for file in filelist:
        os.remove(f'{path}/{file}')

    print('合并完成')
