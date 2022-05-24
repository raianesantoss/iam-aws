import boto3
import json
import random
import string


account = boto3.client('sts').get_caller_identity().get('Account')
client = boto3.client ('iam')
iam = boto3.resource('iam')

N = 20
request = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits + string.punctuation) for _ in range(N))

username = "--Digita o nome/email do usuario a ser criado--"

#Criar usuário no IAM
def create_user():

    response = client.create_user(
        UserName=username,
    )['User']
    print("-----Segue os dados para o usuário-----")
    print("Login de acesso:",response['UserName'])
    print("Arn com o ID Conta:",response['Arn'])

#Criar a senha do usuário
def create_login_profile():

    response = client.create_login_profile (
        UserName=username,
        Password=request,
        PasswordResetRequired=True
    )
    print("Senha para o primeiro acesso:",request)

#Remove police gerenciada pela AWS
def detach_user_policy(policy_arn):
    attached_policy = iam.Policy(policy_arn)
    response = attached_policy.detach_user(
        UserName=username
    )
    print("Deu certo! Removeu a police gerenciada da AWS do usuário")

#Remove police Inline do usuário
def delete_policies():
    response = client.list_attached_user_policies (
        UserName=username
    )
    for police in response['AttachedPolicies']:
        detach_user_policy(police['PolicyArn'])

    response = client.list_user_policies (
        UserName=username
    )
    for police in response['PolicyNames']:
        client.delete_user_policy (
        UserName=username,
        PolicyName=police
    )
        print("Deu certo! Removeu a police inline do usuário")

#Lista police do usuario
def list_polices_user():
    response = client.list_user_policies(
        UserName=username,
    )
    for police in response['PolicyNames']:
        print(police)

#Deleta a senha do usuario
def delete_login_user():
    login_profile = iam.LoginProfile(username)
    login_profile.delete()
    print("Deu certo! Removeu o login do usuário")

#Deleta o usuário
def delete_user():
    response = client.delete_user(
        UserName=username
    )
    print("Deu certo! Excluiu o usuário")

#Lista todos os usuários do IAM
def list_users():
    paginator = iam.get_paginator('list_users')
    for response in paginator.paginate():
        for user in response["Users"]:
            print(user['UserName'])

#Atacha police no usuario
def attach_user_policy(policy_arn):
    iam = boto3.client("iam")
    response = iam.attach_user_policy(
        UserName=username,
        PolicyArn=policy_arn
    )
    print(response)

#Cria police Leitura(escolher o serviço)
def create_police_read():
    my_managed_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "dynamodb:ListTables",
                    "dynamodb:DescribeContributorInsights",
                    "dynamodb:ListTagsOfResource",
                    "dynamodb:DescribeReservedCapacityOfferings",
                    "dynamodb:TagResource",
                    "dynamodb:PartiQLSelect",
                    "dynamodb:DescribeTable",
                    "dynamodb:GetItem",
                    "dynamodb:DescribeContinuousBackups",
                    "dynamodb:DescribeExport",
                    "dynamodb:DescribeKinesisStreamingDestination",
                    "dynamodb:ListExports",
                    "dynamodb:DescribeLimits",
                    "dynamodb:BatchGetItem",
                    "dynamodb:ConditionCheckItem",
                    "dynamodb:UntagResource",
                    "dynamodb:ListBackups",
                    "dynamodb:Scan",
                    "dynamodb:Query",
                    "dynamodb:DescribeStream",
                    "dynamodb:DescribeTimeToLive",
                    "dynamodb:ListStreams",
                    "dynamodb:ListContributorInsights",
                    "dynamodb:DescribeGlobalTableSettings",
                    "dynamodb:ListGlobalTables",
                    "dynamodb:GetShardIterator",
                    "dynamodb:DescribeGlobalTable",
                    "dynamodb:DescribeReservedCapacity",
                    "dynamodb:DescribeBackup",
                    "dynamodb:GetRecords",
                    "dynamodb:DescribeTableReplicaAutoScaling"
                ],
                "Resource": "*"
            }
        ]
    }
    response = iam.create_policy(
        PolicyName='dynamoRead',
        PolicyDocument=json.dumps(my_managed_policy)
    )['Policy']
    print(response['Arn'])

#Cria police Leitura/Escrita(escolher o serviço)
def create_police_read_write():
    my_managed_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "dynamodb:*"
                ],
                "Resource": "*"
            }
        ]
    }
    response = iam.create_policy(
        PolicyName='dynamoReadWrite',
        PolicyDocument=json.dumps(my_managed_policy)
    )['Policy']
    print(response['Arn'])

#Cria police Admin
def create_police_admin():
    my_managed_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": "*",
                "Resource": "*"
            }
        ]
    }
    response = iam.create_policy(
        PolicyName='AdministratorAccess',
        PolicyDocument=json.dumps(my_managed_policy)
    )['Policy']
    print(response['Arn'])


#Criar role (EXTRA)
def create_iam_role():
    assume_role_policy_document = json.dumps({
        "Version": "2012-10-17",
        "Statement": [
            {
            "Effect": "Allow",
            "Principal": {
                "Service": "glue.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
            }
        ]
    })

    response = iam.create_role(
        RoleName = "AwsGestaoAccess",
        AssumeRolePolicyDocument = assume_role_policy_document
    )['Role']

    print(response['RoleName'] + " - " + response["Arn"])


'''Para excluir um usuário no IAM, primeiro tem que fazer os procedimentos abaixo:
1 - Desatachar as polices que o usuário tem
2 - '' os grupos que o usuário está atribuido
3 - Deletar o Login do Usuário > delete_login_user
4 - Deletar usuário
'''
