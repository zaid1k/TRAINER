import boto3
import botocore
import pandas as pd
from datetime import datetime, timedelta, timezone
profile_name={'default'}

########
def get_running_hours(instance_id, start_date, end_date,session):
    # Create a CloudWatch client
    cloudwatch = session.client('cloudwatch')

    # Define the metric and period
    metric_name = 'CPUUtilization'  # You can change this to other metrics like 'NetworkIn', 'NetworkOut', etc.
    namespace = 'AWS/EC2'
    period = 3600  # 1 hour

    # Set the start and end times for the query
    start_time = start_date
    end_time = end_date

    # Get the statistics for the specified metric
    response = cloudwatch.get_metric_statistics(
        Namespace=namespace,
        MetricName=metric_name,
        Dimensions=[
            {'Name': 'InstanceId', 'Value': instance_id}
        ],
        StartTime=start_time,
        EndTime=end_time,
        Period=period,
        Statistics=['Sum']
    )

    # Calculate the total running hours based on the metric data
    total_hours = 0.0
    #print(response['Datapoints'])
    for datapoint in response['Datapoints']:
        total_hours += 1 #datapoint['Sum'] / 100  # Assuming the metric is in percentage, convert it to hours

    return total_hours

########


def get_alarms_for_instance(instance_id,session):
    # Create CloudWatch client
    cloudwatch = session.client('cloudwatch')

    # List metrics for the instance
    metrics = cloudwatch.list_metrics(Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}])
    # Extract metric names and namespaces
    metric_info = [(metric['MetricName'], metric['Namespace']) for metric in metrics['Metrics']]
    # Initialize alarm count for the instance
    alarm_count = 0

    # Iterate through each metric and count associated alarms
    for metric_name, namespace in metric_info:
        metric_alarms = cloudwatch.describe_alarms_for_metric(
            MetricName=metric_name,
            Namespace=namespace,
            Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}]
        )
        for alarm in metric_alarms['MetricAlarms']:
            print(alarm)
        alarm_count += len(metric_alarms['MetricAlarms'])
        print(f'instance id = {instance_id} alarm count = {alarm_count}')  
    return (alarm_count)

def inventoryDetails():
    excel_writer = pd.ExcelWriter(f'C:\\Users\\lgfb4232\\Documents\\CFT\\python-codes\\usfiles\\US-inventory-ason-5jan-with-hours1.xlsx', engine='xlsxwriter')

    for key in profile_name:
        print (key)
        # Create a session using the named profile
        session = boto3.Session(profile_name=key)

        # Initialize Boto3 client for EC2
        ec2_client = session.client('ec2')

        instances = ec2_client.describe_instances()

        # Extract relevant information
        instance_data = []
        for reservation in instances['Reservations']:
            for instance in reservation['Instances']:
                #print(instance)
                #total_alarms=get_alarms_for_instance(instance['InstanceId'],session)
                instance_id=instance['InstanceId']
                
                # launch_time_str = instance['LaunchTime']
                # launch_time = datetime.strptime(str(launch_time_str), "%Y-%m-%d %H:%M:%S%z").replace(tzinfo=timezone.utc)

                # start_date = datetime(2023, 9, 1, 0, 0, 0,tzinfo=timezone.utc)
                # end_date = datetime(2023, 9, 30, 23, 59, 59,tzinfo=timezone.utc)
                # running_hours_sept = get_running_hours(instance_id, start_date, end_date,session)
            
                # start_date = datetime(2023, 10, 1, 0, 0, 0,tzinfo=timezone.utc)
                # end_date = datetime(2023, 10, 31, 23, 59, 59,tzinfo=timezone.utc)
                # running_hours_oct = get_running_hours(instance_id, start_date, end_date,session)
            
                # start_date = datetime(2023, 11, 1, 0, 0, 0,tzinfo=timezone.utc)
                # end_date = datetime(2023, 11, 30, 23, 59, 59,tzinfo=timezone.utc)
                # running_hours_nov = get_running_hours(instance_id, start_date, end_date,session)

                instance_data.append({
                    'InstanceID': instance_id,
                    'InstanceType': instance['InstanceType'],
                    'PrivateIPAddress': instance.get('PrivateIpAddress', 'N/A'),
                    'PublicIPAddress': instance.get('PublicIpAddress', 'N/A'),
                    'State': instance['State']['Name'],
                    'AvailabilityZone': instance['Placement']['AvailabilityZone'],
                    'PlatformDetails': instance['PlatformDetails'],
                    'LaunchTime': instance['LaunchTime'].strftime('%Y-%m-%d %H:%M:%S')
                })
            #    print(instance_data)
            # Create a DataFrame from the extracted data
        df = pd.DataFrame(instance_data)
        df.to_excel(excel_writer, sheet_name=profile_name[key], index=False)

    # Save the Excel file
    excel_writer._save()

    print('EC2 instance details have been saved to ec2_instance_details.xlsx')
            
def instanceCounts():
    instance_data = []
    for key in profile_name:
        # Create a session using the named profile
        session = boto3.Session(profile_name=key)

        # Initialize Boto3 client for EC2
        ec2_client = session.client('ec2')

        instances = ec2_client.describe_instances()
        instance_count = len(instances['Reservations'])
    
        instance_data.append({
            'Account Name': profile_name[key],
            'No of Instances': instance_count
        })
        print(f'No of instances in {profile_name[key]} is = {instance_count}')
    
    excel_writer = pd.ExcelWriter("C:\\Users\\lgfb4232\\Documents\\CFT\\python-codes\\usfiles\\Ec2CountsEU.xlsx", engine='xlsxwriter')
    # Create a DataFrame from the extracted data
    df = pd.DataFrame(instance_data)
    df.to_excel(excel_writer, sheet_name="US EC2 Counts", index=False)

    # Save the Excel file
    excel_writer._save()

#instanceCounts()
inventoryDetails()