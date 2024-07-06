# -- coding: utf-8 --
"""
Scraper class used for scraping web elements and web pages.
"""
from bs4 import BeautifulSoup
from .generator import XpathGenerator
from selenium.webdriver.common.by import By
from selenium.webdriver.common.timeouts import Timeouts
import os

import pandas as pd

RESOURCES_PATH = 'resources'
CURRENT_ELEMENTS = os.path.join(RESOURCES_PATH, 'current_elements.csv')
ELEMENTS = os.path.join(RESOURCES_PATH, 'elements.csv')
GET_ELEMENT_RECT = False

TAGS = [
    'a',
    'div',
    'span',
    'button',
    'input',
    'select',
    'pre',
    'textarea',
    'svg',
    'img'
]


class Scraper:

    def __init__(self, driver):
        self.driver = driver

    def get_elements_from_page_source(self):
        """
        Extracts all elements from the page_source using BeautifulSoup.
        :return:
        """
        print(f'Scraping web page: {self.driver.current_url}')
        elements = []
        try:
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            elements = soup.find_all(TAGS)
        except(Exception,):
            print("Unable to get elements from page source")
        return elements

    def scraping_current_page_elements(self):
        """
        Gets all the data from the elements of the current web page.
        :return:
        """
        # from generator import XpathGenerator

        if not os.path.isdir(RESOURCES_PATH):
            os.mkdir(RESOURCES_PATH)

        xpath_generator = XpathGenerator()
        elements = self.get_elements_from_page_source()
        elem_list = []
        for element in elements:
            try:
                data = {'loc': xpath_generator.from_bs_element(element), 'tag': element.name, 'text': element.text}

                for att in element.attrs.keys():
                    if att == 'class':
                        data[att] = ' '.join(element.attrs.get(att))
                    else:
                        data[att] = element.attrs.get(att, None)

                data['url'] = self.driver.current_url
                if GET_ELEMENT_RECT:
                    timeout = Timeouts()
                    timeout.implicit_wait = 1
                    self.driver.timeouts = timeout
                    element = self.driver.find_element(By.XPATH, data['loc'])
                    data['rect'] = str(element.rect)
                elem_list.append(data)
            except (Exception,) as e:
                print(f"Unable to get current web element info due to {e} exception")
        self.insert_current_page(elem_list, CURRENT_ELEMENTS)

    def save_web_element_scraping(self, web_element, locator):
        """
        Gets all the data of a Selenium web element.
        :param web_element:
        :param locator:
        :return:
        """
        try:
            data = {'loc': locator, 'tag': web_element.tag_name, 'text': web_element.text}

            current_att = self.driver.execute_script(
                'var items = {}; for (index = 0; index < arguments[0].attributes.length; ++index) '
                '{ items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value }; '
                'return items;',
                web_element
            )
            data.update(current_att)
            data['url'] = self.driver.current_url

            if GET_ELEMENT_RECT:
                data['rect'] = str(web_element.rect)
            self.insert_element_data(data, ELEMENTS)
        except (Exception,):
            print(f"Unable to get web element with locator {locator} info")

    def insert_element_data(self, data, csv_path):
        """
        Inserts the data of a web element into a csv.
        :param data:
        :param csv_path:
        :return:
        """
        try:
            file_data = pd.read_csv(csv_path)
        except(Exception,):
            file_data = pd.DataFrame()
            print(f"Creating CSV with path '{csv_path}'")
        atts = [data]
        df_data = pd.DataFrame(atts)
        union_data = pd.concat([file_data, df_data], axis=0, ignore_index=True)
        union_data = union_data.fillna('')
        union_data = union_data.drop_duplicates()
        union_data.to_csv(csv_path, index=False)

    def insert_current_page(self, element_list, csv_path):
        """
        Inserts the data of a web page into a csv.
        :param element_list:
        :param csv_path:
        :return:
        """
        elements_df = pd.DataFrame(element_list)
        elements_df.to_csv(csv_path, index=False)