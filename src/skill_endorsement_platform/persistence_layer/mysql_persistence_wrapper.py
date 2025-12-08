"""Defines the MySQLPersistenceWrapper class."""

from skill_endorsement_platform.application_base import ApplicationBase
from mysql import connector
from mysql.connector.pooling import (MySQLConnectionPool)
import inspect
import json

class MySQLPersistenceWrapper(ApplicationBase):
    """Implements the MySQLPersistenceWrapper class."""

    def __init__(self, config:dict)->None:
        """Initializes object. """
        self._config_dict = config
        self.META = config["meta"]
        self.DATABASE = config["database"]
        super().__init__(subclass_name=self.__class__.__name__,
                   logfile_prefix_name=self.META["log_prefix"])
        self._logger.log_debug(f'{inspect.currentframe().f_code.co_name}:It works!')

        # Database Configuration Constants
        self.DB_CONFIG = {}
        self.DB_CONFIG['database'] = \
            self.DATABASE["connection"]["config"]["database"]
        self.DB_CONFIG['user'] = self.DATABASE["connection"]["config"]["user"]
        self.DB_CONFIG['host'] = self.DATABASE["connection"]["config"]["host"]
        self.DB_CONFIG['port'] = self.DATABASE["connection"]["config"]["port"]

        self._logger.log_debug(f'{inspect.currentframe().f_code.co_name}: DB Connection Config Dict: {self.DB_CONFIG}')

        # Database Connection
        self._connection_pool = self._initialize_database_connection_pool(self.DB_CONFIG)

        self.QUERIES = {
            # user queries
            "get all users":        "SELECT * FROM users",
            "get users by name":    "SELECT * FROM users WHERE username LIKE %s",
            "get users by id":      "SELECT * FROM users WHERE user_id = %s",
            "get users by role":    "SELECT * FROM users WHERE role = %s",

            "get user id":          "SELECT user_id FROM users WHERE username = %s",

            "remove user":          "DELETE FROM users WHERE username = %s",

            "add user": """
                INSERT INTO users (
                    username,
                    email,
                    full_name,
                    role
                ) VALUES (%s, %s, %s, %s)
            """,

            "view users":   "SELECT * FROM users",
            "view skills":  "SELECT * FROM skills",

            # skills queries
            "get all skills":       "SELECT * FROM skills",
            "get skills by name":   "SELECT * FROM skills WHERE name LIKE %s",
            "get skills by cat":    "SELECT * FROM skills WHERE category LIKE %s",

            "get skill id":         "SELECT skill_id FROM skills WHERE name = %s",

            "remove skill":         "DELETE FROM skills WHERE name = %s",

            "add skill": """
                    INSERT INTO skills (
                        name,
                        category,
                        description
                    ) VALUES (%s, %s, %s)""",
            # endorsement queries
            "get all endorsements":         "SELECT * FROM endorsements_xref",

            "add endorsement": """
                INSERT INTO endorsements_xref (
                    endorser_id,
                    endorsee_id,
                    skill_id,
                    comment,
                    rating
                ) VALUES (%s, %s, %s, %s, %s)
            """,

            "get endorsements by endorser":
            "SELECT * FROM endorsements_xref WHERE endorser_id = %s",

            "get endorsements by endorsee":
            "SELECT * FROM endorsements_xref WHERE endorsee_id = %s",

            # user skills queries
            "get all user skills":          "SELECT * FROM user_skills_xref",

            "get user skills by user id":   """SELECT * FROM user_skills_xref
                                                WHERE user_id = %s""",

            "get user skills by skill id":  """SELECT * FROM user_skills_xref
                                                WHERE skill_id = %s""",
            "add user skill": """
                INSERT INTO skills_xref (
                    user_id,
                    skill_id,
                    proficiency_level,
                    years_experience,
                ) VALUES(%s, %s, %s, %s)
            """
        }

    # MySQLPersistenceWrapper Methods
    def execute_sql_query(self, query_name: str, *params):
        results = None
        try:
            # get pooled connection
            connection = self._connection_pool.get_connection()
            with connection:
                cursor = connection.cursor(dictionary=True)
                with cursor:
                    sql = self.QUERIES[query_name]
                    cursor.execute(sql, params)
                    if ("add" in query_name) or ("remove" in query_name):
                        connection.commit()
                    results = cursor.fetchall()

        except Exception as e:
            self._logger.log_error(
                f"[PersistenceLayer] Query failed: {query_name}: {e}"
            )

        return results




        ##### Private Utility Methods #####

    def _initialize_database_connection_pool(self, config:dict)->MySQLConnectionPool:
        """Initializes database connection pool."""
        try:
            self._logger.log_debug(f'Creating connection pool...')
            cnx_pool = \
                MySQLConnectionPool(pool_name = self.DATABASE["pool"]["name"],
                    pool_size=self.DATABASE["pool"]["size"],
                    pool_reset_session=self.DATABASE["pool"]["reset_session"],
                    **config)
            self._logger.log_debug(f'{inspect.currentframe().f_code.co_name}: Connection pool successfully created!')
            return cnx_pool
        except connector.Error as err:
            self._logger.log_error(f'{inspect.currentframe().f_code.co_name}: Problem creating connection pool: {err}')
            self._logger.log_error(f'{inspect.currentframe().f_code.co_name}: Check DB cnfg:\n{json.dumps(self.DATABASE)}')
        except Exception as e:
            self._logger.log_error(f'{inspect.currentframe().f_code.co_name}:Problem creating connection pool: {e}')
            self._logger.log_error(f'{inspect.currentframe().f_code.co_name}:Check DB conf:\n{json.dumps(self.DATABASE)}')
