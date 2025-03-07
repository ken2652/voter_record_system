SET GLOBAL event_scheduler = ON;

DELIMITER //

DROP EVENT IF EXISTS reset_numbers_event//

CREATE EVENT reset_numbers_event
ON SCHEDULE EVERY 1 SECOND
DO
BEGIN
    SET @counter = 0;
    UPDATE voters_record SET NO = (@counter := @counter + 1) ORDER BY VOTERS_NAME;
END//

DELIMITER ; 