"""
SageMaker Pipeline Trigger
Run this when drift is detected to start automated retraining
"""
import boto3
import json
from datetime import datetime

def trigger_retraining_pipeline(
    pipeline_name='fraud-detection-pipeline',
    region='ap-south-1'
):
    """Trigger SageMaker pipeline for retraining"""
    client = boto3.client('sagemaker', region_name=region)

    response = client.start_pipeline_execution(
        PipelineName=pipeline_name,
        PipelineExecutionDisplayName=f"retrain-{datetime.now().strftime('%Y-%m-%d-%H-%M')}",
        PipelineParameters=[
            {'Name': 'trigger_reason', 'Value': 'data_drift_detected'}
        ]
    )

    execution_arn = response['PipelineExecutionArn']
    print(f"Pipeline triggered: {execution_arn}")
    return execution_arn

def check_pipeline_status(execution_arn, region='ap-south-1'):
    """Check if pipeline is still running"""
    client = boto3.client('sagemaker', region_name=region)
    response = client.describe_pipeline_execution(
        PipelineExecutionArn=execution_arn
    )
    status = response['PipelineExecutionStatus']
    print(f"Pipeline status: {status}")
    return status

if __name__ == "__main__":
    print("Triggering SageMaker retraining pipeline...")
    arn = trigger_retraining_pipeline()
    print(f"Pipeline started: {arn}")
    print("Monitor at: https://console.aws.amazon.com/sagemaker/pipelines")
