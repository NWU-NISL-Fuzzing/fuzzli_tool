from enum import Enum


class ClassificationType(Enum):
    FALSE_POSITIVE_NOTE = -1  
    FALSE_POSITIVE = 0  
    SUSPICIOUS_ENGINE_ERROR = 1  
    SUSPICIOUS_ENGINE_NO_ERROR = 2  
    SUSPICIOUS_ALL_NO_EXCEPTION_INFO = 3  


class FilterType(Enum):
    TYPE1 = 1
    TYPE2 = 2
    TYPE3 = 3
