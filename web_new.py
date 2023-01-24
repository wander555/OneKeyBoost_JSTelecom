# coding=utf-8
from selenium import webdriver
import time
import json
import datetime
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging

# python2
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

# python3
# import importlib
# import sys
# importlib.reload(sys)

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
    filename=r'/volume4/backUp/webBoost.log',
    # filename=r'D:/Download/text.log',

    # 打开日志文件的方式
    filemode='a'
)

logging.error("开始处理......")

driver = webdriver.PhantomJS(
    executable_path=r'/volume4/backUp/phantomjs-2.1.1/bin/phantomjs', service_args=['--ignore-ssl-errors=true', '--ssl-protocol=TLSv1'])


# 设置超时，双重保险
driver.set_page_load_timeout(30)
driver.set_script_timeout(30)

# 定义一个全局变量，最大的获取页面次数
maxLoadTime = 0

# 定义一个全局变量，最大的尝试链接次数
maxConnectTime = 0

# 定义一个全局变量，最大的重新刷新次数
maxRefreshTime = 0

# 是否为第一次点击试用出现了提醒时间
firstAlert = 0


# 目标URL地址
target_url = 'http://ts.js118114.com/'


# 0.开始获取连接
def startConnect():
    # 0点，2点，4点，不进行操作
    nowTime = time.strftime("%H", time.localtime())
    if nowTime == '00':
        logging.error(
            "------------0点不进行操作，退出！------------")
        driver.close()
        driver.quit()
        return

    global maxConnectTime

 # 最多尝试3次，不行就直接退出
    if(maxConnectTime == 3):
        logging.error(
            "------------地址加载失败!尝试超过3次，退出！------------")
        driver.close()
        driver.quit()
        return

    isSuccess = getUrl()

    # 地址获取成功
    if isSuccess:
        startMyWork()

    # 获取失败,递归加载，最多尝试3次
    else:
        maxConnectTime = maxConnectTime + 1
        time.sleep(1)
        startConnect()


# 1.尝试登录url
def getUrl():
    try:
        driver.get(target_url)
        return True

    except Exception as e:
        logging.error(
            "------------ts.js.vnet.cn 首次加载失败！------------")
        return False


# 2、执行方法
def startMyWork():

    global maxLoadTime

    # 最多尝试3次，不行就直接退出
    if(maxLoadTime == 20):
        # driver.get_screenshot_as_file('/volume4/backUp/ss.png')
        logging.error(
            "------------尝试超过20次，退出！------------")
        driver.close()
        driver.quit()
        return

    # 开始操作
    flag, d_time = startClick()

    if(flag):
        logging.error("操作成功！")
        driver.close()
        driver.quit()

        senWChat("%s,提速成功!" % d_time)
        return
    else:
        # 失败，时间对不上，则sleep
        maxLoadTime = maxLoadTime + 1
        # 默认等待两分钟
        time.sleep(d_time + 3)
        # 刷新
        if(getUrl()):
            # time.sleep(60)
            # 递归调用。。。。。
            # time.sleep(8)
            startMyWork()
        else:
            logging.error(
                "------------ts.js.vnet.cn 加载失败！------------")
            driver.close()
            driver.quit()
            return


# 3、点击事件
def startClick():
    global maxRefreshTime
    global firstAlert
    try:
        # driver.get_screenshot_as_file('/volume4/backUp/startClick.png')
        # 1、点击同意书
        readBtn = driver.find_elements_by_xpath('//*[@id="CheckAgree"]')[0]
        if readBtn.is_displayed() == True:
            # logging.error(
            #     "-----------已查询到同意书-------------")
            readBtn.click()

            time.sleep(1)
            submitBtn = driver.find_elements_by_xpath('//*[@id="ButtonAgree"]')[0].click()

            time.sleep(1)

            # driver.get_screenshot_as_file('/volume4/backUp/clicked_submit.png')
            cmdBtn = driver.find_elements_by_xpath('//div[@id="CmdBtn"]/div/input[2]')[0].click()

            time.sleep(2)
        # 2、点击试用按钮
        else:
            # logging.error(
            #     "-----------不需要查询同意书，直接试用-------------")
            cmdBtn = driver.find_elements_by_xpath(
                '//div[@id="CmdBtn"]/div[1]/input[2]')[0].click()
            time.sleep(2)

    except Exception as e:
        logging.error(e)

        # driver.get_screenshot_as_file('/volume4/backUp/tryfailed.png')

        maxRefreshTime = maxRefreshTime + 1
        if(maxRefreshTime == 8):
            logging.error(
                "------------刷新尝试超过8次，退出！------------")
            driver.close()
            driver.quit()
            # return
        else:
            if(getUrl()):
                startMyWork()
            else:
                logging.error(
                    "------------ts.js.vnet.cn 加载失败！------------")
                driver.close()
                driver.quit()
                # return

    try:
        # driver.get_screenshot_as_file('/volume4/backUp/clicked_try.png')
        # 查看是否已经到期
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "btnExperiencesOK")))
        # 已经到期——点击确定试用
        time.sleep(5)
        driver.find_element_by_xpath('//input[@id="btnExperiencesOK"]').click()
        # text = driver.find_element_by_xpath(
        #     '//p[@id="OpenResMessage"]').text
        # 截图
        # driver.get_screenshot_as_file('/volume4/backUp/ss.png')
        return True, 0

    except Exception as e:

        # driver.get_screenshot_as_file('/volume4/backUp/clicked_fail.png')
        # 没有到期，找到到期的日期
        text = driver.find_element_by_xpath(
            '//p[@id="OpenResMessage"]').text
        # text = "亲，您今天的下行体验时间将于00点08分到期"
        logging.error(text)
        if len(text) > 0:
            # TODO
            # delayTime = 30
            # return False, delayTime

            # 是否为第一次，第一次获取差值，其余每隔一分钟获取一次
            if(firstAlert == 0):  
                delayTime = getDelayTime(text)
                firstAlert = 1
                return False, delayTime
            else:
                delayTime = 20
                return False, delayTime
        else:
            maxRefreshTime = maxRefreshTime + 1
            if(maxRefreshTime == 10):
                logging.error(
                    "------------刷新尝试超过10次，退出！------------")
                driver.close()
                driver.quit()
            # return
            else:
                if(getUrl()):
                    startMyWork()
                else:
                    logging.error(
                        "------------ts.js.vnet.cn 加载失败！------------")
                    driver.close()
                    driver.quit()

# 算出延迟的时间
def getDelayTime(text):
    # 提醒结束日期
    endTime = text.split('将于')[1].split("分到期")[0].replace('点', ':')
    # 日
    nowDay = time.strftime("%Y-%m-%d ", time.localtime())
    # 拼接，具体的到期日期
    finalTime = nowDay + endTime + ":59"

    # 当前具体日期
    nowTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    # 格式化日期
    d1 = datetime.datetime.strptime(nowTime, '%Y-%m-%d %H:%M:%S')
    d2 = datetime.datetime.strptime(finalTime, '%Y-%m-%d %H:%M:%S')

    # logging.error("当前日期:" + d1)
    # logging.error("到期日期:" + d2)

    # 服务器时间比现实时间慢200秒左右
    d2 = d2 + datetime.timedelta(seconds=437)

    # logging.error("延迟日期:" + d2)


    # 比较日期,如果 到期日期 < 当前日期
    if(d1 > d2):
        differSecond = (d1 - d2).seconds
    else:
        differSecond = (d2 - d1).seconds

    # logging.error("延迟秒数:" + differSecond)

    return differSecond

# 推送微信


def senWChat(content):
    datas = {'token': '76d192bcc74640dcbe080c7b0f312d5e', 'content': content, 'title': '提速結果'}
    # r = requests.post('http://pushplus.hxtrip.com/send', data=datas)


if __name__ == '__main__':
    # 刷新
    # driver.navigate().refresh();

    startConnect()
