import textwrap

import requests
from bs4 import BeautifulSoup


URL = "https://vnexpress.net/"
page = requests.get(URL)

soup = BeautifulSoup(page.content, 'html.parser')

top_news = soup.find('section', class_='section section_topstory')
lower_top_news = soup.find('section', class_='section section_topstory')
only_top_news = top_news.findAll('article', class_='item-news full-thumb article-topstory')
for only_top_new in only_top_news:
    top_news = only_top_new.find('h1', class_='title-news')
    link = top_news.find('a')['href']
    print("Tin sieu hot: " + top_news.text.strip())
    print(URL + str(link) + "\n")

only_sub_top_news = lower_top_news.findAll('div', class_='sub-news-top')
for only_sub_top_new in only_sub_top_news:
    sub_top_news = only_sub_top_new.findAll('h2', class_='title_news')
    for sub_top_new in sub_top_news:
        link = sub_top_new.find('a')['href']
        print("Tin hot: " + sub_top_new.text.strip())
        print(URL + str(link) + "\n")

more_news = soup.find('section', 'section section_container')
real = more_news.find('div', class_='container has_border flexbox')
# print(real)
lefts = real.find('div', class_='col-left col-small')
left = lefts.find_all('article', class_='item-news item-news-common')
left2 = lefts.findAll('article', class_='item-news item-news-common hidden')
for item in left:
    info = item.find('h3', class_='title-news')
    link = info.find('a')['href']
    print("Tin tuc: " + info.text.strip())
    print(URL + str(link) + "\n")

for item in left2:
    info = item.find('h3', class_='title-news')
    link = info.find('a')['href']
    print("Tin tuc: " + info.text.strip())
    print(URL + str(link) + "\n")

rights = real.find('div', class_='col-right col-medium')
right2 = rights.find('div', class_='box-category box-cate-featured has-border')


info2 = rights.find('h4', class_='title-news')
link2 = info2.find('a')['href']
print("Tin khac: " + info2.text.strip())
print(URL + str(link2) + '\n')

right_right_news = rights.findAll('div', class_='sum_gn')
for item in right_right_news:
    info = item.find('h5', class_='title-news')
    link = info.find('a')['href']
    print("Tin nua: " + info.text.strip())
    print(URL + str(link) + "\n")
