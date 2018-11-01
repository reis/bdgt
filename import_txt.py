import os
import re
import config
import db
import sqlite3
import datetime
import sys
from pprint import pprint
import glob

db = db.db()
conn = db.conn
c = conn.cursor()

path = config.IMPORT_PATH
print (path)
for file_name in glob.glob(path):
  print(file_name)
  if os.path.isfile(os.path.join(path, file_name)):
    with open(os.path.join(path, file_name), 'r', encoding="latin-1") as txtfile:
      header = [next(txtfile) for x in range(3)]
      i = 0
      for line in txtfile:
        i += 1
        row = [next(txtfile) for x in range(4)]
        record = {}
        d = datetime.datetime.strptime(row[0].split(':\xa0')[1].strip(), '%d/%m/%Y')
        if (i == 1):
          d0 = d
        record["date"] = datetime.date.strftime(d, "%Y-%m-%d")
        record["description"] = row[1].split(':\xa0')[1].strip()
        record["amount"] = row[2].split(':\xa0')[1].replace('\xa0', '').replace('GBP', '').strip()
        record["balance"] = row[3].split(':\xa0')[1].replace('\xa0', '').replace('GBP', '').strip()
        print(list(record.values()))
        sql = "INSERT OR IGNORE INTO transactions (%s) VALUES (?, ?, ?, ?)" % (', '.join(record.keys()))
    
        try:
          c.execute(sql, list(record.values()))
          conn.commit()
        except sqlite3.Error as er:
          print ('er:', er.message)
    os.rename(os.path.join(path, file_name), config.ARCHIVE_PATH + datetime.date.strftime(d0, "%Y-%m-%d") + ".txt")

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