# Processador de Arquivos com AWS Lambda, S3 e DynamoDB (LocalStack)

Este projeto demonstra um fluxo de trabalho serverless simples usando uma função AWS Lambda escrita em Python. A função é acionada sempre que um novo arquivo é enviado para um bucket S3, processa o conteúdo do arquivo (esperando um JSON) e o armazena em uma tabela do DynamoDB.

Todo o ambiente da AWS é simulado localmente usando o **LocalStack**, permitindo o desenvolvimento e teste sem custos e sem a necessidade de uma conta AWS.

## Fluxo da Aplicação

1.  Um arquivo é enviado para um bucket no S3.
2.  O evento `s3:ObjectCreated` aciona a função Lambda.
3.  A função Lambda lê o arquivo do S3.
4.  Se o arquivo for um JSON válido, seu conteúdo é gravado como um item em uma tabela do DynamoDB.
5.  Se não for um JSON, a função registra um aviso e encerra o processamento para aquele arquivo.

---

## Estrutura do Projeto

```
lab-notas-fiscais/
├── lambda/
│   ├── grava_db.py           # O código-fonte da função Lambda
│   └── build_lambda.sh       # Script para empacotar a função em um .zip
│
├── teste.txt                 # Arquivo de exemplo (não-JSON) para testes
└── README.md                 # Este arquivo
```

---

## Pré-requisitos

Antes de começar, certifique-se de ter as seguintes ferramentas instaladas:

*   Docker
*   AWS CLI
*   LocalStack

---

## Como Executar Localmente

Siga os passos abaixo para configurar e testar o projeto em seu ambiente local.

### 1. Inicie o LocalStack

Abra um terminal e inicie o container do LocalStack:

```bash
localstack start -d
```

### 2. Empacote a Função Lambda

Execute o script de build para criar o pacote `.zip` que será implantado.

```bash
# Navegue até a pasta da lambda
cd lambda

# Dê permissão de execução para o script (necessário apenas na primeira vez)
chmod +x build_lambda.sh

# Execute o script
./build_lambda.sh

# Volte para a pasta raiz
cd ..
```
Isso criará o arquivo `lambda_function.zip` na raiz do projeto.

### 3. Crie os Recursos no LocalStack

Use a AWS CLI para criar o bucket S3 e a tabela DynamoDB.

```bash
# Crie o bucket S3
aws --endpoint-url=http://localhost:4566 s3api create-bucket --bucket notas-fiscais-upload --region us-east-1

# Crie a tabela DynamoDB
aws --endpoint-url=http://localhost:4566 dynamodb create-table \
    --table-name compromissos-gp1 \
    --attribute-definitions AttributeName=id,AttributeType=S \
    --key-schema AttributeName=id,KeyType=HASH \
    --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5
```

### 4. Implante a Função Lambda e o Gatilho

Crie a função Lambda e configure o S3 para acioná-la.

```bash
# Crie a função Lambda
aws --endpoint-url=http://localhost:4566 lambda create-function \
    --function-name processa-arquivo \
    --runtime python3.9 \
    --role arn:aws:iam::000000000000:role/lambda-ex \
    --handler grava_db.lambda_handler \
    --zip-file fileb://lambda_function.zip

# Configure o gatilho (trigger) do S3 para a Lambda
aws --endpoint-url=http://localhost:4566 s3api put-bucket-notification-configuration \
    --bucket notas-fiscais-upload \
    --notification-configuration '{ "LambdaFunctionConfigurations": [{ "LambdaFunctionArn": "arn:aws:lambda:us-east-1:000000000000:function:processa-arquivo", "Events": ["s3:ObjectCreated:*"] }]}'
```

### 5. Teste o Fluxo

Crie um arquivo de exemplo `nota.json`:
```json
{ "id": "NF-123", "cliente": "Empresa Fantasia", "valor": 99.50 }
```

Agora, envie-o para o bucket S3:
```bash
aws --endpoint-url=http://localhost:4566 s3 cp nota.json s3://notas-fiscais-upload/
```

### 6. Verifique o Resultado

Consulte a tabela do DynamoDB para ver se o item foi gravado com sucesso.

```bash
aws --endpoint-url=http://localhost:4566 dynamodb scan --table-name compromissos-gp1
```

Você deverá ver o item `NF-123` na saída do comando!


