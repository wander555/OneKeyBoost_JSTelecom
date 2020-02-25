# coding=utf-8
from selenium import webdriver
import time
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
# import sys
# reload(sys)
# sys.setdefaultencoding('utf-8')

# from urllib2 import urlopen

# 获取公网地址
# my_ip = urlopen('http://ip.42.pl/raw').read()
# logging.info 'ip.42.pl', my_ip

# 初始化日志对象
logging.basicConfig(
    # 日志级别
    level=logging.INFO,
    # 日志格式
    # 时间、代码所在文件名、代码行号、日志级别名字、日志信息
    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
    # 打印日志的时间
    datefmt='%a, %d %b %Y %H:%M:%S',
    # 日志文件存放的目录（目录必须存在）及日志文件名
    filename=r'/volume2/web/text.log',
    # filename=r'D:/Download/text.log',

    # 打开日志文件的方式
    filemode='w'
)


logging.info("------------------------------开始处理------------------------------")
# driver = webdriver.PhantomJS(executable_path=r'D:/phantomjs-2.1.1-windows/bin/phantomjs.exe',
#                              service_args=['--ignore-ssl-errors=true', '--ssl-protocol=TLSv1'])
driver = webdriver.PhantomJS(
    executable_path=r'/volume2/web/phantomjs-2.1.1/bin/phantomjs')

# 设置超时，双重保险
driver.set_page_load_timeout(35)
driver.set_script_timeout(35)


# 定义一个全局变量，最大的尝试链接次数
maxLoadTime = 0


# 获取url
def getUrl():
    try:
        driver.get('http://ts.js.vnet.cn/')
        return True

    except Exception as e:
        logging.error(e)
        return False


# 执行方法
def startMyWork():
    global maxLoadTime
    if(maxLoadTime == 3):
        driver.quit()
        return

    flag, d_time = startClick()
    if(flag):
        # 操作
        logging.info(
            "------------------------------操作成功！------------------------------")
        driver.quit()
    else:
        # 失败，时间对不上，则sleep
        maxLoadTime = maxLoadTime + 1
        time.sleep(d_time)
        startClick()


# 点击事件
def startClick():

    # element =WebDriverWait(driver,10).until(EC.presence_of_element_located((By.ID,"CmdBtn")))
    # 1、点击试用按钮
    driver.find_elements_by_xpath(
        '//div[@id="CmdBtn"]/div[1]/input[2]')[0].click()

    try:
        # 查看是否已经到期
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "btnExperiencesOK")))

        # 已经到期——点击确定试用
        time.sleep(3)
        driver.find_element_by_xpath('//input[@id="btnExperiencesOK"]').click()

        # 截图
        # driver.get_screenshot_as_file('/volume2/web/ss.png')

        return True, 0

    except Exception as e:
        logging.error(e)

        # 没有到期，找到到期的日期
        text = driver.find_element_by_xpath(
            '//input[@id="OpenResMessage"]').text()
        # text = "亲，您今天的下行体验时间将于00点08分到期"
        delayTime = getDelayTime(text)

        return False, delayTime


# 算出延迟的时间
def getDelayTime(text):
    # 到期时间
    endTime = text.split('将于')[1].split("分到期")[0].replace('点', ':')

    # 当前的日期，到日
    nowDay = time.strftime("%Y-%m-%d ", time.localtime())

    # 拼接，具体的到期日期
    finalTime = nowDay + endTime + ":00"

    # 现在的具体日期
    nowTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    # 定义的日期格式需与当前时间格式一致
    d1 = datetime.datetime.strptime(nowTime, '%Y-%m-%d %H:%M:%S')
    d2 = datetime.datetime.strptime(finalTime, '%Y-%m-%d %H:%M:%S')

    # 计算相差的值，到秒
    delayTime = (d2 - d1).seconds + 15
    return delayTime


if __name__ == '__main__':
    # 刷新
    # driver.navigate().refresh();
    isSuccess = getUrl()

    # 地址获取成功
    if isSuccess:
        startMyWork()
    else:
        # 地址加载失败
        time.sleep(30)

        startMyWork()
