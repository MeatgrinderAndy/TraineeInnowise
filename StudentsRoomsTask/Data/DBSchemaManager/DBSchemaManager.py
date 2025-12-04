from FileHelpers.DataReader import DataReader
import logging
from psycopg2.extensions import connection, cursor
logger = logging.getLogger()

class DBSchemaManager:
    def __init__(self, connection:connection, cursor:cursor):
        self.connection = connection
        self.cursor = cursor
        self.config = DataReader.readConfig('.\\Data\\DBSchemaManager\\queries.config')

    def createTables(self):
        try:
            self.cursor.execute(self.config['QUERIES']['CREATE_TABLES'])
            logger.info('Tables are created!')
        except Exception as e:
            logger.error(f'Couldn\'t create tables! Error: {e}')
        
    def createIndexes(self):
        try:
            self.cursor.execute(self.config['QUERIES']['CREATE_INDEXES'])
            logger.info('Indexes are created!')
        except Exception as e:
            logger.error(f'Couldn\'t create indexes! Error: {e}')
