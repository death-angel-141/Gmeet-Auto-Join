from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import pause
import os
import logging
from telegram.ext import Updater, CommandHandler, run_async
from telegram import ChatAction
from config import Config
from os import execl
from sys import executable
import pickle

# Logger
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

updater = Updater(token=Config.BOT_TOKEN, use_context=True)
dp = updater.dispatcher


options = webdriver.ChromeOptions()

options.add_argument("--disable-infobars")
options.add_argument("--window-size=1200,800")
options.add_argument(
    "user-agent='User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36'")
options.add_experimental_option("prefs", {
    "profile.default_content_setting_values.media_stream_mic": 2,
    "profile.default_content_setting_values.media_stream_camera": 2,
    "profile.default_content_setting_values.notifications": 2,
    "profile.default_content_setting_values.geolocation": 2
})

browser = webdriver.Chrome(options=options)


@run_async
def restart(update, context):
    restart_message = context.bot.send_message(
        chat_id=update.message.chat_id, text="Restarting, Please wait!")
    # Save restart message object in order to reply to it after restarting
    browser.quit()
    with open('restart.pickle', 'wb') as status:
        pickle.dump(restart_message, status)
    execl(executable, executable, "class.py")


def status(update, context):
    browser.save_screenshot("ss.png")
    context.bot.send_chat_action(
        chat_id=update.message.chat_id, action=ChatAction.UPLOAD_PHOTO)
    mid = context.bot.send_photo(chat_id=update.message.chat_id, photo=open(
        'ss.png', 'rb'), timeout=120).message_id
    os.remove('ss.png')


def meet(update, context):
    logging.info("Logging In")
    try:
        context.bot.send_chat_action(
            chat_id=update.message.chat_id, action=ChatAction.TYPING)
        usernameStr = Config.USERNAME
        passwordStr = Config.PASSWORD

        url_meet = update.message.text.split()[-1]
        splitt = url_meet.split("/", 3)

        url_meet = splitt[3]

        if os.path.exists("meet.pkl"):
            cookies = pickle.load(open("meet.pkl", "rb"))
            browser.get('https://accounts.google.com/ServiceLogin?ltmpl=meet&continue=https%3A%2F%2Fmeet.google.com%3Fhs%3D193&_ga=2.83620246.1231976264.1598164483-1486329530.1598164483')
            for cookie in cookies:
                browser.add_cookie(cookie)
        else:
            browser.get('https://accounts.google.com/o/oauth2/v2/auth/oauthchooseaccount?redirect_uri=https%3A%2F%2Fdevelopers.google.com%2Foauthplayground&prompt=consent&response_type=code&client_id=407408718192.apps.googleusercontent.com&scope=email&access_type=offline&flowName=GeneralOAuthFlow')
            username = browser.find_element_by_xpath("//*[@id='identifierId']")
            username.send_keys(usernameStr)
            nextButton = browser.find_element_by_xpath(
                "//*[@id='identifierNext']/div/button/div[2]")
            nextButton.click()
            time.sleep(3)

            password = browser.find_element_by_name("password")
            password.send_keys(passwordStr)
            signInButton = browser.find_element_by_xpath(
                "//*[@id='passwordNext']/div/button/div[2]")
            signInButton.click()
            time.sleep(3)

            browser.save_screenshot("ss.png")
            context.bot.send_chat_action(
                chat_id=update.message.chat_id, action=ChatAction.UPLOAD_PHOTO)
            mid = context.bot.send_photo(chat_id=update.message.chat_id, photo=open(
                'ss.png', 'rb'), timeout=120).message_id
            os.remove('ss.png')

            pickle.dump(browser.get_cookies(), open("meet.pkl", "wb"))

        browser.get('https://meet.google.com')

        enterurl = browser.find_element_by_xpath("//*[@id='i3']")
        enterurl.send_keys(url_meet)
        time.sleep(2)

        joinbtn = browser.find_element_by_xpath(
            "//*[@id='yDmH0d']/c-wiz/div/div[2]/div/div[1]/div[3]/div[2]/div[2]/button")
        joinbtn.click()
        time.sleep(5)

        # dismiss
        browser.find_element_by_xpath(
            "//*[@id='yDmH0d']/div[3]/div/div[2]/div[3]/div").click()
        time.sleep(5)
        # join
        browser.find_element_by_xpath(
            "//*[@id='yDmH0d']/c-wiz/div/div/div[7]/div[3]/div/div/div[2]/div/div[1]/div[2]/div/div[2]/div/div[1]/div[1]").click()

        context.bot.send_chat_action(
            chat_id=update.message.chat_id, action=ChatAction.TYPING)
        context.bot.send_message(
            chat_id=update.message.chat_id, text="Attending your lecture.")
        pause
        logging.info("Doing Class!!")

    except:
        browser.quit()
        context.bot.send_message(
            chat_id=update.message.chat_id, text="Some error occurred retry!")


def main():
    dp.add_handler(CommandHandler("meet", meet))
    dp.add_handler(CommandHandler("restart", restart))
    dp.add_handler(CommandHandler("status", status))
    logging.info("Bot Started")
    updater.start_polling()


if __name__ == '__main__':
    main()
