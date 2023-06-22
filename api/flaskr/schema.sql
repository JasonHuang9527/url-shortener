DROP TABLE IF EXISTS urls;

CREATE TABLE urls (
    original_url TEXT PRIMARY KEY,
    short_url TEXT NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (length(short_url) == 8)
);