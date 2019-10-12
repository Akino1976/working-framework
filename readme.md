## Requirements
Work assigment
# System usage
`AWS -> S3 -> SNS -> SQS`
`Python`
`R`
more inside src/main.R
## database
Analysis is done inside R and by connecting to t-sql `(mssql)`.
do this inside windows and then make a connection between `R` and `mssql`.

## Overall structure
  1. RestAPI: A call is made to an API where the payload is parsed and made to `ndjson`. Timeframe is from
    `2017-01-01` until `2017-07-05`
    Call is made to `insert_data.py`usung `make run-app`.
  2. Data is than uploaded to S3 and events to an SQS
  3. Python than reads the SQS and parses the file and insert the data into a database
  4. This is then read into R which make some further cleaning on the data.
  5. Charts are mad


## Automation
All this is done by docker containers and utlize MakeFile

![Average time spent on train](./analysis/GRAF/average_time_distiance.pdf){width=100% height=400}
![Average time spent on train](./analysis/GRAF/late_per_second.pdf){width=100% height=400}

