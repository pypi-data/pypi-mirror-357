import psycopg
from psycopg import Rollback, sql
from SpUD import RFA

def progress_bar(current, total, bar_length=20):
    fraction = current / total

    arrow = int(fraction * bar_length - 1) * '-' + '>'
    padding = int(bar_length - len(arrow)) * ' '

    ending = '\n' if current == total else '\r'

    print(f'Progress: [{arrow}{padding}] {int(fraction*100)}%', end=ending)

def connect(params):
    connection = None
    print('Connecting to the PostgreSQL database {0} as user {1}...'.format(params['dbname'], params['user']))
    try:
        connection = psycopg.connect(**params)
        cursor = connection.cursor()
        with connection.transaction():
            cursor.execute('SELECT version()')
            db_version = cursor.fetchone()
            print(db_version)
        return connection
    except (Exception, psycopg.DatabaseError) as error:
        print(f'Connection Error: {error}')
        raise error

def disconnect(connection):
    connection.close()
    print('Database connection closed.')

def uploadRFAs(RFAs, connectParams, enableProgressBar=False):
    current = 0
    total = len(RFAs)
    if enableProgressBar:
        progress_bar(current, total)
    columns = RFAs[0].__dict__.keys()
    insertSQL = sql.SQL('INSERT INTO RFAs ({}) VALUES ({})').format(sql.SQL(', ').join(map(sql.Identifier, columns)), sql.SQL(', ').join(map(sql.Placeholder, columns)))
    connection = connect(connectParams)
    cursor = connection.cursor()
    with connection.transaction():
        cursor.execute('DELETE FROM RFAs')
        for rfa in RFAs:
            try:
                cursor.execute(insertSQL, vars(rfa))
            except Exception as error:
                print(f'Execute Error: {error}')
                print(f'Error on RFA with serial number: {rfa.serial_number}')
                raise Rollback()
            if enableProgressBar:
                current += 1
                progress_bar(current, total)
    if connection is not None:
        disconnect(connection)