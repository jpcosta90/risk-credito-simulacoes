-- Init script to create database and users used by the project
-- WARNING: passwords stored in plain text for compatibility with old setup

CREATE USER jpcosta WITH ENCRYPTED PASSWORD '12345678';
CREATE DATABASE "Simulacred";
GRANT ALL PRIVILEGES ON DATABASE "Simulacred" TO jpcosta;

-- You can add schema/table creation SQL here if needed
