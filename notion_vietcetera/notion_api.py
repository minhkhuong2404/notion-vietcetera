import json
import os

import requests
from dotenv import load_dotenv

load_dotenv()

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
DATABASE_ID = os.getenv("DATABASE_ID")
headers = {
    "accept": "application/json",
    "Notion-Version": "2022-06-28",
    "content-type": "application/json",
    "Authorization": "Bearer " + NOTION_API_KEY
}


def add_row_to_database(notionRows):
    url = 'https://api.notion.com/v1/pages'
    data = {
        "parent": {"database_id": DATABASE_ID},
        # "icon": {
        #     "emoji": "\U0001F5B1"
        # },
        # "cover": {
        #     "external": {
        #         "url": "https://upload.wikimedia.org/wikipedia/commons/6/62/Tuscankale.jpg"
        #     }
        # },
        "properties": {
            "Keyword": {
                "title": [
                    {
                        "text": {
                            "content": notionRows[0]
                        }
                    }
                ]
            },
            "Title": {
                "rich_text": [
                    {
                        "text": {
                            "content": notionRows[1]
                        }
                    }
                ]
            },
            "What is it?": {
                "rich_text": [
                    {
                        "text": {
                            "content": get_after_the_last_dot_most_2000_characters(notionRows[2])
                        }
                    }
                ]
            },
            "Why is it popular?": {
                "rich_text": [
                    {
                        "text": {
                            "content": get_after_the_last_dot_most_2000_characters(notionRows[3])
                        }
                    }
                ]
            },
            "Link Post": {
                "url": notionRows[4]
            },
            "Image": {
                "files": [
                    {
                        "name": notionRows[5].split('/')[-1].__str__().split('.')[0],
                        "external": {
                            "url": notionRows[5]
                        }
                    }
                ]
            },
            "Topic": {
                "select": {
                    "name": list(map(str, notionRows[6][1:-1].split(',')))[0][1:-1]
                }
            },
            "Published At": {
                "date": {
                    "start": notionRows[7]
                }
            }
        }
        # "children": []
    }

    requests.post(url, data=json.dumps(data), headers=headers)


def filter_database():
    url = "https://api.notion.com/v1/databases/" + DATABASE_ID + "/query"
    # filter payload
    payload = {
        "filter": {
            "property": "Keyword",
            "rich_text": {
                "contains": "boc term"
            }
        }
    }
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    print(response.text)


def retrieve_database():
    url = "https://api.notion.com/v1/databases/" + DATABASE_ID
    response = requests.get(url, headers=headers)

    print(response.text)


def get_after_the_last_dot_most_2000_characters(text):
    sentences = text.split(".")
    for sentence in sentences:
        first_character = sentence[0]
        if text.find(first_character) + len(sentence) < 2000:
            return text[text.find(first_character):text.find(first_character) + len(sentence)]
