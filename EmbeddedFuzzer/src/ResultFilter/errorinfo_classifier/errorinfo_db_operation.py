import json
import logging

from sqlalchemy import Column, Integer, String, Text
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class ErrorType(Base):
    __tablename__ = 'exists_errortype'    
    id = Column(Integer, primary_key=True, autoincrement=True)
    error_type = Column(Integer)
    engine = Column(String(100))
    error_info = Column(Text)
    error_api = Column(String(50))
    count = Column(Integer, default=1)
    
    def __repr__(self):
        return f"<ErrorType(engine='{self.engine}', error_info='{self.error_info}', error_api='{self.error_api}')>"


class DataBase:
    def __init__(self, db_path_url: str) -> None:        
        self.engine = create_engine(db_path_url, echo=False)
        Base.metadata.create_all(self.engine, checkfirst=True)

    def drop_all_table(self):
        Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine, checkfirst=True)

    def add(self, ErrorType: ErrorType) -> int:
        Session = sessionmaker(bind=self.engine)
        session = Session()
        type_id = 0
        try:
            session.add(ErrorType)
            session.flush()
            type_id = ErrorType.id
            session.commit()
        except Exception as e:
            raise e
        finally:
            session.close()
            return type_id

    def query_and_compare(self, _ErrorType: ErrorType) -> [bool, int]:
        Session = sessionmaker(bind=self.engine)
        session = Session()
        flag = True
        type_id = 0
        try:
            all_possible_results = session.query(ErrorType).filter(
                ErrorType.error_type == _ErrorType.error_type,
                ErrorType.engine == _ErrorType.engine,
                ErrorType.error_api == _ErrorType.error_api
                ).all()
            for possible_result in all_possible_results:  
                if DataBase.compare_two_dicts(json.loads(_ErrorType.error_info), json.loads(possible_result.error_info)):
                    flag = False
                    type_id = possible_result.id
                    possible_result.count += 1
                    session.commit()
                    break
        except Exception as e:
            logging.debug(e)
            pass
        finally:
            session.close()
            return flag, type_id

    def query_all(self, entity):
        
        Session = sessionmaker(bind=self.engine)
        session = Session()
        result = None
        try:
            result = session.query(entity).all()
        except Exception:
            pass
        finally:
            session.close()
            return result

    @staticmethod
    def compare_two_dicts(dict_a, dict_b):
        common_keys = dict_a.keys() & dict_b.keys()
        if len(common_keys) == 0:
            return False
        flag = True
        for key in common_keys:
            if dict_a[key] != dict_b[key]:
                flag = False
        return flag
