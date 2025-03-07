DELIMITER //

DROP TRIGGER IF EXISTS after_delete_voter//

CREATE TRIGGER after_delete_voter 
AFTER DELETE ON voters_record
FOR EACH ROW
BEGIN
    CALL reset_record_numbers();
END//

DELIMITER ; 