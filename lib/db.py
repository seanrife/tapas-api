from time import sleep
from contextlib import contextmanager
from psycopg2.pool import ThreadedConnectionPool
from config import db

AVAILABLE_POOLS = ['tapas']
connections = {}


class Connections:

    _available_pools = ['tapas']
    _pools = {}

    def __getitem__(self, database):
        pool = self._pools.get(database, None)
        if database not in AVAILABLE_POOLS:
            raise ValueError('Error. DB not in pool list.')

        if not pool:
            self.init_pool(database)
            pool = self._pools[database]

        return pool

    def init_pool(self, database, retries=3, retry_count=0, retry_wait=3):
        try:
            self._pools[database] = ThreadedConnectionPool(
                1,
                30,
                host=db['host'],
                user=db['user'],
                password=db['passwd'],
                dbname=db['db']
            )
        except Exception as e:
            print("Failed to connect to db")
            print(str(e))

            if retry_count < retries:
                print("Attempting to reconnect to db.")
                sleep(retry_wait)
                self.init_pool(database, retry_count=(retry_count + 1))


connections = Connections()


@contextmanager
def get_cursor(database='tapas', commit=False, cursor_factory=None):

    pool = connections[database]
    conn = pool.getconn()
    cursor = conn.cursor(
        cursor_factory=cursor_factory
    )
    try:
        yield cursor
        if commit:
            conn.commit()
    finally:
        cursor.close()
        pool.putconn(conn)
