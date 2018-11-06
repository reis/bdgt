import os
import configparser
from db import Db
import datetime
from pprint import pprint
import glob

config = configparser.ConfigParser()
config.read("config.ini")

db = Db()

path = config.get("CONFIG", "IMPORT_PATH")
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
        
        sql = """INSERT INTO transactions (date, description, amount, balance) 
        VALUES (:date, :description, :amount, :balance) 
        ON CONFLICT DO NOTHING"""
        db.conn.query(sql, **record)
    
    os.rename(os.path.join(path, file_name), config.get("CONFIG", "ARCHIVE_PATH") + datetime.date.strftime(d0, "%Y-%m-%d") + ".txt")

db.conn.query_file("sql/update_category.sql")