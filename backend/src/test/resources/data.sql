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

INSERT INTO transaction_history (
    id, source_api, source_transaction_key, property_type, transaction_type,
    sido, sigungu, dong, legal_dong_code, jibun, building_name, building_key,
    contract_year_month, contract_day, deposit, monthly_rent, price, area_m2,
    floor, build_year, raw_json, created_at
) VALUES
(
    101, 'MOLIT_TEST', 'tx-101', 'ONE_ROOM', 'MONTHLY_RENT',
    '서울특별시', '관악구', '대학동', '1162010200', '12-3', '그린빌',
    '1162010200:ONE_ROOM:그린빌:12-3', '202605', 11,
    10000000, 520000, NULL, 21.80, 2, 2015, '{}', CURRENT_TIMESTAMP
),
(
    102, 'MOLIT_TEST', 'tx-102', 'ONE_ROOM', 'MONTHLY_RENT',
    '서울특별시', '관악구', '대학동', '1162010200', '12-3', '그린빌',
    '1162010200:ONE_ROOM:그린빌:12-3', '202604', 8,
    12000000, 500000, NULL, 22.10, 4, 2015, '{}', CURRENT_TIMESTAMP
),
(
    103, 'MOLIT_TEST', 'tx-103', 'ONE_ROOM', 'MONTHLY_RENT',
    '서울특별시', '관악구', '대학동', '1162010200', '77-7', '비교빌',
    '1162010200:ONE_ROOM:비교빌:77-7', '202603', 22,
    9000000, 540000, NULL, 24.00, 3, 2018, '{}', CURRENT_TIMESTAMP
),
(
    201, 'MOLIT_TEST', 'tx-201', 'APARTMENT', 'SALE',
    '서울특별시', '관악구', '대학동', '1162010200', '12-3', '그린빌',
    '1162010200:APARTMENT:그린빌:12-3', '202605', 5,
    NULL, NULL, 710000000, 59.80, 7, 2012, '{}', CURRENT_TIMESTAMP
);

INSERT INTO property_score_stat (
    property_id, safety_score, price_score, cctv_count_300m, bell_count_300m,
    light_count_300m, police_count_500m, updated_at
) VALUES
(1, 78, 64, 8, 2, 14, 1, CURRENT_TIMESTAMP),
(2, 85, 71, 10, 3, 18, 2, CURRENT_TIMESTAMP);

INSERT INTO region_price_stat (
    id, region_level, region_code, sido, sigungu, dong, property_type, transaction_type,
    avg_deposit, median_deposit, avg_monthly_rent, median_monthly_rent,
    avg_price, median_price, transaction_count, sample_from_ym, sample_to_ym,
    created_at, updated_at
) VALUES
(
    301, 'DONG', '1162010200', '서울특별시', '관악구', '대학동',
    'ONE_ROOM', 'MONTHLY_RENT', 10500000, 10000000, 520000, 520000,
    NULL, NULL, 3, '202603', '202605', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
),
(
    302, 'DONG', '1162010200', '서울특별시', '관악구', '대학동',
    'APARTMENT', 'SALE', NULL, NULL, NULL, NULL,
    715000000, 710000000, 1, '202605', '202605', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
),
(
    303, 'SIGUNGU', '11620', '서울특별시', '관악구', NULL,
    'ONE_ROOM', 'MONTHLY_RENT', 98000000, 96000000, 620000, 600000,
    NULL, NULL, 12, '202603', '202605', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
);

INSERT INTO building_price_stat (
    id, building_key, building_name, sido, sigungu, dong, legal_dong_code,
    property_type, transaction_type, avg_deposit, median_deposit,
    avg_monthly_rent, median_monthly_rent, avg_price, median_price,
    transaction_count, sample_from_ym, sample_to_ym, created_at, updated_at
) VALUES
(
    401, '1162010200:ONE_ROOM:그린빌:12-3', '그린빌',
    '서울특별시', '관악구', '대학동', '1162010200',
    'ONE_ROOM', 'MONTHLY_RENT', 11000000, 11000000, 510000, 510000,
    NULL, NULL, 2, '202604', '202605', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
),
(
    402, '1162010200:APARTMENT:그린빌:12-3', '그린빌',
    '서울특별시', '관악구', '대학동', '1162010200',
    'APARTMENT', 'SALE', NULL, NULL, NULL, NULL,
    710000000, 710000000, 1, '202605', '202605', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
);
