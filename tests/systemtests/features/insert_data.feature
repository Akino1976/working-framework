Feature: s3_file_import and insert to SQL

  Background:
    Given the entrypoint "python"
    And the command "/usr/src/insert_data.py"
    And the flags "-e docker"
    And the bucket storage-docker-eu-west-1 is empty

  Scenario Outline: A call to insert_data for github service
    Given there is a file in S3 like:
      bucket: storage-docker-eu-west-1
      key: GITHUB/url-2018-08-07-13-00-24-aa234.ndjson
      content: |
        {'source_url': 'current_user_authorizations_html_url', 'url': 'https://github.com/settings/connections/applications{/client_id}'}
        {'source_url': 'authorizations_url', 'url': 'https://api.github.com/authorizations'}
    And the queue !GetAttribute settings.QUEUE_URL is purged
    And following tables are empty:
      database: TestDB
      tablename: github_url
       And the request body:
    event: !AsSQSMessage
        Service: Amazon S3
        Event: 's3:TestEvent'
        Time: '2014-10-13T15:57:02.079Z'
        Bucket: storage-docker-eu-west-1
        RequestId: 5582815E1AEA5ADF
        HostId: 8cLeGAmw098X5cv4Zkwcmo8vvZa3eH3eKxsPzbB9wrR+YstdA6Knx4Ip8EXAMPLE
        key: GITHUB/url-2018-08-07-13-00-24-aa234.ndjson
        size: 12312312
    When the app is called from the command line
    Then the return code should be 0
    And the database should contain:
      table_name: github_url
      database: TestDB
      content:
        - {'dim_date': '201807', 'adjustment_id': '00000000-0000-0000-0000-000000000000', 'elixir_merchant_id': 2, 'external_reference': '40f2dfb0-7234-494e-b31b-92bf37d40204_20180713_3', 'amount': 52218, 'currency': 'SEK', 'adjustment_type': 'GROWTH_FINANCE', 'sub_type': 'GROWTH_FINANCE_EXTERNAL_PROVIDER_PAYOUT', 'comment': 'Growth Finance', 'csv_file_name': null, 's3_object_name': 'ADJUSTSVC_to_ELIX/AdjustmentSvc-00000000-0000-0000-0000-000000000000-1531486821.xml.pgp', 'user_id': 'client_id:00000000-0000-0000-0000-000000000000', 'approval_state': 'approved', 'is_approved': True, 'rejection_reason_code': null, 'created_at': '2018-07-13', 'updated_at': '2018-07-13', 'balance_type': 'CREDIT', 'period_end': '2018-07-13', 'period_start': '2018-07-13', 'reason_spec': null, 'invoicing_period_end': '2018-07-13', 'invoicing_period_start': '2018-07-13', 'charge_date': null, 'charge_origin': null, 'charge_state': 'PENDING', 'is_charged': False, 'update_at': null, 'file_name': 'financial-adjustments-prod-eu-west-1-1-2018-08-07-13-00-24-aa234.ndjson'}
        - {'dim_date': '201807', 'adjustment_id': '00000000-0000-0000-0000-000000000002', 'elixir_merchant_id': 1, 'external_reference': '40f2dfb0-7234-494e-b31b-92bf37d40204_20180713_1', 'amount': 31522, 'currency': 'SEK', 'adjustment_type': 'GROWTH_FINANCE', 'sub_type': 'GROWTH_FINANCE_REPAYMENT', 'comment': 'Growth Finance', 'csv_file_name': null, 's3_object_name': 'ADJUSTSVC_to_ELIX/AdjustmentSvc-00000000-0000-0000-0000-000000000000-1531486821.xml.pgp', 'user_id': 'client_id:00000000-0000-0000-0000-000000000000', 'approval_state': 'approved', 'is_approved': True, 'rejection_reason_code': null, 'created_at': '2018-07-13', 'updated_at': '2018-07-13', 'balance_type': 'DEBIT', 'period_end': '2018-07-13', 'period_start': '2018-07-13', 'reason_spec': null, 'invoicing_period_end': '2018-07-13', 'invoicing_period_start': '2018-07-13', 'charge_date': null, 'charge_origin': null, 'charge_state': 'PENDING', 'is_charged': False, 'update_at': null, 'file_name': 'financial-adjustments-prod-eu-west-1-1-2018-08-07-13-00-24-aa234.ndjson'}
