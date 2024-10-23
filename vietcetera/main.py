from constant import MAX_PAGES
from vietcetera_collection import VietceteraCollection
from vietcetera_topic import VietceteraTopic
import os
import argparse

from dotenv import load_dotenv

load_dotenv()


# available topics: chat-luong-song, van-hoa-di-lam, thuong, ban-than
# available databases: DATABASE_CHAT_LUONG_SONG_ID, DATABASE_VAN_HOA_DI_LAM_ID, DATABASE_THUONG_ID, DATABASE_BAN_THAN_ID

def main():
  parser = argparse.ArgumentParser(description='Optional app description')
  parser.add_argument('-d', '--database_name', type=str,
                      help='Database environment value')

  parser.add_argument('-t','--topic', type=str,
                      help='Get by Vietcetera topic')

  parser.add_argument('-c', '--collection', type=str,
                      help='Get by Vietcetera collection')

  args = parser.parse_args()

  DATABASE_ID = args.database_name
  
  if (args.collection):
    vietcetera = VietceteraCollection(collection=args.collection, total_pages=MAX_PAGES, database_id=DATABASE_ID)
    vietcetera.getPosts()
    return
  
  vietcetera = VietceteraTopic(topic=args.topic, total_pages=MAX_PAGES, database_id=DATABASE_ID)
  vietcetera.getPosts()
  
if __name__ == '__main__':
  main()