from langdetect import detect

from constant import EXCLUDE_FROM_KEYWORD


def extract_keyword(title):
    keyword = []
    if title.find('-') != -1:
        keyword = mergeKeyword(title, '-')
    elif title.find(':') != -1:
        keyword =  mergeKeyword(title, ':')
    elif title.find('?') != -1:
        keyword =  mergeKeyword(title, '?')
    else:
        keyword = title
    return keyword

def mergeKeyword(title:str, delimiter: str):
    keyword = []
    for word in title.split(delimiter)[0].split(' '):
        word = ''.join(c for c in word if c.lower().isalpha() or c.isspace())
        if word.isnumeric():
            continue
        try:
            if word and detect(word) != 'vi' and str(word).lower not in EXCLUDE_FROM_KEYWORD:
                keyword.append(word)
        except Exception as e_mess:
            print('Error')
            print('Word: ', word)
            print('Title: ', title)
            print('Mess: ', e_mess)
    if len(keyword) <= 2:
        return ' '.join(keyword)
    else:
        return title.split(delimiter)[0]


def pre_process(detail, is_why_it_popular=False):
    part = detail
    if is_why_it_popular and not ('phổ biến'.lower()) in part.find('h2').text:
        raise Exception("No phổ biến")
    if part.find('h2'):
        part.find('h2').extract()
    elif part.find('h3'):
        part.find('h3').extract()

    images = part.findAll('figure')

    if len(images) > 0:
        for image in images:
            image.extract()
    return part
