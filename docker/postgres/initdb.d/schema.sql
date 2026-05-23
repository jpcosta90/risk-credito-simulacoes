-- Schema and tables for Simulacred project
-- Creates schema 'jpcosta' and table 'operacoes'

CREATE SCHEMA IF NOT EXISTS jpcosta;

CREATE TABLE IF NOT EXISTS jpcosta.operacoes (
    id BIGSERIAL PRIMARY KEY,
    ref TEXT,
    cliente BIGINT,
    porte TEXT,
    contrato TEXT,
    modalidade TEXT,
    prazo INTEGER,
    valor NUMERIC,
    mes INTEGER,
    dia INTEGER,
    prob_opr DOUBLE PRECISION,
    prob_cli DOUBLE PRECISION,
    prob DOUBLE PRECISION,
    atraso INTEGER,
    pgto NUMERIC,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Indexes that may help performance
CREATE INDEX IF NOT EXISTS idx_operacoes_cliente ON jpcosta.operacoes(cliente);
CREATE INDEX IF NOT EXISTS idx_operacoes_mes ON jpcosta.operacoes(mes);

-- Placeholder/result tables observed in notebooks
CREATE TABLE IF NOT EXISTS jpcosta.perda_obs (
    id BIGSERIAL PRIMARY KEY,
    ref BIGINT,
    perda_obs NUMERIC,
    perda_att NUMERIC,
    saldo NUMERIC,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE IF NOT EXISTS jpcosta.perda_obs_atr (
    id BIGSERIAL PRIMARY KEY,
    ref BIGINT,
    perda_obs NUMERIC,
    atraso INT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE IF NOT EXISTS jpcosta.calculo_pd (
    id BIGSERIAL PRIMARY KEY,
    ref BIGINT,
    pd NUMERIC,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE IF NOT EXISTS jpcosta.calculo_pd_2 (
    id BIGSERIAL PRIMARY KEY,
    ref BIGINT,
    pd NUMERIC,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE IF NOT EXISTS jpcosta.calculo_lgd60 (
    id BIGSERIAL PRIMARY KEY,
    ref BIGINT,
    lgd NUMERIC,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE IF NOT EXISTS jpcosta.calculo_lgd_bst (
    id BIGSERIAL PRIMARY KEY,
    ref BIGINT,
    lgd NUMERIC,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE IF NOT EXISTS jpcosta.prd_anual (
    id BIGSERIAL PRIMARY KEY,
    ano INT,
    prd NUMERIC,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE IF NOT EXISTS jpcosta.perda_lt_12 (
    id BIGSERIAL PRIMARY KEY,
    ref BIGINT,
    perda_lt NUMERIC,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE IF NOT EXISTS jpcosta.prejuizo (
    id BIGSERIAL PRIMARY KEY,
    ref BIGINT,
    prejuizo NUMERIC,
    iPE NUMERIC,
    iprov NUMERIC,
    perda_obs NUMERIC,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

