"""
Camada de Apresentacao, UsinaController (APIRouter).
Leitura e publica; criar, atualizar e remover exigem token JWT.
"""

from fastapi import APIRouter, Depends, status

from app.core.dependencies import obter_usuario_atual
from app.domain.usina import StatusUsina, Usina, UsinaCreate, UsinaUpdate
from app.domain.usuario import Usuario
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
def criar_usina(
    dados: UsinaCreate,
    usuario: Usuario = Depends(obter_usuario_atual),
) -> Usina:
    """Cria uma nova usina. Requer autenticacao."""
    return usina_service.criar(dados)


@router.put("/{usina_id}", response_model=Usina)
def atualizar_usina(
    usina_id: int,
    dados: UsinaUpdate,
    usuario: Usuario = Depends(obter_usuario_atual),
) -> Usina:
    """Atualiza os dados de uma usina existente. Requer autenticacao."""
    return usina_service.atualizar(usina_id, dados)


@router.delete("/{usina_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_usina(
    usina_id: int,
    usuario: Usuario = Depends(obter_usuario_atual),
) -> None:
    """Remove uma usina inativa. Requer autenticacao."""
    usina_service.remover(usina_id)