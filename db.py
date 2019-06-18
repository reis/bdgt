import os
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
        self.conn = records.Database(os.environ['DATABASE_URL'])

    def get_transactions(self, month, category=None, title=None):
        sql = """
            SELECT DATE, DESCRIPTION, CATEGORY, TITLE, AMOUNT, BALANCE
            FROM transactions
            WHERE pay_month = :month
            {}
            {}
            ORDER BY AMOUNT""".format(
                "AND title = :title"    if title else "", 
                "AND category IS NULL" if category == "None" else "AND category = :category" if category else "")
        
        params = {"month": month+'-01'}
        if title:
            params["title"] = title
        if category and category != "None":
            params["category"] = category
        
        rows = self.conn.query(sql, **params).as_dict()
        total = 0
        for row in rows:
            total += row["amount"]
            if " ON " in row["description"]:
                row["description"], row["realdate"] = row["description"].split(" ON ")
                row["description"] = row["description"].split(",")[0]
                row["description"] = row["description"].split("*")[-1]
        row_total = {
            "description": "TOTAL",
            "amount": total,
            "balance": 0.00
        }
        rows.append(row_total)

        return rows

    def get_budget_detail(self, month=datetime.now().strftime("%Y-%m")):
        rows = self.conn.query_file('sql/budget_detail.sql', month=month)

        budget_total, spent_total = 0, 0
        previtem = []
        i=1

        result = dict()
        for row in rows:
            if previtem and previtem["ord"] != row["ord"]:
                result[("BALANCE {}".format(previtem['ord']),previtem['ord'])] = {
                    'category': "BALANCE {}".format(previtem['ord']),
                    'title': None,
                    'ord': i,
                    'budget': budget_total,
                    'date': None,
                    'spent': spent_total
                }
            result[(row['category'],row['title'])] = {
                'category': row['category'],
                'title': row['title'],
                'ord': row['ord'],
                'budget': row['budget'],
                'date': row['date'],
                'spent': row['spent']
            }
            spent_total  = spent_total  + row['spent']
            budget_total = budget_total + row['budget']
            previtem = dict(row)
        
        result[("BALANCE",previtem['ord'])] = {
            'category': "BALANCE",
            'title': None,
            'ord': previtem['ord'],
            'budget': budget_total,
            'spent': spent_total
        }
        return result

    def get_budget_extra(self, month=0):
        rows = self.conn.query_file('sql/budget_extra.sql', month=month)
        return rows

    def get_payday(self, month):
        rows = self.conn.query_file('sql/payday.sql', month=month)
        return rows[0]

    def get_paymonth_spends(self, payday):
        rows = self.conn.query_file('sql/paymonth_spends.sql', payday=payday)
        return [dict(row) for row in rows]

    def get_myquery(self):
        rows = self.conn.query_file('sql/myquery.sql')
        return [dict(row) for row in rows]