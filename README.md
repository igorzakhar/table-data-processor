# Обработчик табличных данных

Скрипт является вспомогательным инструментом для обработки табличных данных в формате [CSV](https://ru.wikipedia.org/wiki/CSV). Умеет разбивать текст на слова, при этом удаляет знаки препинания и пр., приводит слова к нормальной форме(лемматизация), делает подсчет каждого слова в колонках таблицы, ищет общие [гиперонимы](https://ru.wikipedia.org/wiki/Гипоним_и_гипероним) слов, подсчитывает общие гиперонимы. Результат обработки сохраняется в отдельном файле.

## Как установить

В скрипте используются следующие сторонние библиотеки:
- [pymorphy2](https://pymorphy2.readthedocs.io/en/stable/)
- [wiki-ru-wordnet](https://wiki-ru-wordnet.readthedocs.io/en/latest/)

Python3 должен быть уже установлен.

Рекомендуется устанавливать зависимости в виртуальном окружении, используя [venv](https://docs.python.org/3/library/venv.html) или любую другую реализацию, например, [virtualenv](https://github.com/pypa/virtualenv).

В примере используется модуль `venv` который появился в стандартной библиотеке python версии 3.3.

1. Скопируйте репозиторий в текущий каталог. Воспользуйтесь командой:
```bash
$ git clone https://github.com/igorzakhar/table-data-processor.git
```

После этого программа будет скопирована в каталог `table-data-processor`.

2. Создайте и активируйте виртуальное окружение:
```bash
$ cd table-data-processor # Переходим в каталог с программой
$ python3 -m venv my_virtual_environment # Создаем виртуальное окружение
$ source my_virtual_environment/bin/activate # Активируем виртуальное окружение
```

3. Установите сторонние библиотеки  из файла зависимостей:
```bash
$ pip install -r requirements.txt # В качестве альтернативы используйте pip3
```


## Запуск приложения

Скрипт работает с табличными данными в формате [CSV](https://ru.wikipedia.org/wiki/CSV).

На данный момент скрипт по умолчанию читает файл `table.csv` из текущего каталога. Но есть возможность указать имя файла с таблицей через аргумент командной строки `-f <имя файла>`, `--file <имя файла>`.

Пример запуска:
```
python table_processor.py
```

Пример запуска с указанием файла с таблицей.

```
python table_processor.py -f <имя файла>
```

## Пример использования

В качестве примера будет использоваться таблица:

| Животное | Место обитания |
| ---------| -------------- |
| Медведи из семейства млекопитающих отряда хищных. | Евразия, Северная Америка |
| Горилла самая крупная обезьянаиз отряда приматов.   |  Африка |
| Слоны - самые крупные наземные животные на Земле.     | Юго-Восточная Азия, Африка  |
| Белый медведь - самый крупный представитель семейства медвежьих и отряда хищных |Арктика |
| Азиатский слон второе по величине современное наземное животное после саванного слона |  Юго-Восточная Азия |
|Восточная горилла  — вид приматов из рода гориллы (Gorilla) семейства гоминиды |Конго, Уганда, Руанда|

### Функция `parse_csv()`

Читает `csv` файл, при этом первая строка таблицы считается строкой с заголовками. Возвращает словарь в котором каждая пара `ключ: значение` является столбцом таблицы, где ключи словаря это заголовки столбцов, а в значениях списки строк из каждой ячейки. Для таблицы из примера:
```python
>>> from table_processor import parse_csv
>>> from pprint import pprint
>>> filename = 'example.csv'
>>> table = parse_csv(filename)
>>> pprint(table)
{'Животное': ['Медведи из семейства млекопитающих отряда хищных.',
            'Горилла самая крупная обезьянаиз отряда приматов.',
            'Слоны - самые крупные наземные животные на Земле.',
            ...],

'Место обитания': ['Евразия, Северная Америка',
                   'Африка',
                   'Юго-Восточная Азия, Африка',
                    ...]}

>>>
```


### Функция `process_table()`

Основная функция где собраны все обработчики таблицы. Все столбцы таблицы обрабатываются поочередно. Сначала текст в каждой ячейке столбца разбивается на слова, при этом из текста удаляются знаки препинания, в словах буква `ё` заменяется на `е`, удаляются дубликаты слов. Затем слова приводятся к нормальной форме(лемматизация), после этого подсчитываются слова в каждом столбце. Дальше идет поиск общих гиперонимов и их подсчет для каждого столбца в отдельности.

Функция `process_table()` вызывается, когда модуль `table_processor.py` запускается напрямую и используется как скрипт. После запуска в текущем каталоге сохраняется файл `output.csv` с обработанной таблицей.

Пример использования:
```python
>>> from table_processor import parse_csv, process_table
>>> import pymorphy2
>>> from wiki_ru_wordnet import WikiWordnet
>>>
>>> morph = pymorphy2.MorphAnalyzer()
>>> input_filename = 'table.csv'
>>> table = parse_csv(input_filename)
>>> processed_table = process_table(morph, wikiwordnet, table)
>>> output_filename = 'output.csv'
>>> save_csv(output_filename, processed_table)
>>>
```

Для таблицы из примера итоговая таблица будет выглядеть так:

| Животное      |   |Животное_Гиперонимы|   |Место обитания |    |Место обитания_Гиперонимы |  |
|---------------|---|-------------------|---|---------------|----|--------------------------|--|
|семейство      |  3|животное           | 30|африка         |   2|                          |  |
|отряд          |  3|существо           | 15|азия           |   2|                          |  |
|крупный        |  3|создание           | 15|восточный      |   2|                          |  |
|самый          |  3|животина           | 15|америка        |   1|                          |  |
|горилла        |  3|скот               | 15|северный       |   1|                          |  |
|слон           |  3|тварь              | 15|евразия        |   1|                          |  |
|хищный         |  2|млекопитающее      | 10|арктика        |   1|                          |  |
|медведь        |  2|зверь              | 10|руанда         |   1|                          |  |
|примат         |  2|позвоночное        | 10|уганда         |   1|                          |  |
|...            |...|...                |...|...            | ...|                          |  |


Столбец `Место обитания_Гиперонимы` пустой т.к. гиперонимов для названий стран и континентов не нашлось.


### Функция `split_by_words()`

Разбивает произвольный текст на слова, удаляет знаки препинания, заменяет в словах букву `ё` на `е`, избавляется от дубликатов слов.

```python
>>> from table_processor import split_by_words
>>> text = 'Вечнозелёные растения это растения, листва которых сохраняется в течение всего года.'
>>> words = split_by_words(text)
>>> words
{'это', 'которых', 'листва', 'всего', 'года', 'растения', 'сохраняется', 'в', 'Вечнозеленые', 'течение'}
>>>
```

### Функция `lemmatize()`

Приводит слова к нормальной форме ([Wikipedia: Лемматизация](https://ru.wikipedia.org/wiki/Лемматизация)). Отбрасывает предлоги, союзы, междометия и пр., оставляя только следующие части речи:

|Граммема|Значение                    |Примеры                 |
|--------|----------------------------|------------------------|
|NOUN    |имя существительное         |хомяк                  |
|ADJF    |имя прилагательное (полное) |хороший                 |
|ADJS    |имя прилагательное (краткое)|хорош                   |
|VERB    |глагол (личная форма)       |говорю, говорит, говорил|
|INFN    |глагол (инфинитив)          |говорить, сказать       |
|ADVB    |наречие                     |круто                   |


Пример использования:
```python
>>> words
{'это', 'которых', 'листва', 'всего', 'года', 'растения', 'сохраняется', 'в', 'Вечнозеленые', 'течение'}
>>>
>>> from table_processor import lemmatize
>>> import pymorphy2
>>> morph = pymorphy2.MorphAnalyzer()
>>> lemmas = lemmatize(morph, words)
>>> lemmas
['который', 'листва', 'весь', 'год', 'растение', 'сохраняться', 'вечнозелёный', 'течение']
>>>
```

### Функция `count_words()`
Ведет подсчет слов для каждого столбца таблицы. Представляет из себя функцию-замыкание.


Пример использования:
```python
>>> from table_processor import count_words
>>> word_counter = count_words()
>>> words = ['листва', 'год', 'растение', 'сохраняться', 'вечнозелёный', 'течение']
>>> wc = word_counter(words)
>>> wc
[('листва', 1), ('год', 1), ('растение', 1), ('сохраняться', 1), ('вечнозелёный', 1), ('течение', 1)]
>>>
>>> other_words = ['листва', 'год', 'растение']
>>> wc = word_counter(other_words)
>>> wc
[('листва', 2), ('год', 2), ('растение', 2), ('сохраняться', 1), ('вечнозелёный', 1), ('течение', 1)]
>>>
```

### Функция `get_common_hypernyms()`
Функция является экспериментальной, алгоритм поиска и подсчета периодически будет меняться.

У списка слов ищет общие [гиперонимы](https://ru.wikipedia.org/wiki/Гипоним_и_гипероним) и подсчитывает их количество.

Пример использования:
```python
>>> from table_processor import get_common_hypernyms
>>> from wiki_ru_wordnet import WikiWordnet
>>>
>>> wikiwordnet = WikiWordnet()
>>> words = ['медведь', 'млекопитающее', 'отряд', 'хищный', 'семейство', 'примат', 'крупный', 'горилла', 'отряд', 'слон', 'крупный']
>>> hypernyms = get_common_hypernyms(wikiwordnet, words)
>>> hypernyms
Counter({'живот': 6, 'животное': 6, 'млекопитающее': 6, 'создание': 6, 'позвоночное': 6, 'существо': 6, 'тварь': 6, 'скот': 6, 'животина': 6, 'зверь': 6, 'отряд': 1, 'импозантный': 1, 'внушительный': 1, 'крупный': 1})
>>>
```
Автор библиотеки wiki_ru_wordnet в [документации](https://wiki-ru-wordnet.readthedocs.io/en/latest/) указал: "Да, у слова “живот” есть значение “животное”:)".

### Функция `save_csv()`

Сохраняет итоговый результат в файл `output.csv` в текущем каталоге.

