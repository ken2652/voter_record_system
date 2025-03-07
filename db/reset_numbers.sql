DELIMITER //

DROP PROCEDURE IF EXISTS reset_record_numbers//

CREATE PROCEDURE reset_record_numbers()
BEGIN
    SET @counter = 0;
    UPDATE voters_record SET NO = (@counter := @counter + 1) ORDER BY VOTERS_NAME;
END//

DELIMITER ;

CALL reset_record_numbers(); 