import os
import re
import sqlite3
import datetime
import sys
from pprint import pprint


conn = sqlite3.connect("db/beta.db")
c = conn.cursor()

path = 'import/new/'
for fn in os.listdir(path):
  if os.path.isfile(os.path.join(path, fn)):
    with open(os.path.join(path, fn), 'rb') as txtfile:
      header = [next(txtfile) for x in range(3)]
      for line in txtfile:
        row = [next(txtfile) for x in range(4)]
        record = {}
        d = datetime.datetime.strptime(row[0].split(":\xa0")[1].strip(), '%d/%m/%Y')
        record["date"] = datetime.date.strftime(d, "%Y-%m-%d")
        record["description"] = row[1].split(":\xa0")[1].strip()
        record["amount"] = row[2].split(":\xa0")[1].replace('\xa0', '').replace('GBP', '').strip()
        record["balance"] = row[3].split(":\xa0")[1].replace('\xa0', '').replace('GBP', '').strip()
        #print record
        sql = "INSERT OR IGNORE INTO transactions (%s) VALUES (?, ?, ?, ?)" % (', '.join(record.keys()))
    
        try:
          c.execute(sql, record.values())
          conn.commit()
        except sqlite3.Error as er:
          print ('er:', er.message)
    os.rename(path + fn, "import/done/" + fn)

sql = """UPDATE transactions
SET title = 
( SELECT title
  FROM patterns
  WHERE upper(transactions.description) LIKE '%' || pattern || '%'
  AND abs(transactions.amount) < maxamount
  ORDER BY maxamount LIMIT 1
),
category = 
( SELECT category
  FROM patterns
  WHERE upper(transactions.description) LIKE '%' || pattern || '%'
  AND abs(transactions.amount) < maxamount
  ORDER BY maxamount LIMIT 1
),
fixed = 
( SELECT fixed
  FROM patterns
  WHERE upper(transactions.description) LIKE '%' || pattern || '%'
  AND abs(transactions.amount) < maxamount
  ORDER BY maxamount LIMIT 1
)
WHERE ( SELECT category
  FROM patterns
  WHERE upper(transactions.description) LIKE '%' || pattern || '%'
  AND abs(transactions.amount) < maxamount
  ORDER BY maxamount LIMIT 1
) IS NOT NULL
AND category IS NULL;

"""
c.execute(sql)

conn.commit()
conn.close()