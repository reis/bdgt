import records
from datetime import datetime
import configparser

config = configparser.ConfigParser()
config.read("config.ini")

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

class Db(object):

    def __init__(self):
        #self.conn = sqlite3.connect(config.get("CONFIG", "DB_FILE"), check_same_thread=False)
        dsn = "postgresql://{user}:{password}@{host}/{dbname}".format(
            host=config.get("DATABASE", "HOST"),
            dbname=config.get("DATABASE", "DATABASE"),
            user=config.get("DATABASE", "USER"),
            password=config.get("DATABASE", "PASSWORD"),
        )
        self.conn = records.Database(dsn)

    def get_transactions(self, month, category=None, title=None):
        sql = """
            SELECT DATE, DESCRIPTION, CATEGORY, TITLE, AMOUNT 
            FROM transactions
            WHERE CAST(date as varchar) LIKE :month
            {}
            {}
            ORDER BY 1 DESC""".format(
                "AND title = :title"    if title else "", 
                "AND category IS NULL" if category == "None" else "AND category = :category" if category else "")
        
        params = {"month": month+"%"}
        if title:
            params["title"] = title
        if category and category != "None":
            params["category"] = category
        
        rows = self.conn.query(sql, **params).as_dict()

        for row in rows:
            if " ON " in row["description"]:
                row["description"], row["realdate"] = row["description"].split(" ON ")
                row["description"] = row["description"].split(",")[0]
                row["description"] = row["description"].split("*")[-1]

        return rows

    def get_budget_detail(self, month=datetime.now().strftime("%Y-%m")):
        rows = self.conn.query_file('sql/budget_detail.sql', month=month)
        return rows

    def get_budget_extra(self, month=0):
        rows = self.conn.query_file('sql/budget_extra.sql', month=month)
        return rows
