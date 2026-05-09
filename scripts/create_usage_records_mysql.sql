CREATE DATABASE IF NOT EXISTS `agent_project`
DEFAULT CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE `agent_project`;

CREATE TABLE IF NOT EXISTS `users` (
    `id` BIGINT PRIMARY KEY AUTO_INCREMENT,
    `user_id` VARCHAR(20) NOT NULL,
    `nickname` VARCHAR(50) NOT NULL,
    `city` VARCHAR(50),
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY `uk_users_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `devices` (
    `id` BIGINT PRIMARY KEY AUTO_INCREMENT,
    `device_id` VARCHAR(50) NOT NULL,
    `user_id` VARCHAR(20) NOT NULL,
    `model_name` VARCHAR(80) NOT NULL,
    `house_area` VARCHAR(50),
    `family_profile` VARCHAR(100),
    `floor_type` VARCHAR(100),
    `has_pet` TINYINT(1) DEFAULT 0,
    `status` VARCHAR(20) DEFAULT 'active',
    `bind_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY `uk_devices_device_id` (`device_id`),
    KEY `idx_devices_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `usage_records` (
    `id` BIGINT PRIMARY KEY AUTO_INCREMENT,
    `user_id` VARCHAR(20) NOT NULL,
    `device_id` VARCHAR(50),
    `feature` TEXT,
    `efficiency` TEXT,
    `consumables` TEXT,
    `comparison` TEXT,
    `record_month` CHAR(7) NOT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY `uk_user_month` (`user_id`, `record_month`),
    KEY `idx_usage_device_month` (`device_id`, `record_month`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `chat_sessions` (
    `id` BIGINT PRIMARY KEY AUTO_INCREMENT,
    `session_id` VARCHAR(64) NOT NULL,
    `user_id` VARCHAR(20) NOT NULL,
    `title` VARCHAR(100) DEFAULT '智能客服会话',
    `started_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `ended_at` TIMESTAMP NULL,
    UNIQUE KEY `uk_chat_sessions_session_id` (`session_id`),
    KEY `idx_chat_sessions_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `chat_messages` (
    `id` BIGINT PRIMARY KEY AUTO_INCREMENT,
    `session_id` VARCHAR(64) NOT NULL,
    `role` VARCHAR(20) NOT NULL,
    `content` LONGTEXT NOT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    KEY `idx_chat_messages_session_id` (`session_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `knowledge_files` (
    `id` BIGINT PRIMARY KEY AUTO_INCREMENT,
    `file_name` VARCHAR(255) NOT NULL,
    `file_path` VARCHAR(500) NOT NULL,
    `file_type` VARCHAR(20) NOT NULL,
    `md5_hash` VARCHAR(64),
    `file_size` BIGINT DEFAULT 0,
    `import_status` VARCHAR(20) DEFAULT 'imported',
    `imported_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY `uk_knowledge_file_path` (`file_path`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `tool_call_logs` (
    `id` BIGINT PRIMARY KEY AUTO_INCREMENT,
    `session_id` VARCHAR(64),
    `tool_name` VARCHAR(100) NOT NULL,
    `tool_args` TEXT,
    `tool_result` LONGTEXT,
    `success` TINYINT(1) DEFAULT 1,
    `error_message` TEXT,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    KEY `idx_tool_call_logs_session_id` (`session_id`),
    KEY `idx_tool_call_logs_tool_name` (`tool_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `report_records` (
    `id` BIGINT PRIMARY KEY AUTO_INCREMENT,
    `report_id` VARCHAR(64) NOT NULL,
    `user_id` VARCHAR(20) NOT NULL,
    `device_id` VARCHAR(50),
    `record_month` CHAR(7) NOT NULL,
    `report_content` LONGTEXT NOT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY `uk_report_records_report_id` (`report_id`),
    KEY `idx_report_records_user_month` (`user_id`, `record_month`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
