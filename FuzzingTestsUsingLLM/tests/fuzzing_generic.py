"""
Testes genéricos de fuzzing para todas as APIs REST do crAPI
Fase 3: Criação de Fuzz Tests Genéricos
"""
import pytest
import json
from typing import Dict, Any, Callable, Optional, List
from hypothesis import given, settings, HealthCheck, assume
from hypothesis import strategies as st
import logging

logger = logging.getLogger(__name__)


class FuzzTestException(Exception):
    """Exceção base para testes de fuzzing"""
    pass


class FuzzTestResult:
    """Resultado de um teste de fuzzing"""
    
    def __init__(self, endpoint: str, method: str, payload: Any):
        self.endpoint = endpoint
        self.method = method
        self.payload = payload
        self.response_status = None
        self.response_body = None
        self.error = None
        self.is_crash = False
        self.is_unexpected_behavior = False
    
    def __repr__(self):
        return f"FuzzTestResult(endpoint={self.endpoint}, status={self.response_status}, error={self.error})"


class GenericFuzzTester:
    """Classe base para fuzzing genérico de endpoints"""
    
    # Status codes esperados para diferentes métodos
    EXPECTED_STATUS_CODES = {
        'GET': [200, 404, 401, 403],
        'POST': [200, 201, 400, 401, 403, 409],
        'PUT': [200, 204, 400, 401, 403, 404],
        'DELETE': [200, 204, 404, 401, 403],
    }
    
    # Status codes que indicam crash ou erro não tratado
    CRASH_STATUS_CODES = [500, 502, 503]
    
    def __init__(self, client, endpoint: str, method: str = 'GET'):
        self.client = client
        self.endpoint = endpoint
        self.method = method
        self.results: List[FuzzTestResult] = []
    
    def test_with_payload(self, payload: Any, 
                         with_auth: bool = True) -> FuzzTestResult:
        """Testa endpoint com um payload específico"""
        result = FuzzTestResult(self.endpoint, self.method, payload)
        
        try:
            # Fazer requisição
            if self.method.upper() == 'GET':
                if isinstance(payload, dict):
                    response = self.client.get(self.endpoint, params=payload, 
                                             with_auth=with_auth)
                else:
                    response = self.client.get(self.endpoint, with_auth=with_auth)
            else:
                # POST/PUT/DELETE com JSON payload
                response = self.client.request(
                    self.method,
                    self.endpoint,
                    json_data=payload if isinstance(payload, dict) else None,
                    with_auth=with_auth
                )
            
            result.response_status = response.status_code
            
            # Tentar parsear resposta como JSON
            try:
                result.response_body = response.json()
            except:
                result.response_body = response.text
            
            # Verificar se foi crash
            if response.status_code in self.CRASH_STATUS_CODES:
                result.is_crash = True
            
            # Verificar behavior inesperado
            expected = self.EXPECTED_STATUS_CODES.get(self.method.upper(), [200, 400])
            if response.status_code not in expected + self.CRASH_STATUS_CODES:
                result.is_unexpected_behavior = True
            
        except Exception as e:
            result.error = str(e)
            logger.error(f"Erro ao testar {self.endpoint}: {e}")
        
        self.results.append(result)
        return result
    
    def test_malformed_json(self, with_auth: bool = True) -> List[FuzzTestResult]:
        """Testa com JSON malformados"""
        payloads = [
            "{",  # Truncado
            '{"key":',  # Truncado
            '{"key":"value"',  # Sem fechar
            '{"key":"value",}',  # Vírgula extra
            '{"key":"value",,}',  # Dupla vírgula
            '{"":""',  # Chave vazia
            '{null}',  # Estrutura inválida
            '{"key": undefined}',  # Undefined (JavaScript)
            '{"key": NaN}',  # NaN
            '{"key": Infinity}',  # Infinity
        ]
        
        results = []
        for payload in payloads:
            try:
                # Enviar como string raw
                response = self.client.session.request(
                    self.method,
                    f"{self.client.base_url}{self.endpoint}",
                    data=payload,
                    headers=self.client.get_headers(with_auth=with_auth),
                    timeout=10
                )
                result = FuzzTestResult(self.endpoint, self.method, payload)
                result.response_status = response.status_code
                results.append(result)
            except Exception as e:
                result = FuzzTestResult(self.endpoint, self.method, payload)
                result.error = str(e)
                results.append(result)
        
        self.results.extend(results)
        return results
    
    def test_null_and_empty_fields(self, required_fields: Dict[str, Any], 
                                   with_auth: bool = True) -> List[FuzzTestResult]:
        """Testa com campos nulos e vazios"""
        results = []
        
        # Teste 1: Todos os campos nulos
        payload = {key: None for key in required_fields.keys()}
        result = self.test_with_payload(payload, with_auth=with_auth)
        result.payload = "All fields null"
        results.append(result)
        
        # Teste 2: Todos os campos vazios
        payload = {key: "" for key in required_fields.keys()}
        result = self.test_with_payload(payload, with_auth=with_auth)
        result.payload = "All fields empty"
        results.append(result)
        
        # Teste 3: Apenas espaços
        payload = {key: " " for key in required_fields.keys()}
        result = self.test_with_payload(payload, with_auth=with_auth)
        result.payload = "All fields spaces"
        results.append(result)
        
        # Teste 4: Campo ausente para cada campo obrigatório
        for field in required_fields.keys():
            payload = {k: "test" for k in required_fields.keys() if k != field}
            result = self.test_with_payload(payload, with_auth=with_auth)
            result.payload = f"Missing field: {field}"
            results.append(result)
        
        return results
    
    def test_extreme_sizes(self, with_auth: bool = True) -> List[FuzzTestResult]:
        """Testa com payloads de tamanho extremo"""
        results = []
        
        # Payload muito grande
        large_string = "A" * 10_000_000  # 10MB
        payload = {"data": large_string}
        result = self.test_with_payload(payload, with_auth=with_auth)
        result.payload = "Large payload (10MB)"
        results.append(result)
        
        # Array muito grande
        large_array = [1] * 1_000_000
        payload = {"items": large_array}
        result = self.test_with_payload(payload, with_auth=with_auth)
        result.payload = "Large array (1M items)"
        results.append(result)
        
        # Objeto muito aninhado
        nested_obj = {"value": "test"}
        for _ in range(1000):
            nested_obj = {"nested": nested_obj}
        result = self.test_with_payload(nested_obj, with_auth=with_auth)
        result.payload = "Deeply nested object (1000 levels)"
        results.append(result)
        
        return results
    
    def test_type_confusion(self, required_fields: Dict[str, type], 
                           with_auth: bool = True) -> List[FuzzTestResult]:
        """Testa com tipos incorretos para campos"""
        results = []
        
        for field, expected_type in required_fields.items():
            # Enviar tipo errado para cada campo
            wrong_types = []
            
            if expected_type in (str, int, float, bool):
                # Se esperado é string, enviar número, boolean, etc
                if expected_type != str:
                    wrong_types.extend([
                        {field: "123"},  # String onde deve ser número
                        {field: [1, 2, 3]},  # Array
                        {field: {"nested": "object"}},  # Objeto
                    ])
                if expected_type != int:
                    wrong_types.extend([
                        {field: "not_a_number"},  # String
                        {field: [1]},  # Array
                    ])
                if expected_type != bool:
                    wrong_types.extend([
                        {field: "true"},  # String "true"
                        {field: 1},  # Número
                        {field: "1"},  # String "1"
                    ])
            
            for payload_base in wrong_types:
                # Adicionar outros campos com valores válidos
                payload = {k: "valid" for k in required_fields.keys()}
                payload.update(payload_base)
                
                result = self.test_with_payload(payload, with_auth=with_auth)
                result.payload = f"Type confusion on field '{field}': expected {expected_type.__name__}"
                results.append(result)
        
        return results
    
    def test_special_characters(self, field_name: str = "input", 
                               with_auth: bool = True) -> List[FuzzTestResult]:
        """Testa com caracteres especiais"""
        special_chars = [
            "'\"><script>alert('xss')</script>",
            "'; DROP TABLE users; --",
            "${7*7}",
            "{{7*7}}",
            "{%7*7%}",
            "/../../../etc/passwd",
            "\\..\\..\\..\\windows\\system32",
            "%00%00%00",
            "\x00\x01\x02",
            "\uffff\uffff",
        ]
        
        results = []
        for char_payload in special_chars:
            payload = {field_name: char_payload}
            result = self.test_with_payload(payload, with_auth=with_auth)
            result.payload = f"Special chars: {repr(char_payload[:50])}"
            results.append(result)
        
        return results
    
    def test_headers_manipulation(self) -> List[FuzzTestResult]:
        """Testa manipulação de headers"""
        results = []
        
        malicious_headers = [
            {"Authorization": "Bearer invalid_token"},
            {"Authorization": "Bearer " + "x" * 10000},
            {"Authorization": "invalid_scheme_token"},
            {"Content-Type": "application/xml"},
            {"Content-Type": "text/html"},
            {"User-Agent": "../../../etc/passwd"},
            {"X-Forwarded-For": "127.0.0.1"},
            {"X-Original-URL": "/admin"},
        ]
        
        for headers in malicious_headers:
            try:
                response = self.client.session.request(
                    self.method,
                    f"{self.client.base_url}{self.endpoint}",
                    headers={**self.client.get_headers(), **headers},
                    timeout=10
                )
                result = FuzzTestResult(self.endpoint, self.method, headers)
                result.response_status = response.status_code
                results.append(result)
            except Exception as e:
                result = FuzzTestResult(self.endpoint, self.method, headers)
                result.error = str(e)
                results.append(result)
        
        self.results.extend(results)
        return results
    
    def test_extra_fields(self, known_fields: List[str], 
                         with_auth: bool = True) -> List[FuzzTestResult]:
        """Testa com campos extras (mass assignment)"""
        results = []
        
        # Adicionar campos extras potencialmente sensíveis
        extra_fields = [
            {"admin": True},
            {"is_admin": True},
            {"role": "admin"},
            {"permission_level": 999},
            {"is_superuser": True},
            {"user_id": 1},
            {"user": {"id": 1}},
            {"bypass_auth": True},
            {"__class__": {"__bases__": []}},  # Prototype pollution
        ]
        
        for extra in extra_fields:
            payload = {k: "valid" for k in known_fields}
            payload.update(extra)
            
            result = self.test_with_payload(payload, with_auth=with_auth)
            result.payload = f"Extra field: {list(extra.keys())}"
            results.append(result)
        
        return results
    
    def get_crash_results(self) -> List[FuzzTestResult]:
        """Retorna resultados que indicam crash"""
        return [r for r in self.results if r.is_crash or r.error]
    
    def get_unexpected_behavior(self) -> List[FuzzTestResult]:
        """Retorna resultados com comportamento inesperado"""
        return [r for r in self.results if r.is_unexpected_behavior]
    
    def print_summary(self):
        """Imprime resumo dos testes"""
        print(f"\n{'='*80}")
        print(f"Resumo de Fuzzing para {self.endpoint}")
        print(f"{'='*80}")
        print(f"Total de testes executados: {len(self.results)}")
        print(f"Crashes encontrados: {len(self.get_crash_results())}")
        print(f"Comportamentos inesperados: {len(self.get_unexpected_behavior())}")
        print(f"Erros de conexão: {len([r for r in self.results if r.error])}")
        print(f"{'='*80}\n")


# Testes com Hypothesis para property-based testing
class HypothesisFuzzTester:
    """Fuzzer baseado em Hypothesis para testes property-based"""
    
    @staticmethod
    @given(st.text())
    @settings(max_examples=100)
    def test_string_field_accepts_any_string(client, endpoint: str, 
                                             field_name: str, 
                                             value: str):
        """Testa que campo string aceita qualquer string sem crash"""
        payload = {field_name: value}
        try:
            response = client.post(endpoint, json_data=payload, with_auth=False)
            # Não deve fazer crash (500, 502, 503)
            assert response.status_code not in [500, 502, 503], \
                f"Crash ao enviar string: {response.status_code}"
        except Exception as e:
            pytest.fail(f"Exception ao enviar string: {e}")
    
    @staticmethod
    @given(st.integers())
    @settings(max_examples=100)
    def test_integer_field_robustness(client, endpoint: str, 
                                      field_name: str, 
                                      value: int):
        """Testa robustez de campo inteiro com valores extremos"""
        payload = {field_name: value}
        try:
            response = client.post(endpoint, json_data=payload, with_auth=False)
            assert response.status_code not in [500, 502, 503]
        except Exception as e:
            pytest.fail(f"Exception ao enviar inteiro: {e}")
