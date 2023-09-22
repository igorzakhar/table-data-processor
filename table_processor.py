import argparse
import csv
import logging
import os
import re
import string

from collections import Counter
from itertools import chain
from itertools import combinations
from itertools import zip_longest
from operator import itemgetter

import pymorphy2

from wiki_ru_wordnet import WikiWordnet


logger = logging.getLogger(__file__)


def parse_csv(filename):
    file_abspath = os.path.abspath(filename)

    with open(file_abspath, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        table = {
            fieldname:[] for fieldname in reader.fieldnames
            if fieldname
        }

        for row in reader:
            for fieldname, value in row.items():
                if value:
                    table[fieldname].append(value)
    return table


def _clean_word(word):
    word = word.replace('«', '').replace('»', '').replace('…', '')
    word = word.strip(string.punctuation)
    word = word.replace('ё', 'е')
    return word


def split_by_words(text):
    words = set()
    for word in text.split():
        cleaned_word = _clean_word(word)
        words.add(cleaned_word)
    return words


def lemmatize(morph, words):
    lemmas = []
    tag_pos = ['NOUN', 'ADJF', 'ADJS', 'VERB','INFN', 'ADVB']

    for word in words:
        parsed_word = morph.parse(word)[0]
        if 'LATN' in parsed_word.tag or parsed_word.tag.POS in tag_pos:
            lemmas.append(parsed_word.normal_form)
    return lemmas


def count_words():
    word_counter = Counter()

    def counter(tokens):
        word_counter.update(tokens)
        return word_counter.most_common()
    return counter


def get_common_hypernyms(wikiwordnet, words, max_level=10):
    word_syns_pairs = []

    for word in words:
        synsets = wikiwordnet.get_synsets(word)
        if synsets:
            word_syns_pairs.append((word, synsets[0]))

    synsets_combinations = list(combinations(word_syns_pairs , 2))

    hypernyms_counter = Counter()

    for synset_pair1, synset_pair2 in synsets_combinations:
        word1, synset1 = synset_pair1
        word2, synset2 = synset_pair2
        common_hypernyms = wikiwordnet.get_common_hypernyms(
            synset1,
            synset2,
            max_level=max_level
        )

        if common_hypernyms:
            temp = set()
            for common_hypernym, dst1, dst2 in common_hypernyms:

                hypernyms = {
                    hypernym.lemma()
                    for hypernym in common_hypernym.get_words()
                }
                temp.update(hypernyms)
                logger.debug(f'{word1, word2} {hypernyms} {dst1 + dst2}')
            hypernyms_counter.update(temp)
    return hypernyms_counter


def process_table(morph, wordnet, table):
    answers = {}

    for fieldname in table.keys():
        column = table[fieldname]
        word_counter = count_words()
        wc = None

        for cell in column:
            words = split_by_words(cell)
            processed_words = lemmatize(morph, words)
            wc = word_counter(processed_words)
        answers[fieldname] = wc

        tokens = [token for token, _ in wc]
        hypernyms = get_common_hypernyms(wordnet, tokens)

        answers[f'{fieldname}_Гиперонимы'] = sorted(
            list(hypernyms.items()),
            key=itemgetter(1),
            reverse=True
        )
    return answers


def save_csv(filename, table, counters=None):
    with open(filename, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=',')
        if counters:
            fieldnames = list(
                chain.from_iterable((zip(table.keys(), counters)))
            )
        else:
            fieldnames = [
                elem
                for fieldname in zip(*[iter(table.keys())] * 1)
                for elem in fieldname + ('',)
            ]

        csv_writer.writerow(fieldnames)

        columns = table.values()
        rows = zip_longest(*(iter(columns)), fillvalue=('',''))

        for row in rows:
            csv_writer.writerow(list(chain.from_iterable(row)))


def process_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', help='Файл с таблицей в формате csv')
    parser.add_argument(
        '-d',
        '--debug',
        action='store_true',
        help='Вывод отладочных сообщений'
    )
    return parser.parse_args()


def main():
    log_level = logging.WARNING
    input_filename = 'table.csv'

    args = process_args()
    if args.debug:
        log_level = logging.DEBUG

    if args.file:
        input_filename = args.file

    logging.getLogger('pymorphy2').setLevel(logging.WARNING)
    logging.basicConfig(
        format='%(levelname)s:%(funcName)s: %(message)s',
        level=log_level
    )

    morph = pymorphy2.MorphAnalyzer()
    wikiwordnet = WikiWordnet()

    try:
        original_table = parse_csv(input_filename)
    except FileNotFoundError as error:
        logger.exception(error, exc_info=False)
    else:
        answer_counters = [len(answers) for _, answers in original_table.items()]

        processed_table = process_table(morph, wikiwordnet, original_table)

        output_filename = 'output.csv'
        save_csv(output_filename, processed_table)


if __name__ == '__main__':
    main()