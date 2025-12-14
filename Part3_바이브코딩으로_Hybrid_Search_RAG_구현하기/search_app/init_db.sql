-- 데이터베이스 초기화 스크립트
-- Neon PostgreSQL에서 실행

-- 필요한 확장 설치
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_search;

-- 기존 테이블 삭제 (필요시)
DROP TABLE IF EXISTS loan_products CASCADE;

-- loan_products 테이블 생성
CREATE TABLE loan_products (
    id VARCHAR(255) PRIMARY KEY,
    product_code VARCHAR(50),
    product_name VARCHAR(255),
    product_summary TEXT,
    product_description TEXT,
    target_description TEXT,
    loan_limit_description TEXT,
    loan_period_guide TEXT,
    repayment_method VARCHAR(100),
    min_interest_rate DECIMAL(5,2),
    max_interest_rate DECIMAL(5,2),
    required_documents TEXT,
    customer_cost_info TEXT,
    early_repayment_info TEXT,
    overdue_interest_info TEXT,
    important_notices TEXT,
    is_available BOOLEAN,
    is_sale_available BOOLEAN,
    can_apply_online BOOLEAN,
    can_apply_mobile BOOLEAN,
    can_apply_branch BOOLEAN,
    registered_at TIMESTAMP,
    last_modified_at TIMESTAMP,
    searchable_text TEXT,
    cleaned_searchable_text TEXT,
    searchable_text_embedding vector(1536)
);

-- 벡터 검색을 위한 인덱스 생성 (HNSW 알고리즘)
-- 코사인 거리 기반
CREATE INDEX IF NOT EXISTS idx_loan_products_embedding
ON loan_products
USING hnsw (searchable_text_embedding vector_cosine_ops);

-- 참고: BM25 인덱스는 hybrid_search.py에서 동적으로 생성됩니다
-- ngram 토크나이저 설정이 필요하기 때문입니다
