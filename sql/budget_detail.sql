select coalesce(b.position, s.position) as ord, :month as month, 
    coalesce(b.category, s.category) as category, 
    coalesce(b.title, s.title) as title,  
    coalesce(budget, 0.00) as budget, 
    date, 
    coalesce(s.spent, 0.00)::numeric(12,2) as spent 
from (
    select * from (
        select row_number() over (partition by budget.category, title order by month desc) as seq,
        position, budget.category, title, month, budget3 as budget, repeat_every
        from budget
        join categories on categories.category = budget.category
        where :month >= month
        order by position, category, title, month desc
    ) tt
    where seq = 1
    and (:month||'-01')::date in (select generate_series((month||'-01')::date, (:month||'-01')::date, (repeat_every||' months')::interval)::date)
) b
full outer join (
    select t.category, null as title, max(date) as date, sum(amount) as spent, c."position"
    from transactions t
    join categories c on t.category = c.category and ignore_title
    where pay_month = (:month || '-01')::date 
    group by t.category, c.position
    union
    select t.category, title, max(date) as date, sum(amount) as spent, c."position"
    from transactions t
    join categories c on t.category = c.category and not ignore_title
    where pay_month = (:month || '-01')::date 
    group by t.category, title, c."position"
) s on b.category = s.category and (b.title is null or b.title = s.title)
order by ord, b.category, b.title