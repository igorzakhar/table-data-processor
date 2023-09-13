import csv
import re
import string

from collections import Counter
from itertools import chain
from itertools import zip_longest

import pymorphy2


def parse_csv(filename):
    with open(filename, 'r', newline='') as csvfile:
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


def split_by_words(text):
    words = set()
    cleaned_text = re.sub(f"[{string.punctuation}]", ' ', text).strip()
    for word in cleaned_text.split():
        normalized_word = word.replace('ё', 'е')
        words.add(normalized_word)
    return words


def lemmatize(morph, words):
    lemmas = []
    tag_pos = ['NOUN', 'ADJF', 'ADJS', 'VERB','INFN', 'ADVB']
    for word in words:
        parsed_word = morph.parse(word)[0]
        if 'LATN' in parsed_word.tag or parsed_word.tag.POS in tag_pos:
            lemmas.append(parsed_word.normal_form)
    return lemmas


def process_table(morph, table):
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
    return answers


def count_words():
    word_counter = Counter()

    def counter(tokens):
        word_counter.update(tokens)
        return word_counter.most_common()
    return counter


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


def main():
    morph = pymorphy2.MorphAnalyzer()
    input_filename = 'table.csv'
    original_table = parse_csv(input_filename)

    answer_counters = [len(answers) for _, answers in original_table.items()]

    processed_table = process_table(morph, original_table)

    output_filename = 'output.csv'
    save_csv(output_filename, processed_table)


if __name__ == '__main__':
    main()
