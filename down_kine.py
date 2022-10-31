import json
import os
import re

import requests
from requests.adapters import HTTPAdapter
####
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

# lines = []
# keyword_txt = '0_class_cn_0605'
# keyword_txt = 'coco_en'
# with open(keyword_txt + '.txt', 'r', encoding='utf-8') as f:
#     for id_cap in f.readlines():
#         cap = id_cap.split('\t')[-1]
#         lines.append(cap)
# random.shuffle(lines)
# keyword_json = 'labels.json'
# global lines
# lines=[]
# with open(keyword_json,'r',encoding='utf-8')as f:
#     dic1 = json.load(f)
#     for dataset_name,class_list in dic1.items():
#         lines.extend(class_list)
# random.shuffle(lines)

# #save txt
# per_txt_num = len(lines)//5+1
# for index in range(5):
#     with open('labels_part{}.txt'.format(index),'w',encoding='utf-8')as f1:
#         for cell in lines[index*per_txt_num:(index+1)*per_txt_num]:
#             f1.write('{}\n'.format(cell))

# proxies = {'http': 'http://127.0.0.1:1080', 'https': 'http://127.0.0.1:1080', }
# proxies = {'http': 'http://127.0.0.1:10809', 'https': 'http://127.0.0.1:10809', }

lines = []
# with open('labels_part3.txt', 'r', encoding='utf-8') as f:
#     for cell in f.readlines():
#         lines.append(cell.split('\n')[0].replace('/','_'))

import argparse
parse = argparse.ArgumentParser()
parse.add_argument('--port',help='7890/1080/10809')
parse.add_argument('--part',help='1/2/3/4')
parse.add_argument('--pro',type=int,help='num of process')
args = parse.parse_args()
part_index='part{}'.format(args.part)
http_pxy ='http://127.0.0.1:{}'.format(args.port)
proxies = {'http': http_pxy, 'https': http_pxy, }

with open('./kinetics400_600_700_calss.txt', 'r') as f:
    for cell in f.readlines():
        try:
            if '\n' in cell:
                cell = cell.replace('\n', '')
            lines.append(cell)
        except:
            pass




pro = args.pro
# print(args.pro)
nums = len(lines)
per_pro_nums = int(nums/pro) + 1

keywords_url_json_folder_path = './keywords_kinetics_youtube_url_json_folder'
if not os.path.exists(keywords_url_json_folder_path):
    os.mkdir(keywords_url_json_folder_path)


# keyword_txt = 'imagenet21k_zb'
# #n03228533	douche	douche_bag
# with open(keyword_txt + '.txt', 'r', encoding='utf-8') as f:
#     for id_word_word in f.readlines():
#         cap = id_word_word.split('\t')[1:]
#         lines.extend(cap)

###

def roll_window_to_bottom(browser, index, keyword, stop_length=None, step_length=6000, json_path='./'):
    # 无更多结果
    '<yt-formatted-string id="message" class="style-scope ytd-message-renderer">无更多结果</yt-formatted-string>'
    # no_result = browser.find_elements(By.CSS_SELECTOR,'yt-formatted-string[class^="style-scope ytd-message-renderer"]')
    url_set = []  # {kwyword:[https://1,https://2]}


    repeat_times=0
    temp_height = 0

    max_times = 20 #10
    browser.execute_script("window.scrollBy(0,{})".format(100000))
    while repeat_times < max_times :  # 循环向下滑动
        if stop_length:
            if stop_length - step_length < 0:
                browser.execute_script("window.scrollBy(0,{})".format(stop_length))
                break
            stop_length -= step_length

        # time.sleep(0.5 + random.random())

        browser.execute_script("window.scrollBy(0,{})".format(step_length))
        '''
        vis_height = browser.execute_script(
            "return document.documentElement.clientHeight ;")#可视部分高度(就是720/1800等不变的高度-由缩放决定)
        all_height = browser.execute_script(
            "return document.documentElement.scrollHeight ;")  # 截至到目前加载的所有可以看到的高度，比已经滑动的范围大一点
        print('all_height {}'.format(all_height))
        browser.execute_script("window.scrollBy(0,1000000)")
        '''
        import time
        time.sleep(0.1)
        # browser.implicitly_wait(10)  ###千万要加上，不然后面elements加载延迟，就无法打印
        # 获取当前滚动条距离顶部的距离,所有滑动过的距离
        check_height = browser.execute_script(
            "return document.documentElement.scrollTop || window.pageYOffset || document.body.scrollTop;")

        load_height = browser.execute_script(
            "return document.documentElement.scrollHeight ;")  # 截至到目前加载的所有可以看到的高度，比已经滑动的范围大一点

        # if load_height == check_height:#貌似就算到了最低端，还是不相等
        #     break
        step_length = load_height - check_height
        if temp_height==step_length:
            repeat_times+=1  #重复次数加1
            print('repeat_times:{}'.format(repeat_times))
        else:
            repeat_times=0  #复位
        temp_height=step_length
        # print('load_height:{},step_length:{}'.format(load_height, step_length))

        if(repeat_times>=max_times):
            num_page_sentences = browser.find_elements(By.CSS_SELECTOR,
                                                       'a[href^="/shorts"]')
            # sentences_len = len(num_page_sentences)
            # if not (sentences_len > temp_sentence_len):
            #     break
            # temp_sentence_len = sentences_len

            for num_page_sentence in num_page_sentences:
                num_page_sentence = num_page_sentence.get_attribute('outerHTML')

                url = re.findall('href="(.*?)">', num_page_sentence)
                video_window_url = 'https://www.youtube.com' + url[0]  # 一个视频的网页，不是纯视频url
                url_set.append(video_window_url)
            break


        # wait_times=0
        # stop_sign=0
        # #超过15s就不加载了
        # while(check_height == temp_height):
        #     time.sleep(1)
        #     wait_times+=1
        #     print(wait_times)
        #
        #     check_height = browser.execute_script(
        #         "return document.documentElement.scrollTop || window.pageYOffset || document.body.scrollTop;")
        #     #document.documentElement.clientHeight
        #     if(wait_times>15):
        #         stop_sign=1
        #         break

        # if check_height == temp_height:
        #     time.sleep(2)
        #
        #     while()
        #     no_result = browser.find_elements(By.CSS_SELECTOR,
        #                                       'yt-formatted-string[class^="style-scope ytd-message-renderer"]')
        #     if (len(no_result)>0):
        #         print('break')
        #         break
        # if(stop_sign==1):
        #     break
        # temp_height = check_height
        '''
        driver.execute_script("window.scrollBy(0,300)")
        #sleep一下让滚动条反应一下
        time.sleep(2)
        #获取当前滚动条距离顶部的距离
        check_height = driver.execute_script("return document.documentElement.scrollTop || window.pageYOffset || document.body.scrollTop;")
        #如果两者相等说明到底了
        if check_height==temp_height:
            break
        temp_height=check_height
        print(check_height)
        '''
        ##change
        '''
        <a id="thumbnail" class="yt-simple-endpoint inline-block style-scope ytd-thumbnail" aria-hidden="true" tabindex="-1" rel="null" href="/watch?v=yM84O2wEBZk">
        '''
        # num_page_sentences = browser.find_elements(By.CSS_SELECTOR,
        #                                            'a[href^="/shorts"]')
        # print('len is :{}'.format(len(num_page_sentences)))
        # # sentences_len = len(num_page_sentences)
        # # if not (sentences_len > temp_sentence_len):
        # #     break
        # # temp_sentence_len = sentences_len
        #
        # for num_page_sentence in num_page_sentences:
        #     num_page_sentence = num_page_sentence.get_attribute('outerHTML')
        #
        #     url = re.findall('href="(.*?)">', num_page_sentence)
        #     video_window_url = 'https://www.youtube.com' + url[0]  # 一个视频的网页，不是纯视频url
        #     url_set.append(video_window_url)
        #######0610  youtube 没有loads按钮
        # try:
        #     wd.find_element(By.CSS_SELECTOR,
        #                     'button[data-e2e="search-load-more"]').click()  # 模拟鼠标ctrl+a全选，然后删除可以实现clea.send_keys(Keys.CONTROL,"a")clea.send_keys(Keys.DELETE)
        # except:
        #     pass


    dic1 = {}
    dic1[keyword] = list(set(url_set))
    print('index:{}'.format(index), keyword, len(dic1[keyword]))
    if len(dic1[keyword]) > 50:
        try:
            with open(json_path, 'w', encoding='utf-8') as f:
                f.write(json.dumps(dic1))
            print('{} is saved!'.format(json_path))
        except:
            print('{} is not saved due to illegal name!'.format(json_path))


def download_youtube_shorts_single_pro(rank):
    options = Options()
    options.add_argument('--no-sandbox')  # 解决DevToolsActivePort文件不存在的报错
    options.add_argument('window-size=1920x3000')  # 指定浏览器分辨率
    options.add_argument('--disable-gpu')  # 谷歌文档提到需要加上这个属性来规避bug
    options.add_argument('--hide-scrollbars')  # 隐藏滚动条, 应对一些特殊页面
    options.add_argument('--headless')  # 
    options.add_experimental_option('excludeSwitches', ['enable-automation'])  # 开启实验性功能
    options.add_argument('--proxy-server=http://127.0.0.1:{}'.format(args.port))
    # wd = webdriver.Chrome(service=Service(r"C:\Users\zhubin\Desktop\chromedriver_win32\chromedriver.exe"), options=options)
    # wd = webdriver.Chrome(service=Service(r"C:\Users\yuanli\Desktop\chromedriver_103.0.5060.54\chromedriver.exe"),
    #                       options=options)
    wd = webdriver.Chrome(service=Service(r"/remote-home/zb/chromedriver"), options=options)

    # wd = webdriver.Chrome(service=Service(r"F:\chromedriver_win32\chromedriver.exe"), options=options)
    #################################
    # TODO 增加连接重试次数(一共4次链接)
    sess = requests.Session()
    sess.mount('http://', HTTPAdapter(max_retries=3))
    sess.mount('https://', HTTPAdapter(max_retries=3))
    sess.keep_alive = False  # 关闭多余连接

    ################################
    lines_part = lines[rank * per_pro_nums:(rank + 1) * per_pro_nums]
    for idx, keyword in enumerate(lines_part):
        keyword = keyword.replace('\n', '')
        keyword_no_space = keyword.replace(' ', '_')
        json_path = keywords_url_json_folder_path + '/' + 'youtube_{}.json'.format(keyword_no_space)
        if os.path.exists(json_path) or os.path.exists(json_path.replace('.json', '_none.json')):
            print('{} is exist!'.format(json_path))
        else:
            url = 'https://www.youtube.com/results?search_query=%23shorts++++{}'.format(keyword)
            # url = 'https://www.tiktok.com/search/video?lang=en&q={}&t=1655454790398'.format(keyword)
            # time.sleep(random.random() * 8 + 2)
            wd.get(url)  # 1-30  2-60)
            wd.implicitly_wait(20)

            # try:
            #     no_result = wd.find_element(By.CSS_SELECTOR, 'h2[class="tiktok-1ek2nds-H2Title e184a2v81"]').get_attribute(
            #         'outerHTML')  # 模拟鼠标ctrl+a全选，然后删除可以实现clea.send_keys(Keys.CONTROL,"a")clea.send_keys(Keys.DELETE)
            #     json_path = json_path.replace('.json','_none.json')
            #     with open(json_path, 'w', encoding='utf-8') as f:
            #         f.write(json.dumps({}))
            #     print('{} has no findings!'.format(keyword))
            # except:
            roll_window_to_bottom(wd, index=idx, keyword=keyword, stop_length=40000 * 100,
                                  json_path=json_path)


from multiprocessing import Process

if __name__ == "__main__":

    # download_youtube_shorts_single_pro(0)
    process_list = []
    for rank in range(pro):  # 在最上面
        p = Process(target=download_youtube_shorts_single_pro, args=([rank]))
        p.start()
        process_list.append(p)

    for rank in process_list:
        p.join()
