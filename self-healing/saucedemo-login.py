import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from brain.scraping import Scraper


def main():
    driver = webdriver.Chrome()
    driver.get('https://www.saucedemo.com/')

    print('Getting element with locator "//*[@id=\'user-name\']"')
    username = _find_element(driver, By.XPATH, "//*[@id='user-name']")
    username.send_keys('standard_user')
    time.sleep(1)

    print('Getting element with locator "//*[@id=\'password\']"')
    password = _find_element(driver, By.XPATH, "//*[@id='password']")
    password.send_keys('secret_sauce')
    time.sleep(1)

    print('Getting element with locator "//*[@id=\'login-button\']"')
    button = _find_element(driver, By.XPATH, "//*[@id='login-button']")
    button.click()
    time.sleep(3)

    print('Execution finished. Closing browser.')
    driver.quit()


def _find_element(driver, by, locator):
    try:
        element = driver.find_element(by, locator)
        scraper = Scraper(driver)
        scraper.save_web_element_scraping(element, locator)
        return element
    except:
        print(f'Element with locator "{locator}" not found')
        new_locator = self_healing(driver, locator)
        element = driver.find_element(by, new_locator)
        return element


def self_healing(driver, locator):
    """
    Scraps the current page and gets the new healed locator using the self-healing script.
    :return:
    """
    from brain.healing import init_healing
    scraper = Scraper(driver)
    scraper.scraping_current_page_elements()
    new_locator = init_healing(locator)
    return new_locator


if __name__ == '__main__':
    main()
