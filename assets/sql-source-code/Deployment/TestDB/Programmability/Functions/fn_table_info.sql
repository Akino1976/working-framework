CREATE OR ALTER FUNCTION [dbo].[fn_table_info](
	@tablename NVARCHAR(50)
)
RETURNS TABLE
AS RETURN(
	SELECT [system].[Name] AS [FieldName],
		[object].[Name] AS [TableName],
		[types].[Name] AS [DataType],
		[types].[max_length] AS [LengthSize],
		[types].[precision] AS [Precision]
	FROM [sys].[columns] AS [system]
	INNER JOIN [sys].[objects] AS [object] ON(
		[system].[object_id] = [object].[object_id]
	)
	LEFT JOIN [sys].[types] AS [types] ON(
		[types].[user_type_id] = [system].[user_type_id]
	)
	WHERE  [object].[type] = 'U'
	AND [object].[Name] = @tablename
)
