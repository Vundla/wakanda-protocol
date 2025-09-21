-- Initialize database schema for Wakanda Protocol

-- Knowledge Hub tables
CREATE TABLE IF NOT EXISTS knowledge_items (
    id VARCHAR(255) PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(100) NOT NULL,
    tags TEXT[], -- PostgreSQL array type
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Finance tables
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id VARCHAR(255) PRIMARY KEY,
    amount DECIMAL(15,2) NOT NULL,
    currency VARCHAR(3) NOT NULL,
    status VARCHAR(50) NOT NULL,
    merchant_id VARCHAR(255) NOT NULL,
    reference_number VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS accounts (
    account_id VARCHAR(255) PRIMARY KEY,
    balance DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    currency VARCHAR(3) NOT NULL DEFAULT 'USD',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Minerals tables
CREATE TABLE IF NOT EXISTS mineral_samples (
    sample_id VARCHAR(255) PRIMARY KEY,
    latitude DECIMAL(10,8) NOT NULL,
    longitude DECIMAL(11,8) NOT NULL,
    depth_meters DECIMAL(8,2) NOT NULL,
    soil_ph DECIMAL(4,2) NOT NULL,
    moisture_content DECIMAL(5,2) NOT NULL,
    temperature_celsius DECIMAL(5,2) NOT NULL,
    elemental_composition JSONB, -- PostgreSQL JSON type
    predicted_mineral VARCHAR(100),
    confidence_score DECIMAL(5,4),
    quality_grade VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Drones tables
CREATE TABLE IF NOT EXISTS drones (
    drone_id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    model VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'offline',
    current_mission_id VARCHAR(255),
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    altitude DECIMAL(8,2),
    battery_level DECIMAL(5,2) DEFAULT 100.00,
    specs JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS missions (
    mission_id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    mission_type VARCHAR(100) NOT NULL,
    assigned_drone_ids TEXT[], -- Array of drone IDs
    waypoints JSONB, -- Array of coordinate objects
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    status VARCHAR(50) NOT NULL DEFAULT 'planned',
    priority INTEGER DEFAULT 1,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS telemetry_data (
    id SERIAL PRIMARY KEY,
    drone_id VARCHAR(255) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    latitude DECIMAL(10,8) NOT NULL,
    longitude DECIMAL(11,8) NOT NULL,
    altitude DECIMAL(8,2) NOT NULL,
    velocity JSONB, -- x, y, z components
    orientation JSONB, -- roll, pitch, yaw
    battery_level DECIMAL(5,2) NOT NULL,
    signal_strength DECIMAL(6,2) NOT NULL,
    temperature_c DECIMAL(5,2) NOT NULL,
    sensor_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_knowledge_category ON knowledge_items(category);
CREATE INDEX IF NOT EXISTS idx_transactions_status ON transactions(status);
CREATE INDEX IF NOT EXISTS idx_transactions_merchant ON transactions(merchant_id);
CREATE INDEX IF NOT EXISTS idx_mineral_samples_location ON mineral_samples(latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_drones_status ON drones(status);
CREATE INDEX IF NOT EXISTS idx_missions_status ON missions(status);
CREATE INDEX IF NOT EXISTS idx_telemetry_drone_time ON telemetry_data(drone_id, timestamp);

-- Insert default data
INSERT INTO accounts (account_id, balance, currency) 
VALUES ('default', 10000.00, 'USD') 
ON CONFLICT (account_id) DO NOTHING;