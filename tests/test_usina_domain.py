"""
Testes unitarios da camada de Dominio: validacoes do Pydantic.
"""
import pytest
from pydantic import ValidationError

from app.domain.usina import StatusUsina, UsinaCreate


def test_usina_nasce_ativa_por_padrao():
    usina = UsinaCreate(nome="Usina Montes Claros", localizacao="Montes Claros, MG", capacidade_geracao_kwh=3200)
    assert usina.status == StatusUsina.ativa


def test_capacidade_zero_e_rejeitada():
    with pytest.raises(ValidationError):
        UsinaCreate(nome="Usina Zero", localizacao="Betim, MG", capacidade_geracao_kwh=0)


@pytest.mark.parametrize("nome_invalido", ["", "AB", "X" * 101])
def test_nome_fora_do_tamanho_e_rejeitado(nome_invalido):
    with pytest.raises(ValidationError):
        UsinaCreate(nome=nome_invalido, localizacao="Betim, MG", capacidade_geracao_kwh=100)