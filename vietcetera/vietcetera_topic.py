import csv
import logging

import requests
from datetime import datetime
from bs4 import BeautifulSoup

import notion_api
from utils import extract_keyword, pre_process
from constant import BLOG_LINK, IMG_LINK, NOTION_ROWS, VIEW_COUNTER
from dateutil.relativedelta import relativedelta


API_POSTS = "https://api.vietcetera.com/client/api/v2/topic-article?limit=10&topic[]="

class VietceteraTopic:
    def __init__(self, topic, total_pages, database_id):
        self.api_link = API_POSTS + str(topic) + "&page=";
        self.topic = topic
        self.total_pages = total_pages
        self.database_id = database_id

    def getPosts(self):
      logging.basicConfig(filename='log/notion-' + str(self.topic) + '.log', format='%(asctime)s --- %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p', level=logging.INFO)
      for i in range(1, self.total_pages + 1):
          list_posts = requests.get(self.api_link + str(i), timeout=30).json()
          print('Processing page ', self.api_link + str(i))
          if len(list_posts['data']['docs']) == 0:
              print('No more posts in this topic ', str(self.topic))
              break
          for post in list_posts['data']['docs']:
              keyword = extract_keyword(post['title'])
              image_link:str = post['images']['url']
              image_full_link:str = IMG_LINK + image_link

              topics = []
              for topic in post['topic']:
                  topics.append(topic['name'])
              published_at = post['publishDate']

              article_id:str = post['_id']

              title:str = post['title']
              excerpt:str = post['excerpt']

              slug:str = post['slug']
              blog_full_link = BLOG_LINK + slug

              page = requests.get(blog_full_link, timeout=30)
              soup = BeautifulSoup(page.content, 'html.parser')

              payload = {
                  "articleId": article_id,
                  "actionDate": datetime.time,
                  "userTimezone": "Asia/Saigon",
                  "platform": "desktop-web"
              }
              view_counter = requests.post(VIEW_COUNTER, data=payload, timeout=30).json()
              total_likes = view_counter['data']['article']['totalLike']
              total_views = view_counter['data']['article']['views']
              views_per_hour = view_counter['data']['article']['viewsArticle']['1h_TopView'] if '1h_TopView' in view_counter['data']['article']['viewsArticle'] else 0
              views_per_day = view_counter['data']['article']['viewsArticle']['1d_TopView'] if '1d_TopView' in view_counter['data']['article']['viewsArticle'] else 0

              self.process_post(article_id, blog_full_link, image_full_link, keyword, post, published_at, soup, title, topics, excerpt, total_likes, total_views, views_per_hour, views_per_day)
          print('Done: page ', str(i))
          logging.info('Done page: %s/%s', str(i), str(self.total_pages))
          logging.info('Number of posts for page %s: %s', str(i), str(len(list_posts['data']['docs'])))
          logging.info('Number of posts added on %s: %s', str(datetime.now().date()), str(len(NOTION_ROWS) - 1))

      # can be used to import directly to Notion database
      with open('notion_api.csv', 'w', newline='', encoding='utf-8') as file:
          writer = csv.writer(file, delimiter=';')
          writer.writerows(NOTION_ROWS)

      with open('notion_api.csv', newline='', encoding='utf-8') as file:
          reader = csv.reader(file, delimiter=';')
          for index, row in enumerate(reader):
              if index != 0:
                  notion_api.add_row_to_database(row, self.database_id, NOTION_ROWS[0])


    def process_post(self, article_id, blog_full_link, image_full_link, keyword, post, published_at, soup,
                  title, topics, excerpt, total_likes, total_views, views_per_hour, views_per_day):
      try:
          content_detail = soup.find('div', class_='styles_contentWrapper__xo07n')
          if content_detail is None:
              return
          detail = content_detail.find('div', class_='styles_articleContentDetail__mMd_9 article-content-detail')

          list_of_divs = detail.findAll('div')
          introduction = None
          explanation = None
          has_introduction = False
          for idx, div in enumerate(list_of_divs):
              part = div.find('h2')
              if idx == 0 and part is None:
                  has_introduction = True
              if part is not None and div is not None:
                  if has_introduction:
                      if idx == 1:
                          introduction = div
                      elif idx == 2:
                          explanation = div
                  else:
                      if idx == 0:
                          introduction = div
                      elif idx == 1:
                          explanation = div
                  if "1. ".lower() in div.text:
                      introduction = pre_process(div, False)
                  elif "3. ".lower() in div.text:
                      explanation = pre_process(div, False)
                  images = part.findAll('figure')

                  if len(images) > 0:
                      for image in images:
                          image.extract()
          introduction = introduction.text.strip().replace("\xa0", " ").replace('\n', '') if introduction is not None else ''
          explanation = explanation.text.strip().replace("\xa0", " ").replace('\n', '') if explanation is not None else ''
          # fromTime = datetime.strptime("2024-10-23", "%Y-%m-%d")
          if datetime.strptime(published_at, '%Y-%m-%dT%H:%M:%S.%fZ').date() == datetime.now().date():
              NOTION_ROWS.append([keyword, title,
                                  introduction,
                                  explanation,
                                  blog_full_link, image_full_link, topics, published_at, excerpt, total_likes, total_views, views_per_hour, views_per_day])
              logging.info('Done post: %s', post['title'])
      except requests.exceptions.RequestException as e:
          print(f"Request error: {e}")
