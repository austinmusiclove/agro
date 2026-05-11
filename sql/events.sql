CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    venue_id INT, -- Foreign key to a venues table
    -- stage_id INT, -- Foreign key to a stages table

    start_date DATE,
    end_date DATE,
    start_time TIME,
    end_time TIME,

    ages VARCHAR(50), -- e.g., "21+", "All Ages"
    price_range VARCHAR(100),

    status ENUM('pending-review', 'published', 'disabled', 'staged', 'processed') DEFAULT 'pending-review',

    event_page_url TEXT,
    ticket_url TEXT,
    image_url TEXT,

    data_source VARCHAR(100),
    event_list_html_hash VARCHAR(64),
    event_list_markdown_hash VARCHAR(64),
    event_page_html_hash VARCHAR(64),
    event_page_markdown_hash VARCHAR(64),
    event_list_screenshot TEXT, -- S3 url
    event_page_screenshot TEXT, -- S3 url

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
