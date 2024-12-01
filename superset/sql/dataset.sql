SELECT
    f.invoice_id,
    -- Branch dimension
    b.branch_id,
    b.branch,
    b.city,
    -- Product dimension
    pc.product_category_id,
    pc.product_line,
    -- Payment dimension
    p.payment_id,
    p.payment,
    -- Customer dimension
    c.customer_type,
    c.gender,
    -- Date dimension
    d.date,
    d.year,
    d.month,
    d.day,
    d.weekday,
    d.quarter,
    -- Time from fact table
    f.time,
    -- Metrics from fact table
    f.unit_price,
    f.quantity,
    f.tax_5,
    f.total,
    f.cogs,
    f.gross_margin_percentage,
    f.gross_income,
    f.rating
FROM dds.fact_sales f
JOIN dds.dim_branch b
    ON f.branch_id = b.branch_id
JOIN dds.dim_product_category pc
    ON f.product_category_id = pc.product_category_id
JOIN dds.dim_payment p
    ON f.payment_id = p.payment_id
JOIN dds.dim_customer c
    ON f.customer_type = c.customer_type
    AND f.gender = c.gender
JOIN dds.dim_date d
    ON f.date = d.date