import PyPDF2
import re
import csv
from googletrans import Translator


def main():
    # creating a pdf reader object
    pdfReader = PyPDF2.PdfReader('American_Oxford_5000.pdf')

    mapVocab = {
        'n': 'noun',
        'v': 'verb',
        'adj': 'adjective',
        'adv': 'adverb',
        'prep': 'preposition',
        'conj': 'conjunction',
        'pron': 'pronoun',
        'det': 'determiner',
        'num': 'number',
        'modal v': 'modal verb',
        'exclam': 'exclamation',
    }

    # creating a page object
    pageObjs = pdfReader.pages
    listOfWords = []

    # extracting text from pages
    for page in pageObjs:
        extractWordsFromPage(page, listOfWords, mapVocab)

    translator = Translator()
    listOfWordsOnly = [word[0].strip() for word in listOfWords]
    print('Start translating words')
    translatedWords = translator.translate(listOfWordsOnly, dest='vi')
    print('End translating words')
    for idx, word in enumerate(listOfWords):
        word.insert(1, translatedWords[idx].text)

    with open('oxford.csv', 'w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerows(listOfWords)


def extractWordsFromPage(page_obj, list_of_words, map_vocab):
    for word in page_obj.extract_text().split('\n'):
        if len(word) == 0 or len(word) > 50:
            continue

        try:
            wordLevels = re.findall('[ABC][12]', word)
            index = word.find(wordLevels[0])
            if index + 2 < len(word) and not word[index + 2].isspace():
                word = word.replace(wordLevels[0], wordLevels[0] + '#')
                for idx, wordCollect in enumerate(word.split('#')):
                    if len(wordCollect) == 0:
                        continue
                    extractWord(wordCollect, list_of_words, [wordLevels[idx]], map_vocab)
                continue

            extractWord(word, list_of_words, wordLevels, map_vocab)
        except Exception as e:
            print(e)
            print(word)


def extractWord(word, list_of_words, word_levels, map_vocab):
    word = re.sub('[ABC][12]', '', word)
    wordCollection = word.split(' ')
    realWord = ''
    typeOfWord = []
    for idx, wordCollect in enumerate(wordCollection):
        if len(re.findall('[.,]', wordCollect)) == 0:
            realWord += wordCollect + ' '

        if len(wordCollect) == 0:
            continue
        if wordCollect.__contains__('.') or wordCollect.__contains__('.,'):
            key = map_vocab.get(wordCollect.replace('.', '').replace(',', ''))
            typeOfWord.append(key)
        if wordCollect.__eq__(','):
            continue

    list_of_words.append([realWord.strip(), typeOfWord, word_levels])


if __name__ == '__main__':
    main()
