IF NOT EXISTS (
		SELECT *
		FROM sys.tables
		WHERE [name] = N'fun_table'
			AND [type] = 'U'
)
BEGIN

    CREATE TABLE [dbo].[fun_table] (
        [id] [bigint] IDENTITY(1, 1) NOT NULL,
        [error_message] [bigint] NULL,
        [source] [varchar](50) NULL,
        [data_base] [varchar](50) NULL,
        [table_name] [varchar](250) NOT NULL,
        [table_count] [bigint] NULL,
        [table_procedure] [varchar](50) NULL,
        [is_populated] [bit] DEFAULT 0,
        [is_merged] [bit] DEFAULT 0,
        [is_deleted] [bit] DEFAULT 0,
        [update_at] [datetime] NULL,
        CONSTRAINT [PK_cloud_job_checklist] PRIMARY KEY CLUSTERED ([table_name] ASC)
        )
END
