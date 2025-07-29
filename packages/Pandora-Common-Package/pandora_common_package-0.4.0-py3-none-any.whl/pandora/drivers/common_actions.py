import time

from selenium.webdriver.common.by import By

from selenium.webdriver.support import expected_conditions as EC

import pytest
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from urllib3 import request

from pandora.config.config import c_config
from pandora.ai.appliTools import AppliTool
from pandora.utils.email import mailinator_email


def launch_web(load_config):
    driver = webdriver.Edge()
    icicle_url = load_config["web_url"]
    print("icicle_url:", icicle_url)
    driver.get(icicle_url)
    driver.maximize_window()

    # appli_key = c_config.appli_key
    # appli_server = c_config.appli_server
    # app_name = c_config.app_name
    # myapplitool = AppliTool(appli_key, appli_server, app_name)
    # privacy_showup = wait_for_element(driver,By.ID,"onetrust-policy-text",10)
    # if privacy_showup:
    #     driver.find_element(By.ID,"onetrust-accept-btn-handler").click()
    return driver  # , myapplitool


# def login_icile(user_name,password,driver):
#     driver.find_element(By.XPATH, "//*[@data-automation-id='AUID_User_Email']").send_keys(user_name)
#     driver.find_element(By.XPATH,"//*[@data-automation-id='AUID_login_agree']/following-sibling::span").click()
#     driver.find_element(By.XPATH, "//*[@data-automation-id='AUID_Login_Sign']").click()
#     hp_login_username = wait_for_element(driver,By.ID,"user-name-form-submit",10)
#     if hp_login_username:
#         driver.find_element(By.ID, "user-name-form-submit").click()
#     hp_password = wait_for_element(driver,By.ID,"password",10)
#     if hp_password:
#         driver.find_element(By.ID, "password").send_keys(password)
#         driver.find_element(By.ID,"sign-in").click()  #
#     #mfa_showup = wait_for_element(driver,By.XPATH,"//button[@data-auid='auid_verify_otp_resendbutton']",50)
#     mfa_showup = wait_for_element(driver, By.XPATH, "//div[contains(text(), 'Verification Code')]", 50)
#     if mfa_showup:
#         #time.sleep(20)
#         mfa_code = get_mfa("New authentication request")
#        # driver.find_element(By.XPATH,"//button[@data-auid='auid_verify_otp_resendbutton'/preceding-sibling::div[1]]").send_keys(mfa_code)
#         driver.find_element(By.XPATH,"//input[@aria-label='Please enter verification code. Digit 1']").send_keys(mfa_code)
#
#
# def wait_for_element(driver,locator_type:str,locator_value:str,timeout=10):
#     try:
#         # 显式等待某个元素出现
#         element = WebDriverWait(driver, timeout).until(
#             EC.presence_of_element_located((locator_type, locator_value))   # EC.presence_of_element_located((By.ID, "value"))
#         )
#         print(f"Element '{locator_value}' is present")
#         return True
#     except:
#         return False
#
# def get_mfa(subject): #New authentication request
#     inbox = c_config.user_name_1.split('@')[0]
#     emails = mailinator_email.get_email_list(inbox)
#     mail_id = mailinator_email.get_email_id(emails,subject)
#     mail_details = mailinator_email.get_email_details(mail_id)
#     pat = r':#0076AD;">(.*?)</div>'
#     mfa = mailinator_email.get_mfa_from_email(mail_details,pat)
#     print("mfa:",mfa.strip())
#     return mfa
