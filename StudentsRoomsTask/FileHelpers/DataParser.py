import json
import xml.etree.ElementTree as ET
from xml.dom import minidom
from pathlib import Path
from decimal import Decimal
import logging
logger = logging.getLogger(__name__)

class DataParser:
    @staticmethod
    def xmlParse(dictionary, rootTag='root'):
        def _to_xml(element, data):
            if isinstance(data, dict):
                for key, value in data.items():
                    child = ET.SubElement(element, str(key))
                    _to_xml(child, value)
            elif isinstance(data, list):
                for item in data:
                    child = ET.SubElement(element, 'item')
                    _to_xml(child, item)
            else:
                element.text = str(data)
        
        root = ET.Element(rootTag)
        _to_xml(root, dictionary)
        
        rough_string = ET.tostring(root, encoding='utf-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")


    @staticmethod
    def jsonParse(dictionary, indent=2, ensure_ascii=False):
        def decimal_default(obj):
            if isinstance(obj, Decimal):
                return float(obj) 
        
        return json.dumps(
            dictionary, 
            indent=indent, 
            ensure_ascii=ensure_ascii,
            default= decimal_default,
            sort_keys=True
        )

    @classmethod
    def dataDictParser(cls, data:dict, format, filePath):
        outputData = None
        try:
            if format == 'xml':
                outputData = cls.xmlParse(data, 'QueryRows') 
            elif format == 'json':
                outputData = cls.jsonParse(data)
            else:
                raise Exception(f'Format {format} is not supported!')

            file_path = Path(filePath + '.' + format)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(outputData)
        except Exception as e:
            logger.error(f'Error while parsing data: {e}')
        