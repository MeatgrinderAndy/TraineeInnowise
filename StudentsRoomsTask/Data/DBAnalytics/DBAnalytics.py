from FileHelpers.DataReader import DataReader
import logging
from psycopg2.extensions import cursor
logger = logging.getLogger(__name__)

class DBAnalytics:
    def __init__(self, cursor:cursor):
        self.cursor = cursor
        self.queriesConfig = DataReader.readConfig('.\\Data\\DBAnalytics\\queries.config')

    def dataDictionaryConvertation(self):
        column_names = [desc[0] for desc in self.cursor.description]
        
        rows = self.cursor.fetchall()
        data_list = []
        for row in rows:
            data_list.append(dict(zip(column_names, row)))
            
        return data_list

    def getStudentsInRoomsCount(self):
        try:
            self.cursor.execute(self.queriesConfig['QUERIES']['COUNT_STUDENTS_IN_ROOMS'])
            return self.dataDictionaryConvertation()
        except Exception as e:
            logger.error(f"Error in students in rooms counts query: {e}")
            return []

    def getRoomsWithSmallesAverageAge(self):
        try:
            self.cursor.execute(self.queriesConfig['QUERIES']['SMALLEST_AVG_AGE_GAP'])
            return self.dataDictionaryConvertation()
        except Exception as e:
            logger.error(f"Error in smallest average age query: {e}")
            return []

    def getRoomsWithLargestAgeDifference(self):
        try:
            self.cursor.execute(self.queriesConfig['QUERIES']['LARGEST_AGE_DIFFERENCE'])
            return self.dataDictionaryConvertation()
        except Exception as e:
            logger.error(f"Error in largest age difference query: {e}")
            return []

    def getMixedGenderRooms(self):
        try:
            self.cursor.execute(self.queriesConfig['QUERIES']['MIXED_GENDERS_ROOMS'])
            return self.dataDictionaryConvertation()
        except Exception as e:
            logger.error(f"Error in mixed gender rooms query: {e}")
            return []