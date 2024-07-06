# -- coding: utf-8 --
"""
File with functions for the self-healing process.
"""
import os
from sklearn.preprocessing import OneHotEncoder
from sklearn.neighbors import NearestNeighbors
import pandas as pd
from pandas.errors import EmptyDataError

RESOURCES_PATH = 'resources'
CURRENT_ELEMENTS = os.path.join(RESOURCES_PATH, 'current_elements.csv')
ELEMENTS_CSV = os.path.join(RESOURCES_PATH, 'elements.csv')


def init_healing(old_locator):
    """
        Function that uses the Nearest Neighbors ML algorithm to find the most similar elements
        to a not found element in a web page.
        :param old_locator:
        :return:
    """
    n_neighbors = 1
    algorithm = 'auto'
    tolerance = 0.9
    healed_locator = None
    element = read_successful_element(old_locator)
    page, page_locators = read_current_page()
    if len(element.index) != 0 and len(page.index) != 0 and len(page_locators.index) != 0:
        max_elems = len(page)
        if n_neighbors > max_elems:
            n_neighbors = max_elems
        element = pd.DataFrame(element, columns=page.columns)
        element = element.to_numpy()
        page = page.to_numpy()
        encoded_page, encoded_elem = encode(page, element)
        if encoded_page is not None and encoded_elem is not None:
            healed_locator, similarity = get_healed_locator(encoded_page, encoded_elem, n_neighbors, algorithm,
                                                            page_locators)
            if tolerance and similarity < tolerance:
                show_console(old_locator, healed_locator, round(similarity * 100, 2), False)
                healed_locator = None
            else:
                show_console(old_locator, healed_locator, round(similarity * 100, 2), True)
    else:
        print(f'Element with locator {old_locator} has never been found before or current page is empty')
    return healed_locator


def read_successful_element(locator):
    """
        Reads the info of the last successful element found from the csv using the old locator
        :param locator:
        :return:
    """
    try:
        element = pd.read_csv(ELEMENTS_CSV, encoding='utf-8-sig')
        element = element.loc[element['loc'] == locator]
        element = element.drop(columns=['loc'])
    except (FileNotFoundError, EmptyDataError) as exception:
        print(f'Unable to read file:{ELEMENTS_CSV}')
        print(exception)
        element = pd.DataFrame()
    return element


def read_current_page():
    """
        Reads the info of the scraped web page rom the csv
        :return:
    """
    try:
        page = pd.read_csv(CURRENT_ELEMENTS, encoding='utf-8-sig')
        page_locators = page['loc']
        page = page.drop(columns=['loc'])
    except (FileNotFoundError, EmptyDataError) as exception:
        print(f'Unable to read file:{CURRENT_ELEMENTS}')
        print(exception)
        page = pd.DataFrame()
        page_locators = pd.DataFrame()
    return page, page_locators


def encode(page, element):
    """
        Converts all web elements from a list of strings to a list of binary integers
        :param page:
        :param element:
        :return:
    """
    encoded_elem = None
    encoded_page = None
    try:
        encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
        encoded_page = encoder.fit_transform(page)
        encoded_elem = encoder.transform(element)
    except Exception as exception:
        print(f'Unable to encode web elements')
        print(exception)
    return encoded_page, encoded_elem


def get_healed_locator(encoded_page, encoded_elem, n_neighbors, algorithm, page_locators):
    """
        Uses the NearestNeighbors algorithm from the sklearn library to compare and find the most similar
        web element to the las successful element in the current page
        :param encoded_page:
        :param encoded_elem:
        :param n_neighbors:
        :param algorithm:
        :param page_locators:
        :return:
    """
    healed_locator = None
    first_elem_similarity = None
    try:
        neighbors = NearestNeighbors(n_neighbors=n_neighbors, algorithm=algorithm, metric='cosine').fit(encoded_page)
        distances, indexes = neighbors.kneighbors(encoded_elem)
        first_elem_similarity = distances[0].tolist()[0]
        first_elem_similarity = 1 - float(first_elem_similarity)
        healed_locator = page_locators.iloc[indexes.tolist()[0][0]]
    except Exception as exception:
        print("Unable to execute the NearestNeighbors algorithm")
        print(exception)
    return healed_locator, first_elem_similarity


def show_console(old_locator, healed_locator, similarity, valid):
    """
        If activated in the settings prints the result of the self-healing in the console
        :param old_locator:
        :param healed_locator:
        :param similarity:
        :return:
    """
    print(f'\n\tElement with locator "{old_locator}" not found')
    print(f'\tSimilar element found with locator: {healed_locator}')
    print(f'\tElement similarity: {similarity}%')
    if not valid:
        print('\tSimilarity below tolerance. Element not valid\n')
    else:
        print('\tElement valid. Returning new locator\n')