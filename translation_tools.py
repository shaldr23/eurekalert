# %%
from selenium import webdriver
from requests import Request
import time
import os
from bs4 import BeautifulSoup
import random


def translate_text(browser, text):
    """
    Function to translate piece of text using
    yandex.tranlate
    """
    basic_url = 'https://translate.yandex.ru/'
    params = {'lang': 'en-ru'}
    params['text'] = text
    url = Request('GET', basic_url, params=params).prepare().url
    browser.get(url)
    element = browser.find_element_by_css_selector('[data-complaint-type=fullTextTranslation]')
    ihtml = element.get_attribute('innerHTML')
    soup = BeautifulSoup(ihtml, 'html.parser')
    return soup.text


def translate_collection(browser, collection, min_sleep=5, max_sleep=30,
                         delimiter='#@', max_text_length=500):
    """
    Translates collection of texts.
    gauss_sleep_gen is used to wait between requests.
    delimiter is used to join short texts for translation
    and then split.
    """
    sleep_gen = gauss_sleep_gen(min_sleep, max_sleep)
    translated_collection = []
    chunk = ''
    for piece in collection:
        assert len(chunk) <= max_text_length
        to_add = delimiter + piece if chunk else piece
        if len(chunk + to_add) <= max_text_length:
            chunk += to_add
        else:
            translated = translate_text(browser, chunk)
            translated_collection.extend(translated.split(delimiter))
            chunk = piece
            to_sleep = next(sleep_gen)
            print(f'Sleep {to_sleep} sec before next request...')
            time.sleep(to_sleep)
    # final translation of residual chunk
    translated = translate_text(browser, chunk)
    translated_collection.extend(translated.split(delimiter))
    return translated_collection


def gauss_sleep_gen(min_val, max_val):
    """
    Returns normally distributed value belonging to interval
    with probability 0.9973. If result isn't in interval -
    generate result until it is in there.
    """
    assert max_val > min_val, 'max_val must be greater than min_val'
    mu = (min_val + max_val) / 2
    sigma = (mu - min_val) / 3
    while True:
        result = random.gauss(mu, sigma)
        if min_val <= result <= max_val:
            yield result


if __name__ == '__main__':
    """
    In case yandex thinks you are robot just run
    browser for 30 sec and pass captcha
    """
    this_dir = os.path.dirname(__file__)
    driver_path = os.path.join(this_dir, 'driver/chromedriver.exe')
    basic_url = 'https://translate.yandex.ru/'
    try:
        browser = webdriver.Chrome(driver_path)
        browser.get(basic_url)
        time.sleep(30)
    finally:
        browser.quit()
