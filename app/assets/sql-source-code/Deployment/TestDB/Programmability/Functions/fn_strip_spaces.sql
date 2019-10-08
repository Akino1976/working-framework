CREATE OR ALTER FUNCTION [dbo].[fn_strip_spaces] (@str VARCHAR(8000))
RETURNS VARCHAR(8000)
AS
BEGIN
	WHILE CHARINDEX('  ', @str) > 0
		SET @str = REPLACE(@str, '  ', ' ')

	RETURN @str
END
