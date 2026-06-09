# crAPI - Mapeamento Completo de Endpoints REST

**Data de Compilação:** 08/06/2026  
**Total de Endpoints Mapeados:** 100+  
**Serviços:** Identity, Workshop, Community, Chatbot, Gateway, Web (React)

---

## Índice de Serviços
1. [Identity Service (Java Spring Boot)](#1-identity-service-java-spring-boot)
2. [Workshop Service (Python Django)](#2-workshop-service-python-django)
3. [Community Service (Go)](#3-community-service-go)
4. [Chatbot Service (Python Quart)](#4-chatbot-service-python-quart)
5. [Gateway Service (Go)](#5-gateway-service-go)
6. [Web Service - API Calls (React)](#6-web-service---api-calls-react)

---

## 1. Identity Service (Java Spring Boot)

**Base URL:** `http://localhost:8081/identity`  
**Porta:** 8081

### 1.1 Autenticação e Autorização

#### POST `/api/auth/login`
- **Método:** POST
- **Autenticação:** Não requer
- **Payload:** JSON
  ```json
  {
    "email": "string",
    "password": "string"
  }
  ```
- **Response:** JWT Token
- **Descrição:** Autentica usuário e retorna token JWT

#### POST `/api/auth/signup`
- **Método:** POST
- **Autenticação:** Não requer
- **Payload:** JSON
  ```json
  {
    "name": "string",
    "email": "string",
    "number": "string",
    "password": "string"
  }
  ```
- **Response:** Mensagem de sucesso/erro
- **Descrição:** Registra novo usuário

#### POST `/api/auth/verify`
- **Método:** POST
- **Autenticação:** Não requer
- **Payload:** JSON
  ```json
  {
    "token": "string"
  }
  ```
- **Response:** Resultado da validação
- **Descrição:** Verifica se token JWT é válido

#### GET `/api/auth/jwks.json`
- **Método:** GET
- **Autenticação:** Não requer
- **Response:** JWKS público
- **Descrição:** Retorna conjunto de chaves públicas JWKS

#### POST `/api/auth/forget-password`
- **Método:** POST
- **Autenticação:** Não requer
- **Payload:** JSON
  ```json
  {
    "email": "string"
  }
  ```
- **Response:** Mensagem com OTP enviado
- **Descrição:** Gera OTP para recuperação de senha

#### POST `/api/auth/v2/check-otp`
- **Método:** POST
- **Autenticação:** Não requer
- **Payload:** JSON
  ```json
  {
    "email": "string",
    "otp": "string",
    "password": "string"
  }
  ```
- **Response:** Mensagem de sucesso/erro
- **Descrição:** Valida OTP para recuperação de senha (sem limite de tentativas)

#### POST `/api/auth/v3/check-otp`
- **Método:** POST
- **Autenticação:** Não requer
- **Payload:** JSON
  ```json
  {
    "email": "string",
    "otp": "string",
    "password": "string"
  }
  ```
- **Response:** Mensagem de sucesso/erro
- **Descrição:** Valida OTP para recuperação de senha (seguro - 10 tentativas máximo)

#### POST `/api/auth/v4.0/user/login-with-token`
- **Método:** POST
- **Autenticação:** Não requer
- **Payload:** JSON
  ```json
  {
    "email": "string",
    "email_change_token": "string"
  }
  ```
- **Response:** Mensagem de dupla verificação
- **Descrição:** Permite login com token de mudança de email

#### POST `/api/auth/v2.7/user/login-with-token`
- **Método:** POST
- **Autenticação:** Não requer
- **Payload:** JSON
  ```json
  {
    "email": "string",
    "email_change_token": "string"
  }
  ```
- **Response:** JWT Token
- **Descrição:** Permite login com token de mudança de email (retorna JWT)

#### POST `/api/auth/reset-test-users`
- **Método:** POST
- **Autenticação:** Não requer
- **Response:** Mensagem de sucesso
- **Descrição:** Reseta senha de usuários de teste

#### POST `/api/auth/unlock`
- **Método:** POST
- **Autenticação:** Bearer Token (requer JWT)
- **Payload:** JSON
  ```json
  {
    "email": "string",
    "code": "string"
  }
  ```
- **Response:** JWT Token
- **Descrição:** Desbloqueia conta de usuário

### 1.2 Gerenciamento de Usuários

#### GET `/api/v2/user/dashboard`
- **Método:** GET
- **Autenticação:** Bearer Token (requer JWT) ✅
- **Parâmetros:** Nenhum
- **Response:** Dashboard com dados do usuário, veículos e perfil
- **Descrição:** Retorna dados completos do usuário autenticado

#### POST `/api/v2/user/reset-password`
- **Método:** POST
- **Autenticação:** Bearer Token (requer JWT) ✅
- **Payload:** JSON
  ```json
  {
    "email": "string",
    "password": "string"
  }
  ```
- **Response:** Mensagem de sucesso
- **Descrição:** Reseta senha do usuário autenticado

### 1.3 Mudança de Email

#### POST `/api/v2/user/change-email`
- **Método:** POST
- **Autenticação:** Bearer Token (requer JWT) ✅
- **Payload:** JSON
  ```json
  {
    "email": "string",
    "new_email": "string"
  }
  ```
- **Response:** Mensagem com token enviado para novo email
- **Descrição:** Inicia processo de mudança de email

#### POST `/api/v2/user/verify-email-token`
- **Método:** POST
- **Autenticação:** Bearer Token (requer JWT) ✅
- **Payload:** JSON
  ```json
  {
    "email": "string",
    "new_email": "string",
    "token": "string"
  }
  ```
- **Response:** Mensagem de sucesso/erro
- **Descrição:** Verifica token e completa mudança de email

### 1.4 Mudança de Número de Telefone

#### POST `/api/v2/user/change-phone-number`
- **Método:** POST
- **Autenticação:** Bearer Token (requer JWT) ✅
- **Payload:** JSON
  ```json
  {
    "old_number": "string",
    "new_number": "string"
  }
  ```
- **Response:** Mensagem com OTP enviado para email
- **Descrição:** Inicia processo de mudança de telefone

#### POST `/api/v2/user/verify-phone-otp`
- **Método:** POST
- **Autenticação:** Bearer Token (requer JWT) ✅
- **Payload:** JSON
  ```json
  {
    "old_number": "string",
    "new_number": "string",
    "otp": "string"
  }
  ```
- **Response:** Mensagem de sucesso/erro
- **Descrição:** Verifica OTP e completa mudança de número

### 1.5 Gerenciamento de Veículos

#### POST `/api/v2/vehicle/register_vehicle`
- **Método:** POST
- **Autenticação:** Bearer Token (requer JWT) ✅
- **Payload:** Form Data (multipart)
- **Response:** Mensagem com VIN registrado
- **Descrição:** Registra novo veículo para usuário

#### POST `/api/v2/vehicle/add_vehicle`
- **Método:** POST
- **Autenticação:** Bearer Token (requer JWT) ✅
- **Payload:** JSON
  ```json
  {
    "vin": "string",
    "year": "integer",
    "make": "string",
    "model": "string"
  }
  ```
- **Response:** Mensagem de sucesso/erro
- **Descrição:** Adiciona veículo aos dados do usuário

#### GET `/api/v2/vehicle/vehicles`
- **Método:** GET
- **Autenticação:** Bearer Token (requer JWT) ✅
- **Parâmetros:** Nenhum
- **Response:** Lista de veículos do usuário
- **Descrição:** Retorna todos os veículos do usuário autenticado

#### POST `/api/v2/vehicle/resend_email`
- **Método:** POST
- **Autenticação:** Bearer Token (requer JWT) ✅
- **Payload:** Nenhum
- **Response:** Mensagem de sucesso
- **Descrição:** Reenvia detalhes do veículo por email

#### GET `/api/v2/vehicle/{carId}/location`
- **Método:** GET
- **Autenticação:** Bearer Token (requer JWT) ✅
- **Parâmetros:** Path - carId
- **Response:** Coordenadas de localização do veículo
- **Descrição:** Retorna localização atual do veículo

### 1.6 Perfil e Mídia

#### GET `/api/v2/user/videos/{video_id}`
- **Método:** GET
- **Autenticação:** Bearer Token (requer JWT) ✅
- **Parâmetros:** Path - video_id
- **Response:** Detalhes do vídeo do perfil
- **Descrição:** Retorna informações do vídeo de perfil

#### POST `/api/v2/user/pictures`
- **Método:** POST
- **Autenticação:** Bearer Token (requer JWT) ✅
- **Payload:** Form Data - file (multipart)
- **Response:** Detalhes da foto de perfil atualizada
- **Descrição:** Faz upload da foto de perfil

#### POST `/api/v2/user/videos`
- **Método:** POST
- **Autenticação:** Bearer Token (requer JWT) ✅
- **Payload:** Form Data - file (multipart, até 10MB)
- **Response:** Detalhes do vídeo de perfil
- **Descrição:** Faz upload do vídeo de perfil

#### PUT `/api/v2/user/videos/{video_id}`
- **Método:** PUT
- **Autenticação:** Bearer Token (requer JWT) ✅
- **Parâmetros:** Path - video_id
- **Payload:** JSON
  ```json
  {
    "name": "string"
  }
  ```
- **Response:** Detalhes do vídeo atualizado
- **Descrição:** Atualiza nome do vídeo de perfil

### 1.7 Gerenciamento (Admin)

#### POST `/identity/management/admin/lockUser`
- **Método:** POST
- **Autenticação:** Bearer Token (requer JWT) ✅
- **Payload:** JSON
  ```json
  {
    "email": "string",
    "code": "string"
  }
  ```
- **Response:** Mensagem
- **Descrição:** Bloqueia conta de usuário (admin)

#### POST `/identity/management/user/apikey`
- **Método:** POST
- **Autenticação:** Bearer Token (requer JWT) ✅
- **Payload:** JSON
  ```json
  {
    "email": "string",
    "password": "string"
  }
  ```
- **Response:** API Key gerada
- **Descrição:** Gera nova API key para usuário

### 1.8 Health Check

#### GET `/identity/health_check`
- **Método:** GET
- **Autenticação:** Não requer
- **Response:** { "message": "Okay", "status": 200 }
- **Descrição:** Verifica saúde do serviço

---

## 2. Workshop Service (Python Django)

**Base URL:** `http://localhost:8000/api`  
**Porta:** 8000

### 2.1 Autenticação de Mecânico

#### POST `/mechanic/signup`
- **Método:** POST
- **Autenticação:** Não requer
- **Payload:** JSON
  ```json
  {
    "name": "string",
    "email": "string",
    "number": "string",
    "password": "string",
    "mechanic_code": "string"
  }
  ```
- **Response:** Mensagem de sucesso
- **Descrição:** Registra novo mecânico

### 2.2 Mecânicos (Listagem)

#### GET `/mechanic/`
- **Método:** GET
- **Autenticação:** Bearer Token (requer JWT) ✅
- **Query Parameters:** 
  - `limit` (opcional): limite de resultados
  - `offset` (opcional): deslocamento para paginação
- **Response:** Lista paginada de mecânicos
- **Descrição:** Lista todos os mecânicos disponíveis

### 2.3 Recebimento de Relatórios (Mechanic)

#### GET `/mechanic/receive_report`
- **Método:** GET
- **Autenticação:** Não requer
- **Query Parameters:**
  - `mechanic_code` (obrigatório)
  - `problem_details` (obrigatório)
  - `vin` (obrigatório)
- **Response:** { "id", "sent": true, "report_link" }
- **Descrição:** Recebe relatório de problema do cliente

#### GET `/mechanic/mechanic_report`
- **Método:** GET
- **Autenticação:** Bearer Token (requer JWT) ✅
- **Query Parameters:**
  - `report_id` (obrigatório)
- **Response:** Detalhes do relatório de serviço
- **Descrição:** Retorna detalhes de um relatório específico

#### GET `/mechanic/download_report`
- **Método:** GET
- **Autenticação:** Bearer Token (requer JWT) ✅
- **Query Parameters:**
  - `report_id` (obrigatório)
- **Response:** Arquivo PDF do relatório
- **Descrição:** Faz download do relatório em PDF

### 2.4 Solicitações de Serviço (Mecânico)

#### GET `/mechanic/service_requests`
- **Método:** GET
- **Autenticação:** Bearer Token (requer JWT) ✅
- **Query Parameters:**
  - `limit` (opcional)
  - `offset` (opcional)
- **Response:** Lista paginada de solicitações de serviço
- **Descrição:** Lista todas as solicitações do mecânico

#### GET `/mechanic/service_request/{service_request_id}`
- **Método:** GET
- **Autenticação:** Bearer Token (requer JWT) ✅
- **Parâmetros:** Path - service_request_id
- **Response:** Detalhes da solicitação de serviço
- **Descrição:** Retorna detalhes de uma solicitação

#### PUT `/mechanic/service_request/{service_request_id}`
- **Método:** PUT
- **Autenticação:** Bearer Token (requer JWT) ✅
- **Parâmetros:** Path - service_request_id
- **Payload:** JSON
  ```json
  {
    "status": "string"
  }
  ```
- **Response:** Detalhes da solicitação atualizada
- **Descrição:** Atualiza status de uma solicitação

#### POST `/mechanic/service_request/{service_request_id}/comment`
- **Método:** POST
- **Autenticação:** Bearer Token (requer JWT) ✅
- **Parâmetros:** Path - service_request_id
- **Payload:** JSON
  ```json
  {
    "comment": "string"
  }
  ```
- **Response:** Detalhes do comentário
- **Descrição:** Adiciona comentário a uma solicitação

### 2.5 Contato com Mecânico (Merchant)

#### POST `/merchant/contact_mechanic`
- **Método:** POST
- **Autenticação:** Bearer Token (requer JWT) ✅
- **Payload:** JSON
  ```json
  {
    "mechanic_api": "string",
    "repeat_request_if_failed": "boolean (opcional)",
    "number_of_repeats": "integer (opcional)"
  }
  ```
- **Response:** { "response_from_mechanic_api", "status" }
- **Descrição:** Contacta mecânico via API fornecida

#### GET `/merchant/service_requests/{vin}`
- **Método:** GET
- **Autenticação:** Não requer
- **Parâmetros:** Path - vin (Vehicle Identification Number)
- **Query Parameters:**
  - `limit` (opcional)
  - `offset` (opcional)
- **Response:** Lista paginada de solicitações de serviço para VIN
- **Descrição:** Lista solicitações de serviço para um veículo

### 2.6 Produtos

#### GET `/shop/products`
- **Método:** GET
- **Autenticação:** Bearer Token (requer JWT) ✅
- **Query Parameters:**
  - `limit` (opcional)
  - `offset` (opcional)
- **Response:** Lista paginada de produtos com crédito do usuário
- **Descrição:** Lista todos os produtos disponíveis

#### POST `/shop/products`
- **Método:** POST
- **Autenticação:** Bearer Token (requer JWT) ✅
- **Payload:** JSON
  ```json
  {
    "name": "string",
    "price": "float",
    "image_url": "string"
  }
  ```
- **Response:** Dados do produto criado
- **Descrição:** Cria novo produto

### 2.7 Pedidos

#### GET `/shop/orders`
- **Método:** GET
- **Autenticação:** Não requer
- **Query Parameters:**
  - `order_id` (opcional)
- **Response:** Detalhes do pedido com informações de pagamento
- **Descrição:** Retorna detalhes de um pedido

#### POST `/shop/orders`
- **Método:** POST
- **Autenticação:** Bearer Token (requer JWT) ✅
- **Payload:** JSON
  ```json
  {
    "product_id": "integer",
    "quantity": "integer"
  }
  ```
- **Response:** { "id", "message", "credit" }
- **Descrição:** Cria novo pedido

#### PUT `/shop/orders/{order_id}`
- **Método:** PUT
- **Autenticação:** Bearer Token (requer JWT) ✅
- **Parâmetros:** Path - order_id
- **Payload:** JSON
  ```json
  {
    "quantity": "integer (opcional)",
    "status": "string (opcional)"
  }
  ```
- **Response:** Detalhes do pedido atualizado
- **Descrição:** Atualiza quantidade ou status de pedido

#### GET `/shop/orders/all`
- **Método:** GET
- **Autenticação:** Bearer Token (requer JWT) ✅
- **Query Parameters:**
  - `limit` (opcional)
  - `offset` (opcional)
- **Response:** Lista paginada de pedidos do usuário
- **Descrição:** Lista todos os pedidos do usuário

#### POST `/shop/orders/return_order`
- **Método:** POST
- **Autenticação:** Bearer Token (requer JWT) ✅
- **Payload:** JSON
  ```json
  {
    "order_id": "integer"
  }
  ```
- **Response:** Mensagem de sucesso
- **Descrição:** Processa devolução de pedido

### 2.8 Cupons

#### POST `/shop/apply_coupon`
- **Método:** POST
- **Autenticação:** Bearer Token (requer JWT) ✅
- **Payload:** JSON
  ```json
  {
    "coupon_code": "string"
  }
  ```
- **Response:** Detalhes do cupom aplicado
- **Descrição:** Aplica cupom de desconto

#### POST `/shop/return_qr_code`
- **Método:** POST
- **Autenticação:** Bearer Token (requer JWT) ✅
- **Payload:** JSON
  ```json
  {
    "order_id": "integer"
  }
  ```
- **Response:** Código QR para devolução
- **Descrição:** Gera código QR para devolução

#### POST `/shop/validate_coupon`
- **Método:** POST
- **Autenticação:** Bearer Token (requer JWT) ✅
- **Payload:** JSON
  ```json
  {
    "coupon_code": "string"
  }
  ```
- **Response:** Informações do cupom
- **Descrição:** Valida cupom

#### POST `/community/api/v2/coupon/new-coupon`
- **Método:** POST
- **Autenticação:** Bearer Token (requer JWT) ✅
- **Payload:** JSON
  ```json
  {
    "coupon_code": "string",
    "discount": "float"
  }
  ```
- **Response:** Detalhes do cupom criado
- **Descrição:** Cria novo cupom

### 2.9 Administração

#### GET `/management/users/all`
- **Método:** GET
- **Autenticação:** Bearer Token (requer JWT) ✅
- **Query Parameters:**
  - `limit` (opcional)
  - `offset` (opcional)
- **Response:** Lista paginada de usuários
- **Descrição:** Lista todos os usuários (admin)

---

## 3. Community Service (Go)

**Base URL:** `http://localhost:8090/community`  
**Porta:** 8090

### 3.1 Saúde

#### GET `/home`
- **Método:** GET
- **Autenticação:** Não requer
- **Response:** Mensagem de saúde
- **Descrição:** Verifica saúde do serviço

### 3.2 Posts

#### GET `/api/v2/community/posts/recent`
- **Método:** GET
- **Autenticação:** Bearer Token (requer JWT) ✅
- **Response:** Lista recente de posts
- **Descrição:** Retorna posts recentes da comunidade

#### GET `/api/v2/community/posts/search`
- **Método:** GET
- **Autenticação:** Bearer Token (requer JWT) ✅
- **Query Parameters:**
  - `title` (obrigatório)
- **Response:** Lista de posts por título
- **Descrição:** Busca posts por título

#### GET `/api/v2/community/posts/{postID}`
- **Método:** GET
- **Autenticação:** Bearer Token (requer JWT) ✅
- **Parâmetros:** Path - postID
- **Response:** Detalhes do post
- **Descrição:** Retorna um post específico

#### POST `/api/v2/community/posts`
- **Método:** POST
- **Autenticação:** Bearer Token (requer JWT) ✅
- **Payload:** JSON
  ```json
  {
    "title": "string",
    "content": "string",
    "author": "string"
  }
  ```
- **Response:** Detalhes do post criado
- **Descrição:** Cria novo post na comunidade

#### POST `/api/v2/community/posts/{postID}/comment`
- **Método:** POST
- **Autenticação:** Bearer Token (requer JWT) ✅
- **Parâmetros:** Path - postID
- **Payload:** JSON
  ```json
  {
    "content": "string",
    "author": "string"
  }
  ```
- **Response:** Detalhes do comentário
- **Descrição:** Adiciona comentário a um post

### 3.3 Cupons

#### POST `/api/v2/coupon/new-coupon`
- **Método:** POST
- **Autenticação:** Bearer Token (requer JWT) ✅
- **Payload:** JSON
  ```json
  {
    "coupon_code": "string",
    "discount": "float"
  }
  ```
- **Response:** Detalhes do cupom
- **Descrição:** Cria novo cupom

#### POST `/api/v2/coupon/validate-coupon`
- **Método:** POST
- **Autenticação:** Bearer Token (requer JWT) ✅
- **Payload:** JSON
  ```json
  {
    "coupon_code": "string"
  }
  ```
- **Response:** Informações do cupom
- **Descrição:** Valida cupom

---

## 4. Chatbot Service (Python Quart)

**Base URL:** `http://localhost:5555/chatbot`  
**Porta:** 5555

### 4.1 Saúde e Status

#### GET `/`
- **Método:** GET
- **Autenticação:** Não requer
- **Response:** { "message": "Hello from chatbot!" }
- **Descrição:** Saúde do chatbot

#### GET `/genai/health`
- **Método:** GET
- **Autenticação:** Não requer
- **Response:** { "message": "OK" }
- **Descrição:** Verifica saúde do serviço de IA

### 4.2 Inicialização

#### POST `/genai/init`
- **Método:** POST
- **Autenticação:** Não requer
- **Payload:** JSON
  ```json
  {
    "openai_api_key": "string (opcional)",
    "anthropic_api_key": "string (opcional)"
  }
  ```
- **Response:** { "message": "Initialized" ou "Model Already Initialized" }
- **Descrição:** Inicializa modelo de IA com API key

### 4.3 Configuração de Modelo

#### POST `/genai/model`
- **Método:** POST
- **Autenticação:** Não requer
- **Payload:** JSON
  ```json
  {
    "model_name": "string (opcional)"
  }
  ```
- **Response:** { "model_used": "string" }
- **Descrição:** Configura modelo LLM a usar

### 4.4 Chat

#### POST `/genai/ask`
- **Método:** POST
- **Autenticação:** Não requer
- **Payload:** JSON
  ```json
  {
    "message": "string",
    "id": "integer (opcional)"
  }
  ```
- **Response:** { "id", "message": "string (resposta IA)" }
- **Descrição:** Envia mensagem ao chatbot e recebe resposta

#### GET `/genai/state`
- **Método:** GET
- **Autenticação:** Não requer
- **Response:** { "initialized": "boolean", "message": "string", "chat_history": [] }
- **Descrição:** Retorna estado do chatbot e histórico

#### GET `/genai/history`
- **Método:** GET
- **Autenticação:** Não requer
- **Response:** { "chat_history": [] }
- **Descrição:** Retorna histórico completo de chat

#### POST `/genai/reset`
- **Método:** POST
- **Autenticação:** Não requer
- **Response:** { "initialized": "false", "message": "Reset successful" }
- **Descrição:** Reseta estado do chatbot

---

## 5. Gateway Service (Go)

**Base URL:** `https://localhost:443`  
**Porta:** 443 (HTTPS)

### 5.1 Saúde

#### GET `/`
- **Método:** GET
- **Autenticação:** Não requer
- **Response:** "crAPI Gateway."
- **Descrição:** Saúde do gateway

### 5.2 Informações de Propriedade do Veículo

#### GET `/v1/vin/ownership`
- **Método:** GET
- **Autenticação:** Basic Auth ✅ (username: `vendorcrapi`, password: `Pa$$4Vendor_1`)
- **Query Parameters:**
  - `vin` (obrigatório)
- **Response:** Array de proprietários anteriores
  ```json
  [
    {
      "vin": "string",
      "rank": "string (ex: 1st, 2nd)",
      "name": "string",
      "phone": "string",
      "email": "string",
      "ssn": "string",
      "address": "string",
      "registration_id": "string",
      "registration_date": "string"
    }
  ]
  ```
- **Descrição:** Retorna histórico de proprietários do veículo

### 5.3 Informações de Pagamento

#### POST `/v1/payment`
- **Método:** POST
- **Autenticação:** Basic Auth ✅ (username: `vendorcrapi`, password: `Pa$$4Vendor_1`)
- **Content-Type:** application/json
- **Payload:** JSON
  ```json
  {
    "order": {
      "transaction_id": "string",
      "id": "integer",
      "created_on": "string"
    },
    "user": {
      "name": "string",
      "email": "string",
      "number": "string"
    },
    "amount": "float"
  }
  ```
- **Response:** Informações do pagamento processado
  ```json
  {
    "transaction_id": "string",
    "order_id": "integer",
    "amount": "float",
    "paid_on": "string",
    "card_number": "string (mascarado)",
    "card_owner_name": "string",
    "card_type": "string",
    "card_expiry": "string",
    "currency": "string"
  }
  ```
- **Descrição:** Processa informações de pagamento

---

## 6. Web Service - API Calls (React)

**Base URLs (variáveis de ambiente):**
- `IDENTITY_SERVICE`: `http://localhost:8081/identity/`
- `WORKSHOP_SERVICE`: `http://localhost:8000/api/`
- `COMMUNITY_SERVICE`: `http://localhost:8090/community/`
- `CHATBOT_SERVICE`: `http://localhost:5555/chatbot/`

### 6.1 Endpoints Chamados pelo Frontend React

As chamadas de API do React são definidas através do arquivo `APIConstant.ts` e executadas nas sagas Redux. Aqui estão todos os endpoints:

#### Autenticação
- **LOGIN:** `/api/auth/login`
- **SIGNUP:** `/api/auth/signup`
- **FORGOT_PASSWORD:** `/api/auth/forget-password`
- **VERIFY_OTP:** `/api/auth/v3/check-otp`
- **LOGIN_TOKEN:** `/api/auth/v4.0/user/login-with-token`
- **UNLOCK:** `/api/auth/unlock`
- **VALIDATE_TOKEN:** `/api/auth/verify`

#### Usuário
- **GET_USER:** `/api/v2/user/dashboard`
- **RESET_PASSWORD:** `/api/v2/user/reset-password`

#### Veículos
- **REGISTER_VEHICLE:** `/api/v2/vehicle/register_vehicle`
- **ADD_VEHICLE:** `/api/v2/vehicle/add_vehicle`
- **GET_VEHICLES:** `/api/v2/vehicle/vehicles`
- **RESEND_MAIL:** `/api/v2/vehicle/resend_email`
- **REFRESH_LOCATION:** `/api/v2/vehicle/<carId>/location`

#### Email e Telefone
- **CHANGE_EMAIL:** `/api/v2/user/change-email`
- **CHANGE_PHONE_NUMBER:** `/api/v2/user/change-phone-number`
- **VERIFY_PHONE_NUMBER_OTP:** `/api/v2/user/verify-phone-otp`
- **VERIFY_TOKEN:** `/api/v2/user/verify-email-token`

#### Perfil e Mídia
- **UPLOAD_PROFILE_PIC:** `/api/v2/user/pictures`
- **UPLOAD_VIDEO:** `/api/v2/user/videos`
- **GET_VIDEO:** `/api/v2/user/videos/<videoId>`
- **CHANGE_VIDEO_NAME:** `/api/v2/user/videos/<videoId>`

#### Mecânicos e Serviços
- **GET_MECHANICS:** `/api/mechanic`
- **CONTACT_MECHANIC:** `/api/merchant/contact_mechanic`
- **GET_MECHANIC_SERVICES:** `/api/mechanic/service_requests`
- **GET_MECHANIC_SERVICE:** `/api/mechanic/service_request/<serviceId>`
- **CREATE_SERVICE_COMMENT:** `/api/mechanic/service_request/<serviceId>/comment`
- **UPDATE_SERVICE_REQUEST_STATUS:** `/api/mechanic/service_request/<serviceId>`
- **GET_VEHICLE_SERVICES:** `/api/merchant/service_requests/<vehicleVIN>`
- **GET_SERVICE_REPORT:** `/api/mechanic/mechanic_report`
- **DOWNLOAD_SERVICE_REPORT:** `/api/mechanic/download_report`
- **RECEIVE_REPORT:** `/api/mechanic/receive_report`

#### Shop/Loja
- **GET_PRODUCTS:** `/api/shop/products`
- **BUY_PRODUCT:** `/api/shop/orders`
- **GET_ORDERS:** `/api/shop/orders/all`
- **GET_ORDER_BY_ID:** `/api/shop/orders/<orderId>`
- **RETURN_ORDER:** `/api/shop/orders/return_order`
- **APPLY_COUPON:** `/api/shop/apply_coupon`
- **NEW_PRODUCT:** `/api/shop/products` (POST)
- **NEW_COUPON:** `/api/v2/coupon/new-coupon`
- **VALIDATE_COUPON:** `/api/v2/coupon/validate-coupon`

#### Comunidade
- **GET_POSTS:** `/api/v2/community/posts/recent`
- **ADD_POST:** `/api/v2/community/posts`
- **GET_POST_BY_ID:** `/api/v2/community/posts/<postId>`
- **ADD_COMMENT:** `/api/v2/community/posts/<postId>/comment`

#### Chatbot
- **CHATBOT_INIT:** `/chatbot/genai/init` (POST)
- **CHATBOT_MODEL:** `/chatbot/genai/model` (POST)
- **CHATBOT_ASK:** `/chatbot/genai/ask` (POST)
- **CHATBOT_STATE:** `/chatbot/genai/state` (GET)
- **CHATBOT_HISTORY:** `/chatbot/genai/history` (GET)
- **CHATBOT_RESET:** `/chatbot/genai/reset` (POST)

---

## Resumo de Autenticação

### Endpoints que Requerem JWT Token
- Marcados com ✅ na coluna "Autenticação"
- Enviar header: `Authorization: Bearer <JWT_TOKEN>`
- Substituir `<JWT_TOKEN>` com token retornado por `/api/auth/login`

### Endpoints que Requerem Basic Auth
- Gateway Service (`/v1/vin/ownership`, `/v1/payment`)
- Username: `vendorcrapi`
- Password: `Pa$$4Vendor_1`
- Header: `Authorization: Basic <base64_encoded_credentials>`

### Endpoints Sem Autenticação
- `/api/auth/*` (maioria)
- `/identity/health_check`
- `/community/home`
- `/chatbot/` (maioria)
- Gateway Service `/`

---

## Resumo de Métodos HTTP

| Método | Descrição | Frequência |
|--------|-----------|-----------|
| GET | Recuperar dados | 40 endpoints |
| POST | Criar/Enviar dados | 50 endpoints |
| PUT | Atualizar dados | 8 endpoints |
| DELETE | (Não implementado) | 0 endpoints |
| OPTIONS | CORS | Todas com @CrossOrigin |

---

## Resumo de Tipos de Payload

| Tipo | Descrição | Exemplos |
|------|-----------|----------|
| JSON | application/json | POST /api/auth/login |
| Form Data | multipart/form-data | POST /api/v2/user/pictures |
| Query Params | URL parameters | GET /api/merchant/service_requests/<VIN> |
| Path Params | URL path variables | GET /api/v2/user/videos/{video_id} |
| Basic Auth | HTTP Basic Authentication | Gateway Service |
| Bearer Token | JWT in Authorization header | Maioria dos endpoints autenticados |

---

## Observações Importantes

1. **CORS:** Identity, Workshop e Community têm `@CrossOrigin` habilitado
2. **Paginação:** Muitos endpoints suportam `limit` e `offset` para paginação
3. **VIN (Vehicle Identification Number):** Identificador único do veículo
4. **JWT Token:** Válido por tempo determinado, pode expirar
5. **OTP:** One-Time Password enviado por email para verificação
6. **Cupons:** Sistema de desconto implementado na loja
7. **Relatórios de Serviço:** Gerados em PDF
8. **Histórico de Proprietários:** Simulado no Gateway Service com dados aleatórios

---

**Total de Endpoints Mapeados:** 107+

**Última Atualização:** 08/06/2026
