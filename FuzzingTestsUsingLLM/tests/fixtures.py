"""
Geradores de payloads para testes de fuzzing
Contém fixtures reutilizáveis para todos os tipos de entrada malformada
"""
import pytest
import json
import string
from hypothesis import strategies as st
from typing import Any, List, Dict, Union


class PayloadGenerator:
    """Gerador de payloads para fuzzing"""
    
    # Strings malformadas
    MALFORMED_STRINGS = [
        "",  # String vazia
        " ",  # Apenas espaço
        "\x00",  # Null byte
        "\n\r\t",  # Caracteres de controle
        "'" + "'" * 10000,  # Aspas em excesso
        '"' * 5000,  # Aspas duplas em excesso
        "\\" * 1000,  # Barras de escape em excesso
        "<?xml version='1.0'?>",  # XML injection
        "<script>alert('xss')</script>",  # XSS payload
        "'; DROP TABLE users; --",  # SQL injection
        "${7*7}",  # Template injection
        "{{7*7}}",  # Template injection
        "%00%00%00",  # Null bytes
        "../../../etc/passwd",  # Path traversal
        "\\\\..\\\\..\\\\windows\\\\system32",  # Path traversal Windows
        "\u0000" * 100,  # Unicode null
        "\uffff" * 100,  # Unicode extremo
        "A" * 1000000,  # String gigante
    ]
    
    # Números extremos
    EXTREME_NUMBERS = [
        0,
        1,
        -1,
        2**31 - 1,  # Max int32
        -(2**31),  # Min int32
        2**63 - 1,  # Max int64
        -(2**63),  # Min int64
        float('inf'),  # Infinity
        float('-inf'),  # Negative infinity
        float('nan'),  # NaN
        1.7976931348623157e+308,  # Max float
        2.2250738585072014e-308,  # Min positive float
        1e1000,  # Overflow
        -1e1000,  # Negative overflow
    ]
    
    # Arrays e objetos extremos
    EXTREME_STRUCTURES = [
        [],  # Array vazio
        [None] * 10000,  # Array grande de nulls
        list(range(100000)),  # Array grande
        {},  # Objeto vazio
        {f"key_{i}": i for i in range(10000)},  # Objeto com muitas chaves
        {"a": {"b": {"c": {"d": {"e": {"f": None}}}}}},  # Profundidade extrema
        [[[[[[[[[[None]]]]]]]]]]],  # Nesting profundo
    ]
    
    # Payloads especiais
    SPECIAL_PAYLOADS = [
        None,
        True,
        False,
        "",
        0,
        [],
        {},
    ]
    
    # Caracteres especiais para diferentes contextos
    SPECIAL_CHARS_URL = [
        "%",
        "%00",
        "%2e",
        "%2f",
        "%3f",
        "&",
        "?",
        "#",
        "\\",
    ]
    
    SPECIAL_CHARS_JSON = [
        "\\",
        '"',
        "\n",
        "\r",
        "\t",
        "\b",
        "\f",
    ]
    
    SPECIAL_CHARS_SQL = [
        "'",
        '"',
        ";",
        "--",
        "/*",
        "*/",
        "\\",
        "\x00",
    ]
    
    SPECIAL_CHARS_COMMAND = [
        ";",
        "|",
        "&",
        "`",
        "$",
        "(",
        ")",
        "<",
        ">",
        "\n",
        "\r",
    ]
    
    @staticmethod
    def string_with_special_chars(chars: List[str], length: int = 100) -> List[str]:
        """Gera strings com caracteres especiais"""
        results = []
        for char in chars:
            results.append(char * (length // len(char) if char else 1))
            results.append("test" + char + "test")
            results.append(char + "test" + char)
        return results
    
    @staticmethod
    def create_deeply_nested_object(depth: int = 50) -> Dict:
        """Cria objeto profundamente aninhado"""
        obj = {"value": "test"}
        for _ in range(depth):
            obj = {"nested": obj}
        return obj
    
    @staticmethod
    def create_circular_reference() -> Dict:
        """Cria estrutura com referência circular (para serialização)"""
        obj = {"key": "value"}
        # Não pode ser JSON, mas pode ser testado em contextos que lidam com estruturas
        return obj
    
    @staticmethod
    def mutate_json(json_obj: Dict, depth: int = 0) -> List[str]:
        """Gera múltiplas variações malformadas de um JSON"""
        results = []
        json_str = json.dumps(json_obj)
        
        # Truncado
        results.append(json_str[:len(json_str)//2])
        
        # Com chave duplicada
        results.append(json_str.replace("}", ', "dup": "key"}'))
        
        # Com vírgula ausente
        results.append(json_str.replace('", "', '" "'))
        
        # Com aspas ausentes
        results.append(json_str.replace('"', ''))
        
        # Com caracteres aleatórios
        results.append(json_str + "\x00\x01\x02")
        
        return results


@pytest.fixture
def payload_generator():
    """Fixture que fornece gerador de payloads"""
    return PayloadGenerator


@pytest.fixture
def malformed_strings():
    """Payloads de strings malformadas"""
    return PayloadGenerator.MALFORMED_STRINGS


@pytest.fixture
def extreme_numbers():
    """Payloads de números extremos"""
    return PayloadGenerator.EXTREME_NUMBERS


@pytest.fixture
def extreme_structures():
    """Payloads de estruturas extremas"""
    return PayloadGenerator.EXTREME_STRUCTURES


@pytest.fixture
def special_payloads():
    """Payloads especiais"""
    return PayloadGenerator.SPECIAL_PAYLOADS


# Hypothesis strategies para property-based testing
@st.composite
def valid_email_like_strings(draw):
    """Strategy para strings que parecem emails"""
    username = draw(st.text(min_size=1, max_size=50))
    domain = draw(st.text(alphabet=string.ascii_letters + string.digits + "-", 
                         min_size=1, max_size=20))
    return f"{username}@{domain}.com"


@st.composite
def valid_jwt_like_strings(draw):
    """Strategy para strings que parecem JWTs"""
    header = draw(st.text(alphabet=string.ascii_letters + string.digits, 
                         min_size=10, max_size=50))
    payload = draw(st.text(alphabet=string.ascii_letters + string.digits, 
                          min_size=20, max_size=100))
    signature = draw(st.text(alphabet=string.ascii_letters + string.digits + "-_", 
                            min_size=20, max_size=50))
    return f"{header}.{payload}.{signature}"


@st.composite
def uuid_like_strings(draw):
    """Strategy para strings que parecem UUIDs"""
    import uuid as uuid_module
    return str(uuid_module.uuid4())


@pytest.fixture
def hypothesis_strategies():
    """Fixture com strategies do Hypothesis"""
    return {
        'email_like': valid_email_like_strings(),
        'jwt_like': valid_jwt_like_strings(),
        'uuid_like': uuid_like_strings(),
        'large_strings': st.text(min_size=10000, max_size=100000),
        'large_integers': st.integers(min_value=2**31, max_value=2**63),
        'nested_dicts': st.recursive(
            st.dictionaries(st.text(min_size=1), st.text()),
            lambda children: st.dictionaries(st.text(min_size=1), children),
            max_leaves=50
        ),
        'special_chars': st.characters(blacklist_categories=('Cc',)),
    }


# Fixtures para payloads específicos de contexto

@pytest.fixture
def sql_injection_payloads():
    """Payloads conhecidos de SQL injection"""
    return [
        "1' OR '1'='1",
        "admin' --",
        "1; DROP TABLE users;--",
        "1' UNION SELECT NULL,NULL,NULL--",
        "1' AND SLEEP(5)--",
        "1' AND 1=CAST(CHR(65)||CHR(66) AS INT)--",
    ]


@pytest.fixture
def nosql_injection_payloads():
    """Payloads conhecidos de NoSQL injection"""
    return [
        {"$ne": None},
        {"$ne": ""},
        {"$regex": ".*"},
        {"$gt": ""},
        {"$where": "return true"},
        '{"$or": [{"":1}]}',
    ]


@pytest.fixture
def xss_payloads():
    """Payloads conhecidos de XSS"""
    return [
        "<script>alert('xss')</script>",
        "<img src=x onerror=alert('xss')>",
        "<svg onload=alert('xss')>",
        "javascript:alert('xss')",
        "<iframe src=javascript:alert('xss')>",
        "'\"><script>alert('xss')</script>",
        "<body onload=alert('xss')>",
    ]


@pytest.fixture
def path_traversal_payloads():
    """Payloads conhecidos de path traversal"""
    return [
        "../../../etc/passwd",
        "..\\..\\..\\windows\\system32\\config\\sam",
        "....//....//....//etc/passwd",
        "..%252f..%252f..%252fetc%252fpasswd",
        "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
    ]


@pytest.fixture
def command_injection_payloads():
    """Payloads conhecidos de command injection"""
    return [
        "; ls -la",
        "| cat /etc/passwd",
        "` whoami `",
        "$(whoami)",
        "; sleep 5",
        "& powershell whoami",
    ]


@pytest.fixture
def xml_injection_payloads():
    """Payloads conhecidos de XML injection"""
    return [
        '<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]><root>&xxe;</root>',
        '<?xml version="1.0"?><!DOCTYPE foo [<!ELEMENT foo ANY><!ENTITY xxe SYSTEM "file:///c:/boot.ini">]><foo>&xxe;</foo>',
    ]


@pytest.fixture
def ssrf_payloads():
    """Payloads conhecidos de SSRF"""
    return [
        "http://localhost/admin",
        "http://127.0.0.1:8080/admin",
        "http://169.254.169.254/latest/meta-data/",  # AWS metadata
        "file:///etc/passwd",
        "gopher://localhost:25",
        "dict://localhost:11211",
        "http://[::1]/admin",  # IPv6 localhost
    ]


@pytest.fixture
def jwt_bypass_payloads():
    """Payloads para bypass de JWT"""
    return [
        # Token vazio/inválido
        "",
        "invalid",
        "invalid.token.here",
        # Modificações comuns
        "eyJhbGciOiJub25lIn0.eyJpc3MiOiJhZG1pbiJ9.",  # alg: none
        # Token com payload modificado mas mesma assinatura
    ]


@pytest.fixture
def mass_assignment_payloads():
    """Payloads para teste de mass assignment"""
    return [
        {"admin": True},
        {"is_admin": True},
        {"role": "admin"},
        {"permission_level": 999},
        {"is_superuser": True},
        {"balance": 999999},
        {"credit": 999999},
    ]


@pytest.fixture
def authentication_bypass_payloads():
    """Payloads para teste de bypass de autenticação"""
    return [
        {"email": None, "password": None},
        {"email": "", "password": ""},
        {"email": " ", "password": " "},
        {"email": "admin' OR '1'='1", "password": "anything"},
        {"email": "admin", "password": {"$ne": None}},
    ]
