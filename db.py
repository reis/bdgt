import sys
import sqlite3
from datetime import datetime
from dateutil.relativedelta import relativedelta
import configparser

config = configparser.ConfigParser()
config.read("config.ini")

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

class db(object):

    def __init__(self):
        self.conn = sqlite3.connect(config.get("CONFIG", "DB_FILE"), check_same_thread=False)

    def get_query(self, filename):
        # Open and read the file
        fd = open(config.get("CONFIG", "ROOT") + 'sql/' + filename, 'r')
        sqlFile = fd.read()
        fd.close()
        return sqlFile

    def get_transactions(self, month, category=None, title=None):
        self.conn.row_factory = dict_factory

        sql = """
            SELECT DATE, DESCRIPTION, CATEGORY, TITLE, AMOUNT 
            FROM transactions
            WHERE date LIKE ?
            {}
            {}
            ORDER BY 1 DESC""".format(
                "AND title = ?"    if title else "", 
                "AND category IS NULL" if category == "None" else "AND category = ?" if category else "")
        cur = self.conn.cursor()
        para = [month+"%"]
        if title:
            para.append(title)
        if category and category != "None":
            para.append(category)
        cur.execute(sql, para)

        rows = list()
        while True:
            row = cur.fetchone()
            if not row:
                break
            if " ON " in row["description"]:
                row["description"], row["realdate"] = row["description"].split(" ON ")
            row["description"] = row["description"].split(",")[0]
            row["description"] = row["description"].split("*")[-1]
            rows.append(row)

        return rows

    def get_budget_detail(self, month=datetime.now().strftime("%Y-%m")):
        self.conn.row_factory = dict_factory
        c = self.conn.cursor()
        sql = self.get_query("budget_detail.sql")
        rows = list()
        c.execute(sql, {"month": month})
        rows = c.fetchall()
        return rows

    def get_budget_extra(self, month=0):
        self.conn.row_factory = dict_factory
        c = self.conn.cursor()
        sql = self.get_query("budget_extra.sql")
        rows = list()
        c.execute(sql, {"month": month})
        rows = c.fetchall()
        return rows
