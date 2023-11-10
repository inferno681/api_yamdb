import sqlite3
import os
import csv

DIRECTORY = "./static/data"
DATA = {
    'category.csv': 'reviews_category',
    'comments.csv': 'reviews_comment',
    'genre.csv': 'reviews_genre',
    'genre_title.csv': 'reviews_genretitle',
    'review.csv': 'reviews_review',
    'titles.csv': 'reviews_title',
    'users.csv': 'reviews_user',
}


def fields_checker(required_fields, columns, data):
    for column in columns:
        if column in required_fields:
            required_fields.remove(column)
            continue
        if column + '_id' in required_fields:
            columns[columns.index(column)] = column + '_id'
            required_fields.remove(column + '_id')
    if required_fields:
        columns.extend(required_fields)
        default_values = [''] * len(required_fields)
        for value in data:
            value.extend(default_values)
    return columns, data


con = sqlite3.connect('db.sqlite3')
cur = con.cursor()
files = os.listdir(DIRECTORY)
for file in files:
    with open(f'{DIRECTORY}/{file}', 'r') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        table_name = DATA[file]
        csv_file = [i for i in spamreader]
        columns = csv_file[0]
        values_data = csv_file[1:]
        cur.execute(f'PRAGMA table_info("{table_name}")')
        required_columns = [i[1] for i in cur.fetchall()]
        columns, validate_data = fields_checker(
            required_columns, columns, values_data)
        placeholders = ', '.join(['?'] * len(columns))
        query = f"""
        INSERT INTO {table_name} ({', '.join(columns)}) 
        VALUES ({placeholders})"""
        cur.executemany(query, validate_data)
        con.commit()
con.close()
