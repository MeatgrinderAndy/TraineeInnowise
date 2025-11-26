import sys
import logging
from Data.DBConnectionManager import DBConnectionManager
from Data.DBSchemaManager.DBSchemaManager import DBSchemaManager
from Data.DBLoader import DBLoader
from Data.DBAnalytics.DBAnalytics import DBAnalytics
from FileHelpers.DataReader import DataReader
from FileHelpers.DataParser import DataParser
logger = logging.getLogger(__name__)

try:
    config = DataReader.readConfig()
    logging.basicConfig(filename='app.log', level=logging.INFO)

    roomsFile = config['DEFAULT_PATHS']['DEFAULT_ROOMS_FILES']
    studentsFile = config['DEFAULT_PATHS']['DEFAULT_STUDENTS_FILES']
    outputFormat = config['DEFAULT_PATHS']['DEFAULT_OUTPUT_FORMAT']
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

    DataParser.dataDictParser(amountOfStudentsInRooms, outputFormat, config['OUTPUT_PATHS']['AMOUNT_OF_STUDENTS_FILE'])
    DataParser.dataDictParser(roomsWithLargestAgeDifference, outputFormat, config['OUTPUT_PATHS']['LARGEST_AGE_DIFFERENCE_FILE'])
    DataParser.dataDictParser(roomsWithSmallestAverageAge, outputFormat, config['OUTPUT_PATHS']['SMALLEST_AVG_AGE_FILE'])
    DataParser.dataDictParser(mixedGenderRooms, outputFormat, config['OUTPUT_PATHS']['MIXED_GENDER_ROOMS_FILE'])

except Exception as e:
    logger.error(f'Error: {e}')
finally:
    connectionManager.close()
