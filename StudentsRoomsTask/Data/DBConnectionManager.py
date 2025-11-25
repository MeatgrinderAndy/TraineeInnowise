import psycopg2
import os

class DBConnectionManager():         

    def __init__(self):
        self.connection = None
        self.cursor = None

    def connect(self):
        try:
            if self.connection is None:
                self.connection = psycopg2.connect(
                    host="localhost",   
                    database="postgres",
                    user="postgres",
                    password="12345",
                    port="5433"
                )
                print('Connected succesfully!')
            else:
                print('Connection exists!')
        except Exception as e:
            print('Failed connecting! Error: ', e)

    def createCursor(self):
        try:
            if self.connection is None:
                self.connect()
            self.cursor = self.connection.cursor()
            print('Cursor was created!')
        except Exception as e:
            print('Failed creating cursor!')
    
    def close(self):
        try:
            if self.cursor is not None:
                self.cursor.close() 
                self.cursor = None
                print('Cursor was closed!')
            
            if self.connection is not None:
                self.connection.close()
                self.connection = None
                print('Connection was closed!')
            else:
                print('No active connections')
        except Exception as e:
            print('Failed to close connection! Error: ')

    


