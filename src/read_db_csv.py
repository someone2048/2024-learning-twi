import csv


def read_db_csv(path):
    with open(path, encoding='utf-8-sig') as csvfile:
        database = csv.reader(csvfile)
        database = [r for r in database]
    return database


if __name__ == '__main__':
    with open('twi.csv', encoding='utf-8-sig') as csvfile:
        database = csv.reader(csvfile)
        database = [r for r in database]
    for row in database:
        print(",   ".join(row))