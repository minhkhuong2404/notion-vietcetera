import logging
import csv

from datetime import datetime
from bs4 import BeautifulSoup
from langdetect import detect

import requests
import notion_api

# https://img.vietcetera.com/uploads/images/20-dec-2022/bocterm.jpg

IMG_LINK = "https://img.vietcetera.com/"
BLOG_LINK = "https://vietcetera.com/vn/"

API_POSTS = "https://api.vietcetera.com/client/api/v2/collection/detail?limit=12&slug=boc-term&language=VN&page="

notion_rows = []

# max 21 ???
TOTAL_PAGES = 1


def main():
    logging.basicConfig(filename='notion.log', format='%(asctime)s --- %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p',
                        level=logging.INFO)
    notion_rows.append(
        ["Keyword", "Title", "What is it?", "Why is it popular?", "Link Post", "Image", "Topic", "Published At"])
    for i in range(1, TOTAL_PAGES + 1):
        list_posts = requests.get(API_POSTS + str(i), timeout=30).json()
        for post in list_posts['data']['articles']:
            keyword = extract_keyword(post['title'])

            image_link = post['images']['url']
            image_full_link = IMG_LINK + image_link

            topics = []
            for topic in post['topic']:
                topics.append(topic['name'])
            published_at = post['publishDate']

            slug = post['slug']
            blog_full_link = BLOG_LINK + slug

            page = requests.get(blog_full_link, timeout=30)
            soup = BeautifulSoup(page.content, 'html.parser')
            try:
                content_detail = soup.find('div', class_='styles_contentWrapper__xo07n')
                detail = content_detail.find('div', class_='styles_articleContentDetail__mMd_9 article-content-detail')

                list_of_divs = detail.findAll('div')
                what_isit_part = list_of_divs[0]
                why_it_popular_part = list_of_divs[0]

                for div in list_of_divs:
                    if "1. ".lower() in div.text:
                        what_isit_part = pre_process(div, False)
                    elif "3. ".lower() in div.text:
                        why_it_popular_part = pre_process(div, False)

                if datetime.strptime(published_at, '%Y-%m-%dT%H:%M:%S.%fZ').date() == datetime.now().date():
                    notion_rows.append([keyword, post['title'],
                                        what_isit_part.text.strip().replace("\xa0", " ").replace('\n', ''),
                                        why_it_popular_part.text.strip().replace("\xa0", " ").replace('\n', ''),
                                        blog_full_link, image_full_link, topics, published_at])
                    logging.info('Done: %s', post['title'])
            except Exception as e_mess:
                print(e_mess)
        logging.info('Done page: %s/%s', str(i), str(TOTAL_PAGES))
        logging.info('Number of posts for page %s: %s', str(i), str(len(list_posts['data']['articles'])))
        logging.info('Number of posts added on %s: %s', str(datetime.now().date()), str(len(notion_rows) - 1))

    # can be used to import directly to Notion database
    with open('notion_api.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerows(notion_rows)

    with open('notion_api.csv', newline='', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter=';')
        for index, row in enumerate(reader):
            if index != 0:
                notion_api.add_row_to_database_boc_term(row)


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
        except Exception as e_mess:
            print(word)
            print(title)
            print(e_mess)
    return ' '.join(keyword)


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


if __name__ == '__main__':
    main()
