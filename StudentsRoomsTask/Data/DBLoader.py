import logging
from psycopg2.extensions import cursor
logger = logging.getLogger(__name__)

class DBLoader:
    def __init__(self, cursor:cursor, rooms:list, students:list):
        self.cursor = cursor
        self.rooms = rooms
        self.students = students

    def insert(self):
        try:
            insert_rooms_query = "INSERT INTO rooms (id, name) VALUES (%s, %s) ON CONFLICT (id) DO NOTHING;"
            self.cursor.executemany(insert_rooms_query, [(room['id'], room['name']) for room in self.rooms])

            insert_students_query = "INSERT INTO students (birthday, id, name, room_id, sex) VALUES (%s, %s, %s, %s, %s) ON CONFLICT (id) DO NOTHING;"
            self.cursor.executemany(insert_students_query, [(student['birthday'], student['id'], student['name'], student['room'], student['sex']) for student in self.students])
            
            logger.info('Data inserted!')
        except Exception as e:
            logger.error(f'Couldn\'t insert data! Error: {e}')
