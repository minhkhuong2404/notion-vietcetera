import json
import os
import requests
from dotenv import load_dotenv

load_dotenv()

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
DATABASE_BOC_TERM_ID = os.getenv("DATABASE_ID")
DATABASE_BAN_THAN_ID = os.getenv("DATABASE_BAN_THAN_ID")
headers = {
    "accept": "application/json",
    "Notion-Version": "2022-06-28",
    "content-type": "application/json",
    "Authorization": "Bearer " + NOTION_API_KEY
}


def add_row_to_database(notion_rows, database_id, row_headers):
    url = 'https://api.notion.com/v1/pages'
    data = {
        "parent": {"database_id": database_id},
        # "icon": {
        #     "emoji": "\U0001F5B1"
        # },
        # "cover": {
        #     "external": {
        #         "url": "https://upload.wikimedia.org/wikipedia/commons/6/62/Tuscankale.jpg"
        #     }
        # },
        "properties": {
            row_headers[0]: {
                "title": [
                    {
                        "text": {
                            "content": notion_rows[0]
                        }
                    }
                ]
            },
            row_headers[1]: {
                "rich_text": [
                    {
                        "text": {
                            "content": notion_rows[1]
                        }
                    }
                ]
            },
            row_headers[2]: {
                "rich_text": [
                    {
                        "text": {
                            "content": get_after_the_last_dot_most_2000_characters(notion_rows[2])
                        }
                    }
                ]
            },
            row_headers[3]: {
                "rich_text": [
                    {
                        "text": {
                            "content": get_after_the_last_dot_most_2000_characters(notion_rows[3])
                        }
                    }
                ]
            },
            row_headers[4]: {
                "url": notion_rows[4]
            },
            row_headers[5]: {
                "files": [
                    {
                        "name": str(notion_rows[5].split('/')[-1]).split('.', maxsplit=1)[0],
                        "external": {
                            "url": notion_rows[5]
                        }
                    }
                ]
            },
            row_headers[6]: {
                "select": {
                    "name": list(map(str, notion_rows[6][1:-1].split(',')))[0][1:-1]
                }
            },
            row_headers[7]: {
                "date": {
                    "start": notion_rows[7]
                }
            },
            row_headers[8]: {
                "rich_text": [
                    {
                        "text": {
                            "content": get_after_the_last_dot_most_2000_characters(notion_rows[8])
                        }
                    }
                ]
            },
            row_headers[9]: {
                "number": int(notion_rows[9])
            },
            row_headers[10]: {
                "number": int(notion_rows[10])
            },
            row_headers[11]: {
                "number": int(notion_rows[11])
            },
            row_headers[12]: {
                "number": int(notion_rows[12])
            }
        }
        # "children": []
    }

    response = requests.post(url, data=json.dumps(data), headers=headers, timeout=60)
    print(response.text)


def filter_database():
    url = "https://api.notion.com/v1/databases/" + DATABASE_BOC_TERM_ID + "/query"
    # filter payload
    payload = {
        "filter": {
            "property": "Keyword",
            "rich_text": {
                "contains": "boc term"
            }
        }
    }
    response = requests.post(url, data=json.dumps(payload), headers=headers, timeout=60)
    print(response.text)


def retrieve_database(database_id):
    url = "https://api.notion.com/v1/databases/" + database_id
    response = requests.get(url, headers=headers, timeout=60)

    print(response.text)


def get_after_the_last_dot_most_2000_characters(text):
    sentences = text.split(".")
    if len(sentences) < 2:
        return text
    for sentence in sentences:
        first_character = sentence[0] if sentence else ''
        if text.find(first_character) + len(sentence) < 2000:
            return text[text.find(first_character):text.find(first_character) + len(sentence)]
    return text


if __name__ == '__main__':
    retrieve_database(DATABASE_BAN_THAN_ID)
