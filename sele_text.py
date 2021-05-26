from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import sleep
import openpyxl
import requests
import pandas as pd
import numpy as np
from lxml import etree
import matplotlib.pyplot as plt
from PIL import Image
import pytesseract as tess
import re

#无头浏览器
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable_gpu')


def get_bin_img(img, threshold=128):
    img = img.convert('L')    # 灰度处理
    table = []
    for i in range(256):
        if i < threshold:
            table.append(0)
        else:
            table.append(1)
    img = img.point(table, '1') #二值化
    return img
#获得将要获取的值


browser = webdriver.Chrome(executable_path='./chromedriver.exe',options=chrome_options)
#最终获取的值
pid_token = []
#导入实例
dir_ = './list.xlsx'
df = pd.read_excel(dir_)
df.columns = ['num','names']
wk = openpyxl.load_workbook(dir_)
wk_sheet = wk[wk.sheetnames[0]]
for name in df['names']:
    #打印公司名称
    print('公司名称为：',name)
    #打开网页
    browser.get('https://wzxxbg.mofcom.gov.cn/gspt/')
    #输入搜索词
    sinput = browser.find_element_by_id('searchKeyWord')
    sinput.send_keys (name)
    #点击搜索按钮
    btn = browser.find_element_by_xpath('/html/body/div[1]/div[2]/div/div[1]/div[2]/a')
    btn.click()

    browser.switch_to.default_content()	#回到主框架
    #获取iframe位置
    frame = browser.find_elements_by_tag_name("iframe")
    browser.switch_to.frame(frame[0].get_attribute('id'))
    text = []
    while text == []:
        browser.find_element_by_xpath('//*[@id="imgVCode"]').click()
        sleep(1)
        browser.save_screenshot('./vCode.png')

        browser.switch_to.default_content()
        iframe1 = browser.find_element_by_id(frame[0].get_attribute('id'))
        left = iframe1.location['x'] + 97
        top = iframe1.location['y'] +72
        right = iframe1.location['x'] + iframe1.size['width'] -306
        bottom = iframe1.location['y'] + iframe1.size['height'] - 110

        photo = Image.open('./vCode.png')
        photo = photo.crop((left, top, right, bottom))
        photo.save('vCode.png')
        #图像处理
        #tesseract识别验证码
        wh = Image.new('RGB', (200, 200), 'white')
        im = Image.open('vCode.png').resize((200,40))
        #图像复制粘贴
        wh.paste(im, (0, 0))
        plt.imshow(wh)
        plt.axis('off')
        plt.savefig('bin_img.png')
        im = Image.open('bin_img.png')


        im = get_bin_img(im, 140)
        #把图像放大
        pic_str = tess.image_to_string(im)
        pic_str = re.sub('[^a-zA-Z]+', '', pic_str)
        print('验证码为：',pic_str.strip())

        ##输入验证码
        browser.switch_to.frame(frame[0].get_attribute('id'))
        pinput = browser.find_element_by_xpath('//*[@id="iptVCode"]')
        pinput.clear()
        pinput.send_keys(pic_str.strip())
        # #点击查询按钮
        btn1 = browser.find_element_by_xpath('/html/body/div[2]/div/a')
        btn1.click()
        #等待页面加载（显示等待不知道有没有错误）
        sleep(7)
        #获取pid和token
        page_text = browser.page_source
        tree = etree.HTML(page_text)
        text = tree.xpath('//*[@id="searchList"]/dl')
        dl_list = tree.xpath('//*[@id="searchList"]/dl/dt')
    with open('./token.txt','a',encoding='utf-8') as f:
        if dl_list != []:
            for dl in dl_list:
                url_token = dl.xpath('./a/@href')[0]

                pid_token.append(url_token)
                f.write('\n'+url_token+',')
            print('本次总采集网页：',pid_token)
        else: print('本次总采集网页：',pid_token)
    wk_sheet.delete_rows((df['names']==name).index.any()+1,1)
    wk.save(dir_)
    # df = df.drop(index=(df.loc[(df['names']==name)].index))





