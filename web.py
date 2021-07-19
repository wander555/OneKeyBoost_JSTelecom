# coding=utf-8
from selenium import webdriver
import time
import datetime
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
    filename=r'/volume2/web/webBoost.log',
    # filename=r'D:/Download/text.log',

    # 打开日志文件的方式
    filemode='a'
)

logging.error("开始处理......")
# driver =
# webdriver.PhantomJS(executable_path=r'D:/phantomjs-2.1.1-windows/bin/phantomjs.exe',
# service_args=['--ignore-ssl-errors=true', '--ssl-protocol=TLSv1'])
driver = webdriver.PhantomJS(
    executable_path=r'/volume2/web/phantomjs-2.1.1/bin/phantomjs')

# 设置超时，双重保险
driver.set_page_load_timeout(30)
driver.set_script_timeout(30)

# 定义一个全局变量，最大的获取页面次数
maxLoadTime = 0

# 定义一个全局变量，最大的尝试链接次数
maxConnectTime = 0

# 定义一个全局变量，最大的重新刷新次数
maxRefreshTime = 0


# 目标URL地址
target_url = 'http://ts.js.vnet.cn/'


# 0.开始获取连接
def startConnect():
    # 0点，2点，4点，不进行操作
    nowTime = time.strftime("%H", time.localtime())
    if nowTime == '00':
        logging.error(
            "------------0点不进行操作，退出！------------")
        driver.quit()
        return

    global maxConnectTime

 # 最多尝试3次，不行就直接退出
    if(maxConnectTime == 3):
        logging.error(
            "------------地址加载失败!尝试超过3次，退出！------------")
        driver.quit()
        return

    isSuccess = getUrl()
    # 地址获取成功
    if isSuccess:
        startMyWork()
    else:
        maxConnectTime = maxConnectTime + 1
        # 地址加载失败
        time.sleep(5)

        startConnect()


def getUrl():
    try:
        driver.get(target_url)
        # logging.info("ts.js.vnet.cn 加载成功！")
        # 截图
        # driver.get_screenshot_as_file('/volume2/web/ss.png')
        return True

    except Exception as e:
        logging.error(
            "------------ts.js.vnet.cn 加载失败！------------")
        return False


# 2、执行方法
def startMyWork():

    global maxLoadTime

    # 最多尝试3次，不行就直接退出
    if(maxLoadTime == 10):
        logging.error(
            "------------尝试超过10次，退出！------------")
        driver.quit()
        return

    # 开始操作
    flag, d_time = startClick()

    if(flag):
        logging.error("操作成功！")
        driver.quit()
        return
    else:
        # 失败，时间对不上，则sleep
        maxLoadTime = maxLoadTime + 1
        # logging.info("时间未到，休眠60s后继续")
        # logging.info("当前操作次数:%s", maxLoadTime)

        # 时间过长，大于15分钟，则直接退出
        # if(d_time > 600):
        #     logging.error(
        #         "------------时间大于10分钟，直接退出------------")
        #     driver.quit()
        #     return
        # else:
        #     # if(d_time > 300):
        #     #     time.sleep(d_time)
        #     # else:
        #     #     time.sleep(60)
        #     # 到期的时间总是慢2分钟
        #     time.sleep(d_time + 120 + 8)
        time.sleep(d_time + 120)
        # 刷新
        if(getUrl()):
            # time.sleep(60)
            # 递归调用。。。。。
            # time.sleep(8)
            startMyWork()
        else:
            logging.error(
                "------------ts.js.vnet.cn 加载失败！------------")
            driver.quit()
            return


# 3、点击事件
def startClick():
    global maxRefreshTime

    try:
        # 1、点击试用按钮
        cmdBtn = driver.find_elements_by_xpath(
            '//div[@id="CmdBtn"]/div[1]/input[2]')[0].click()

    except Exception as e:

        maxRefreshTime = maxRefreshTime + 1
        if(maxRefreshTime == 10):

            logging.error(
                "------------刷新尝试超过10次，退出！------------")
            driver.quit()
            # return
        else:
            if(getUrl()):
                startMyWork()
            else:
                logging.error(
                    "------------ts.js.vnet.cn 加载失败！------------")
                driver.quit()
                # return

        # logging.error(
        #     "------------找不到试用按钮，直接退出------------")
        # driver.quit()
        # return

    try:
        # 查看是否已经到期
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "btnExperiencesOK")))

        # 已经到期——点击确定试用
        time.sleep(1)
        driver.find_element_by_xpath('//input[@id="btnExperiencesOK"]').click()

        # 截图
        # driver.get_screenshot_as_file('/volume2/web/ss.png')

        return True, 0

    except Exception as e:

        # 没有到期，找到到期的日期
        text = driver.find_element_by_xpath(
            '//p[@id="OpenResMessage"]').text
        # text = "亲，您今天的下行体验时间将于00点08分到期"

        if len(text) > 0:
            delayTime = getDelayTime(text)
            # logging.info("最后需要等待的时间(s):" + str(delayTime))
            return False, delayTime
        else:
            maxRefreshTime = maxRefreshTime + 1
            if(maxRefreshTime == 10):
                logging.error(
                    "------------刷新尝试超过10次，退出！------------")
                driver.quit()
            # return
            else:
                if(getUrl()):
                    startMyWork()
                else:
                    logging.error(
                        "------------ts.js.vnet.cn 加载失败！------------")
                    driver.quit()

# 算出延迟的时间


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

    # 比较日期,如果 到期日期 < 当前日期
    if(d1 > d2):
        differSecond = (d1 - d2).seconds
    else:
        differSecond = (d2 - d1).seconds

    logging.info("当前的时间:" + nowTime)
    logging.info("到期的时间:" + finalTime)

    # return 150 if differSecond < 130 else differSecond

    return differSecond


if __name__ == '__main__':
    # 刷新
    # driver.navigate().refresh();

    startConnect()
