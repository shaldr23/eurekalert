# %%
from bs4 import BeautifulSoup
import requests
import datetime
import pandas as pd
import numpy as np
from journal_tools import get_journals_from_file


def get_text_from_item(item, selector):
    try:
        text = item.select(selector)[0].text.strip()
    except IndexError:
        text = ''
    return text


def get_link(item, selector):
    try:
        link = item.select(selector)[0]['href']
    except Exception:
        link = ''
    return link


def frame_from_request(req: requests.Request):
    soup = BeautifulSoup(req.text, 'html.parser')
    frame = pd.DataFrame()
    for item in soup.select('article.post'):
        element = {}
        element['title'] = get_text_from_item(item, '.post_title')
        element['abstract'] = get_text_from_item(item, '.intro')
        element['journal'] = get_text_from_item(item, '.dl-horizontal em')
        link = get_link(item, 'a')
        link = 'https://www.eurekalert.org' + link
        element['link'] = link
        frame = frame.append(element, ignore_index=True)
    return frame


FROM_DATE = datetime.date.today()
DAYS = 10
basic_url = 'https://www.eurekalert.org/news-releases/browse/all'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
           'AppleWebKit/537.36 (KHTML, like Gecko) '
           'Chrome/83.0.4103.61 Safari/537.36'}
journals_file = 'journals.txt'
big_frame = pd.DataFrame()
for day in range(DAYS):
    date = FROM_DATE - datetime.timedelta(days=day)
    str_date = date.strftime('%m/%d/%Y')
    page = 0
    while True:
        page += 1
        params = {'view': 'summaries',
                  'date': str_date}
        url = f'{basic_url}/{page}'
        req = requests.get(url, headers=headers, params=params)
        frame = frame_from_request(req)
        if frame.empty:
            break
        frame['date'] = date.strftime('%d.%m.%Y')
        frame['page'] = page
        big_frame = big_frame.append(frame, ignore_index=True)
    day_print = date.strftime('%d.%m.%Y')
    print(f'{day_print} Done')
print('All pages collected into dataframe')

journals = get_journals_from_file(journals_file)
journal_column_lower = big_frame['journal'].str.lower()
journal_list_lower = [j.lower() for j in journals]
big_frame = big_frame[journal_column_lower.isin(journal_list_lower)]
big_frame.index = np.arange(1, len(big_frame) + 1)
print('Filtering by journals done')
big_frame.to_excel('result.xlsx')
