### **Tool to collect news data from from eurekalert.org**
#### Usage:
run.py [-h] [--days DAYS] [--fromdate FROMDATE] [--threshold THRESHOLD] [--notfilter]

optional arguments:

-h, --help            show this help message and exit

--days DAYS, -d Number of days related to collected news. Default = 5

--fromdate FROMDATE, -f FROMDATE From which date start parsing. Default - today. Format: dd.mm.yyyy

--threshold THRESHOLD, -t THRESHOLD Similarity threshold of journal names when compare to those used in journals.txt. Default = 0.9

--notfilter, -n Not to use filtering by journal names

--translate, -T Translate titles by yandex.translate (works with problems, better not to use).

*Translation works with help of selenium because web page is dynamic. Nevertheless it's better not to use it*
