# Handson: CRUD de Usinas em FastAPI

Projeto Ciência de Dados II, Bulbe Energia.

CRUD completo da entidade **Usina** em FastAPI, com arquitetura em camadas
(Apresentação, Serviço, Domínio e Persistência) e os **4 exercícios propostos resolvidos**.

A "base de dados" é uma estrutura em memória. Quando o banco relacional entrar,
só a camada de Persistência (`usina_repository.py`) muda; o resto do código continua igual.

---

## Como rodar

Windows (PowerShell ou CMD), a partir da pasta `handson-crud-usinas`:

```bat
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Mac ou Linux:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

A API sobe em <http://localhost:8000>. O Swagger UI fica em <http://localhost:8000/docs>,
onde dá para testar todos os endpoints direto do navegador.

---

## Estrutura

```
handson-crud-usinas/
├── app/
│   ├── domain/usina.py                 # Domínio: entidade e schemas Pydantic
│   ├── repositories/usina_repository.py # Persistência: dicionário em memória
│   ├── services/usina_service.py       # Serviço: regras de negócio e ErroDeNegocio
│   ├── controllers/usina_controller.py # Apresentação: rotas HTTP
│   └── main.py                         # Ponto de entrada e handlers de erro
├── docs/
│   ├── sequencia_post_usinas.puml      # Exercício 4: diagrama de sequência
│   └── sequencia_post_usinas.png       # O mesmo diagrama já renderizado
├── requirements.txt
└── README.md
```

---

## Endpoints

| Método | Rota | Descrição |
| --- | --- | --- |
| GET | `/v1/usinas` | Lista todas as usinas cadastradas |
| GET | `/v1/usinas/status/{status}` | **(Exercício 1)** Lista as usinas de um status |
| GET | `/v1/usinas/{id}` | Retorna uma usina específica |
| POST | `/v1/usinas` | Cria uma nova usina |
| PUT | `/v1/usinas/{id}` | Atualiza uma usina existente |
| DELETE | `/v1/usinas/{id}` | **(Exercício 2)** Remove, só se o status for `inativa` |

Valores válidos de status: `ativa`, `em_manutencao`, `inativa`.

---

## Exercícios resolvidos

### Exercício 1, filtrar usinas por status

`GET /v1/usinas/status/{status}` atravessa as quatro camadas:

- **Controller** (`usina_controller.py`): rota declarada **antes** de `/{usina_id}` e com o
  parâmetro tipado como `StatusUsina`. Assim o próprio FastAPI recusa qualquer valor fora da
  enum, antes da requisição chegar ao Service.
- **Service** (`usina_service.py`): `listar_por_status()` apenas delega ao repositório, porque
  aqui não existe regra de negócio nenhuma a aplicar.
- **Repository** (`usina_repository.py`): `listar_por_status()` filtra a lista em memória.
  Quando o banco entrar, essa linha vira um `WHERE status = :status` e nada mais muda.

```bash
curl http://localhost:8000/v1/usinas/status/ativa
```

Status inválido devolve 422 já no formato padronizado:

```json
{
  "error": {
    "code": "ERRO_DE_VALIDACAO",
    "message": "A requisicao possui 1 campo invalido.",
    "status": 422,
    "details": [
      { "campo": "path.status", "mensagem": "Input should be 'ativa', 'em_manutencao' or 'inativa'", "tipo": "enum" }
    ]
  }
}
```

### Exercício 2, uma usina só pode ser removida se estiver inativa

A regra vive no **Service**, não no Controller nem no Repository, porque é uma decisão de
negócio: uma usina `ativa` ou `em_manutencao` ainda gera (ou volta a gerar) créditos para os
clientes, então não pode simplesmente sumir do sistema.

`UsinaService.remover()` primeiro busca a usina (404 se não existir) e depois checa o status:

```python
if usina.status != StatusUsina.inativa:
    raise ErroDeNegocio(
        code="REMOCAO_NAO_PERMITIDA",
        message=f"Usina com id {usina_id} esta com status '{usina.status.value}'. ...",
        status=409,
    )
```

```bash
curl -X DELETE http://localhost:8000/v1/usinas/1
```

```json
{
  "error": {
    "code": "REMOCAO_NAO_PERMITIDA",
    "message": "Usina com id 1 esta com status 'ativa'. Apenas usinas com status 'inativa' podem ser removidas.",
    "status": 409
  }
}
```

Para remover de verdade, primeiro inative a usina:

```bash
curl -X PUT http://localhost:8000/v1/usinas/1 -H "Content-Type: application/json" -d "{\"status\": \"inativa\"}"
curl -X DELETE http://localhost:8000/v1/usinas/1   # 204 No Content
```

### Exercício 3, padronizar também os erros de validação do Pydantic

Por padrão o FastAPI devolve os erros do Pydantic no formato dele
(`{"detail": [{"type": ..., "loc": ..., "msg": ...}]}`), diferente do
`error.code/message/status` usado no resto da API. Em `main.py`, um handler de
`RequestValidationError` reescreve essa resposta no formato padronizado, guardando em
`details` a lista de campos que falharam com o `loc` achatado (`body.capacidade_geracao_kwh`).

Existe também um handler de `StarletteHTTPException`, para que rota inexistente (404) e
método não permitido (405) saiam no mesmo formato. Resultado: a API tem **um único formato de
erro**, venha ele do negócio, da validação ou do framework.

```bash
curl -X POST http://localhost:8000/v1/usinas -H "Content-Type: application/json" ^
  -d "{\"nome\": \"AB\", \"localizacao\": \"Uberlandia, MG\", \"capacidade_geracao_kwh\": -5}"
```

```json
{
  "error": {
    "code": "ERRO_DE_VALIDACAO",
    "message": "A requisicao possui 2 campos invalidos.",
    "status": 422,
    "details": [
      { "campo": "body.nome", "mensagem": "String should have at least 3 characters", "tipo": "string_too_short" },
      { "campo": "body.capacidade_geracao_kwh", "mensagem": "Input should be greater than 0", "tipo": "greater_than" }
    ]
  }
}
```

### Exercício 4, diagrama de sequência do POST /v1/usinas

Em `docs/sequencia_post_usinas.puml` (fonte PlantUML) e `docs/sequencia_post_usinas.png`
(já renderizado). O diagrama mostra os dois caminhos da operação: o corpo inválido, que para
na validação do Pydantic e sai pelo handler do Exercício 3 com 422; e o corpo válido, que
percorre Controller → Service → Repository, cria a entidade de Domínio com `id` e
`data_ativacao`, e volta como 201 Created.

Para renderizar de novo, cole o conteúdo do `.puml` em <https://www.plantuml.com/plantuml>
ou use a extensão PlantUML do VS Code.

---

## Exemplo de criação de usina

```bash
curl -X POST http://localhost:8000/v1/usinas -H "Content-Type: application/json" ^
  -d "{\"nome\": \"Usina Solar Uberlandia\", \"localizacao\": \"Uberlandia, MG\", \"capacidade_geracao_kwh\": 1500.5}"
```

```json
{
  "nome": "Usina Solar Uberlandia",
  "localizacao": "Uberlandia, MG",
  "capacidade_geracao_kwh": 1500.5,
  "status": "ativa",
  "id": 1,
  "data_ativacao": "2026-09-01"
}
```

> Nas linhas `curl` acima, o `^` quebra linha no CMD do Windows. No PowerShell use `` ` `` e no
> Mac/Linux use `\`.

---

## Observações sobre as camadas

- **Controller**: só recebe a requisição e chama o `usina_service`. Não tem regra de negócio
  nem acessa dados diretamente.
- **Service**: decide o que é erro de negócio (usina não encontrada, remoção não permitida) e
  levanta `ErroDeNegocio` com `code`, `message` e `status`.
- **Domain**: define os formatos de entrada e saída com Pydantic, com validação automática
  (`min_length`, `gt=0`, enum de status).
- **Repository**: a única camada que sabe como os dados são guardados. Hoje é um dicionário em
  memória; na Aula 19 vira uma tabela no banco.

Como o armazenamento é em memória, os dados se perdem a cada reinício do servidor. Com
`--reload` ligado, salvar um arquivo também reinicia a aplicação e limpa as usinas cadastradas.
