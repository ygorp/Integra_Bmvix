import requests
import time
from autenticacao import token_acesso
from database import conn
import smtplib
import threading
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Dados do e-mail
de_email = 'email Oringem'
para_email = 'email final'
senha = 'senha email'

# Exemplo de utilização (assumindo que você já tem o 'token_acesso' e o 'id_banco' da lista de bancos):
id_banco_selecionado = "id recebido pela autenticação"

# Função para fazer a requisição POST para o webservice
def fazer_requisicao_post_incluir_ponto(token_acesso, id_banco, dados_ponto):
    url = "https://pontowebintegracaoexterna.secullum.com.br/IntegracaoExterna/InclusaoPonto/Incluir"
    headers = {
        "Authorization": f"Bearer {token_acesso}",
        "secullumbancoselecionado": id_banco,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, headers=headers, json=dados_ponto)
        response.raise_for_status()  # Verifica se houve algum erro na resposta
        return response.json() if response.text.strip() else None
    
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição do webservice: {e}")
        
# Função para obter o último ID registrado na tabela
def get_last_id(conn):
    query = """
    SELECT
        MAX(id)
    FROM
        dbo.vw_acessos
    """
    cursor = conn.cursor()
    cursor.execute(query)
    last_id = cursor.fetchone()[0]
    cursor.close()
    return last_id

# Função para obter o n_pis da pessoa que registrou o último acesso
def get_access_data(conn, last_id):
    query = """
        SELECT 
            p.n_pis,
            p.nome
        FROM 
            dbo.vw_acessos a 
        INNER JOIN 
            dbo.pessoas p 
        ON 
            a.pessoa_n_identificador = p.n_identificador 
        WHERE 
            a.id = ? AND 
            p.n_identificador IS NOT NULL AND 
            a.negado = 0 AND
            p.n_pis IS NOT NULL AND
            p.classificacao_id = 6
    """
    cursor = conn.cursor()
    cursor.execute(query, last_id)
    access_data = cursor.fetchone()
    cursor.close()
    return access_data if access_data else None

# Obtém o último ID registrado inicialmente
last_id = get_last_id(conn)

# Loop infinito para verificar continuamente novos registros
while True:
    # Verifica o último ID registrado
    current_last_id = get_last_id(conn)
    
    # Se houver um novo ID registrado, imprime o n_pis da pessoa
    if current_last_id > last_id:
        last_id = current_last_id
        access_data = get_access_data(conn, last_id)
        if access_data:
            
            n_pis, nome = access_data
            
            dados_ponto = {
                "PIS": n_pis
            }
            dados_resposta = fazer_requisicao_post_incluir_ponto(token_acesso, id_banco_selecionado, dados_ponto)
        
            if dados_resposta is not None:
                print(dados_resposta)
            else:
                print(f"PIS = {n_pis} e Último id Acesso = {last_id}")
                def fazer_requisicao_get_pendencias(token_acesso, id_banco, pis):
                    url = f"https://pontowebintegracaoexterna.secullum.com.br/IntegracaoExterna/InclusaoPonto/Pendencias?pis={pis}"
                    headers = {
                        "Authorization": f"Bearer {token_acesso}",
                        "secullumbancoselecionado": id_banco
                    }

                    try:
                        response = requests.get(url, headers=headers)
                        response.raise_for_status()  # Verifica se houve algum erro na resposta
                        return response.json() if response.text.strip() else None
                    except requests.exceptions.RequestException as e:
                        print(f"Erro na requisição do webservice: {e}")

                dados_resposta = fazer_requisicao_get_pendencias(token_acesso, id_banco_selecionado, n_pis)
                                
                status = dados_resposta[0]['Status']
                motivo = dados_resposta[0]['MotivoRejeicao']
                
                if status == 2:
                    def enviar_email():
                        # Criando mensagem de e-mail
                        assunto = 'Erro de integração'
                        mensagem = f"Status: {status}\nMotivo: {motivo}\nPIS: {n_pis}\nFuncionário: {nome}"
                        
                        msg = MIMEMultipart()
                        msg['From'] = de_email
                        msg['To'] = para_email
                        msg['Subject'] = assunto
                        msg.attach(MIMEText(mensagem, 'plain'))
                        
                        # Conexão com o servidor SMTP do Gmail
                        server = smtplib.SMTP('smtp.outlook.com', 587)
                        server.starttls()

                        # Login na conta de e-mail
                        server.login(de_email, senha)

                        # Envio do e-mail
                        texto_email = msg.as_string()
                        server.sendmail(de_email, para_email, texto_email)

                        # Encerrando a conexão
                        server.quit()
                        
                    # Criando a thread para envio de e-mail
                    thread_envio = threading.Thread(target=enviar_email)

                    # Iniciando a thread
                    thread_envio.start()

    else:
        print(f"Nenhum novo registro encontrado")
            
    # Aguarda 1 segundo antes da próxima verificação
    time.sleep(1)