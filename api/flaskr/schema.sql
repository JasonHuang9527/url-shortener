DROP TABLE IF EXISTS urls;

CREATE TABLE urls (
    original_url text NOT NULL,
    short_url text NOT NULL CHECK (char_length(short_url) = 8),
    created TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (original_url)
);