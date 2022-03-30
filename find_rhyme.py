from ru_accent_poet import accent_line
from nltk.tokenize import word_tokenize
import re
import sqlite3


# считает кол-во гласных (слогов)
def count_vowels(word):
    vowels = "аяоеуюыиэё"
    c_vowels = 0
    if word:
        for i in word:
            if i in vowels:
                c_vowels += 1
        return c_vowels


# находит номер ударного слога
def stress_position(stressed_word):  # нужно слово уже с ударением - например, результат функции accent_line('учится')
    vowels = "аяоеуюыиэё"
    word_vowels = []
    flag = 0
    if stressed_word:
        for letter in stressed_word:
            flag += 1
            if letter in vowels:
                if flag != len(stressed_word):
                    if stressed_word[flag] == "'":
                        word_vowels.extend([letter, "+"])
                    else:
                        word_vowels.append(letter)
                else:
                    word_vowels.append(letter)
        if len(word_vowels) > 1:
            if "ё" not in stressed_word:
                try:
                    stressed_position = word_vowels.index("+")
                except ValueError:
                    return None
            else:
                stressed_position = word_vowels.index("ё") + 1
        else:
            stressed_position = 1
        return stressed_position


# находит рифмующееся окончание для односложных слов
def word_piece_1(stressed_word):
    vowels = "аяоеуюыиэё"
    for i in stressed_word:
        if i in vowels and stressed_word[-1] == i:
            return stressed_word[stressed_word.index(i) - 1:]
        elif i in vowels and stressed_word[-1] != i:
            return stressed_word[stressed_word.index(i):]


# находит рифмующееся окончание для неодносложных слов
def word_piece(stressed_word):
    if "ё" in stressed_word:
        return stressed_word[stressed_word.index("ё"):]
    elif stressed_word[-1] == "'":
        return stressed_word[stressed_word.index("'") - 2:].replace("'", "")
    elif "'" in stressed_word:
        return stressed_word[stressed_word.index("'") - 1:].replace("'", "")


# ищет последнее слово в списке токенов
def find_word(line_lst):
    token = ""
    for t in reversed(line_lst):
        if re.search("[а-яА-Я]", t) and len(t) > 1:
            token = t
            break
        elif re.search("[а-яА-Я]", t) and len(t) == 1:
            new_list = list(reversed(line_lst))
            if new_list[new_list.index(t)+1] == "'":
                token = new_list[new_list.index(t)+2] + "'" + t
                break
            elif t == "я" and new_list[new_list.index(t)+1] != "'":
                token = t
                break
            else:
                continue
    return token


# обрабатывает сообщение из чата (получает нужную информацию для подбора рифмы)
def get_rhyme(given_line):
    try:
        lword = find_word(word_tokenize(given_line))
        tok_line = word_tokenize(accent_line(given_line))
        searched_rhyme = ()
        if tok_line:
            last_word = find_word(tok_line)
            if "'" not in last_word and count_vowels(last_word) > 1 and "ё" not in last_word:
                last_word += "'"
            syllable = count_vowels(last_word)
            stress_pos = stress_position(last_word)
            rhyme = ""
            if syllable == 1:
                rhyme = word_piece_1(last_word)
            elif syllable and syllable > 1:
                rhyme = word_piece(last_word)
            searched_rhyme += (syllable, stress_pos, rhyme, lword)
        return searched_rhyme
    except IndexError:
        return None


# обрабатывает результат функции get_rhyme() и находит рифмующуюся строку в базе данных
def find_rhymef(searched_rhyme):
    if searched_rhyme is None:
        return "Прости, кажется, у нас нет для тебя рифмы!\n Если хочешь попробовать еще раз, нажми /start"
    # на входе дается tuple из данных слова: количество слогов, ударный слог, рифмующееся окончание
    # далее по этим данным идет поиск в базе на соответсвие
    else:
        try:
            con = sqlite3.connect('rhy.db')
            cur = con.cursor()
            syll = searched_rhyme[0]
            stressed = searched_rhyme[1]
            rhy = searched_rhyme[2].lower()
            lw = searched_rhyme[3].lower()
            random_poem_query = """
                SELECT syllable, stress_pos, rhyme, line, poem, author, last 
                FROM rhymes
                WHERE syllable = ? AND stress_pos = ? AND rhyme = ? AND NOT last = ?
                ORDER BY RANDOM()
                LIMIT 1
                """
            cur.execute(random_poem_query, (syll, stressed, rhy, lw))
            result = cur.fetchall()
            # возвращает строку стихотворения, автора и текст стихотворения
            return result[0][3], result[0][5] + '\n\n' + result[0][4]
        except IndexError:
            return "Прости, кажется, у нас нет для тебя рифмы!\nЕсли хочешь попробовать еще раз, нажми /start"
