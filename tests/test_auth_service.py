"""
Testes unitarios do AuthService.
"""
import pytest

from app.domain.usuario import UsuarioCreate
from app.repositories.usuario_repository import UsuarioRepository
from app.services.auth_service import AuthService
from app.services.usina_service import ErroDeNegocio


@pytest.fixture
def auth() -> AuthService:
    return AuthService(UsuarioRepository())


@pytest.fixture
def novo_usuario() -> UsuarioCreate:
    return UsuarioCreate(nome="Operadora Bulbe", email="operacao@bulbe.com.br", senha="solar12345")


def test_registrar_nao_devolve_a_senha(auth, novo_usuario):
    usuario = auth.registrar(novo_usuario)
    assert usuario.email == "operacao@bulbe.com.br"
    assert not hasattr(usuario, "senha_hash")


def test_email_duplicado_levanta_409(auth, novo_usuario):
    auth.registrar(novo_usuario)
    with pytest.raises(ErroDeNegocio) as erro:
        auth.registrar(novo_usuario)
    assert erro.value.status == 409


def test_login_com_senha_errada_levanta_401(auth, novo_usuario):
    auth.registrar(novo_usuario)
    with pytest.raises(ErroDeNegocio) as erro:
        auth.autenticar("operacao@bulbe.com.br", "senhaerrada")
    assert erro.value.code == "CREDENCIAIS_INVALIDAS"


def test_login_correto_gera_token_valido(auth, novo_usuario):
    auth.registrar(novo_usuario)
    token = auth.autenticar("operacao@bulbe.com.br", "solar12345")
    usuario = auth.usuario_do_token(token.access_token)
    assert usuario.nome == "Operadora Bulbe"


def test_token_invalido_levanta_401(auth):
    with pytest.raises(ErroDeNegocio) as erro:
        auth.usuario_do_token("isto.nao.e.um.token")
    assert erro.value.code == "TOKEN_INVALIDO"