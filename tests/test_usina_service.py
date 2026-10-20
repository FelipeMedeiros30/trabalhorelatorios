"""
Testes unitarios do UsinaService.

Duas estrategias:
1. Repositorio em memoria NOVO para cada teste (isolamento simples).
2. Mock do repositorio, para testar o Service sem depender de nenhuma
   implementacao de persistencia.
"""
from unittest.mock import Mock

import pytest

from app.domain.usina import StatusUsina, UsinaCreate, UsinaUpdate
from app.repositories.usina_repository import UsinaRepository
from app.services.usina_service import ErroDeNegocio, UsinaService


@pytest.fixture
def service() -> UsinaService:
    return UsinaService(UsinaRepository())


@pytest.fixture
def dados_usina() -> UsinaCreate:
    return UsinaCreate(nome="Usina Solar Uberlandia", localizacao="Uberlandia, MG", capacidade_geracao_kwh=5000)


def test_criar_atribui_id_sequencial(service, dados_usina):
    primeira = service.criar(dados_usina)
    segunda = service.criar(dados_usina)
    assert primeira.id == 1
    assert segunda.id == 2


def test_buscar_usina_existente(service, dados_usina):
    criada = service.criar(dados_usina)
    encontrada = service.buscar_por_id(criada.id)
    assert encontrada.nome == "Usina Solar Uberlandia"


def test_buscar_usina_inexistente_levanta_erro_404(service):
    with pytest.raises(ErroDeNegocio) as erro:
        service.buscar_por_id(99)
    assert erro.value.code == "RECURSO_NAO_ENCONTRADO"
    assert erro.value.status == 404


def test_atualizar_altera_apenas_campos_enviados(service, dados_usina):
    criada = service.criar(dados_usina)
    atualizada = service.atualizar(criada.id, UsinaUpdate(status=StatusUsina.em_manutencao))
    assert atualizada.status == StatusUsina.em_manutencao
    assert atualizada.nome == criada.nome
    assert atualizada.capacidade_geracao_kwh == criada.capacidade_geracao_kwh


def test_remover_inexistente_levanta_erro(service):
    with pytest.raises(ErroDeNegocio):
        service.remover(42)


def test_service_com_mock_do_repositorio():
    repositorio_falso = Mock()
    repositorio_falso.buscar_por_id.return_value = None
    service = UsinaService(repositorio_falso)

    with pytest.raises(ErroDeNegocio):
        service.buscar_por_id(7)

    # Confere que o Service consultou o repositorio com o id certo.
    repositorio_falso.buscar_por_id.assert_called_once_with(7)