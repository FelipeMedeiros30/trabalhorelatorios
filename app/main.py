"""
Ponto de entrada da aplicacao.
"""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.controllers.auth_controller import router as auth_router
from app.controllers.usina_controller import router as usina_router
from app.services.usina_service import ErroDeNegocio

app = FastAPI(
    title="Bulbe Energia, API de Usinas",
    description="Handson de CRUD em FastAPI, arquitetura em camadas (Aula 09) + JWT e testes (Aula 10).",
    version="2.0.0",
)

app.include_router(auth_router)
app.include_router(usina_router)


def resposta_de_erro(code: str, message: str, status: int, details: list | None = None) -> JSONResponse:
    """
    Monta a resposta de erro no formato padronizado da Aula 10.
    Todo erro da API sai por aqui, seja de negocio ou de validacao.
    """
    corpo: dict = {
        "error": {
            "code": code,
            "message": message,
            "status": status,
        }
    }
    if details:
        corpo["error"]["details"] = details
    headers = {"WWW-Authenticate": "Bearer"} if status == 401 else None
    return JSONResponse(status_code=status, content=corpo, headers=headers)


@app.exception_handler(ErroDeNegocio)
def tratar_erro_de_negocio(request: Request, exc: ErroDeNegocio) -> JSONResponse:
    return resposta_de_erro(exc.code, exc.message, exc.status)


# Exercicio 3: por padrao o FastAPI devolve os erros do Pydantic em um formato
# proprio ({"detail": [{"type": ..., "loc": ..., "msg": ...}]}), diferente do
# formato error.code/message/status usado no resto da API. O handler abaixo
# intercepta o RequestValidationError e reescreve a resposta no nosso formato,
# mantendo em "details" a lista de campos que falharam.
@app.exception_handler(RequestValidationError)
def tratar_erro_de_validacao(request: Request, exc: RequestValidationError) -> JSONResponse:
    details = []
    for erro in exc.errors():
        # loc vem como ("body", "capacidade_geracao_kwh"); viramos "body.capacidade_geracao_kwh"
        campo = ".".join(str(parte) for parte in erro.get("loc", ()))
        details.append(
            {
                "campo": campo,
                "mensagem": erro.get("msg", ""),
                "tipo": erro.get("type", ""),
            }
        )

    quantidade = len(details)
    plural = "campo invalido" if quantidade == 1 else "campos invalidos"
    return resposta_de_erro(
        code="ERRO_DE_VALIDACAO",
        message=f"A requisicao possui {quantidade} {plural}.",
        status=422,
        details=details,
    )


# Padroniza tambem os erros levantados pelo proprio framework
# (rota inexistente, metodo nao permitido), para que a API nunca devolva
# dois formatos de erro diferentes.
@app.exception_handler(StarletteHTTPException)
def tratar_erro_http(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    codigos = {
        404: "RECURSO_NAO_ENCONTRADO",
        405: "METODO_NAO_PERMITIDO",
    }
    return resposta_de_erro(
        code=codigos.get(exc.status_code, "ERRO_HTTP"),
        message=str(exc.detail),
        status=exc.status_code,
    )


@app.get("/", tags=["Status"])
def raiz() -> dict:
    return {"mensagem": "API de Usinas no ar. Acesse /docs para o Swagger."}