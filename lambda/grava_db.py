import json
from decimal import Decimal
import boto3

# Para o laboratório, vamos usar os valores fixos para o LocalStack
dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:4566")
table = dynamodb.Table("compromissos-gp1")
s3 = boto3.client('s3', endpoint_url="http://localhost:4566")

def lambda_handler(event, context):
    records = event.get("Records", [])
    if not records:
        print("Nenhum registro encontrado no evento")
        return {"statusCode": 400, "body": "Nenhum registro"}

    for record in records:
        bucket = record["s3"]["bucket"]["name"]
        key = record["s3"]["object"]["key"]
        print(f"\nProcessando arquivo '{key}' do bucket '{bucket}'")

        try:
            # Baixar o objeto do S3
            obj = s3.get_object(Bucket=bucket, Key=key)
            data = obj['Body'].read().decode('utf-8')

            # Tentar carregar como JSON
            try:
                nota = json.loads(data)
            except json.JSONDecodeError:
                print(f"Arquivo '{key}' não é um JSON válido. Ignorando.")
                continue

            # Converter floats para Decimal (necessário para DynamoDB)
            if 'valor' in nota:
                nota['valor'] = Decimal(str(nota['valor']))

            # Gravar no DynamoDB
            table.put_item(Item=nota)
            print(f"Registro {nota.get('id', 'N/A')} gravado com sucesso!")

        except Exception as e:
            print(f"Erro ao processar '{key}': {str(e)}")

    return {"statusCode": 200, "body": "Processamento concluído"}
