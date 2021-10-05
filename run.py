# %%
from bs4 import BeautifulSoup
import requests
import datetime
import pandas as pd
import numpy as np
from journal_tools import get_journals_from_file
from difflib import SequenceMatcher
import re
import argparse
import os

# ------------------ Functions ---------------------------------------------


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


def similarity(a, b, skip_pattern=None):
    """
    Count similarity between two strings
    """
    if skip_pattern:
        a = re.sub(skip_pattern, '', a)
        b = re.sub(skip_pattern, '', b)
    s = SequenceMatcher(None, a, b)
    return s.ratio()


def similar_to_any_element(cell: str, elements: list,
                           similarity_threshold: float) -> bool:
    """
    Function to use in pd.Series.apply() method
    """
    similarities = [similarity(cell, elem) for elem in elements]
    over_threshold = [sim >= similarity_threshold for sim in similarities]
    return any(over_threshold)


# ------------ Command line tool ------------------------------------

description = 'Tool to collect news data from from eurekalert.org'
parser = argparse.ArgumentParser(description=description)
parser.add_argument('--days', '-d', type=int, default=5,
                    help='Number of days related to collected news. Default = 5')
parser.add_argument('--fromdate', '-f', type=str,
                    default=datetime.date.today().strftime('%d.%m.%Y'),
                    help='From which date start parsing. Default - today. '
                    'Format: dd.mm.yyyy')
parser.add_argument('--threshold', '-t', type=float, default=.9,
                    help='Similarity threshold of journal names when compare '
                    'to those used in journals.txt. Default = 0.9')
parser.add_argument('--notfilter', '-n', action='store_true',
                    help='Not to use filtering by journal names')
args = parser.parse_args()

# ---------------- Variables ----------------------------------------

FROM_DATE = datetime.datetime.strptime(args.fromdate, '%d.%m.%Y')
DAYS = args.days
JOURNAL_SIMILARITY_THRESHOLD = args.threshold
NOT_FILTER = args.notfilter

basic_url = 'https://www.eurekalert.org/news-releases/browse/all'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
           'AppleWebKit/537.36 (KHTML, like Gecko) '
           'Chrome/83.0.4103.61 Safari/537.36'}
script_dir = os.path.dirname(__file__)
results_dir = os.path.join(script_dir, 'data/results')
journals_file = os.path.join(script_dir, 'data/source/journals.txt')
ignore_file = os.path.join(script_dir, 'data/source/ignore_journals.txt')

# --------------- Main script -------------------------------------

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
ordered_columns = ['title', 'journal', 'abstract', 'date', 'page', 'link']
big_frame = big_frame[ordered_columns]

if not NOT_FILTER:
    journals = get_journals_from_file(journals_file)
    ignore_journals = get_journals_from_file(ignore_file)
    journal_column_lower = big_frame['journal'].str.lower()
    journal_list_lower = [j.lower() for j in journals]
    is_good_journal = journal_column_lower.apply(similar_to_any_element,
                                                 args=(journal_list_lower,
                                                       JOURNAL_SIMILARITY_THRESHOLD))
    big_frame = big_frame[is_good_journal]
    big_frame = big_frame[~big_frame['journal'].isin(ignore_journals)]
    print('Filtering by journals done')

big_frame.index = np.arange(1, len(big_frame) + 1)
now = datetime.datetime.now().strftime('%d.%m.%Y_%Hh%Mm%Ss')
result_file = os.path.join(results_dir, f'result_{now}.xlsx')
big_frame.to_excel(result_file)
print('Result saved into .../data/results')
