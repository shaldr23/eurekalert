import os


def get_journals_from_file(journals_file):
    with open(journals_file) as f:
        journals = f.read().split('\n')
        journals = [j.strip() for j in journals]
        journals = [j for j in journals if j]
    return journals


def sort_journals(journals_file):
    journals = get_journals_from_file(journals_file)
    journals = list(set(journals))
    journals.sort()
    journals_text = '\n'.join(journals)
    with open(journals_file, 'w') as f:
        f.write(journals_text)


if __name__ == '__main__':
    """
    When executed by itself sort records in files
    journals.txt and ignore_journals.txt
    """
    script_dir = os.path.dirname(__file__)
    journals_file = os.path.join(script_dir, 'data/source/journals.txt')
    ignore_file = os.path.join(script_dir, 'data/source/ignore_journals.txt')
    sort_journals(journals_file)
    sort_journals(ignore_file)
    print('Journals sorting done!')
