CREATE TABLE staged_transactions (
    id SERIAL PRIMARY KEY,
    target_table VARCHAR(50),
    current_data_row_id INT,
    staged_data_id INT,

    transaction_type ENUM('create', 'update', 'delete') NOT NULL,
    data_index INT,

    screenshot TEXT, -- S3 Object Id
    schema_blob JSON,

    scrape_url TEXT,
    scrape_html_hash VARCHAR(64),
    scrape_markdown_hash VARCHAR(64),

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
