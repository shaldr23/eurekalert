# Program to parse articles information published in "Nature"
# using website www.nature.com/search

import argparse
from bs4 import BeautifulSoup
import requests
import time
import random
import pandas as pd
import os
"""
# ------------ Создание инструмента командной строки ------
description = ('This instrument was made to collect article titles from '
               'nature.com. Requests to the site are made with different'
               'time periods normally distribured within custom interval')
parser = argparse.ArgumentParser(description=description)
parser.add_argument('--pages', '-p', type=int, default=10,
                    help='Number of consecutive pages to parse '
                    'and download. Default = 10')
parser.add_argument('--frompage', '-fp', type=int, default=1,
                    help='From which page start parsing. Default = 1')
parser.add_argument('--mintime', '-mit', type=float, default=5,
                    help='Minimum time to wait before making another request')
parser.add_argument('--maxtime', '-mat', type=float, default=15,
                    help='Maximum time to wait before making another request')
parser.add_argument('--minif', '-mif', type=float, default=12,
                    help='Minimum impact factor for journals to filter. '
                    'Journals with unknown values will be also removed. '
                    'Set 0 for not filtering.')
parser.add_argument('--file', '-f', type=str, default='result.xlsx',
                    help='Destination file to save results. Use .xlsx extension')
parser.add_argument('--subject', '-s', type=str, default='health-sciences',
                    help='Subject of articles: https://www.nature.com/subjects/ '
                    'default = health-sciences')
args = parser.parse_args()
"""
# ------------ Функции ----------------------------------

def gauss_minmax(min_val, max_val):
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
            return result


def parse_page(soup: BeautifulSoup) -> pd.DataFrame:
    type_date = []
    for obj in soup.select('li.cleared p'):
        obj = obj.text.split('\n')
        obj = [x.strip() for x in obj if len(x.strip()) > 1][:2]
        type_date.append(obj)
    titles = [x.text.strip() for x in soup.select('li.cleared h2 a')]
    j_names = [x.text.strip().split('\n')[0] for x in soup.select('li.cleared div.mt10')]
    result = {key: [x[num] for x in type_date] for num, key in enumerate(('type', 'date'))}
    result.update({'title': titles, 'journal': j_names})
    return pd.DataFrame(result)

# ----------- Main script ----------------------------

basic_url = 'https://www.nature.com/search'
params = {'order': 'relevance',
          'subject': args.subject,
          'article_type': 'research'}

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
           'AppleWebKit/537.36 (KHTML, like Gecko) '
           'Chrome/83.0.4103.61 Safari/537.36'}
page = args.frompage
frame = pd.DataFrame()
print('Scrapping is beginning...')
while page < args.pages + args.frompage:
    new_params = params.copy()
    new_params.update({'page': page})
    req = requests.get(basic_url, params=new_params, headers=headers)
    if req.status_code == 200:
        soup = BeautifulSoup(req.text, 'html.parser')
        frame = frame.append(parse_page(soup))
        print(f'Page {page} done. DataFrame size: {len(frame)}')
    else:
        to_do = input(f'Bad status code: {req.status_code}. '
                      'Try once more/skip/finish? (T/S/F)')
        if to_do.lower() == 't':
            continue
        elif to_do.lower() == 'f':
            break
    page += 1
    # Sleep some time in the end of each iteration but not last step
    if page < args.pages + args.frompage:
        to_wait = gauss_minmax(args.mintime, args.maxtime)
        print(f'Waiting {round(to_wait, 2)} seconds...')
        time.sleep(to_wait)

frame.drop_duplicates(inplace=True)
print(f'Unique results: {len(frame)}')
program_folder = os.path.dirname(os.path.abspath(__file__))
if_table_path = os.path.join(program_folder, 'data/source/Nature_impact_factors.tsv')
IF_frame = pd.read_csv(if_table_path, sep='\t')[['Journal', '2-year Impact Factor']]
frame = pd.merge(frame, IF_frame, left_on='journal', right_on='Journal', how='left')
frame.drop(columns='Journal', inplace=True)
if args.minif:
    frame = frame[frame['2-year Impact Factor'] >= args.minif]
    print(f'Filtering done. Results count: {len(frame)}')
output_path = os.path.join(program_folder, 'data/output', args.file)
frame.to_excel(output_path)
print('The result has been saved.')
