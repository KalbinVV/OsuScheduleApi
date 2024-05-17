from keydb import KeyDB
from keydb import ConnectionPool

pool = ConnectionPool(host='keydb')
db = KeyDB(connection_pool=pool)
