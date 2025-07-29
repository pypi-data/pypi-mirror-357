---
orphan: true
---

# DMS Serverless

In that output, please note that the value of `ReplicationConfigArn` is of significant
relevance for the next steps in the walkthrough. It is the unique global identifier for
your replication configuration.

You can use it as value for the `--replication-config-arn` option 1:1, and we also
recommend last fragment of the value, the local identifier for your replication
configuration, into an environment variable for easier access.
```shell
export DMS_REPLICATION_ID=OZRAVXDSNFCUTG5UZNI6HRDWVY
```


```shell
aws logs get-log-events \
  --log-group-name dms-serverless-replication-${DMS_REPLICATION_ID} \
  --log-stream-name dms-serverless-replication-orchestrator-${DMS_REPLICATION_ID} | jq .events[].message
```

```shell
aws logs start-live-tail --log-group-identifiers \
    arn:aws:logs:eu-central-1:831394476016:log-group:/aws/rds/instance/testdrive-dms-postgresql-dev-db/postgresql \
    arn:aws:logs:eu-central-1:831394476016:log-group:dms-serverless-replication-${DMS_REPLICATION_ID}
```

```shell
aws dms start-replication \
    --start-replication-type=start-replication \
    --replication-config-arn \
    arn:aws:dms:eu-central-1:831394476016:replication-config:EAM3JEHXGBGZBPN5PLON7NPDEE
```

Enumerate all configured replications.
```shell
aws dms describe-replications
```


```shell
aws dms describe-replications | \
  jq '.Replications[] | {ReplicationConfigIdentifier, ReplicationConfigArn, ReplicationType, StartReplicationType, Status, StopReason, FailureMessages, ProvisionData}'

aws logs describe-log-groups
```


```text
"{'replication_state':'initializing', 'message': 'Initializing the replication workflow.'}"
"{'replication_state':'preparing_metadata_resources', 'message': 'Preparing the resources for metadata collection. This can take some time.'}"
"{'replication_state':'testing_connection', 'message': 'Completed preparing resources for metadata collection. Testing connection to source and target endpoints to ensure proper configuration.'}"
```
After a while, you will see DMS connecting to your RDS PostgreSQL instance.
```text
2024-08-03 14:44:05 UTC:10.0.0.75(48820):[unknown]@[unknown]:[3000]:LOG:  connection received: host=10.0.0.75 port=48820
2024-08-03 14:44:05 UTC:10.0.0.75(48820):dynapipe@postgres:[3000]:LOG:  connection authenticated: identity="dynapipe" method=md5 (/rdsdbdata/config/pg_hba.conf:13)
```

Relevant failure or replication shutdown message can look like this. Please
keep an eye on them.
```text
"{'replication_state':'failed', 'message': 'Test connection failed for endpoint testdrive-dms-postgresql-dev-endpoint-source.', 'failure_message': 'Test connection failed for endpoint 'testdrive-dms-postgresql-dev-endpoint-source' and replication config 'testdrive-dms-postgresql-dev-dms-serverless'. Failure Message: 'Error Details: [message=Unknown exception while calling 'Test endpoint' API, errType=, status=0, errMessage=, errDetails=]''}"
"{'replication_state':'deleting', 'message': 'Replication is being deleted.'}"
```

aws dms stop-replication


[AWS::DMS::ReplicationConfig]: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationconfig.html
[Working with AWS DMS Serverless]: https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Serverless.html
