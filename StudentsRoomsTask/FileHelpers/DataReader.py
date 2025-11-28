import os
import json
from configparser import ConfigParser

class DataReader:
    @staticmethod
    def checkAccessability(filePath:str):
        if not os.path.exists(filePath):
            raise Exception(f"File {filePath} does not exist!")
        if not os.path.isfile(filePath):
            raise Exception(f"{filePath} is not a file!")
        return True

    @classmethod
    def fileRead(cls, filePath:str):
        if cls.checkAccessability(filePath):
            with open(filePath, 'r') as file:
                json_data = json.load(file) 
                return json_data
            
    
    @classmethod
    def readConfig(cls, configPath:str='./.config'):
        config = ConfigParser()
        config.read(configPath)
        return config