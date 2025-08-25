-- Database initialization script for PostgreSQL
-- Building Energy Optimizer v2.0

-- Create database extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create custom types
DO $$ BEGIN
    CREATE TYPE building_type_enum AS ENUM ('residential', 'commercial', 'industrial');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE priority_enum AS ENUM ('low', 'medium', 'high');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_energy_records_timestamp ON energy_records(timestamp);
CREATE INDEX IF NOT EXISTS idx_energy_records_building_timestamp ON energy_records(building_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_optimization_results_building ON optimization_results(building_id);
CREATE INDEX IF NOT EXISTS idx_optimization_results_created ON optimization_results(created_at);

-- Create views for common queries
CREATE OR REPLACE VIEW v_building_summary AS
SELECT 
    b.id,
    b.name,
    b.building_type,
    b.floor_area,
    b.building_age,
    b.renewable_energy,
    COUNT(er.id) as total_energy_records,
    AVG(er.energy_consumption) as avg_consumption,
    MAX(er.timestamp) as last_record_date,
    COUNT(opt.id) as optimization_count,
    MAX(opt.created_at) as last_optimization_date
FROM buildings b
LEFT JOIN energy_records er ON b.id = er.building_id
LEFT JOIN optimization_results opt ON b.id = opt.building_id
GROUP BY b.id, b.name, b.building_type, b.floor_area, b.building_age, b.renewable_energy;

CREATE OR REPLACE VIEW v_daily_consumption AS
SELECT 
    building_id,
    DATE(timestamp) as date,
    AVG(energy_consumption) as avg_consumption,
    MIN(energy_consumption) as min_consumption,
    MAX(energy_consumption) as max_consumption,
    SUM(energy_consumption) as total_consumption,
    COUNT(*) as hourly_records
FROM energy_records
GROUP BY building_id, DATE(timestamp)
ORDER BY building_id, date;

CREATE OR REPLACE VIEW v_hourly_patterns AS
SELECT 
    building_id,
    EXTRACT(hour FROM timestamp) as hour_of_day,
    AVG(energy_consumption) as avg_consumption,
    STDDEV(energy_consumption) as consumption_stddev,
    COUNT(*) as record_count
FROM energy_records
GROUP BY building_id, EXTRACT(hour FROM timestamp)
ORDER BY building_id, hour_of_day;

-- Insert sample building data
INSERT INTO buildings (name, building_type, floor_area, building_age, insulation_level, hvac_efficiency, occupancy_max, renewable_energy, latitude, longitude)
VALUES 
    ('Demo Office Building', 'commercial', 2500, 8, 0.75, 0.85, 150, true, 41.9028, 12.4964),
    ('Sample Residential Complex', 'residential', 1200, 12, 0.65, 0.75, 80, false, 40.7128, -74.0060),
    ('Test Industrial Facility', 'industrial', 5000, 15, 0.70, 0.80, 200, true, 34.0522, -118.2437)
ON CONFLICT DO NOTHING;

-- Create stored procedures for common operations
CREATE OR REPLACE FUNCTION get_building_efficiency_score(building_id_param INTEGER)
RETURNS NUMERIC AS $$
DECLARE
    efficiency_score NUMERIC;
BEGIN
    SELECT 
        (b.insulation_level * 0.3 + 
         b.hvac_efficiency * 0.4 + 
         CASE WHEN b.renewable_energy THEN 0.3 ELSE 0 END) * 100
    INTO efficiency_score
    FROM buildings b
    WHERE b.id = building_id_param;
    
    RETURN COALESCE(efficiency_score, 0);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_recent_optimization_summary(days_back INTEGER DEFAULT 30)
RETURNS TABLE(
    building_name TEXT,
    optimization_count BIGINT,
    avg_savings_percent NUMERIC,
    total_cost_savings NUMERIC,
    last_optimization TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        b.name::TEXT,
        COUNT(opt.id),
        AVG(opt.potential_savings_percent),
        SUM(opt.cost_savings_eur),
        MAX(opt.created_at)
    FROM buildings b
    LEFT JOIN optimization_results opt ON b.id = opt.building_id
    WHERE opt.created_at >= NOW() - INTERVAL '%s days' 
    GROUP BY b.id, b.name
    ORDER BY AVG(opt.potential_savings_percent) DESC;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for automatic timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS update_buildings_updated_at ON buildings;
CREATE TRIGGER update_buildings_updated_at
    BEFORE UPDATE ON buildings
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO energy_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO energy_user;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO energy_user;

-- Print completion message
DO $$
BEGIN
    RAISE NOTICE 'Building Energy Optimizer database initialized successfully!';
    RAISE NOTICE 'Sample buildings created. Ready for energy optimization.';
END $$;
