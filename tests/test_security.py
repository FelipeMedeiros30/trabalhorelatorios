"""
Testes unitarios das funcoes de seguranca (hash e JWT).
"""
from datetime import timedelta

import jwt
import pytest

from app.core.security import (
    criar_token_acesso,
    decodificar_token,
    gerar_hash_senha,
    verificar_senha,
)


def test_hash_nao_guarda_a_senha_original():
    senha_hash = gerar_hash_senha("solar12345")
    assert senha_hash != "solar12345"
    assert senha_hash.startswith("$2")  # prefixo do bcrypt


def test_verificar_senha_correta_e_incorreta():
    senha_hash = gerar_hash_senha("solar12345")
    assert verificar_senha("solar12345", senha_hash) is True
    assert verificar_senha("senhaerrada", senha_hash) is False


def test_mesma_senha_gera_hashes_diferentes():
    # O salt aleatorio impede que duas senhas iguais tenham o mesmo hash.
    assert gerar_hash_senha("solar12345") != gerar_hash_senha("solar12345")


def test_token_carrega_o_email_do_usuario():
    token = criar_token_acesso("operacao@bulbe.com.br")
    assert decodificar_token(token) == "operacao@bulbe.com.br"


def test_token_expirado_e_rejeitado():
    token = criar_token_acesso("operacao@bulbe.com.br", expira_em=timedelta(seconds=-1))
    with pytest.raises(jwt.ExpiredSignatureError):
        decodificar_token(token)


def test_token_adulterado_e_rejeitado():
    token = criar_token_acesso("operacao@bulbe.com.br")
    token_adulterado = token[:-2] + ("AA" if not token.endswith("AA") else "BB")
    with pytest.raises(jwt.PyJWTError):
        decodificar_token(token_adulterado)