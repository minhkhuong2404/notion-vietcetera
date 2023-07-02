from bs4 import BeautifulSoup
import requests

URL = 'https://kenh14.vn/'

page = requests.get(URL)

soup = BeautifulSoup(page.content, 'html.parser')

all_news = soup.find('div', class_='kbw-content')
# print(all_news)

top_news = all_news.find('div', class_='klw-featured-news mt-20')
info = top_news.find('div', class_='klwfn-left fl')
print("Tin hot nhat: " + info.text.strip())
# print(info.find('img')['src'])
print(URL + info.find('a')['href'] + '\n')

info_sub_top_news = all_news.find('div', class_='klwfn-right fr')
print("Tin hot: " + info_sub_top_news.text.strip())
# print(info_sub_top_news.find('img')['src'])
print(URL + info_sub_top_news.find('a')['href'] + '\n')

slide_news = all_news.findAll('li', class_='klwfnswn swiper-slide')
for slide_new in slide_news:
    link = slide_new.find('a')['href']
    print("Tin hot: " + slide_new.text.strip())
    try:
        print(slide_new.find('img')['src'])
    except TypeError:
        print(slide_new.find('video')['data-src'])
    print(URL + link + '\n')

scroll_news = all_news.findAll('li', class_='knswli need-get-value-facebook clearfix')
for scroll_new in scroll_news:
    link = scroll_new.find('a')['href']
    scroll_new.find('div', class_='knswli-meta').extract()
    try:
        scroll_new.find('span', class_='knswli-sapo sapo-need-trim').extract()
    except AttributeError:
        continue
    try:
        print("Tin tiep: " + scroll_new.text.strip())
        print(URL + link + '\n')
    except AttributeError:
        print("No info")
# other_news = all_news.find('div', class_='kds-new-stream-wrapper')
# print(other_news)
# listed_news = other_news.findAll('li', class_='knswli need-get-value-facebook clearfix')
notice_news = all_news.findAll('li', class_='knswli need-get-value-facebook need-get-value-facebook clearfix')
for notice_new in notice_news:
    link = notice_new.find('a')['href']
    notice_new.find('div', class_='knswli-left fl').extract()
    notice_new.find('label', class_='knswli-facebook item-fb').extract()
    notice_new.find('span', class_='knswli-view item-view').extract()

    print("Tin dang chu y: " + notice_new.text.strip())
    print(URL + link + '\n')

middle_news = all_news.find('li', class_='knswli trendAd featured-cat-new clearfix')
upper_middles = middle_news.findAll('div', class_='klwcng-left')
for upper_middle in upper_middles:
    link = upper_middle.find('a')['href']
    upper_middle.find('p').extract()
    print("Tin them: " + upper_middle.text.strip())
    print(URL + link + '\n')

lower_middles = middle_news.findAll('li', class_='klwcngrn clearfix')
for lower_middle in lower_middles:
    link = lower_middle.find('a')['href']
    print("Tin them nua: " + lower_middle.text.strip())
    print(URL + link + '\n')

all_caring_news = all_news.find('div', class_='knswli-object-content')
caring_news = all_caring_news.findAll('li', class_='koli swiper-slide')
for caring_new in caring_news:
    link = caring_new.find('a')['href']
    caring_new.find('label', class_='social-count').extract()
    caring_new.find('b').extract()
    print("Tin duoc quan tam: " + caring_new.text.strip())
    print(URL + link + '\n')
