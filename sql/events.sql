CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    event_name VARCHAR(255) NOT NULL,
    venue_id INT, -- Foreign key to a venues table
    -- stage_id INT, -- Foreign key to a stages table

    start_date DATE,
    end_date DATE,
    start_time TIME,
    end_time TIME,

    ages VARCHAR(50), -- e.g., "21+", "All Ages"
    price_range VARCHAR(100),

    status ENUM('pending-review', 'published', 'disabled', 'staged') DEFAULT 'pending-review',

    data_source VARCHAR(100),
    event_page_url TEXT,
    ticket_url TEXT,
    event_image TEXT, -- S3 Object key
    event_image_url TEXT,

    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
