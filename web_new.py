# coding=utf-8
from selenium import webdriver
import time
import json
import datetime
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import logging
import importlib
import sys
import os
importlib.reload(sys)

# 初始化日志对象
logging.basicConfig(
    # 日志级别
    level=logging.ERROR,
    # 日志格式
    # 时间、代码所在文件名、代码行号、日志级别名字、日志信息
    format='%(levelname)s 【%(asctime)s】 %(message)s ',
    # 打印日志的时间
    datefmt='%m-%d %H:%M:%S',
    # 日志文件存放的目录（目录必须存在）及日志文件名
    filename=r'/root/webBoost.log',
    # filename=r'D:/Download/text.log',
    # 打开日志文件的方式
    filemode='a'
)


# 定义一个全局变量，最大的获取页面次数,最大6次
maxLoadTime = 0
# 定义一个全局变量，最大的尝试链接次数，最大3次
maxConnectTime = 0
# 定义一个全局变量，最大的重新刷新次数，最大8次
maxRefreshTime = 0


class MyWebBoost():
    def __init__(self, chromedriver_path, target_url):
        chromedriver = chromedriver_path
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        self.s = Service(chromedriver)
        self.driver = webdriver.Chrome(service=self.s, options=chrome_options)
        # 设置超时，双重保险
        self.driver.set_page_load_timeout(30)
        self.driver.set_script_timeout(30)
        self.target_url = target_url

    # 0.开始获取连接
    def startConnect(self):
        global maxConnectTime

        # 最多尝试3次，不行就直接退出
        if maxConnectTime == 3:
            self.quit()
            return

        isSuccess = self.getUrl()

        # 地址获取成功
        if isSuccess:
            self.startMyWork()

        # 获取失败,递归加载，最多尝试3次
        else:
            maxConnectTime = maxConnectTime + 1
            time.sleep(1)
            self.startConnect()

    # 1.尝试登录url
    def getUrl(self):
        try:
            self.driver.get(self.target_url)
            return True

        except Exception as e:
            logging.error(
                "------------ts.js.vnet.cn 首次加载失败！------------")
            return False

    # 2、执行方法
    def startMyWork(self):

        global maxLoadTime

        # 最多尝试3次，不行就直接退出
        if maxLoadTime == 6:
            self.quit()
            return

        # 开始操作
        flag, d_time = self.startClick()

        if flag:
            logging.error("操作成功！")
            self.quit()

            # senWChat("提速成功!")
            return
        else:
            # 失败，时间对不上，则sleep
            maxLoadTime = maxLoadTime + 1
            logging.error("需要休眠:%s秒" % str(d_time))
            time.sleep(d_time + 5)
            # 刷新
            if self.getUrl():
                self.startMyWork()
            else:
                self.quit()
                return

    # 3、点击事件
    def startClick(self):
        global maxRefreshTime
        try:
            self.driver.get_screenshot_as_file('/root/startClick.png')
            # 1、点击同意书
            readBtn = self.driver.find_elements(By.XPATH, '//*[@id="CheckAgree"]')[0]
            if readBtn.is_displayed():
                # logging.error(
                #     "-----------已查询到同意书-------------")
                readBtn.click()

                time.sleep(1)
                self.driver.find_elements(By.XPATH, '//*[@id="ButtonAgree"]')[0].click()

                time.sleep(3)

                # self.driver.get_screenshot_as_file('/root/clicked_submit.png')
                self.driver.find_elements(By.XPATH, '//div[@id="CmdBtn"]/div/input[2]')[0].click()

                time.sleep(5)
            # 2、点击试用按钮
            else:
                # logging.error(
                #     "-----------不需要查询同意书，直接试用-------------")
                self.driver.find_elements(By.XPATH,
                                          '//div[@id="CmdBtn"]/div[1]/input[2]')[0].click()
                time.sleep(5)

        except Exception as e:
            # logging.error(e)

            # self.driver.get_screenshot_as_file('/volume2/web/tryfailed.png')

            maxRefreshTime = maxRefreshTime + 1
            if maxRefreshTime == 8:
                self.quit()
            else:
                if self.getUrl():
                    self.startMyWork()
                else:
                    self.quit()

        try:
            self.driver.get_screenshot_as_file('/root/clicked_try.png')
            # 查看是否已经到期
            # WebDriverWait(self.driver, 10).until(
            #     EC.presence_of_element_located((By.ID, "btnExperiencesOK")))
            # 已经到期——点击确定试用
            time.sleep(5)
            self.driver.find_element(By.XPATH, '//input[@id="btnExperiencesOK"]').click()
            # text = driver.find_element_by_xpath(
            #     '//p[@id="OpenResMessage"]').text
            # 截图
            # self.driver.get_screenshot_as_file('/volume2/web/ss.png')
            return True, 0

        except Exception as e:
            self.driver.get_screenshot_as_file('/root/clicked_fail.png')
            # 没有到期，找到到期的日期
            text = self.driver.find_element(By.XPATH, '//p[@id="OpenResMessage"]').text
            # text = "亲，您今天的下行体验时间将于00点08分到期"
            logging.error(text)

            if len(text) > 0:
                # TODO
                delayTime = self.getDelayTime(text)
                # logging.info("最后需要等待的时间(s):" + str(delayTime))
                return False, delayTime
            else:
                maxRefreshTime = maxRefreshTime + 1
                if maxRefreshTime == 10:
                    self.quit()
                else:
                    if self.getUrl():
                        self.startMyWork()
                    else:
                        self.quit()

    # 算出延迟的时间
    @ staticmethod
    def getDelayTime(text):

        logging.info("提醒时间:" + text)

        endTime = text.split('将于')[1].split("分到期")[0].replace('点', ':')

        nowDay = time.strftime("%Y-%m-%d ", time.localtime())

        # 拼接，具体的到期日期
        finalTime = nowDay + endTime + ":59"

        # 现在的具体日期
        nowTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        d1 = datetime.datetime.strptime(nowTime, '%Y-%m-%d %H:%M:%S')
        d2 = datetime.datetime.strptime(finalTime, '%Y-%m-%d %H:%M:%S')

        # 服务器时间比现实时间慢200秒左右
        d2 = d2 + datetime.timedelta(seconds=240)

        # 比较日期,如果 到期日期 < 当前日期
        if d1 > d2:
            differSecond = (d1 - d2).seconds
        else:
            differSecond = (d2 - d1).seconds

        logging.info("当前的时间:" + nowTime)
        logging.info("到期的时间:" + finalTime)

        # return 150 if differSecond < 130 else differSecond
        return differSecond

    # 退出Chromedriver
    def quit(self):
        # self.driver.close()
        self.driver.quit()
        self.s.stop()
        os.system('ps -ef|grep chromedriver|grep -v grep|awk \'{print $2}\'|xargs kill -9')
        os.system('ps -ef|grep chrome|grep -v grep|awk \'{print $2}\'|xargs kill -9')


# 推送微信
def senWChat(content):
    data = {'token': '76d192bcc74640dcbe080c7b0f312d5e', 'content': content, 'title': '提速結果'}
    r = requests.post('http://pushplus.hxtrip.com/send', data=data)


if __name__ == '__main__':
    webBoost = MyWebBoost('/usr/bin/chromedriver', 'https://ts.js.vnet.cn/')

    # 0点,不进行操作
    nowTime = time.strftime("%H", time.localtime())
    if nowTime != '00':
        # 开始点击
        webBoost.startClick()
