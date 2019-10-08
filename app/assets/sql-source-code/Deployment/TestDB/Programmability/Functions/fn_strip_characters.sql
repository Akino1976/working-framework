CREATE OR ALTER FUNCTION [dbo].[fn_strip_character](
	@input NVARCHAR(100)
)
RETURNS NVARCHAR(100)
AS
BEGIN
    WHILE PATINDEX('%[^0-9]%', @input) > 0
    SET @input = STUFF(@input, PATINDEX('%[^0-9]%', @input), 1, '')
    RETURN @input
END
