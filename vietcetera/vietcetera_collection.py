import logging
import csv

from datetime import datetime
from bs4 import BeautifulSoup

import requests
from dotenv import load_dotenv

import notion_api
from constant import BLOG_LINK, IMG_LINK, NOTION_ROWS, VIEW_COUNTER
from utils import extract_keyword, pre_process

load_dotenv()

# https://img.vietcetera.com/uploads/images/20-dec-2022/bocterm.jpg

API_POSTS = "https://api.vietcetera.com/client/api/v2/collection/detail?limit=12&slug="


class VietceteraCollection:
		def __init__(self, total_pages, collection: str, database_id: str):
				self.total_pages = total_pages
				self.collection = collection
				self.api_link = API_POSTS + str(self.collection) + '&language=VN&page='
				self.database_id = database_id
		def getPosts(self):
				logging.basicConfig(filename='log/notion-' + str(self.collection) + '.log', format='%(asctime)s --- %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p',
														level=logging.INFO)
				for i in range(1, self.total_pages + 1):
						list_posts = requests.get(self.api_link + str(i), timeout=30).json()
						print('Processing page ', self.api_link + str(i))
						if len(list_posts['data']['articles']) == 0:
								print('No more posts in this collection ', str(self.collection))
								break
						for post in list_posts['data']['articles']:
								keyword = extract_keyword(post['title'])

								image_link = post['images']['url']
								image_full_link = IMG_LINK + image_link

								topics = []
								for topic in post['topic']:
										topics.append(topic['name'])
								published_at = post['publishDate']
								article_id:str = post['_id']
								excerpt:str = post['excerpt']
								slug = post['slug']
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
								views_per_hour = view_counter['data']['article']['viewsArticle']['1h_TopView']
								views_per_day = view_counter['data']['article']['viewsArticle']['1d_TopView']

								try:
										content_detail = soup.find('div', class_='styles_contentWrapper__xo07n')
										detail = content_detail.find('div', class_='styles_articleContentDetail__mMd_9 article-content-detail')

										list_of_divs = detail.findAll('div')
										what_is_it_part = list_of_divs[0]
										why_it_popular_part = list_of_divs[0]


										for div in list_of_divs:
												if "1. ".lower() in div.text:
														what_is_it_part = pre_process(div, False)
												elif "3. ".lower() in div.text:
														why_it_popular_part = pre_process(div, False)

										if datetime.strptime(published_at, '%Y-%m-%dT%H:%M:%S.%fZ').date() == datetime.now().date():
												NOTION_ROWS.append([keyword, post['title'],
																						what_is_it_part.text.strip().replace("\xa0", " ").replace('\n', ''),
																						why_it_popular_part.text.strip().replace("\xa0", " ").replace('\n', ''),
																						blog_full_link, image_full_link, topics, published_at, excerpt, total_likes, total_views, views_per_hour, views_per_day])
												logging.info('Done: %s', post['title'])
								except Exception as e_mess:
										print(e_mess)
						logging.info('Done page: %s/%s', str(i), str(self.total_pages))
						logging.info('Number of posts for page %s: %s', str(i), str(len(list_posts['data']['articles'])))
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
