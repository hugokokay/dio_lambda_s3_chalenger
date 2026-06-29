import boto3
import urllib.parse
from datetime import datetime

# Inicializa o cliente S3
s3_client = boto3.client('s3')

#  NOMES DOS BUCKETS (ALTERE AQUI PELOS SEUS NOMES REAIS)
BUCKET_ORIGEM = 'seu-bucket-origem-exemplo'
BUCKET_DESTINO = 'seu-bucket-destino-exemplo'

def lambda_handler(event, context):
    # Extrai o nome do arquivo (Key) do evento disparado pelo S3
    key_origem = urllib.parse.unquote_plus(
        event['Records'][0]['s3']['object']['key'], 
        encoding='utf-8'
    )
    
    # Validação opcional (boa prática): garante que o evento veio do bucket esperado
    bucket_do_evento = event['Records'][0]['s3']['bucket']['name']
    if bucket_do_evento != BUCKET_ORIGEM:
        print(f"⚠️ Atenção: Evento recebido de '{bucket_do_evento}', mas o configurado é '{BUCKET_ORIGEM}'")

    # Gera a data e hora atual formatada
    agora = datetime.now()
    data_hora = agora.strftime("%Y-%m-%d_%H-%M-%S")
    
    # Cria o novo nome do arquivo com data/hora + nome original
    if '.' in key_origem:
        nome, extensao = key_origem.rsplit('.', 1)
        novo_nome = f"{data_hora}_{nome}.{extensao}"
    else:
        novo_nome = f"{data_hora}_{key_origem}"
        
    try:
        # Copia o arquivo do bucket de origem para o de destino com o novo nome
        s3_client.copy_object(
            Bucket=BUCKET_DESTINO,
            CopySource={'Bucket': bucket_do_evento, 'Key': key_origem},
            Key=novo_nome
        )
        
        print(f"✅ Sucesso! Arquivo copiado como: {novo_nome}")
        return {
            'statusCode': 200,
            'body': f"Arquivo processado: {novo_nome}"
        }
        
    except Exception as e:
        print(f"❌ Erro ao processar o arquivo: {str(e)}")
        raise e