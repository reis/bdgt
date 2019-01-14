select 1 as ord, b.category, b.title, :month as month,
b.budget1, case when coalesce(s1.amount,0) = 0 and b.fixed then b.budget1 else coalesce(s1.amount,0) end as amount1, 
           case when coalesce(s1.amount,0) = 0 and b.fixed and b.budget1 <> 0 then 1 else 0 end as pred1,
b.budget2, case when coalesce(s2.amount,0) = 0 and b.fixed then b.budget2 else coalesce(s2.amount,0) end as amount2, 
           case when coalesce(s2.amount,0) = 0 and b.fixed and b.budget2 <> 0 then 1 else 0 end as pred2,
b.budget3, case when coalesce(s3.amount,0) = 0 and b.fixed then b.budget3 else coalesce(s3.amount,0) end as amount3, 
           case when coalesce(s3.amount,0) = 0 and b.fixed and b.budget3 <> 0 then 1 else 0 end as pred3,
abs(b.budget3) as budget_abs
from budget b
left join (
    select category, title, sum(amount) as amount
    from transactions 
    where cast(date as varchar) like :month || '%'
    and cast(date_part('day', date) as integer) <= 10
    and title is not null
    group by category, title
) s1 on b.category = s1.category and b.title = s1.title
left join (
    select category, title, sum(amount) as amount
    from transactions 
    where cast(date as varchar) like :month || '%'
    and cast(date_part('day', date) as integer) <= 20
    and title is not null
    group by category, title
) s2 on b.category = s2.category and b.title = s2.title
left join (
    select category, title, sum(amount) as amount
    from transactions 
    where cast(date as varchar) like :month || '%'
    and title is not null
    group by category, title
) s3 on b.category = s3.category and b.title = s3.title
where (month is null or month = :month)
and b.title is not null
union
-- SELECT BUDGETS THAT TITLE IS NULL
select case when b.category in ('CASH', 'TRANSFER') then 9 else 1 end as ord, b.category, b.title, :month as month,
b.budget1, case when coalesce(s1.amount,0) = 0 and b.fixed then b.budget1 else coalesce(s1.amount,0) end as amount1,
case when b.budget1 <> 0 and b.fixed and coalesce(s1.amount,0) = 0  then 1 else 0 end as pred1,
b.budget2, case when coalesce(s2.amount,0) = 0 and b.fixed then b.budget2 else coalesce(s2.amount,0) end as amount2,
case when b.budget2 <> 0 and b.fixed and coalesce(s2.amount,0) = 0  then 1 else 0 end as pred2,
b.budget3, case when coalesce(s3.amount,0) = 0 and b.fixed then b.budget3 else coalesce(s3.amount,0) end as amount3,
 case when b.budget3 <> 0 and b.fixed and coalesce(s3.amount,0) = 0  then 1 else 0 end as pred3,
abs(b.budget3) as budget_abs
from budget b
left join (
    select category, sum(amount) as amount
    from transactions 
    where cast(date as varchar) like :month || '%'
    and cast(date_part('day', date) as integer) <= 10
    group by category
) s1 on b.category = s1.category
left join (
    select category, sum(amount) as amount
    from transactions 
    where cast(date as varchar) like :month || '%'
    and cast(date_part('day', date) as integer) <= 20
    group by category
) s2 on b.category = s2.category
left join (
    select category, sum(amount) as amount
    from transactions 
    where cast(date as varchar) like :month || '%'
    group by category
) s3 on b.category = s3.category
where (month is null or month = :month)
and b.title is null
union
-- SELECT TRANSACTIONS WITHOUT BUDGET
select 2 as ord, category, title, :month as month, 
0 as budget1, sum(case when cast(date_part('day', date) as integer) <= 10 then amount when date is null then 0 else 0 end) as amount1, 0 as pred1,
0 as budget2, sum(case when cast(date_part('day', date) as integer) <= 20 then amount when date is null then 0 else 0 end) as amount2, 0 as pred2,
0 as budget3, sum(amount) as amount3, 0 as pred3,
0 as budget_abs
from (
    -- SELECT ALL TRANSACTIONS OF THE MONTH
    select date, description, amount, balance, type, category, title, fixed from transactions 
    where cast(date as varchar) like :month || '%'
    except
    -- SELECT ALL TRANSACTIONS WITH BUDGET
    select date, description, amount, balance, type, category, title, fixed from (
        -- SELECT BUDGETS THAT TITLE IS NOT NULL
        select t.* from budget b
        left join transactions t 
        on b.category = t.category and b.title = t.title
        and cast(date as varchar) like :month || '%'
        and b.title is not null
        where (month is null or month = :month)
        union
        -- SELECT BUDGETS THAT TITLE IS NULL
        select t.* from budget b
        left join transactions t 
        on b.category = t.category
        and cast(date as varchar) like :month || '%'
        and b.title is null
        where (month is null or month = :month)
    ) a
) a
group by 1,2,3
order by 1,2,3