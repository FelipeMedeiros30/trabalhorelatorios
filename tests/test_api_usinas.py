"""
Testes da API pelo HTTP, usando o TestClient do FastAPI.
Verificam que as rotas de escrita estao protegidas pelo JWT.
"""


def test_listar_usinas_e_publico(client):
    resposta = client.get("/v1/usinas")
    assert resposta.status_code == 200
    assert resposta.json() == []


def test_criar_usina_sem_token_retorna_401(client, usina_valida):
    resposta = client.post("/v1/usinas", json=usina_valida)
    assert resposta.status_code == 401
    assert resposta.json()["error"]["code"] == "TOKEN_INVALIDO"


def test_criar_usina_com_token_retorna_201(client, headers_auth, usina_valida):
    resposta = client.post("/v1/usinas", json=usina_valida, headers=headers_auth)
    assert resposta.status_code == 201
    assert resposta.json()["id"] == 1


def test_token_falso_retorna_401(client, usina_valida):
    resposta = client.post(
        "/v1/usinas",
        json=usina_valida,
        headers={"Authorization": "Bearer token.falso.qualquer"},
    )
    assert resposta.status_code == 401


def test_remover_usina_com_token(client, headers_auth, usina_valida):
    # No meu projeto so usina inativa pode ser removida (exercicio 2 da Aula 09),
    # entao a usina do teste ja nasce com status "inativa".
    usina_inativa = {**usina_valida, "status": "inativa"}
    client.post("/v1/usinas", json=usina_inativa, headers=headers_auth)
    resposta = client.delete("/v1/usinas/1", headers=headers_auth)
    assert resposta.status_code == 204
    assert client.get("/v1/usinas/1").status_code == 404


def test_rota_me_devolve_o_usuario_logado(client, headers_auth):
    resposta = client.get("/v1/auth/me", headers=headers_auth)
    assert resposta.status_code == 200
    assert resposta.json()["email"] == "operacao@bulbe.com.br"