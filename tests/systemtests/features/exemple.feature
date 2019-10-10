Feature: example command line test

  Background:
    Given the entrypoint "ls"

  Scenario: A call to ls in a folder
    Given the command "/usr/src/"
    And the flags "-a"
    And the bucket bambora-bi-storage-formatted-docker-eu-west-1 is empty
    When the app is called from the command line
    Then the return code should be 0
