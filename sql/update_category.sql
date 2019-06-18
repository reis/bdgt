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

update transactions
set pay_month = new_pay
from (
select *, date_trunc('month', (
	select t2.date from transactions t2
	where category = 'EARNINGS'
	and t2.date < t.date
	order by t2.date desc
	limit 1) + '1 month'::interval)::date as new_pay
from transactions t
where category <> 'EARNINGS'
union
select *, date_trunc('month', date+'1 month'::interval)::date
from transactions t3
where category = 'EARNINGS'
) z 
where z.date = transactions.date
and z.description = transactions.description
and z.amount = transactions.amount
and z.balance = transactions.balance
and transactions.pay_month is null;