import psycopg2
import os
import logging
from dotenv import load_dotenv
logger = logging.getLogger(__name__)

class DBConnectionManager():         

    def __init__(self):
        self.connection = None
        self.cursor = None

    def connect(self):
        try:
            if self.connection is None:
                load_dotenv()
                self.connection = psycopg2.connect(
                    host=os.getenv('DB_HOST'),   
                    database=os.getenv('DB_NAME'),
                    user=os.getenv('DB_USER'),
                    password=os.getenv('DB_PASSWORD'),
                    port=os.getenv('DB_PORT')
                )
                logger.info('Connected succesfully!')
            else:
                logger.info('Connection exists!')
        except Exception as e:
            logger.error(f'Failed connecting! Error: {e}')

    def createCursor(self):
        try:
            if self.connection is None:
                self.connect()
            self.cursor = self.connection.cursor()
            logger.info('Cursor was created!')
        except Exception as e:
            logger.error(f'Failed creating cursor! Error: {e}')
    
    def close(self):
        try:
            if self.cursor is not None:
                self.cursor.close() 
                self.cursor = None
                logger.info('Cursor was closed!')
            
            if self.connection is not None:
                self.connection.close()
                self.connection = None
                logger.info('Connection was closed!')
            else:
                logger.info('No active connections')
        except Exception as e:
            logger.error(f'Failed to close connection! Error: {e}')

    


