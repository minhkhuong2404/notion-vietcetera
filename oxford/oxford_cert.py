import PyPDF2
import re
import csv
from googletrans import Translator


def main():
    pdfReader = PyPDF2.PdfReader('The_Oxford_3000_by_CEFR_level.pdf')

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
        'number': 'number',
        'modal v': 'modal verb',
        'exclam': 'exclamation',
    }

    # creating a page object
    pageObjs = pdfReader.pages
    listOfWords = []
    current_level = ''

    for page in pageObjs:
        current_level = extractWordsFromPage(page, listOfWords, mapVocab, current_level)

    translator = Translator()
    listOfWordsOnly = [word[0].strip() for word in listOfWords]
    print('Start translating words')
    translatedWords = translator.translate(listOfWordsOnly, dest='vi')
    print('End translating words')
    for idx, word in enumerate(listOfWords):
        word.insert(1, translatedWords[idx].text)

    with open('oxford_cefr.csv', 'w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerows(listOfWords)


def extractWordsFromPage(page_obj, list_of_words, map_vocab, current_level):
    for word in page_obj.extract_text().split('\n'):
        if len(word) == 0 or len(word) > 50:
            continue
        try:
            wordLevel = re.findall('[ABC][12]', word)
            if len(wordLevel) == 1:
                current_level = wordLevel[0]
                continue
            else:
                index = word.find('.')
                if index + 1 < len(word) and (word[index + 1] != ' ' and word[index + 1] != '/'):
                    word = word.replace(word[index], word[index] + '#', 1)
                    for idx, wordCollect in enumerate(word.split('#')):
                        if len(wordCollect) == 0:
                            continue
                        extractWord(wordCollect, list_of_words, current_level, map_vocab)
                    continue

                extractWord(word, list_of_words, current_level, map_vocab)

        except Exception as e:
            print(e)
            continue
    return current_level


def extractWord(word, list_of_words, current_level, map_vocab):
    realWord = ''
    typeOfWord = []
    wordCollection = word.replace('/', ' ').replace(',', ' ').split(' ')
    for idx, wordCollect in enumerate(wordCollection):
        if len(wordCollect) == 0:
            continue
        if len(re.findall('[.]', wordCollect)) == 0:
            realWord += wordCollect + ' '
        if wordCollect.__contains__('.'):
            key = map_vocab.get(wordCollect.replace('.', ''))
            typeOfWord.append(key)
        if wordCollect.__eq__(','):
            continue

    list_of_words.append([realWord.strip(), typeOfWord, current_level])


if __name__ == '__main__':
    main()
