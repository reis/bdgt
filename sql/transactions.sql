SELECT DATE, DESCRIPTION, CATEGORY, TITLE, AMOUNT, :month as "month"
FROM transactions 
WHERE CAST(date as varchar) LIKE :month 
--AND title = :title 
--AND category = :category 
--AND category IS NULL
ORDER BY 1 DESC
