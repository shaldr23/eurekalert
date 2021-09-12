def get_journals_from_file(journals_file):
    with open(journals_file) as f:
        journals = f.read().split('\n')
        journals = [j.strip() for j in journals]
        journals = [j for j in journals if j]
    return journals


def sort_journals(journals_file):
    journals = get_journals_from_file(journals_file)
    journals.sort()
    journals_text = '\n'.join(journals)
    with open(journals_file, 'w') as f:
        f.write(journals_text)
