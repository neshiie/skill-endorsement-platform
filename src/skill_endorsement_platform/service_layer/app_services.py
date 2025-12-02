"""Implements AppServices Class."""

from skill_endorsement_platform.application_base import ApplicationBase
from skill_endorsement_platform.persistence_layer.mysql_persistence_wrapper import MySQLPersistenceWrapper
import inspect
import json

class AppServices(ApplicationBase):
    """AppServices Class Definition."""
    def __init__(self, config:dict)->None:
        """Initializes object. """
        self._config_dict = config
        self.META = config["meta"]
        super().__init__(subclass_name=self.__class__.__name__,
				   logfile_prefix_name=self.META["log_prefix"])
        self.DB = MySQLPersistenceWrapper(config)
        self._logger.log_debug(f'{inspect.currentframe().f_code.co_name}:It works!')

    # params:
    # query (string) - an sql query key defined in the persistence layer dictionary
    # args  (any)    - the arguments for the sql query (e.g. name "john" or id "2")
    # return sql query result
    def query(self, query_name: str, *args):
        return self.DB.execute_sql_query(query_name, *args)

    # return query result in json format
    def query_json(self, query_name: str, *params) -> str:
        results = self.DB.execute_sql_query(query_name, *params)
        return json.dumps(results, default=str)
