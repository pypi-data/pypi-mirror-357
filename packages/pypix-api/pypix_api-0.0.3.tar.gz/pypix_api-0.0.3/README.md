# pypix-api

Biblioteca em Python para comunicação com APIs bancárias, focada na integração com o PIX.

## Sumário

- [pypix-api](#pypix-api)
  - [Sumário](#sumário)
  - [Visão Geral](#visão-geral)
  - [Instalação](#instalação)
  - [Exemplo de Uso](#exemplo-de-uso)
  - [Estrutura do Projeto](#estrutura-do-projeto)
  - [Configuração](#configuração)
  - [Testes](#testes)
  - [Contribuição](#contribuição)
  - [Licença](#licença)

## Visão Geral

O `pypix-api` facilita a integração de sistemas Python com APIs bancárias brasileiras, com ênfase no ecossistema do PIX. A biblioteca abstrai autenticação, comunicação segura (MTLS/OAuth2), e operações comuns de bancos como Banco do Brasil e Sicoob.

## Instalação

Recomenda-se o uso de ambiente virtual.

```bash
pip install .
```

Ou, para desenvolvimento:

```bash
git clone https://github.com/seu-usuario/pypix-api.git
cd pypix-api
pip install -e .
```

## Exemplo de Uso

```python
from pypix_api.banks.bb import BancoDoBrasil

# Instanciação do banco (OAuth2 é inicializado internamente)
bb = BancoDoBrasil(
    client_id="SEU_CLIENT_ID",
    client_secret="SEU_CLIENT_SECRET",
    cert_path="caminho/do/certificado.pem",
    key_path="caminho/da/chave.key"
)

# Exemplo: Cobrança com Vencimento
payload = {
    "calendario": {
        "dataDeVencimento": "2025-12-31",
        "validadeAposVencimento": 30
    },
    "loc": {
        "id": 789
    },
    "devedor": {
        "logradouro": "Alameda Souza, Numero 80, Bairro Braz",
        "cidade": "Recife",
        "uf": "PE",
        "cep": "70011750",
        "cpf": "12345678909",
        "nome": "Francisco da Silva"
    },
    "valor": {
        "original": "123.45",
        "multa": {
        "modalidade": "2",
        "valorPerc": "15.00"
        },
        "juros": {
        "modalidade": "2",
        "valorPerc": "2.00"
        },
        "desconto": {
        "modalidade": "1",
        "descontoDataFixa": [
            {
            "data": "2025-11-30",
            "valorPerc": "30.00"
            }
        ]
        }
    },
    "chave": "5f84a4c5-c5cb-4599-9f13-7eb4d419dacc",
    "solicitacaoPagador": "Cobrança dos serviços prestados."
    }
cobv = bb.criar_cobv(txid="uuid-unico", body=payload)
print(cobv)
```

## Estrutura do Projeto

```
pypix_api/
├── auth/           # Autenticação (MTLS, OAuth2)
├── banks/          # Integrações com bancos (BB, Sicoob, métodos PIX)
├── models/         # Modelos de dados do PIX
├── utils/          # Utilitários (HTTP client, helpers)
tests/              # Testes automatizados
openapi.yaml        # Especificação OpenAPI (se aplicável)
pyproject.toml      # Configuração do projeto Python
Makefile            # Comandos úteis para desenvolvimento
.env.exemplo        # Exemplo de variáveis de ambiente
```

## Configuração

Crie um arquivo `.env` baseado em `.env.exemplo` com as credenciais e configurações necessárias para autenticação e acesso às APIs bancárias.

## Testes

Para rodar os testes automatizados:

```bash
make test
```
ou diretamente com pytest:
```bash
pytest
```

## Contribuição

Contribuições são bem-vindas! Siga os passos:

1. Fork este repositório
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas alterações (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## Licença

Este projeto está licenciado sob os termos da licença MIT.
