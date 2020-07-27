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
    level=logging.INFO,
    # 日志格式
    # 时间、代码所在文件名、代码行号、日志级别名字、日志信息
    format='%(asctime)s %(message)s',
    # 打印日志的时间
    datefmt='%Y %m %d %H:%M:%S',
    # 日志文件存放的目录（目录必须存在）及日志文件名
    filename=r'/volume2/web/webBoost.log',
    # filename=r'D:/Download/text.log',

    # 打开日志文件的方式
    filemode='a'
)

# 首先休眠5分钟，防止时间对不上
# time.sleep(120)


logging.info("$$$$$$$$$$$$$$$$$$$$$$开始处理$$$$$$$$$$$$$$$$$$$$$$")
# driver =
# webdriver.PhantomJS(executable_path=r'D:/phantomjs-2.1.1-windows/bin/phantomjs.exe',
# service_args=['--ignore-ssl-errors=true', '--ssl-protocol=TLSv1'])
driver = webdriver.PhantomJS(
    executable_path=r'/volume2/web/phantomjs-2.1.1/bin/phantomjs')
# driver = webdriver.Firefox()

# 设置超时，双重保险
driver.set_page_load_timeout(35)
driver.set_script_timeout(35)


# 定义一个全局变量，最大的获取页面次数
maxLoadTime = 0


# 定义一个全局变量，最大的尝试链接次数
maxConnectTime = 0


# 0.开始获取连接
def startConnect():

    global maxConnectTime

 # 最多尝试3次，不行就直接退出
    if(maxConnectTime == 3):
        logging.error(
            "------------------------------尝试超过3次，退出！------------------------------")
        driver.quit()
        return

    isSuccess = getUrl()
    # 地址获取成功
    if isSuccess:
        logging.info(
            "------------------------------地址获取成功，开始执行方法！------------------------------")
        startMyWork()
    else:
        logging.error(
            "------------------------------地址加载失败，休眠30秒后，重新加载------------------------------")

        maxConnectTime = maxConnectTime + 1
        # 地址加载失败
        time.sleep(30)
        logging.info(
            "------------------------------休眠结束，开始重新加载------------------------------")
        startConnect()


def getUrl():
    try:
        driver.get('http://ts.js.vnet.cn/')
        # driver.get('file:///D:/Download/demo.html')
        return True

    except Exception as e:
        logging.error(
            "------------------------------加载失败！------------------------------")
        return False


# 2、执行方法
def startMyWork():

    global maxLoadTime

    # 最多尝试3次，不行就直接退出
    if(maxLoadTime == 5):
        logging.error(
            "------------------------------尝试超过5次，退出！------------------------------")
        driver.quit()
        return

    # 开始操作
    flag, d_time = startClick()

    if(flag):
        logging.info("================== 操作成功！==================")
        driver.quit()
        return
    else:
        # 失败，时间对不上，则sleep
        maxLoadTime = maxLoadTime + 1

        logging.info(
            "------------------------------开始休眠------------------------------")

        # 时间过长，大于15分钟，则直接退出
        if(d_time > 900):
            logging.error(
                "------------------------------时间过长，直接退出------------------------------")
            driver.quit()
            return
        else:
            time.sleep(d_time)

        # 刷新
        if(getUrl()):

            time.sleep(2)
            # 递归调用。。。。。
            startMyWork()


# 3、点击事件
def startClick():

    try:
         # 1、点击试用按钮
        cmdBtn = driver.find_elements_by_xpath(
            '//div[@id="CmdBtn"]/div[1]/input[2]')[0].click()

    except Exception as e:
        logging.error(
            "------------------------------找不到确认按钮，直接退出------------------------------")
        driver.quit()
        return

    try:
        # 查看是否已经到期
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "btnExperiencesOK")))

        logging.info(
            "------------------------------已经到期，点击确定试用------------------------------")
        # 已经到期——点击确定试用
        time.sleep(2)
        driver.find_element_by_xpath('//input[@id="btnExperiencesOK"]').click()

        # 截图
        # driver.get_screenshot_as_file('/volume2/web/ss.png')

        return True, 0

    except Exception as e:

        # 没有到期，找到到期的日期
        text = driver.find_element_by_xpath(
            '//p[@id="OpenResMessage"]').text
        # text = "亲，您今天的下行体验时间将于00点08分到期"

        delayTime = getDelayTime(text)

        logging.info(
            "------------------------------没有到期，找到到期的日期------------------------------")
        logging.info(delayTime)

        return False, delayTime


# 算出延迟的时间
def getDelayTime(text):

    endTime = text.split('将于')[1].split("分到期")[0].replace('点', ':')

    nowDay = time.strftime("%Y-%m-%d ", time.localtime())

    # 拼接，具体的到期日期
    finalTime = nowDay + endTime + ":00"

    # 现在的具体日期
    nowTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    d1 = datetime.datetime.strptime(nowTime, '%Y-%m-%d %H:%M:%S')
    d2 = datetime.datetime.strptime(finalTime, '%Y-%m-%d %H:%M:%S')

    logging.info(
        "------------------------------到期日期------------------------------")
    # 到期日期
    logging.info(d2)
    logging.info(
        "------------------------------当前日期------------------------------")
    # 当前日期
    logging.info(d1)

    # 比较日期,如果 到期日期 < 当前日期
    if(d1 > d2):
        differSecond = (d1 - d2).seconds
        # return (d1 - d2).seconds + 2
    else:
        differSecond = (d2 - d1).seconds
        # return (d2 - d1).seconds + 2
    return 124 if differSecond < 120 else differSecond


if __name__ == '__main__':
    # 刷新
    # driver.navigate().refresh();
    startConnect()
