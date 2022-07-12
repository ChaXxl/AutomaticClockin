from time import sleep
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

from info import infos


def action(sno, pwd):
    options = Options()
    options.add_argument('--headless')  # 无界面运行
    options.add_argument('blink-settings=imagesEnabled=False')  # 禁止图片加载
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option('useAutomationExtension', False)
    options.add_experimental_option('prefs', {'profile.managed_default_content_settings.images': 2})  # 禁止图片加载
    options.add_experimental_option('detach', True)
    options.add_argument('--disable-gpu')  # 禁用gpu

    options.binary_location = 'C:\software\浏览器\CentBrowser\Application\chrome.exe'  # 浏览器安装路径
    service = Service('E:\Code\chromedriver 86.exe')  # 传入chromedriver路径

    browser = webdriver.Chrome(service=service, options=options)

    browser.get('https://yqtb.gzhu.edu.cn/infoplus/form/XNYQSB/start')
    browser.implicitly_wait(20)  # 等页面加载一下

    print("正在自动登录...", end='\t')
    browser.find_element(By.XPATH, '//input[@id="un"]').send_keys(sno)  # 学号
    browser.find_element(By.XPATH, '//input[@id="pd"]').send_keys(pwd)  # 密码
    browser.find_element(By.XPATH, '//a[@id="index_login_btn"]').click()  # 登录按钮
    print("已完成自动登录...", end='\t')

    browser.implicitly_wait(20)  # 等页面加载一下
    sleep(5)
    print("点击开始上报按钮...", end='\t')
    browser.find_element(By.XPATH, '//a[@id="preview_start_button"]').click()  # 开始上报按钮

    browser.implicitly_wait(20)  # 等页面加载一下

    print("选择广东省", end='\t')
    browser.find_element(By.XPATH, '//span[@aria-labelledby="select2-V1_CTRL119-container"]').click()
    sleep(5)
    browser.find_element(By.XPATH, '//input[@class="select2-search__field"]').send_keys('广东省')
    sleep(5)
    browser.find_element(By.XPATH, '//ul[@id="select2-V1_CTRL119-results"]//li[1]').click()

    print("选择广州市", end='\t')
    browser.find_element(By.XPATH, '//span[@aria-labelledby="select2-V1_CTRL120-container"]').click()
    sleep(5)
    browser.find_element(By.XPATH, '//input[@class="select2-search__field"]').send_keys('广州市')
    sleep(5)
    browser.find_element(By.XPATH, '//ul[@id="select2-V1_CTRL120-results"]//li[1]').click()

    print("选择番禺区", end='\t')
    browser.find_element(By.XPATH, '//span[@aria-labelledby="select2-V1_CTRL121-container"]').click()
    sleep(5)
    browser.find_element(By.XPATH, '//input[@class="select2-search__field"]').send_keys('番禺区')
    sleep(5)
    browser.find_element(By.XPATH, '//ul[@id="select2-V1_CTRL121-results"]//li[1]').click()

    browser.find_element(By.XPATH, '//input[@id="V1_CTRL122"]').send_keys('广州大学')

    print("点击三个复选框按钮...", end='\t')
    sleep(5)

    browser.find_element(By.XPATH, '//input[@id="V1_CTRL243"]').click()  # 本人身体状况
    browser.find_element(By.XPATH, '//input[@id="V1_CTRL238"]').click()  # 当日是否外出

    browser.find_element(By.XPATH, '//input[@id="V1_CTRL46"]').click()  # 是否接触过半个月内有疫情重点地区旅居史的人员
    browser.find_element(By.XPATH, '//input[@id="V1_CTRL262"]').click()  # 健康码是否为绿码
    browser.find_element(By.XPATH, '//input[@id="V1_CTRL37"]').click()  # 半个月内是否到过国内疫情重点地区
    browser.find_element(By.XPATH, '//input[@id="V1_CTRL82"]').click()  # 承诺

    print("点击提交按钮...", end='\t')
    browser.find_element(By.XPATH, '//a[@class="command_button_content"]').click()  # 提交按钮

    sleep(5)
    browser.refresh()  # 刷新，即打卡完成

    print(f"\t{sno}打卡完成...")

    saveToLog(sno)  # 保存打卡成功的学号到log.txt文件中


def saveToLog(sno):
    """将打卡记录保存到日志"""
    with open('log.txt', mode='a', encoding='utf-8') as f:
        f.write(f'\n{datetime.now()}\t{sno} 打卡成功')


if __name__ == '__main__':
    # 遍历列表，调用打卡函数
    for stu in infos:
        action(stu['sno'], stu['pwd'])