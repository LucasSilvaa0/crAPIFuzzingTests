# crAPI - Documentação Técnica

## Visão Geral do Projeto

crAPI é uma aplicação vulnerável por design criada para treinar desenvolvedores e profissionais de segurança em riscos críticos de APIs. O sistema simula um marketplace/oficina de carros com comunidade, autenticação, compras e um chatbot de IA integrado.

O repositório combina múltiplas tecnologias e microserviços:

- Frontend React + TypeScript (`services/web`)
- Serviço de identidade Java Spring Boot (`services/identity`)
- Serviço de comunidade Go (`services/community`)
- Serviço de oficina Python/Django (`services/workshop`)
- Chatbot IA Python/Quart (`services/chatbot`)
- Gateway de mock/vendor API Go (`services/gateway-service`)
- Mailhog para e-mails de teste
- Postgres e MongoDB para persistência
- ChromaDB para vetores/embeddings do chatbot

## Arquitetura do Sistema

### Padrão geral

O sistema usa uma arquitetura de microserviços com serviços alinhados por domínio:

- `web`: interface de usuário e ponte para APIs internas
- `identity`: autenticação, registro e gerenciamento de usuário
- `community`: blogs, posts e comentários
- `workshop`: cadastro de veículos, mecânicos, solicitações de serviço, relatórios e marketplace
- `chatbot`: assistente conversacional com integração a provedores LLM
- `gateway-service`: mock de API de terceiros para simular integração externa

O frontend faz chamadas diretas para serviços definidos por prefixos de URL no arquivo `services/web/src/config.ts`.

### Comunicação entre serviços

- O frontend consome serviços via HTTP usando nomes de serviço Docker Compose:
  - `identity/`
  - `workshop/`
  - `community/`
  - `chatbot/`
- O serviço `workshop` valida JWT chamando `/identity/api/auth/verify` no serviço de identidade.
- O serviço `community` também depende do serviço de identidade para autenticação via middleware JWT.
- O chatbot usa ChromaDB para persistência de embeddings e MongoDB para histórico de conversa.

## Serviços Principais

### 1. `services/web`

- SPA React com `redux`, `redux-saga` e `redux-persist`
- Usa `antd` para componentes UI
- Faz fetch em APIs REST com `Authorization: Bearer <token>`
- Possui roteamento interno via `react-router-dom`
- Usa `redux-saga` para fluxo de chamadas assíncronas
- Roda sob Nginx em `services/web/Dockerfile`

### 2. `services/identity`

- Java Spring Boot
- Expõe endpoints em `/identity/api/auth/*` e `/identity/api/v2/user/*`
- JWT é emitido neste serviço e verificado internamente
- Suporta:
  - login (`POST /identity/api/auth/login`)
  - signup (`POST /identity/api/auth/signup`)
  - verify token (`POST /identity/api/auth/verify`)
  - password recovery/OTP (`POST /identity/api/auth/forget-password`, `/api/auth/v3/check-otp`, `/api/auth/v2/check-otp`)
  - login com token por e-mail
  - desbloqueio de conta
  - dashboard de usuário e reset de senha via token
- Segurança notável:
  - `WebSecurityConfig` permite muitas rotas públicas, incluindo `/identity/api/v2/user/dashboard`
  - senha de teste e fluxo de OTP deliberadamente inseguro para fins de treinamento
  - `entrypoint.sh` carrega `jwks.json` customizado se presente

### 3. `services/community`

- Serviço Go com rotas REST para posts, comentários e cupons
- Usa Postgres e MongoDB para persistência
- Endpoints principais:
  - `GET /community/api/v2/community/posts/recent`
  - `GET /community/api/v2/community/posts/search`
  - `GET /community/api/v2/community/posts/{postID}`
  - `POST /community/api/v2/community/posts`
  - `POST /community/api/v2/community/posts/{postID}/comment`
  - `POST /community/api/v2/coupon/new-coupon`
  - `POST /community/api/v2/coupon/validate-coupon`
- Possui middleware de autenticação que verifica JWT via serviço de identidade e valida usuário em Postgres
- O serviço também oferece `/community/home` para health ou home check

### 4. `services/workshop`

- Django REST Framework + PostgreSQL + MongoDB via Djongo
- Configurações no `crapi_site/settings.py`
- Usa JWT e delega verificação de token para `identity/api/auth/verify`
- Principais domínios:
  - Usuário
  - Veículo
  - Mecânico
  - Requisições de serviço
  - Produtos e compras
- Endpoints pelo frontend:
  - `POST /identity/api/v2/vehicle/register_vehicle`
  - `POST /identity/api/v2/vehicle/add_vehicle`
  - `GET /identity/api/v2/vehicle/vehicles`
  - `POST /identity/api/v2/vehicle/resend_email`
  - `GET /identity/api/v2/user/dashboard`
  - `POST /identity/api/v2/user/reset-password`
  - `GET /api/mechanic`
  - `POST /api/merchant/contact_mechanic`
  - `GET /api/merchant/service_requests/<vin>`
  - `GET /api/mechanic/service_requests`
  - `GET /api/mechanic/service_request/<serviceId>`
  - `POST /api/mechanic/service_request/<serviceId>/comment`
  - `PUT /api/mechanic/service_request/<serviceId>`
  - `GET /api/shop/products`
  - `POST /api/shop/orders`
  - `GET /api/shop/orders/all`
  - `GET /api/shop/orders/<orderId>`
  - `POST /api/shop/orders/return_order`
  - `POST /api/shop/apply_coupon`

### 5. `services/chatbot`

- Python Quart + async API
- Usa `langgraph`, `langchain`, provedores LLM e embeddings
- Armazena histórico em MongoDB (`chat_sessions`)
- Usa ChromaDB para indexação vetorial e RAG
- Endpoints:
  - `POST /chatbot/genai/init`
  - `POST /chatbot/genai/model`
  - `POST /chatbot/genai/ask`
  - `GET /chatbot/genai/state`
  - `GET /chatbot/genai/history`
  - `POST /chatbot/genai/reset`
  - `GET /chatbot/genai/health`
- Suporta provedores:
  - `openai`, `anthropic`, `azure_openai`, `bedrock`, `vertex`, `groq`, `mistral`, `cohere`
- Configuração via variáveis de ambiente, incluindo chaves específicas e deploys
- Fluxo de inicialização especial para `openai` e `anthropic` onde a chave é enviada por request
- O agente IA usa ferramentas:
  - SQLDatabaseToolkit para Postgres
  - `get_retriever_tool` para pesquisa semântica de histórico de chat
  - MCP tools se disponível

### 6. `services/gateway-service`

- Serviço Go próprio mockando APIs externas
- Expõe:
  - `GET /v1/vin/ownership` com autenticação Basic Auth fixa (`vendorcrapi:Pa$$4Vendor_1`)
  - `POST /v1/payment` com autenticação Basic Auth fixa
- Gera respostas fictícias usando `faker`
- Destina-se a simular integração de terceiros com dados de veículo e pagamento

## Banco de Dados e Persistência

### Postgres

- Usado para dados principais de aplicação em `identity`, `community` e `workshop`
- Configurações em Docker Compose:
  - usuário: `admin`
  - senha: `crapisecretpassword`
  - banco: `crapi`
- Serviço `workshop` usa conexões persistentes e `CONN_MAX_AGE=600`

### MongoDB

- Usado por `mailhog` como storage e por `chatbot` para histórico de conversas
- Serviço `community` também inicializa dados no Mongo (via seed)
- Configurações em Docker Compose:
  - usuário: `admin`
  - senha: `crapisecretpassword`

### ChromaDB

- Usado pelo `chatbot` como vetor store para embeddings
- Configurações no Compose: `chromadb` service, porta `8000`

### Outras persistências

- Mailhog armazena e-mails em MongoDB
- O frontend não possui armazenamento server-side além de cookies/local storage de sessão

## Infraestrutura e Deploy

### Docker Compose

O principal fluxo de deploy local é via `deploy/docker/docker-compose.yml`.

Serviços orquestrados:

- `crapi-identity`
- `crapi-community`
- `crapi-workshop`
- `crapi-chatbot`
- `crapi-web`
- `postgresdb`
- `mongodb`
- `chromadb`
- `mailhog`
- `api.mypremiumdealership.com`

Portas expostas no compose padrão:

- `8888` -> frontend HTTP
- `8443` -> frontend HTTPS
- `8025` -> MailHog UI
- `5500` -> chatbot MCP server

### Build local

- `deploy/docker/build-all.sh` ou `build-all.bat`
- `docker compose -f docker-compose.yml --compatibility up -d`

### Helm / Kubernetes

Existe suporte a Helm em `deploy/helm` com valores para:

- `values.yaml`
- `values-pv.yaml`
- `values-safe.yaml`
- `values-tls.yaml`

### Vagrant

Opção de VM em `deploy/vagrant` com `Vagrantfile` e provisionamento.

## Configurações Importantes

### Variáveis de ambiente críticas

- `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`
- `MONGO_DB_HOST`, `MONGO_DB_PORT`, `MONGO_DB_USER`, `MONGO_DB_PASSWORD`, `MONGO_DB_NAME`
- `IDENTITY_SERVICE`, `WORKSHOP_SERVICE`, `COMMUNITY_SERVICE`, `CHATBOT_SERVICE`
- `TLS_ENABLED`, `TLS_CERTIFICATE`, `TLS_KEY`
- `CHATBOT_LLM_PROVIDER`, `CHATBOT_OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT`, `AWS_REGION`, `VERTEX_PROJECT`, `MISTRAL_API_KEY`, `COHERE_API_KEY`
- `API_GATEWAY_URL` para `workshop` e `identity`
- `JWT_SECRET` e `JWT_EXPIRATION` no `identity`

### Chaves / JWT

- `services/identity/entrypoint.sh` carrega `jwks.json` customizado se presente
- `crapi-chatbot` aceita chaves por sessão para OpenAI/Anthropic

## Padrões Técnicos

- Frontend: React + Redux + Saga + TypeScript
- Identity: Spring Boot + JWT + BCrypt
- Community: Go + Gorilla Mux + Gorm + Mongo/Postgres
- Workshop: Django REST + Djongo + PostgreSQL
- Chatbot: Quart + LangGraph + LangChain + ChromaDB
- Mock gateway: Go básico com TLS opcional

## Fluxo Principal de Uso

1. Usuário acessa `http://localhost:8888`
2. O frontend faz login via `POST /identity/api/auth/login`
3. Recebe JWT e usa em todas as requisições subsequentes
4. O usuário pode:
   - registrar veículos
   - buscar mecânicos
   - abrir ordens de serviço
   - ver relatórios e compras
   - publicar posts e comentários na comunidade
   - usar o chatbot IA
5. O serviço `workshop` valida JWT ligando para `identity/api/auth/verify`
6. O chatbot mantém histórico em Mongo e usa Chroma para embeddings

## Observabilidade e Manutenção

- Healthchecks presentes no Docker Compose para `identity`, `community`, `workshop`, `web`, `mailhog`, `chromadb`
- Logs são emitidos nos serviços e coletados localmente nos containers
- `services/workshop/crapi_site/settings.py` define logging para arquivo `debug.log`
- O frontend implementa um interceptor que detecta `401` e dispara `INVALID_SESSION`

## Vulnerabilidades e Decisões de Projeto

- O app é propositalmente inseguro para fins educacionais
- `identity` expõe endpoints de verificação/OTP com níveis diferentes de segurança
- `workshop` aceita JWT verificado externamente e confia em `identity` sem checar assinatura localmente
- `gateway-service` usa credenciais Basic Auth fixas e é destinado a simular terceiros
- `chatbot` pode operar com chaves sensíveis em tempo de execução

## Lacunas de Documentação Identificadas

- Falta descrição detalhada de entidades e modelos de dados
- Não há documentação de migrações ou versionamento de banco
- Não há fluxo de dados detalhado entre serviços além do Compose
- Não há orientações de CI/CD no repositório
- O `openapi-spec/crapi-openapi-spec.json` existe, mas não está referenciado como documentação de API interna

## Sugestões de Melhoria

- Adicionar diagrama de arquitetura de microserviços
- Documentar o contrato de API de cada serviço com exemplos de payload
- Especificar claramente quais dados residem em Postgres vs MongoDB
- Documentar estratégias de segurança deliberadamente inseguras e quais desafios elas representam
- Adicionar documentação de onboarding para desenvolvimento local de cada serviço

## Referências Úteis no Repositório

- `README.md`
- `docs/overview.md`
- `docs/setup.md`
- `deploy/docker/docker-compose.yml`
- `services/web/src/constants/APIConstant.ts`
- `services/identity/src/main/java/com/crapi/controller/AuthController.java`
- `services/chatbot/src/chatbot/chat_api.py`
- `services/chatbot/src/chatbot/langgraph_agent.py`
- `services/workshop/crapi_site/settings.py`
- `services/community/api/router/routes.go`
- `openapi-spec/crapi-openapi-spec.json`
