import awswrangler as wr
from api import convertToDataframe
from botocore.awsrequest import AWSHTTPSConnection
import os

S3_BUCKET = "awswrangler-storage-bucket"
FOLDER_PATH = "datasets"
RAW_PATH = f"s3://{S3_BUCKET}/{FOLDER_PATH}/THE_GUARDIAN.csv"



def writeToS3Bucket():
    dataframe = convertToDataframe()
    
    try:
        data = wr.s3.to_csv(df=dataframe,  path = RAW_PATH)
        
    except AWSHTTPSConnection as e:
        print(f"An Error Occured : {e}")
    return data
    

def readFromS3Bucket():
    data = wr.s3.read_csv(path=RAW_PATH)
        
    return data

readResult = readFromS3Bucket()
print(readResult)