UPDATE transactions
SET title = 
( SELECT title
  FROM patterns
  WHERE transactions.description LIKE '%' || pattern || '%'
  AND abs(transactions.amount) < maxamount
  ORDER BY maxamount LIMIT 1
),
category = 
( SELECT category
  FROM patterns
  WHERE transactions.description LIKE '%' || pattern || '%'
  AND abs(transactions.amount) < maxamount
  ORDER BY maxamount LIMIT 1
),
fixed = 
( SELECT fixed
  FROM patterns
  WHERE transactions.description LIKE '%' || pattern || '%'
  AND abs(transactions.amount) < maxamount
  ORDER BY maxamount LIMIT 1
)
WHERE ( SELECT category
  FROM patterns
  WHERE transactions.description LIKE '%' || pattern || '%'
  AND abs(transactions.amount) < maxamount
  ORDER BY maxamount LIMIT 1
) IS NOT NULL
AND category IS NULL;