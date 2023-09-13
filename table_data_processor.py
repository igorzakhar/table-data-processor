import csv
import re
import string

from collections import Counter
from itertools import chain
from itertools import zip_longest
from operator import itemgetter

import pymorphy2


def parse_csv(filename):
    with open(filename, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        table = {fieldname:[] for fieldname in reader.fieldnames}
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


def process_words(morph, words):
    processed_words = []
    tag_pos = ['NOUN', 'ADJF', 'ADJS', 'VERB','INFN', 'ADVB']
    for word in words:
        parsed_word = morph.parse(word)[0]
        if 'LATN' in parsed_word.tag or parsed_word.tag.POS in tag_pos:
            processed_words.append(parsed_word.normal_form)
    return processed_words


def collect_answers(morph, table):
    answers = {}
    for fieldname in table.keys():
        column = table[fieldname]
        answers[fieldname] = []

        for cell in column:
            words = split_by_words(cell)

            processed_words = process_words(morph, words)
            if processed_words:
                answers[fieldname].extend(processed_words)
    return answers


def count_words(table):
    word_count = {}
    for column_name in table.keys():
        answers = table[column_name]
        counter = Counter(list(answers))
        word_count[column_name] = sorted(
            [(word, count) for word, count in counter.items()],
            key=itemgetter(1),
            reverse=True
        )
    return word_count


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
    input_filename = 'survey.csv'
    table = parse_csv(input_filename)

    answer_counters = [len(answers) for _, answers in table.items()]

    answer_groups = collect_answers(morph, table)
    word_count = count_words(answer_groups)

    output_filename = 'output.csv'
    save_csv(output_filename, word_count, counters=answer_counters)


if __name__ == '__main__':
    main()
