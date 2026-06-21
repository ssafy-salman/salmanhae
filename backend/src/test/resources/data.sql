INSERT INTO properties (
    id, title, building_name, building_key, property_type, transaction_type,
    deposit, monthly_rent, price, maintenance_fee, area_m2, floor, total_floor,
    address, road_address, sido, sigungu, dong, legal_dong_code,
    latitude, longitude, description, source, source_property_id, registered_at,
    is_active, created_at, updated_at
) VALUES
(
    1, '대학동 그린빌 월세', '그린빌', '1162010200:ONE_ROOM:그린빌:12-3',
    'ONE_ROOM', 'MONTHLY_RENT', 10000000, 550000, NULL, 70000,
    22.50, 3, 5, '서울특별시 관악구 대학동 12-3', '서울특별시 관악구 대학길 12',
    '서울특별시', '관악구', '대학동', '1162010200',
    37.4701230, 126.9364560, '대학가 인근 원룸입니다.',
    'MVP_SYNTHETIC', 'synthetic-1', DATE '2026-06-01', TRUE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
),
(
    2, '대학동 그린빌 매매', '그린빌', '1162010200:APARTMENT:그린빌:12-3',
    'APARTMENT', 'SALE', NULL, NULL, 720000000, 120000,
    59.90, 8, 15, '서울특별시 관악구 대학동 12-3', '서울특별시 관악구 대학길 12',
    '서울특별시', '관악구', '대학동', '1162010200',
    37.4710000, 126.9370000, '실거래가 기반 매매 더미입니다.',
    'MVP_SYNTHETIC', 'synthetic-2', DATE '2026-06-01', TRUE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
),
(
    3, '비활성 매물', '비활성빌', '1162010200:ONE_ROOM:비활성빌:99-9',
    'ONE_ROOM', 'MONTHLY_RENT', 5000000, 400000, NULL, 50000,
    18.00, 2, 4, '서울특별시 관악구 대학동 99-9', NULL,
    '서울특별시', '관악구', '대학동', '1162010200',
    37.4705000, 126.9365000, '노출되지 않아야 합니다.',
    'MVP_SYNTHETIC', 'synthetic-3', DATE '2026-06-01', FALSE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
),
(
    4, '범위 밖 매물', '멀리빌', '1162010200:ONE_ROOM:멀리빌:1-1',
    'ONE_ROOM', 'MONTHLY_RENT', 9000000, 520000, NULL, 60000,
    20.00, 4, 5, '서울특별시 관악구 대학동 1-1', NULL,
    '서울특별시', '관악구', '대학동', '1162010200',
    37.6000000, 127.1000000, '지도 범위 밖 매물입니다.',
    'MVP_SYNTHETIC', 'synthetic-4', DATE '2026-06-01', TRUE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
);
