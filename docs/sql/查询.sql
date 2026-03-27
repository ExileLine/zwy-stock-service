-- 按某个分类统计当前库存数量：

SELECT
    category_id,
    SUM(COALESCE(stock_qty, 0)) AS stock_qty_total
FROM stock_in_out_record
WHERE category_id = 1
  AND is_outbound = 0
  AND is_deleted = 0
GROUP BY category_id;

-- 按某个分类统计当前库存记录数：

SELECT
    category_id,
    COUNT(*) AS stock_count
FROM stock_in_out_record
WHERE category_id = 1
  AND is_outbound = 0
  AND is_deleted = 0
GROUP BY category_id;

-- 查询所有分类的库存汇总：

SELECT
    c.id AS category_id,
    c.product_name,
    c.product_brand,
    c.product_spec,
    COUNT(r.id) AS stock_count,
    SUM(COALESCE(r.stock_qty, 0)) AS stock_qty_total
FROM stock_category c
LEFT JOIN stock_in_out_record r
    ON r.category_id = c.id
   AND r.is_outbound = 0
   AND r.is_deleted = 0
WHERE c.is_deleted = 0
GROUP BY c.id, c.product_name, c.product_brand, c.product_spec
ORDER BY c.id;

-- 查哪些出入库记录还没匹配上分类：

SELECT
    id,
    product_name,
    product_brand,
    product_spec,
    pn_code,
    material_code,
    document_no
FROM stock_in_out_record
WHERE category_id IS NULL
  AND is_deleted = 0;
