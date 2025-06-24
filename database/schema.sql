-- Bitcoin Address Classifier Database Schema

-- Create database (run this separately if needed)
-- CREATE DATABASE bitcoin_classifier;

-- Create classifications table
CREATE TABLE IF NOT EXISTS classifications (
    id SERIAL PRIMARY KEY,
    address VARCHAR(255) NOT NULL,
    classification INTEGER NOT NULL CHECK (classification IN (0, 1)),
    confidence DECIMAL(5,4) NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    features JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_classifications_address ON classifications(address);
CREATE INDEX IF NOT EXISTS idx_classifications_created_at ON classifications(created_at);
CREATE INDEX IF NOT EXISTS idx_classifications_classification ON classifications(classification);

-- Create unique constraint on address to prevent duplicates
CREATE UNIQUE INDEX IF NOT EXISTS idx_classifications_address_unique ON classifications(address);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_classifications_updated_at 
    BEFORE UPDATE ON classifications 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Create view for recent classifications
CREATE OR REPLACE VIEW recent_classifications AS
SELECT 
    address,
    classification,
    confidence,
    created_at,
    CASE 
        WHEN classification = 1 THEN 'Suspicious'
        ELSE 'Normal'
    END as classification_text
FROM classifications
ORDER BY created_at DESC;

-- Insert some sample data for testing (optional)
-- INSERT INTO classifications (address, classification, confidence, features) VALUES
-- ('1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa', 0, 0.85, '{"PAIa13": 0.5, "S2-3": 10}'),
-- ('3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy', 1, 0.72, '{"PAIa13": 2.1, "S2-3": 45}'); 