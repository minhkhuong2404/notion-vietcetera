import logging

from bs4 import BeautifulSoup
from langdetect import detect
from datetime import datetime

import requests
import csv
import notion_api

# https://img.vietcetera.com/uploads/images/20-dec-2022/bocterm.jpg

IMG_LINK = "https://img.vietcetera.com/"
BLOG_LINK = "https://vietcetera.com/vn/"

apiPosts = "https://api.vietcetera.com/client/api/v2/collection/detail?limit=12&slug=boc-term&language=VN&page="

notionRows = []

# max 21 ???
totalPages = 1


def main():
    logging.basicConfig(filename='notion.log', format='%(asctime)s --- %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p', level=logging.INFO)
    notionRows.append(
        ["Keyword", "Title", "What is it?", "Why is it popular?", "Link Post", "Image", "Topic", "Published At"])
    for i in range(1, totalPages + 1):
        listPosts = requests.get(apiPosts + str(i)).json()
        for post in listPosts['data']['articles']:
            keyword = extract_keyword(post['title'])

            image_link = post['images']['url']
            image_full_link = IMG_LINK + image_link

            topics = []
            for topic in post['topic']:
                topics.append(topic['name'])
            published_at = post['publishDate']

            slug = post['slug']
            blog_full_link = BLOG_LINK + slug

            page = requests.get(blog_full_link)
            soup = BeautifulSoup(page.content, 'html.parser')
            try:
                contentDetail = soup.find('div', class_='styles_contentWrapper__xo07n')
                detail = contentDetail.find('div', class_='styles_articleContentDetail__mMd_9 article-content-detail')

                listOfDivs = detail.findAll('div')
                whatIsitPart = listOfDivs[0]
                whyItPopularPart = listOfDivs[0]

                for div in listOfDivs:
                    if div.text.__contains__("1. ".lower()):
                        whatIsitPart = pre_process(div, False)
                    elif div.text.__contains__("3. ".lower()):
                        whyItPopularPart = pre_process(div, False)

                if datetime.strptime(published_at, '%Y-%m-%dT%H:%M:%S.%fZ').date() == datetime.now().date():
                    notionRows.append([keyword, post['title'],
                                       whatIsitPart.text.strip().replace("\xa0", " ").replace('\n', ''),
                                       whyItPopularPart.text.strip().replace("\xa0", " ").replace('\n', ''),
                                       blog_full_link, image_full_link, topics, published_at])
                    logging.info('Done: ' + post['title'])
            except Exception as e:
                print(e)
        logging.info('Done page: ' + str(i) + '/' + str(totalPages))
        logging.info('Number of posts for page ' + str(i) + ': ' + str(len(listPosts['data']['articles'])))
        logging.info('Number of posts added on ' + datetime.now().date().__str__() + ": " + str(len(notionRows) - 1))

    # can be used to import directly to Notion database
    with open('notion_api.csv', 'w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerows(notionRows)

    with open('notion_api.csv', newline='') as file:
        reader = csv.reader(file, delimiter=';')
        for index, row in enumerate(reader):
            if index != 0:
                notion_api.add_row_to_database(row)


def extract_keyword(title):
    if title.find('-') != -1:
        return mergeKeyword(title, '-')
    if title.find(':') != -1:
        return mergeKeyword(title, ':')
    if title.find('?') != -1:
        return mergeKeyword(title, '?')


def mergeKeyword(title, delimiter):
    keyword = []
    for word in title.split(delimiter)[0].split(' '):
        try:
            if word and detect(word) != 'vi':
                keyword.append(word)
        except Exception as e:
            print(word)
            print(title)
            print(e)
    return ' '.join(keyword)


def pre_process(detail, is_why_it_popular=False):
    part = detail
    if is_why_it_popular and not part.find('h2').text.__contains__('phổ biến'.lower()):
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


if __name__ == '__main__':
    main()
