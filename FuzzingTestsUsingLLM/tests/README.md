# 🧪 Testes de Fuzzing para crAPI

Este diretório contém uma suíte completa de testes de fuzzing para o crAPI, cobrindo todas as APIs REST com foco em segurança e robustez.

## 📋 Conteúdo

### Fase 1: Descoberta de APIs ✅
- Mapeamento de **107+ endpoints** REST
- Identificação de métodos HTTP, payloads, autenticação
- Organização por serviço e categoria funcional

### Fase 2: Pontos Críticos ✅
Identificadas 5 prioridades principais:
1. **Autenticação & Autorização** (BOLA/BFLA) - 15 endpoints
2. **Validação & Injeção** (SQL/NoSQL/XSS) - 12 endpoints
3. **File/Data Handling** - 5 endpoints
4. **Business Logic** - 8 endpoints
5. **Chatbot/LLM** - 3 endpoints

### Fase 3: Fuzzing Genérico ✅
- Testes aplicáveis a **qualquer endpoint REST**
- `fuzzing_generic.py` - Classe `GenericFuzzTester`
  - JSON malformado
  - Campos nulos/vazios
  - Tamanhos extremos
  - Confusão de tipos
  - Caracteres especiais
  - Manipulação de headers

### Fase 4: Fuzzing Especial ✅
- **Workshop** (`fuzzing_workshop.py`) - BOLA, injeção, mass assignment, lógica de negócio
- **Identity** (`fuzzing_identity.py`) - Autenticação, JWT, recuperação de senha, enumeração
- **Community** (`fuzzing_community.py`) - Posts, comentários, cupons, rate limiting
- **Chatbot** (`fuzzing_chatbot.py`) - Prompt injection, extração de credenciais, impersonação

## 🚀 Como Executar

### Pré-requisitos

1. **crAPI rodando**
   ```bash
   # Em outro terminal, execute crAPI
   cd deploy/docker
   docker compose up -d
   ```

2. **Instalar dependências**
   ```bash
   cd FuzzingTestsUsingLLM/tests
   pip install -r requirements.txt
   ```

3. **Configurar variáveis de ambiente** (opcional)
   ```bash
   # Criar arquivo .env
   cat > .env << EOF
   IDENTITY_URL=http://localhost:8080
   WORKSHOP_URL=http://localhost:8000
   COMMUNITY_URL=http://localhost:8087
   CHATBOT_URL=http://localhost:8080
   GATEWAY_URL=http://localhost:8090
   EOF
   ```

### Executar Todos os Testes

```bash
# Todos os testes com output verbose
pytest -v

# Com relatório HTML
pytest -v --html=report.html

# Com cobertura
pytest -v --cov

# Em paralelo (mais rápido)
pytest -v -n auto
```

### Executar por Serviço

```bash
# Apenas testes do Workshop
pytest fuzzing_workshop.py -v -m workshop

# Apenas testes de autenticação
pytest fuzzing_identity.py -v -m authentication

# Apenas testes de injeção
pytest -v -m injection

# Apenas endpoints críticos
pytest -v -m critical
```

### Executar Testes Específicos

```bash
# Teste específico de fuzzing
pytest fuzzing_workshop.py::TestWorkshopAuthorizationFuzzing::test_order_id_tampering -v

# Todos os testes de um arquivo
pytest fuzzing_identity.py -v

# Testes lentos (cuidado, demoram mais)
pytest -v -m slow
```

### Execução com Flags Customizadas

```bash
# Debug mode (para, para, para em erro)
pytest -v -x

# Com logs detalhados
pytest -v -s

# Apenas falhas
pytest --lf

# Executar último teste que falhou
pytest --ff

# Gerar relatório com stack trace
pytest -v --tb=long

# Com seed specific para Hypothesis (reproducível)
pytest -v --hypothesis-seed=12345
```

## 📊 Estrutura de Testes

```
tests/
├── conftest.py                 # Configuração, fixtures e clientes
├── fixtures.py                 # Geradores de payloads e strategies
├── fuzzing_generic.py          # Framework genérico de fuzzing
├── fuzzing_workshop.py         # Testes especializados - Workshop
├── fuzzing_identity.py         # Testes especializados - Identity
├── fuzzing_community.py        # Testes especializados - Community
├── fuzzing_chatbot.py          # Testes especializados - Chatbot
├── pytest.ini                  # Configuração do Pytest
├── requirements.txt            # Dependências
└── README.md                   # Este arquivo
```

## 🎯 Funcionalidades Principais

### GenericFuzzTester
Classe base para fuzzing de qualquer endpoint:

```python
fuzz_tester = GenericFuzzTester(client, "/api/endpoint", method="POST")

# Testar com payload específico
result = fuzz_tester.test_with_payload({"key": "value"})

# Testar JSON malformados
fuzz_tester.test_malformed_json()

# Testar campos nulos/vazios
fuzz_tester.test_null_and_empty_fields({"required_field": "string"})

# Testar tipos incorretos
fuzz_tester.test_type_confusion({"field": str, "number": int})

# Testar caracteres especiais
fuzz_tester.test_special_characters()

# Resumo dos resultados
fuzz_tester.print_summary()

# Obter crashes detectados
crashes = fuzz_tester.get_crash_results()
```

### Payloads Disponíveis

```python
# Via fixtures em conftest.py
@pytest.fixture
def sql_injection_payloads
@pytest.fixture
def nosql_injection_payloads
@pytest.fixture
def xss_payloads
@pytest.fixture
def path_traversal_payloads
@pytest.fixture
def command_injection_payloads
@pytest.fixture
def ssrf_payloads
@pytest.fixture
def jwt_bypass_payloads
@pytest.fixture
def mass_assignment_payloads
@pytest.fixture
def authentication_bypass_payloads
```

## 🔍 Casos de Teste Principais

### Workshop (Lógica de Negócio & Autorização)
- ✅ Acesso a pedidos de outros usuários (Challenge 9)
- ✅ Acesso a relatórios de mecânicos (Challenge 2)
- ✅ Injeção em cupons (Challenge 13)
- ✅ SSRF via URLs (Challenge 11)
- ✅ Mass assignment em pedidos (Challenge 8-9)
- ✅ Manipulação de quantidade/preço

### Identity (Autenticação)
- ✅ Bypass de login (Challenge 3)
- ✅ Bypass de registro
- ✅ Forjamento de JWT (Challenge 15)
- ✅ Brute force de OTP (Challenge 3)
- ✅ User enumeration
- ✅ Timing attacks em OTP

### Community (Injeção & Rate Limiting)
- ✅ BOLA em posts (Challenge 4)
- ✅ XSS em comentários (Challenge 4)
- ✅ Injeção em busca (Challenge 12)
- ✅ Rate limiting bypass (Challenge 6)
- ✅ Mass assignment em cupons

### Chatbot (Vulnerabilidades de LLM)
- ✅ Prompt injection (Challenge 16)
- ✅ Extração de credenciais (Challenge 17)
- ✅ Impersonação de usuário (Challenge 18)
- ✅ Injeção via arquivo
- ✅ Cross-session access

## 📈 Relatórios

### Saída de Teste
```
RESUMO DE FUZZING PARA /api/shop/orders/1
================================================================================
Total de testes executados: 45
Crashes encontrados: 2
Comportamentos inesperados: 8
Erros de conexão: 0
================================================================================
```

### Arquivo de Log
Todos os testes geram log em `fuzzing_results.log`:
```
2024-01-15 10:30:45 [WARNING] ⚠️ SQL Injection possível: 1' OR '1'='1
2024-01-15 10:31:02 [WARNING] ⚠️ JWT verificado como válido: eyJ...
2024-01-15 10:31:15 [ERROR] Crash ao enviar mensagem grande: 500
```

## ⚠️ Avisos Importantes

1. **Ambiente de Teste**: Executar **APENAS** em ambiente de desenvolvimento
2. **Dados**: Os testes **PODEM** modificar dados da aplicação
3. **Performance**: Fuzzing gera muitas requisições - pode sobrecarregar
4. **Rate Limiting**: Alguns testes intentam contornar rate limiting
5. **Segurança**: Este é um repositório de treinamento - nunca usar em produção

## 🛠️ Estendendo os Testes

### Adicionar novo endpoint para fuzzing

```python
# Em fuzzing_workshop.py
def test_my_new_endpoint(self, authenticated_workshop_client):
    fuzz_tester = GenericFuzzTester(
        authenticated_workshop_client,
        "/api/new/endpoint",
        method="POST"
    )
    
    # Testar várias estratégias
    fuzz_tester.test_malformed_json()
    fuzz_tester.test_extreme_sizes()
    fuzz_tester.test_special_characters()
    
    # Verificar resultados
    crashes = fuzz_tester.get_crash_results()
    assert len(crashes) == 0, f"Crashes encontrados: {crashes}"
```

### Adicionar novo tipo de payload

```python
# Em fixtures.py
@pytest.fixture
def my_custom_payloads():
    return [
        "payload1",
        "payload2",
        {"complex": "payload"},
    ]
```

## 📚 Referências

- [OWASP API Top 10](https://owasp.org/www-project-api-security/)
- [crAPI Challenges](../docs/challenges.md)
- [crAPI Architecture](../docs/crAPI_architecture.md)
- [Pytest Documentation](https://docs.pytest.org/)
- [Hypothesis Testing](https://hypothesis.readthedocs.io/)

## 🐛 Troubleshooting

### Erro de Conexão
```
APIClientError: Erro ao fazer requisição: Connection refused
```
**Solução**: Verificar se crAPI está rodando
```bash
docker compose ps
```

### Token Inválido
```
APIClientError: Não foi possível obter token de autenticação
```
**Solução**: Verificar credenciais em `conftest.py`

### Timeout em Testes
```
pytest.exceptions.Timeout: Test took longer than 30.0s
```
**Solução**: Aumentar timeout em `pytest.ini` ou executar com `-m "not slow"`

## 📝 Próximas Etapas

- [ ] Implementar CI/CD integration (GitHub Actions)
- [ ] Adicionar fuzzing com AFL/libFuzzer
- [ ] Integração com SonarQube para análise
- [ ] Dashboard de resultados
- [ ] Testes de performance
- [ ] Integração com OWASP ZAP
- [ ] Fuzzing cross-service (workflows)
- [ ] Análise automática de vulnerabilidades

## 👥 Contribuindo

Para adicionar mais testes:
1. Criar teste em arquivo apropriado (`fuzzing_<service>.py`)
2. Usar decoradores de marcadores: `@pytest.mark.<marker>`
3. Adicionar logging: `logger.warning(f"Vulnerabilidade: {}")`
4. Documentar em docstring

## 📞 Suporte

Para dúvidas ou problemas:
- Consultar logs em `fuzzing_results.log`
- Executar com `-v -s` para verbose output
- Validar endpoints com `curl` antes de fuzz test
