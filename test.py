# %%
from bs4 import BeautifulSoup
import requests
import datetime

basic_url = 'https://www.eurekalert.org/news-releases/browse/all'
PAGE = 3
DATE = datetime.date.today() - datetime.timedelta(days=2)
date = DATE.strftime('%m/%d/%Y')
params = {'view': 'summaries',
          'date': date}

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
           'AppleWebKit/537.36 (KHTML, like Gecko) '
           'Chrome/83.0.4103.61 Safari/537.36'}

url = f'{basic_url}/{PAGE}'

req = requests.get(url, headers=headers, params=params)

soup = BeautifulSoup(req.text, 'html.parser')
for item in soup.select('article.post'):
    title = item.select('.post_title')[0].text
    print(title, end='\n\n')
# %%
