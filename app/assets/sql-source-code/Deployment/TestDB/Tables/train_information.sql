IF NOT EXISTS (
		SELECT *
		FROM sys.tables
		WHERE [name] = N'train_information'
			AND [type] = 'U'
)
BEGIN

    CREATE TABLE [dbo].[train_information] (
        [id] [bigint] IDENTITY(1, 1) NOT NULL,
        [query_date] [varchar](10) NOT NULL,
        [trainNumber] [varchar](50) NOT NULL,
        [departureDate] [varchar](255) NOT NULL,
        [operatorUICCode] [int] NULL,
        [operatorShortCode] [varchar](10) NULL,
        [trainType] [varchar](10) NULL,
        [trainCategory] [varchar](50) NULL,
        [commuterLineID] [varchar](50) NULL,
        [runningCurrently] [varchar](10) NULL,
        [cancelled] [varchar](10) NULL,
        [version] [varchar](50) NULL,
        [timetableType] [varchar](50) NULL,
        [timetableAcceptanceDate] [varchar](30) NULL,
        [timeTableRows] [text] NOT NULL,
        [insert_at] [datetime] default getdate(),
        CONSTRAINT [PK_id] PRIMARY KEY CLUSTERED ([id] ASC)
    )
END
