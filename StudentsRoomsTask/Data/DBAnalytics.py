class DBAnalytics:
    def __init__(self, cursor):
        self.cursor = cursor

    def dataDictionaryConvertation(self):
        column_names = [desc[0] for desc in self.cursor.description]
        
        rows = self.cursor.fetchall()
        data_list = []
        for row in rows:
            data_list.append(dict(zip(column_names, row)))
            
        return data_list

    def getStudentsInRoomsCount(self):
        query = '''
            SELECT 
                rooms.name, 
                COUNT(students.id) AS student_count
            FROM rooms
            LEFT JOIN students ON rooms.id = students.room_id
            GROUP BY rooms.id
            ORDER BY student_count DESC
        '''
        try:
            self.cursor.execute(query)
            return self.dataDictionaryConvertation()
        except Exception as e:
            print("Error in students in rooms counts query:", e)
            return []

    def getRoomsWithSmallesAverageAge(self):
        query = """
        SELECT 
            r.id AS room_id,
            r.name AS room_name,
            ROUND(AVG(EXTRACT(YEAR FROM AGE(NOW(), s.birthday)))::numeric, 2) AS average_age
        FROM rooms r
        JOIN students s ON r.id = s.room_id
        GROUP BY r.id, r.name
        ORDER BY average_age ASC
        LIMIT 5;
        """
        try:
            self.cursor.execute(query)
            return self.dataDictionaryConvertation()
        except Exception as e:
            print("Error in smallest average age query:", e)
            return []

    def getRoomsWithLargestAgeDifference(self):
    
        query = """
        SELECT 
            r.id AS room_id,
            r.name AS room_name,
            MAX(EXTRACT(YEAR FROM AGE(NOW(), s.birthday))) - 
            MIN(EXTRACT(YEAR FROM AGE(NOW(), s.birthday))) AS age_difference
        FROM rooms r
        JOIN students s ON r.id = s.room_id
        GROUP BY r.id, r.name
        HAVING COUNT(s.id) > 1
        ORDER BY age_difference DESC
        LIMIT 5;
        """
        try:
            self.cursor.execute(query)
            return self.dataDictionaryConvertation()
        except Exception as e:
            print("Error in largest age difference query:", e)
            return []

    def getMixedGenderRooms(self):
        query = """
        SELECT 
            r.name AS room_name
        FROM rooms r
        JOIN students s ON r.id = s.room_id
        GROUP BY r.id, r.name
        HAVING COUNT(DISTINCT s.sex) > 1
        ORDER BY r.id;
        """
        try:
            self.cursor.execute(query)
            return self.dataDictionaryConvertation()
        except Exception as e:
            print("Error in mixed gender rooms query: ", e)
            return []