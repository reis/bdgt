select a.*, balance from (
select strftime('%Y-%m', date) as month, min(oid) as maxoid
from transactions 
group by 1 order by 1 desc
) as a
join  transactions t on t.oid = maxoid