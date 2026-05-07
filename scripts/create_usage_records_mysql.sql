CREATE DATABASE IF NOT EXISTS `agent_project`
DEFAULT CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE `agent_project`;

CREATE TABLE IF NOT EXISTS `usage_records` (
    `id` BIGINT PRIMARY KEY AUTO_INCREMENT,
    `user_id` VARCHAR(20) NOT NULL,
    `feature` TEXT,
    `efficiency` TEXT,
    `consumables` TEXT,
    `comparison` TEXT,
    `record_month` CHAR(7) NOT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY `uk_user_month` (`user_id`, `record_month`)
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_unicode_ci;
