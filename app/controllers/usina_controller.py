"""
Camada de Apresentacao, UsinaController (APIRouter).
"""

from fastapi import APIRouter, status

from app.domain.usina import StatusUsina, Usina, UsinaCreate, UsinaUpdate
from app.services.usina_service import usina_service

router = APIRouter(prefix="/v1/usinas", tags=["Usinas"])


@router.get("", response_model=list[Usina])
def listar_usinas() -> list[Usina]:
    """Lista todas as usinas cadastradas."""
    return usina_service.listar()


# Exercicio 1: esta rota fica declarada ANTES de /{usina_id}.
# A rota "/status/{status}" tem dois segmentos e "/{usina_id}" tem um, entao
# nao ha conflito real, mas manter a rota mais especifica em cima e uma boa
# pratica: se um dia a rota virar "/{usina_id}/status", a ordem passa a importar.
# O tipo StatusUsina no parametro faz o FastAPI recusar qualquer valor fora de
# ativa, em_manutencao e inativa antes de chegar no Service.
@router.get("/status/{status}", response_model=list[Usina])
def listar_usinas_por_status(status: StatusUsina) -> list[Usina]:
    """Lista as usinas filtrando por status (ativa, em_manutencao, inativa)."""
    return usina_service.listar_por_status(status)


@router.get("/{usina_id}", response_model=Usina)
def buscar_usina(usina_id: int) -> Usina:
    """Retorna os dados de uma usina especifica."""
    return usina_service.buscar_por_id(usina_id)


@router.post("", response_model=Usina, status_code=status.HTTP_201_CREATED)
def criar_usina(dados: UsinaCreate) -> Usina:
    """Cria uma nova usina."""
    return usina_service.criar(dados)


@router.put("/{usina_id}", response_model=Usina)
def atualizar_usina(usina_id: int, dados: UsinaUpdate) -> Usina:
    """Atualiza os dados de uma usina existente."""
    return usina_service.atualizar(usina_id, dados)


@router.delete("/{usina_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_usina(usina_id: int) -> None:
    """Remove uma usina. So e permitido quando o status e 'inativa'."""
    usina_service.remover(usina_id)
