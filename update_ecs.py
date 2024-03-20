import json
import os
import boto3

# Entry point of the program
def lambda_handler(event, context):
    try:
        # Get list of cluster ARNs excluding production clusters
        cluster_names = get_all_clusters_arn()
        running_tasks = []  # Initialize a list to store running task ARNs

        # Iterate over each cluster
        for cluster_name in cluster_names:
            # Iterate over each service in the cluster
            for service in get_all_services_arn(cluster_name):
                # Extract service name from ARN
                service_name = extract_service_name(service)
                # Get the count of running tasks for the service
                running_task_count = get_running_task(cluster_name, service)

                # If there are running tasks for the service, add it to the list
                if running_task_count > 0:
                    running_tasks.append(service_name)

        print("Running tasks:", running_tasks)

    except Exception as e:
        print(e)
        return response(500, str(e))

# Function to remove 'prod' clusters from the list of ARNs
def remove_prod_arns(arn_list):
    return [arn for arn in arn_list if "prod" not in arn.lower()]

# Function to extract service name from ARN
def extract_service_name(service_arn):
    return service_arn.split("/")[-1]

# Function to get AWS ECS client
def get_client():
    region = os.environ.get("AWS_REGION")
    return boto3.client("ecs", region_name=region)

# Function to get list of cluster ARNs
def get_all_clusters_arn():
    ecs = get_client()
    try:
        cluster_response = ecs.list_clusters()
        clusters_arns = cluster_response["clusterArns"]
        return remove_prod_arns(clusters_arns)
    except Exception as e:
        print(e)
        return response(500, str(e))

# Function to get list of service ARNs for a given cluster
def get_all_services_arn(cluster):
    ecs = get_client()
    try:
        service_response = ecs.list_services(cluster=cluster)
        return service_response["serviceArns"]
    except Exception as e:
        print(e)
        return response(500, str(e))

# Function to get the count of running tasks for a service in a cluster
def get_running_task(cluster, service):
    ecs = get_client()
    try:
        response = ecs.describe_services(
            cluster=cluster,
            services=[service]
        )
        return response['services'][0]['runningCount']
    except Exception as e:
        print(e)
        return 0  # If there's an error, assume running count as 0

# Utility function to construct response object
def response_object(status, message):
    return {"statusCode": status, "body": json.dumps({"message": message})}

# Utility function to construct response based on status
def response(status, message):
    if status == 200:
        return response_object(status, message)
    else:
        return response_object(status, message)

# Utility function to extract request body and handle JSON parsing
def request_object(event):
    try:
        body = json.loads(event["body"])
        return body
    except:
        return event

# Utility function to get desired tasks from request body
def get_desired_tasks(body):
    return body['desired_tasks']

# Utility function to extract cluster names from request body
def extract_clusters(body):
    return body["cluster_names"].split(',')

# Utility function to extract environment from request body
def get_environment(body):
    return body['environment'].split(',')

# Main entry point of the program
if __name__ == "__main__":
    print("Hello World")  # Initial print statement

