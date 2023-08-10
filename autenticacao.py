import requests

def autenticar_usuario(email, senha):
    url = "https://autenticador.secullum.com.br/Token"
    payload = {
        "grant_type": "password",
        "username": email,
        "password": senha,
        "client_id": "3"
    }

    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()  # Verifica se houve algum erro na resposta
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao realizar a autenticação: {e}")
        return None

# Exemplo de utilização:
email_usuario = "email do banco de ponto"
senha_usuario = "senha do banco ponto"

resultado_autenticacao = autenticar_usuario(email_usuario, senha_usuario)
if resultado_autenticacao:
    token_acesso = resultado_autenticacao.get("access_token")
    if token_acesso:
        print("Autenticação bem-sucedida!")
    else:
        print("Não foi possível obter o token de acesso.")
else:
    print("Erro ao realizar a autenticação.")
