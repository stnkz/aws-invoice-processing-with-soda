## Getting started with Soda Core in AWS Pipeline

This project is a sample of serverless architecture that can process scanned invoices in PDF or image formats as inputs for submitting payment information to a database, with Soda Core checks applied.

## Table of Contents

1. [About the Project](#about-the-project)
2. [Prerequisites](#prerequisites)
3. [Deploy](#deploy)
4. [Testing the solution](#testing-the-solution)
5. [References](#references)

## About the Project

Using Step Functions and Amazon Textract you can build a workflow that enables invoice reading and processing. Adding a layer of data quality checks in the pipeline should minimize the risk of having bad data. Using Soda Core to test data quality in an AWS Pipeline involves integrating Soda Core checks into data pipeline process, which can be orchestrated using AWS Step Functions. This project is based on ab aws sample project [Getting started with RPA using AWS Step Functions and Amazon Textract](https://github.com/aws-samples/aws-step-functions-rpa) and [blog post](https://aws.amazon.com/blogs/compute/getting-started-with-rpa-using-aws-step-functions-and-amazon-textract/)

## Prerequisites

1. [Python](https://www.python.org/)

2. [AWS Command Line Interface (AWS CLI)](https://aws.amazon.com/cli/)
    -- for instructions, see [Installing the AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html)

3. [AWS Serverless Application Model Command Line Interface (AWS SAM CLI)](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-command-reference.html)
    -- for instructions, see [Installing the AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)

4. Available PostgreSQL instance. You can setup an instance in AWS RDS (expensive) or setup PostgreSQL on an EC2 instance.

5. AWS account

## Deploy

1. Run the following command to build the artifacts locally:

        sam build

2. Run the following command to create a CloudFormation stack and deploy your resources:

        sam deploy --guided 

## Testing the solution

1. Prepare checks in soda_check lambda function
2. Upload the PDF test invoice to the S3 bucket named scanned-invoices in your AWS account. You can reuse one from the invoices
3. Go to AWS Step Function executions page and follow the execution.

## References

- [AWS CLI](https://aws.amazon.com/cli/)
- [Soda documentation](https://docs.soda.io/)
- [Soda Core](https://github.com/sodadata/soda-core)
- [AWS Sample](https://github.com/aws-samples/aws-step-functions-rpa)
- [Soda Integrations](https://www.soda.io/integrations#all)
