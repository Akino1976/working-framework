IF NOT EXISTS (
		SELECT *
		FROM sys.tables
		WHERE [name] = N'github_url'
			AND [type] = 'U'
)
BEGIN

    CREATE TABLE [dbo].[github_url] (
        [id] [bigint] IDENTITY(1, 1) NOT NULL,
        [source_url] [varchar](50) NOT NULL,
        [url] [varchar](255) NOT NULL,
        [insert_at] [datetime] default getdate(),
        CONSTRAINT [PK_github_url_id] PRIMARY KEY CLUSTERED ([id] ASC)
        )
END
