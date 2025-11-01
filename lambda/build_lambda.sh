#!/bin/bash
set -e
cd "$(dirname "$0")"

# Remove o zip antigo, se existir
rm -f ../lambda_function.zip

# Cria o novo pacote .zip contendo o código Python da Lambda
zip -j ../lambda_function.zip grava_db.py

echo "✅ Lambda empacotada com sucesso em ../lambda_function.zip"
