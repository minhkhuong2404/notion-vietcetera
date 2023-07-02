import requests
import json
import os
import random
import sys
import pytz

from multiprocessing import cpu_count, Pool

from operator import itemgetter
from datetime import datetime
from dotenv import load_dotenv

sys.path.append("..")
from constants.list_emojis import all_emojis

load_dotenv()

headers = {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9,vi;q=0.8",
    "content-type": "application/json",
}
BATCH_SIZE = 16
DATABASE_SHOPEE_ID = os.getenv("DATABASE_SHOPEE_ID")
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_PAGE_URL = 'https://api.notion.com/v1/pages'
FLASH_SALE_URL = "https://shopee.vn/api/v4/flash_sale/flash_sale_batch_get_items"

notion_headers = {
    "accept": "application/json",
    "Notion-Version": "2022-06-28",
    "content-type": "application/json",
    "Authorization": "Bearer " + NOTION_API_KEY
}


def main():
    clean_up()
    all_sessions_url = "https://shopee.vn/api/v4/flash_sale/get_all_sessions?category_personalization_type=1"
    all_categories_json = json.loads(requests.get(all_sessions_url, headers=headers).text)['data']['sessions'][0][
        'categories']
    all_categories = (list(map(itemgetter('catid', 'catname'), all_categories_json)))

    url = "https://shopee.vn/api/v4/flash_sale/flash_sale_get_items?" \
          "limit=16&need_personalize=true&offset=0&order_mode=2&sort_soldout=true&with_dp_items=true"

    response = requests.get(url, headers=headers)
    promotion_info = json.loads(response.text)['data']['items'][0]
    promotion_id, start_time, end_time = itemgetter('promotionid', 'start_time', 'end_time')(promotion_info)
    vn_tz = pytz.timezone("Asia/Bangkok")
    iso_date_start_time = datetime.utcfromtimestamp(start_time)\
        .replace(tzinfo=pytz.utc).astimezone(vn_tz).strftime("%d/%m %H:%M")
    iso_date_end_time = datetime.fromtimestamp(end_time)\
        .replace(tzinfo=pytz.utc).astimezone(vn_tz).strftime("%d/%m %H:%M")
    update_database_header(iso_date_start_time, iso_date_end_time)
    # clear content of file
    open('temp_page_id.txt', 'w').close()

    flash_sale_url = "https://shopee.vn/api/v4/flash_sale/get_all_itemids?" \
                     "need_personalize=true&order_mode=2&promotionid=" + str(promotion_id) + "&sort_soldout=true"
    all_flash_sale_items = json.loads(requests.get(flash_sale_url, headers=headers).text)['data']['item_brief_list']
    all_items_id_and_is_sold_out = list(map(itemgetter('itemid', 'is_soldout'), all_flash_sale_items))
    all_items_id = list(map(itemgetter(0), all_items_id_and_is_sold_out))

    all_items_size = all_items_id_and_is_sold_out.__len__()
    for i in range(0, all_items_size, BATCH_SIZE):
        get_flash_sale_items(promotion_id, all_items_id[i:i + BATCH_SIZE],
                             all_items_id_and_is_sold_out[i:i + BATCH_SIZE], all_categories)


def get_flash_sale_items(promotion_id, all_items_id, all_items_id_and_is_sold_out, all_categories):
    payload = {
        "promotionid": promotion_id,
        "categoryid": 0,
        "itemids": all_items_id[:BATCH_SIZE],
        "limit": BATCH_SIZE,
        "with_dp_items": True
    }

    flash_sale_items_info = \
        json.loads(requests.post(FLASH_SALE_URL, data=json.dumps(payload), headers=headers).text)['data']['items']

    flash_catid = list(map(itemgetter('flash_catid'), flash_sale_items_info))
    flash_category_name = list(filter(lambda x: x[0] == flash_catid[0], all_categories))[0][1]
    # add new attribute to flash_sale_items_info
    for item in flash_sale_items_info:
        item['flash_category_name'] = flash_category_name
        item['is_soldout'] = list(filter(lambda x: x[0] == item['itemid'], all_items_id_and_is_sold_out))[0][1]

    pool = Pool(cpu_count() - 1)
    pool.map(add_flash_sale_item_to_database, flash_sale_items_info)


def update_database_header(iso_date_start_time, iso_date_end_time):
    database_data = {
        "title": [
            {
                "text": {
                    "content": "Flash Sale " + iso_date_start_time.__str__() + " --> " + iso_date_end_time.__str__()
                }
            }
        ]
    }
    notion_database_url = 'https://api.notion.com/v1/databases/' + DATABASE_SHOPEE_ID
    requests.patch(notion_database_url, data=json.dumps(database_data), headers=notion_headers)


def add_flash_sale_item_to_database(flash_sale_item):
    promo_name, name, image, price, price_before_discount, shopid, itemid, flash_category_name, is_soldout, \
        raw_discount, is_shop_official, is_shop_preferred, flash_sale_stock, stock = \
        itemgetter('promo_name', 'name', 'image', 'price', 'price_before_discount', 'shopid', 'itemid',
                   'flash_category_name', 'is_soldout', 'raw_discount',
                   'is_shop_official', 'is_shop_preferred', 'flash_sale_stock', 'stock')(flash_sale_item)

    data = {
        "parent": {
            "database_id": DATABASE_SHOPEE_ID
        },
        "icon": {
            "emoji": random.choice(all_emojis())
        },
        "cover": {
            "external": {
                "url": "https://source.unsplash.com/featured/2048x1024"
            }
        },
        "properties": {
            "Promo Name": {
                "title": [
                    {
                        "text": {
                            "content": promo_name
                        }
                    }
                ]
            },
            "Price (VND)": {
                "number": int(str(price)[:-5])
            },
            "Price Before Discount (VND)": {
                "number": int(str(price_before_discount)[:-5])
            },
            "Discount": {
                "number": raw_discount
            },
            "Shopee Mail": {
                "checkbox": is_shop_official
            },
            "Shopee Preferred": {
                "checkbox": is_shop_preferred
            },
            "Stock Left": {
                "rich_text": [
                    {
                        "text": {
                            "content": str(round(stock / flash_sale_stock * 100,
                                                 2)) + "% (" + stock.__str__() + "/" + flash_sale_stock.__str__() + ")"
                        }
                    }
                ]
            },
            "Link Shopee": {
                "url": "https://shopee.vn/" + str(name.replace(" ", "-")) + "-i." + str(shopid) + "." + str(itemid)
            },
            "Category": {
                "select": {
                    "name": flash_category_name
                }
            },
            "Sold Out": {
                "checkbox": is_soldout
            }
        },
        "children": [
            {
                "object": "block",
                "type": "image",
                "image": {
                    "type": "external",
                    "external": {
                        "url": "https://down-vn.img.susercontent.com/file/" + image + ".jpg"
                    }
                }
            }
        ]
    }
    response = requests.post(NOTION_PAGE_URL, data=json.dumps(data), headers=notion_headers)
    try:
        page_id = json.loads(response.text)['id']
        with open('temp_page_id.txt', 'a') as f:
            f.write(page_id + "\n")
    except Exception as e:
        print("Error when adding item to database", e)
        print(response.text)


def clean_up():
    # create file if not exists
    if not os.path.exists('temp_page_id.txt'):
        open('temp_page_id.txt', 'w').close()

    with open('temp_page_id.txt', 'r') as f:
        old_flash_sale_item_ids = f.readlines()

    pool = Pool(cpu_count() - 1)
    pool.map(archive_page, old_flash_sale_item_ids)
    print("Finished archived " + old_flash_sale_item_ids.__len__().__str__() + " pages")


def archive_page(old_flash_sale):
    archive_url = NOTION_PAGE_URL + "/" + str(old_flash_sale).strip('\n')
    data = {
        "archived": True
    }
    requests.patch(archive_url, headers=notion_headers, data=json.dumps(data))


if __name__ == '__main__':
    main()
