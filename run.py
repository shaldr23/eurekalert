# %%
from bs4 import BeautifulSoup
import requests
import datetime
import pandas as pd
from journal_tools import get_journals_from_file


def get_text_from_item(item, selector):
    try:
        text = item.select(selector)[0].text.strip()
    except IndexError:
        text = ''
    return text


def frame_from_request(req: requests.Request):
    soup = BeautifulSoup(req.text, 'html.parser')
    frame = pd.DataFrame()
    for item in soup.select('article.post'):
        element = {}
        element['title'] = get_text_from_item(item, '.post_title')
        element['abstract'] = get_text_from_item(item, '.intro')
        element['journal'] = get_text_from_item(item, '.dl-horizontal em')
        frame = frame.append(element, ignore_index=True)
    return frame


FROM_DATE = datetime.date.today()
DAYS = 5
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
        frame['date'] = date
        frame['page'] = page
        big_frame = big_frame.append(frame, ignore_index=True)
    day_print = date.strftime('%d.%m.%Y')
    print(f'{day_print} Done')
print('All pages collected into dataframe')

journals = get_journals_from_file(journals_file)
big_frame = big_frame[big_frame['journal'].isin(journals)]
print('Filtering by journals done')

big_frame.to_excel('result.xlsx')
