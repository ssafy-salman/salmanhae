DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS property_score_stat;
DROP TABLE IF EXISTS building_price_stat;
DROP TABLE IF EXISTS region_price_stat;
DROP TABLE IF EXISTS transaction_history;
DROP TABLE IF EXISTS properties;

CREATE TABLE users (
    id UUID DEFAULT RANDOM_UUID() PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    nickname VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE properties (
    id BIGINT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    building_name VARCHAR(200),
    building_key VARCHAR(300),
    anchor_transaction_id BIGINT,
    property_type VARCHAR(20) NOT NULL,
    transaction_type VARCHAR(20) NOT NULL,
    deposit BIGINT,
    monthly_rent BIGINT,
    price BIGINT,
    maintenance_fee BIGINT,
    area_m2 DECIMAL(8, 2),
    floor INT,
    total_floor INT,
    address TEXT,
    road_address TEXT,
    sido VARCHAR(20),
    sigungu VARCHAR(30),
    dong VARCHAR(30),
    legal_dong_code VARCHAR(10),
    latitude DECIMAL(10, 7),
    longitude DECIMAL(10, 7),
    geocoding_provider VARCHAR(50),
    geocoding_quality VARCHAR(30),
    geocoded_at TIMESTAMP,
    description TEXT,
    source VARCHAR(30),
    source_property_id VARCHAR(120),
    source_url TEXT,
    crawled_at TIMESTAMP,
    registered_at DATE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE transaction_history (
    id BIGINT PRIMARY KEY,
    source_api VARCHAR(50) NOT NULL,
    source_transaction_key VARCHAR(160) NOT NULL,
    property_type VARCHAR(20) NOT NULL,
    transaction_type VARCHAR(20) NOT NULL,
    sido VARCHAR(20) NOT NULL,
    sigungu VARCHAR(30) NOT NULL,
    dong VARCHAR(30) NOT NULL,
    legal_dong_code VARCHAR(10) NOT NULL,
    jibun VARCHAR(50),
    building_name VARCHAR(200),
    building_key VARCHAR(300) NOT NULL,
    contract_year_month VARCHAR(6) NOT NULL,
    contract_day INT,
    deposit BIGINT,
    monthly_rent BIGINT,
    price BIGINT,
    area_m2 DECIMAL(8, 2),
    floor INT,
    build_year INT,
    raw_json TEXT,
    created_at TIMESTAMP
);

CREATE TABLE property_score_stat (
    property_id BIGINT PRIMARY KEY,
    safety_score INT,
    price_score INT,
    cctv_count_300m INT,
    bell_count_300m INT,
    light_count_300m INT,
    police_count_500m INT,
    updated_at TIMESTAMP
);

CREATE TABLE region_price_stat (
    id BIGINT PRIMARY KEY,
    region_level VARCHAR(20) NOT NULL,
    region_code VARCHAR(80) NOT NULL,
    sido VARCHAR(20) NOT NULL,
    sigungu VARCHAR(30),
    dong VARCHAR(30),
    property_type VARCHAR(20) NOT NULL,
    transaction_type VARCHAR(20) NOT NULL,
    avg_deposit BIGINT,
    median_deposit BIGINT,
    avg_monthly_rent BIGINT,
    median_monthly_rent BIGINT,
    avg_price BIGINT,
    median_price BIGINT,
    transaction_count INT NOT NULL,
    sample_from_ym VARCHAR(6),
    sample_to_ym VARCHAR(6),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE building_price_stat (
    id BIGINT PRIMARY KEY,
    building_key VARCHAR(300) NOT NULL,
    building_name VARCHAR(200),
    sido VARCHAR(20) NOT NULL,
    sigungu VARCHAR(30) NOT NULL,
    dong VARCHAR(30) NOT NULL,
    legal_dong_code VARCHAR(10) NOT NULL,
    property_type VARCHAR(20) NOT NULL,
    transaction_type VARCHAR(20) NOT NULL,
    avg_deposit BIGINT,
    median_deposit BIGINT,
    avg_monthly_rent BIGINT,
    median_monthly_rent BIGINT,
    avg_price BIGINT,
    median_price BIGINT,
    transaction_count INT NOT NULL,
    sample_from_ym VARCHAR(6),
    sample_to_ym VARCHAR(6),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
