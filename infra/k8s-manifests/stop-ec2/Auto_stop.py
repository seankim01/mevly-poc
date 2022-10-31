'''
Auto_Stop_Policy
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "EC2",
            "Effect": "Allow",
            "Action": [
                "ec2:*"
            ],
            "Resource": "*"
        },
        {
            "Sid": "RDS",
            "Effect": "Allow",
            "Action": [
                "rds:*"
            ],
            "Resource": "*"
        },
        {
            "Sid": "AutoScale",
            "Effect": "Allow",
            "Action": [
                "autoscaling:*"
            ],
            "Resource": "*"
        },        
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:*:*:*"
        }
    ]
  }

Reference: 
    https://github.com/michimani/start-stop-ec2-python/blob/master/auto_start_stop_ec2.py
    https://gist.github.com/mlapida/1917b5db84b76b1d1d55

'''
import boto3
import logging

#setup simple logging for INFO
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def ec2_rds_stop(regions_list):
    #define the connection
    for region in regions_list:
        client_ec2 = boto3.client('ec2', region_name=region)
        client_rds = boto3.client('rds', region_name=region)

        #Use the filter() method of the instances collection to retrieve
        #all running EC2 instances.
        EC2_filter = [
            {
                'Name': 'instance-state-name', 
                'Values': ['running']
            }
        ]
        RDS_filter = [
            {
                'Name': 'DBInstanceStatus', 
                'Values': ['available']
            }
        ]

        #filter the instances, rds
        instances = client_ec2.describe_instances(Filters=EC2_filter)
        rds_instances = client_rds.describe_db_instances()

        target_instans_ids = []
        for reservation in instances['Reservations']:
            for instance in reservation['Instances']:
                #instance targetting 
                target_instans_ids.append(instance['InstanceId'])

        target_aurora_rds = []
        target_rds = []
        for dbinstances in rds_instances['DBInstances']:
            if dbinstances['Engine'] in "aurora":
                # for instance in dbinstances['Engine']:
                target_aurora_rds.append(dbinstances['DBClusterIdentifier'])
            else:
                # for instance in dbinstances['Engine']:
                target_rds.append(dbinstances['DBInstanceIdentifier'])

        #print the instances for logging purposes
        print(region)
        
        #make sure there are actually instances to shut down. 
        if len(target_instans_ids) > 0:
            #perform the EC2 stop
            print("Running_Instances: ", target_instans_ids)
            shuttingDown = client_ec2.stop_instances(InstanceIds=target_instans_ids)
            print(shuttingDown)
        else:
            print("EC2 Nothing to see here")

        if len(target_aurora_rds) > 0:
            #perform the Aurora Cluster stop
            for dbClusterIdentifier in target_aurora_rds:
                try: 
                    print("Aurora_cluster: ", dbClusterIdentifier)
                    shuttingDown = client_rds.stop_db_cluster(DBClusterIdentifier=dbClusterIdentifier)
                    print(shuttingDown)
                except:
                    pass
        else:
            print("Aurora Nothing to see here")

        if len(target_rds) > 0:
            #perform the other rds stop
            try:
                for dbInstanceIdentifier in target_rds:
                    print("RDS_Instances: ", dbInstanceIdentifier)
                    shuttingDown = client_rds.stop_db_instance(DBInstanceIdentifier=dbInstanceIdentifier)
                    print(shuttingDown)
            except:
                pass
        else:
            print("RDS Nothing to see here")
    return 0

def lambda_handler(event, context):
    #define the connection
    ec2 = boto3.client('ec2')

    # selecting all region 
    response = ec2.describe_regions()
    regions_list = [region['RegionName'] for region in response['Regions']]
    ec2_rds_stop(regions_list)

# auto_stop_asg
client = boto3.client('ec2')
regions = [region['RegionName'] for region in client.describe_regions()['Regions']]

for region in regions:
    client = boto3.client('autoscaling', region_name=region)
    all_asg = client.describe_auto_scaling_groups(
    )
    for semi_target in all_asg['AutoScalingGroups']:

        str_target = semi_target["AutoScalingGroupName"]
        
        response = client.update_auto_scaling_group(
            AutoScalingGroupName=str_target,
            MinSize=0,
            DesiredCapacity=0,
            DefaultCooldown=30,
        )    
