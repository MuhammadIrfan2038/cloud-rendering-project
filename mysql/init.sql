-- init.sql

CREATE TABLE IF NOT EXISTS render_metadata (
    id INT AUTO_INCREMENT PRIMARY KEY,
    filename VARCHAR(255),
    frame_start INT,
    frame_end INT,
    output_format VARCHAR(50),
    output_dir VARCHAR(255),
    status VARCHAR(50),
    rendered_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS render_result (
    id INT AUTO_INCREMENT PRIMARY KEY,
    filename VARCHAR(255),
    output_path VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS render_progress (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_name VARCHAR(255) UNIQUE,
    total_frames INT,
    rendered_frames INT DEFAULT 0,
    current_frame INT DEFAULT 0,
    status VARCHAR(50) DEFAULT 'in_progress'
);
