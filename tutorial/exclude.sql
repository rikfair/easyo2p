SELECT 'TABLE ' || table_name exclude
  FROM user_tab_comments
 WHERE comments LIKE 'DEPRECATED%'
 UNION ALL
SELECT 'COLUMN '|| table_name || '.' || column_name
  FROM user_col_comments
 WHERE comments LIKE 'DEPRECATED%'
