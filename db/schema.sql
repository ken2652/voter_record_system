-- Create the database if it doesn't exist
CREATE DATABASE IF NOT EXISTS voter_records;
USE voter_records;

-- Create voters_record table with exact field definitions from MySQL Workbench
CREATE TABLE IF NOT EXISTS voters_record (
    NO int NOT NULL,
    VOTERS_NAME varchar(100) DEFAULT NULL,
    PRECINCT_NO varchar(20) DEFAULT NULL,
    BARANGAY varchar(100) DEFAULT NULL,
    SITIO varchar(100) DEFAULT NULL,
    RICE_BENEFICIARY_1 varchar(1) DEFAULT NULL,
    RICE_BENEFICIARY_HEAD_2 varchar(1) DEFAULT NULL,
    BARANGAY_LEADER_3 varchar(1) DEFAULT NULL,
    LEVEL_1 varchar(1) DEFAULT NULL,
    LEVEL_2 varchar(1) DEFAULT NULL,
    LEVEL_3 varchar(1) DEFAULT NULL,
    REMARKS text DEFAULT NULL,
    RBH_NAME varchar(100) DEFAULT NULL,
    BL_NAME varchar(100) DEFAULT NULL,
    PRIMARY KEY (NO)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Create stored procedure for resetting record numbers
DELIMITER //

DROP PROCEDURE IF EXISTS reset_record_numbers//

CREATE PROCEDURE reset_record_numbers()
BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE record_id INT;
    DECLARE counter INT DEFAULT 1;
    DECLARE cur CURSOR FOR SELECT NO FROM voters_record ORDER BY VOTERS_NAME;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;
    
    START TRANSACTION;
    OPEN cur;
    
    read_loop: LOOP
        FETCH cur INTO record_id;
        IF done THEN
            LEAVE read_loop;
        END IF;
        
        UPDATE voters_record SET NO = counter WHERE NO = record_id;
        SET counter = counter + 1;
    END LOOP;
    
    CLOSE cur;
    COMMIT;
END//

DELIMITER ;

-- Clean existing data before inserting
TRUNCATE TABLE voters_record;

-- Insert validated/consolidated records
INSERT INTO voters_record (
    NO,
    VOTERS_NAME,
    PRECINCT_NO,
    BARANGAY,
    SITIO,
    RICE_BENEFICIARY_1,
    RICE_BENEFICIARY_HEAD_2,
    BARANGAY_LEADER_3,
    LEVEL_1,
    RBH_NAME,
    BL_NAME
) VALUES 
    (1, 'AGUILAR, DARREL', '102B', 'BRGY. 1', 'ZONE 1', '1', NULL, NULL, '1', NULL, 'ALADO, SITI'),
    (2, 'ALADO, SITI', '101A', 'BRGY. 1', 'ZONE 1', '1', NULL, '3', '1', 'DAPITON, QUIRINO', 'ALADO, SITI'),
    (3, 'BALATAYO, RENIER', '101A', 'BRGY. 1', 'ZONE 2', '1', NULL, NULL, '1', 'DAPITON, QUIRINO', 'DEMALATA, CARL'),
    (4, 'BARANDA, ELORA', '102B', 'BRGY. 1', 'ZONE 3', '1', NULL, NULL, '1', 'DALIVA, JULIUS', 'DELLOMOS, EMELINE'),
    (5, 'BENGA-ORA, MARIFE', '101A', 'BRGY. 1', 'ZONE 2', '1', NULL, NULL, '1', 'DAPITON, QUIRINO', 'ALADO, SITI'),
    (6, 'BOLARDE, CLAIRE', '101A', 'BRGY. 1', 'ZONE 2', '1', NULL, NULL, '1', 'DAPITON, QUIRINO', NULL),
    (7, 'BORJA, CHRISTINE', '102A', 'BRGY. 1', 'ZONE 1', '1', NULL, NULL, '1', 'DALIVA, JULIUS', NULL),
    (8, 'BORRO, WILMA', '101B', 'BRGY. 1', 'ZONE 1', '1', NULL, NULL, '1', 'DAPITON, QUIRINO', 'DEMALATA, CARL'),
    (9, 'CABE, RONNEL', '101B', 'BRGY. 1', 'ZONE 3', '1', NULL, NULL, '1', 'DAPITON, QUIRINO', 'DEMALATA, CARL'),
    (10, 'DALIVA, JULIUS', '102A', 'BRGY. 1', 'ZONE 2', '1', '2', NULL, '1', 'DALIVA, JULIUS', NULL),
    (11, 'DAPITON, QUIRINO', '101B', 'BRGY. 1', 'ZONE 3', '1', '2', NULL, '1', 'DAPITON, QUIRINO', NULL),
    (12, 'DELLOMOS, EMELINE', '102A', 'BRGY. 1', 'ZONE 1', '1', NULL, '3', '1', NULL, NULL),
    (13, 'DEMALATA, CARL', '101A', 'BRGY. 1', 'ZONE 3', '1', NULL, '3', '1', NULL, 'DELLOMOS, EMELINE'),
    (14, 'LABTO, JAMES', '101B', 'BRGY. 1', 'ZONE 3', '1', NULL, NULL, '1', NULL, 'DEMALATA, CARL'),
    (15, 'MEDINA, JOY', '101A', 'BRGY. 1', 'ZONE 1', '1', NULL, NULL, '1', NULL, 'DELLOMOS, EMELINE');

-- Call the procedure to ensure initial numbering is correct
CALL reset_record_numbers();
