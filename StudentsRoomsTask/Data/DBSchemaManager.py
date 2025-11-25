class DBSchemaManager:
    def __init__(self, connection, cursor):
        self.connection = connection
        self.cursor = cursor

    def createTables(self):
        try:
            createTablesQuery = '''CREATE TABLE IF NOT EXISTS rooms (
                id INTEGER PRIMARY KEY,
                name VARCHAR(50) NOT NULL UNIQUE
            );

            CREATE TABLE IF NOT EXISTS students (
                birthday TIMESTAMP,
                id INTEGER PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                room_id INTEGER REFERENCES rooms(id) ON DELETE SET NULL,
                sex VARCHAR(1) CHECK (sex in ('M', 'F'))
            );
                    '''
            self.cursor.execute(createTablesQuery)
            print('Tables are created!')
        except Exception as e:
            print('Couldn\'t create tables! Error: ', e)
        
    def createIndexes(self):
        try:
            createIndexesQuery = '''
            CREATE INDEX IF NOT EXISTS IDX_STUDENT_ROOM_ID ON students (room_id);
            CREATE INDEX IF NOT EXISTS IDX_ROOM_AGE ON students (room_id, birthday);
            CREATE INDEX IF NOT EXISTS IDX_ROOM_GENDER ON students (room_id, sex);
        '''
            self.cursor.execute(createIndexesQuery)
            print('Indexes are created!')
        except Exception as e:
            print('Couldn\'t create indexes! Error: ', e)
