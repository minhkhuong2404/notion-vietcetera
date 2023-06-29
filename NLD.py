import textwrap

import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont
import os
from io import BytesIO


def createPicture(title, picture, header):
    fileName = "img.png"

    basewidth = 20
    web_pic = requests.get(picture)
    pic = Image.open(BytesIO(web_pic.content))
    wpercent = (basewidth / float(pic.size[0]))
    hsize = int((float(pic.size[1]) * float(wpercent)))
    # pic.resize((basewidth, hsize), Image.ANTIALIAS)

    MAX_W, MAX_H = 1024, 1024

    image = Image.new(mode="RGBA", size=(MAX_W, MAX_H), color="white")
    draw = ImageDraw.Draw(image)
    fontsFolder = 'Library/Fonts'
    arialFont = ImageFont.truetype(os.path.join(fontsFolder, 'BreeSerif.otf'), 32)

    current_h, pad = 50, 10
    para = textwrap.wrap(title, width=50)

    for line in para:
        w, h = draw.textsize(line, font=arialFont)
        draw.text(((MAX_W - w) / 2, current_h), line, fill="black", font=arialFont)
        current_h += h + pad

    header_info = Image.new(mode="RGBA", size=(MAX_W, MAX_H), color="white")
    info = ImageDraw.Draw(header_info)
    infos = textwrap.wrap(header, width=50)

    for line in infos:
        w, h = info.textsize(line, font=arialFont)
        info.text(((MAX_W - w) / 2, (current_h + 200) / 4), line, fill="black", font=arialFont)
        current_h += h + pad

    img_w, img_h = pic.size
    picCopy = image.copy()
    picCopy.paste(pic, ((MAX_W - img_w) // 2, (MAX_H - img_h) // 4))
    picCopy = header_info.copy()
    picCopy.paste(pic, ((MAX_W - img_w) // 2, (MAX_H - img_h) // 8))

    picCopy.save(fileName)


URL = 'https://nld.com.vn/'
page = requests.get(URL)

soup = BeautifulSoup(page.content, 'html.parser')

results = soup.find(id='admWrapsite')

news_elems = results.find_all('div', class_='body-content')
# print(news_elems)

for news_elem in news_elems:
    top_news = news_elem.find_all('div', class_='top1-focus')
    for top_new in top_news:
        link = top_new.find('a')['href']
        top_new.find('p').extract()
        print("Tin hot: " + top_new.text.strip())
        # print(top_new.find('img')['src'])
        print("https://nld.com.vn" + str(link) + "\n")
        # createPicture(top_new.text.strip(), top_new.find('img')['src'], str(top_new.find('p', class_='sapo')))

    other_news = news_elem.find_all('div', class_='news-horizontal-item')
    for other_new in other_news:
        link = other_new.find('a')['href']
        print("Tin kha hot: " + other_new.text.strip().replace('\n', '. '))
        # try:
        #     print(other_new.find('img')['src'])
        # except TypeError:
        #     print("No image")
        print("https://nld.com.vn" + str(link) + "\n")

    related_news = news_elem.find_all('div', class_='news-item')
    for related_new in related_news:
        link = related_new.find('a')['href']
        print("Tin khac: " + related_new.text.strip().replace('\n', '. '))
        # try:
        #     print(related_new.find('img')['src'])
        # except TypeError:
        #     print("No image")
        print("https://nld.com.vn" + str(link) + "\n")

    # print(top_news)
    # print(other_news)
