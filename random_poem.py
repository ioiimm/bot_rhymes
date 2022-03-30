import sqlite3


def random_poemf():
    con = sqlite3.connect('rhy.db')
    cur = con.cursor()
    random_poem_query = """
    SELECT DISTINCT poem, author 
    FROM rhymes
    ORDER BY RANDOM()
    LIMIT 1
    """
    cur.execute(random_poem_query)
    result = cur.fetchall()
    return result[0][0] + '\n\n' + result[0][1]
