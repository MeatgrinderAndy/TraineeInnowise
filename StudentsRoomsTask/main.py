import sys
from Data.DBConnectionManager import DBConnectionManager
from Data.DBSchemaManager import DBSchemaManager
from Data.DBLoader import DBLoader
from Data.DBAnalytics import DBAnalytics
from FileHelpers.DataReader import DataReader
from FileHelpers.DataParser import DataParser

DEFAULT_ROOMS_FILES = '.\\Files\\json\\rooms.json'
DEFAULT_STUDENTS_FILES = '.\\Files\\json\\students.json'
DEFAULT_OUTPUT_FORMAT = 'json'

AMOUNT_OF_STUDENTS_FILE = '.\\Files\\output\\amount_of_students'
LARGEST_AGE_DIFFERENCE_FILE = '.\\Files\\output\\largest_age_difference'
SMALLEST_AVG_AGE_FILE = '.\\Files\\output\\smalles_avg_age'
MIXED_GENDER_ROOMS_FILE = '.\\Files\\output\\mixed_gender_rooms'


try:
    roomsFile = DEFAULT_ROOMS_FILES
    studentsFile = DEFAULT_STUDENTS_FILES
    outputFormat = DEFAULT_OUTPUT_FORMAT
    argvNum = len(sys.argv)

    if argvNum > 1:
        
        roomsFile = sys.argv[1]
    if argvNum > 2:
        studentsFile = sys.argv[2]
    if argvNum > 3:
        outputFormat = sys.argv[3]

    connectionManager = DBConnectionManager()
    connectionManager.connect()
    connectionManager.createCursor()
    
    schemaManager = DBSchemaManager(connectionManager.connection, connectionManager.cursor)
    schemaManager.createTables()
    schemaManager.createIndexes()

    rooms = DataReader.fileRead(roomsFile)
    students = DataReader.fileRead(studentsFile)

    loader = DBLoader(connectionManager.cursor, rooms, students)
    loader.insert()

    analytics = DBAnalytics(connectionManager.cursor)
    
    amountOfStudentsInRooms = analytics.getStudentsInRoomsCount()
    roomsWithLargestAgeDifference = analytics.getRoomsWithLargestAgeDifference()
    roomsWithSmallestAverageAge = analytics.getRoomsWithSmallesAverageAge()
    mixedGenderRooms = analytics.getMixedGenderRooms()

    DataParser.dataDictParser(amountOfStudentsInRooms, outputFormat, AMOUNT_OF_STUDENTS_FILE)
    DataParser.dataDictParser(roomsWithLargestAgeDifference, outputFormat, LARGEST_AGE_DIFFERENCE_FILE)
    DataParser.dataDictParser(roomsWithSmallestAverageAge, outputFormat, SMALLEST_AVG_AGE_FILE)
    DataParser.dataDictParser(mixedGenderRooms, outputFormat, MIXED_GENDER_ROOMS_FILE)

except Exception as e:
    print('Error: ', e)
finally:
    connectionManager.close()
