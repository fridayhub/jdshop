#!/usr/bin/env python3
# coding:utf-8
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from PIL import Image
#from utils.baiduAPI import parseVscode
from time import sleep

import pickle

def GetVcode(driver):
    driver.save_screenshot('button.png')
    element = driver.find_element_by_id("vcJpeg")
    print(element.location)                # 打印元素坐标
    print(element.size)                    # 打印元素大小

    left = element.location['x']
    top = element.location['y']
    right = element.location['x'] + element.size['width']
    bottom = element.location['y'] + element.size['height']

    im = Image.open('button.png')
    im = im.crop((left, top, right, bottom))
    im.save('button.png')
    #return parseVscode('button.png')


def Login(driver, vcode):
    #操作登录入口
    select_name_input = driver.find_element_by_id("username")
    select_name_input.clear()
    select_name_input.send_keys("gczf06")

    select_password_input = driver.find_element_by_id("password")
    select_password_input.clear()
    select_password_input.send_keys("tfb666")

    select_institute_input = driver.find_element_by_id("institute")
    select_institute_input.clear()
    select_institute_input.send_keys("49403320")

    select_vcode_input = driver.find_element_by_id('validateCode')
    select_vcode_input.clear()
    select_vcode_input.send_keys(vcode)


def main():
    driver = webdriver.Chrome()
    driver.get('https://passport.jd.com/uc/login?ltype=logout')
    #切换到frame里面 负责找不到CheckBox元素
    #driver.switch_to.frame("loginMain")

    driver.find_element_by_link_text("账户登录").click()
    driver.find_element_by_name("loginname").send_keys("13078882277")
    driver.find_element_by_name("nloginpwd").send_keys("chj137619778")
    driver.find_element_by_id("loginsubmit").click()
    sleep(1)
    authcodeFlag = driver.find_element_by_id("o-authcode").get_attribute('style')
    print(authcodeFlag)
    if 'block' in authcodeFlag:
        print("find authcode")
        while True:
            authcode = input('input authcode:')
            driver.find_element_by_name("authcode").send_keys(authcode)
            driver.find_element_by_id("loginsubmit").click()
            sleep(1)
            print(driver.current_url)
            if driver.current_url == 'https://www.jd.com/':
                break


    #login success, save cookies
    cookies = {

    }

    for item in driver.get_cookies():
        print(item['name'], item['value'])
        cookies[item['name']] = item['value']
    with open('cookies', 'wb') as f:
        pickle.dump(cookies, f)


    '''
    #get login addr
    link = driver.find_element_by_class_name('login-box').get_attribute('src')
    #driver.quit()

    print(link)
    driver.get(link)
    #当“数字证书”checkbox出现再继续
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'chkCfcaCer')))
    while True:
     if driver.find_element_by_xpath('//*[@id="chkOpenCtrl"]').is_selected():
        #选择数字证书
        driver.find_element_by_xpath('//*[@id="chkCfcaCer"]').click()
        break
    vcode = GetVcode(driver)
    while(len(vcode) != 4):
        driver.find_element_by_xpath('//*[@id="vcJpeg"]').click()
        vcode = GetVcode(driver)
        sleep(1)
    Login(driver, vcode)
    '''



if __name__ == '__main__':
    main()
    while True:
        sleep(10000)
