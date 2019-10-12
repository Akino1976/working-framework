#!/usr/bin/env Rscript
## load tables
options(scipen=999)

source(
    list.files(
        pattern = "common_function.R",
        recursive = TRUE,
        full.names = TRUE
    )
)
.pkg 		<- c(
    "data.table",
	"ggplot2",
	"parallel",
	"grid",
	'bit64',
	'RODBC',
	'gridExtra',
	'lubridate',
	'jsonlite',
	'odbc',
	'ggthemes'
)
Object 	<- new("startUps", pkgs = .pkg , Input = c("data", "graf") )

Object$instant_pkgs( )

get_data 	<- function(table_name, data_base = 'TestDB', query = NULL, nr_time=4)
{
	con		<- odbcConnect(data_base)
	if( !is.null(query))
	{
		query <- query
	} else {
		query		<- sprintf("select * from [%s].[dbo].[%s]", data_base, table_name)
	}
	dataSet	<- sqlQuery(con, query, as.is = rep(nr_time, 'TRUE'))
	setDT(dataSet)
	close(con)
	return(dataSet)
}
con <- odbc::dbConnect(odbc::odbc(),
                 Driver = "ODBC Driver 17 for SQL Server",
                 Server = 'storage',
                 Database = 'TestDB',
                 UID = 'SA',
                 PWD = 'Test-password')

query = sprintf('SELECT [query_date]
      ,[trainNumber]
      ,[departureDate]
      ,[operatorUICCode]
      ,[operatorShortCode]
      ,[trainType]
      ,[trainCategory]
      ,[commuterLineID]
      ,[runningCurrently]
      ,[cancelled]
      ,[version]
      ,[timetableType]
      ,[timetableAcceptanceDate]
      ,[timeTableRows]
  FROM [TestDB].[dbo].[train_information]')

result     <- odbc::dbSendQuery(con, query)
dataDT     <- odbc::dbFetch(result)
setDT(dataDT)

dataDT[, nr_of_rows := 1:.N, by = .(query_date)]
dataDT	<- dataDT[nr_of_rows == 1]
## parse the json column and merge back again
id_nr 	<- which(names(dataDT) == 'timeTableRows')
identity_columnes 	<- dataDT[, -c(id_nr), with = FALSE]

parseDT	<- dataDT[, c(1,id_nr), with = FALSE]
newDT	<- list()
for( .nr in seq_len(NROW(parseDT)))
{
	cat(strrep('#', 60), '\n')

	.row 		<-  parseDT[.nr]
	cat('Running ', .row[, query_date] , '\n')
	json_blob 	<- fromJSON(
		.row[,  timeTableRows],
		flatten = TRUE
	)

	old_names 	<- names(json_blob)
	new_names 	<- gsub('\\.', '_', old_names)
	colnames(json_blob) 	<- new_names

	json_blob[['query_date']] <- as.character(.row[, query_date])

	newDT[[.nr]] <- as.data.table(json_blob)
}

newDT 	<-  rbindlist(newDT, fill=TRUE)
newDT	<- newDT[query_date != 'TRUE']

setkey(identity_columnes, query_date)
setkey(newDT, query_date)

datasetDT	<- newDT[identity_columnes]
rm(identity_columnes, newDT, dataDT, json_blob, old_names,new_names, parseDT, result)
gc(reset = TRUE)

## rm strange column
datasetDT[, causes := NULL]
GRAF	<- dir(path = '.', pattern = 'GRAF', full.names = TRUE)
fwrite(datasetDT, file = file.path(GRAF, 'train.csv'))
HKI

TPE

intitalDT		<- datasetDT[stationShortCode %in% c('HKI', 'TPE')  ]
trainDT			<- rbind(
		intitalDT[(stationShortCode == 'TPE' & type == 'ARRIVAL')],
		intitalDT[(stationShortCode == 'HKI' & type == 'DEPARTURE')]
)
trainDT[, ':=' (
		scheduledTime = ymd_hms(scheduledTime),
		actualTime = ymd_hms(actualTime)
)]

trainDT[, late_in_sec := as.integer(difftime(actualTime, scheduledTime, units = 'sec'))]
trainDT[, days_late := wday(actualTime, label = TRUE, abbr = TRUE)]


trainDT[  , unix_time_schedual := as.numeric(as.POSIXct(scheduledTime))]
trainDT[order(scheduledTime), time_travel_min := diff(unix_time_schedual), by = 'departureDate']

average_time_travel 	<- unique(
		trainDT, by = c('query_date')
)[, mean(time_travel_min)/60, by = 'days_late']

BAR	<-		ggplot( average_time_travel, aes( x = days_late, y = V1 )) +
				geom_bar(stat = "identity", position = "stack" )	+
				theme_igray() +
				labs(x = '', y = 'Minutes', title = 'Average time spend on train')

pdf( file = file.path( GRAF, "average_time_distiance.pdf") ,
     height = unit(6,"cm"), width = unit(9,"cm"),
     pointsize = 10, colormodel = "rgb")
print(BAR)
dev.off( )


lateDT	<- trainDT[, .(late_min = mean(late_in_sec)/60), by = .(days_late, type)]

BAR	<-		ggplot( lateDT, aes( x = days_late, y = late_min )) +
				geom_bar(stat = "identity", position = "stack" )	+
				facet_wrap( . ~type) +
				theme_igray() +
				labs(x = 'week-days', 'Late per secund', title = 'Late between Tampere (ARRIVAL) and Helsinki (DEPARTURE)')

pdf( file = file.path( GRAF, "late_per_second.pdf") ,
     height = unit(6,"cm"), width = unit(9,"cm"),
     pointsize = 10, colormodel = "rgb")
print(BAR)
dev.off( )
rm(BAR)


trainDT[, quantile(late_in_sec, probs = seq(0,1,0.01))]
trainDT[, table(stationShortCode)]
trainDT[, table(stationShortCode, type)]
