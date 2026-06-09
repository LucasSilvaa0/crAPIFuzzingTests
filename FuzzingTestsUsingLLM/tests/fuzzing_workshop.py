"""
Testes de fuzzing especializados para Workshop Service
Fase 4: Fuzzing Direcionado para Pontos Críticos
Foca em: Autorização, Injeção, Lógica de Negócio
"""
import pytest
import logging
from fuzzing_generic import GenericFuzzTester

logger = logging.getLogger(__name__)


class TestWorkshopAuthorizationFuzzing:
    """Testes de fuzzing para vulnerabilidades de autorização (BOLA/BFLA)"""
    
    def test_order_id_tampering(self, authenticated_workshop_client):
        """
        Challenge 9: Teste de acesso a pedidos de outros usuários
        Testa diferentes formatos de order_id
        
        Expected: BOLA vulnerability if unauthorized access returns 200
        """
        fuzz_tester = GenericFuzzTester(
            authenticated_workshop_client,
            "/api/shop/orders/1",
            method="GET"
        )
        
        # Valores extremos para order_id - tentar acessar pedidos que não pertencem ao usuário
        order_id_payloads = [
            1,  # Menor válido
            -1,  # Negativo
            0,  # Zero
            999999999,  # Muito grande
            2**31 - 1,  # Max int32
            2**63 - 1,  # Max int64
            "1",  # String
            "1.0",  # Float como string
            "1e10",  # Notação científica
            "0x1",  # Hexadecimal
        ]
        
        bola_vulnerabilities = []
        
        for order_id in order_id_payloads:
            # Substituir o ID na URL
            if isinstance(order_id, (int, str)) and order_id not in [None, [], {}]:
                endpoint = f"/api/shop/orders/{order_id}"
            else:
                endpoint = "/api/shop/orders/invalid"
            
            fuzz_tester.endpoint = endpoint
            result = fuzz_tester.test_with_payload(None, with_auth=True)
            
            # Log de resultado interessante
            if result.response_status == 200:
                bola_vulnerabilities.append(f"Unauthorized access to order {order_id}")
        
        # Validar: BOLA vulnerability seria status 200 em order que não pertence ao usuário
        # Esperado: 403 Forbidden ou 404 Not Found
        assert len(bola_vulnerabilities) == 0, \
            f"BOLA Vulnerabilities found: {bola_vulnerabilities}"
    
    def test_mechanic_request_id_tampering(self, authenticated_workshop_client):
        """
        Challenge 2: Teste de acesso a relatórios de mecânicos de outros usuários
        Testa diferentes formatos de service_id
        
        Expected: BOLA vulnerability if unauthorized access returns 200
        """
        fuzz_tester = GenericFuzzTester(
            authenticated_workshop_client,
            "/api/mechanic/service_request/1",
            method="GET"
        )
        
        # Payloads de ID
        id_payloads = [
            "1",
            "-1",
            "0",
            "99999",
            "999999999",
            "2**31-1",
        ]
        
        bola_vulnerabilities = []
        
        for service_id in id_payloads:
            fuzz_tester.endpoint = f"/api/mechanic/service_request/{service_id}"
            result = fuzz_tester.test_with_payload(None, with_auth=True)
            
            if result.response_status == 200:
                bola_vulnerabilities.append(f"Unauthorized access to service_request {service_id}")
        
        assert len(bola_vulnerabilities) == 0, \
            f"BOLA Vulnerabilities in mechanic requests: {bola_vulnerabilities}"


class TestWorkshopInjectionFuzzing:
    """Testes de fuzzing para vulnerabilidades de injeção"""
    
    def test_apply_coupon_injection(self, authenticated_workshop_client, 
                                   sql_injection_payloads,
                                   nosql_injection_payloads):
        """
        Challenge 13: Teste de injeção SQL/NoSQL no endpoint de cupom
        
        Expected: Injection attempts should be rejected (400, 401, 403, 500 but NOT 200 with success)
        """
        fuzz_tester = GenericFuzzTester(
            authenticated_workshop_client,
            "/api/shop/apply_coupon",
            method="POST"
        )
        
        injection_vulnerabilities = []
        
        # Payloads de injeção SQL
        for sql_payload in sql_injection_payloads:
            payload = {
                "coupon_code": sql_payload,
                "amount": 100
            }
            result = fuzz_tester.test_with_payload(payload, with_auth=True)
            
            # Vulnerable if: injection payload accepted with 200 and successful discount
            if result.response_status == 200 and result.response_body:
                if isinstance(result.response_body, dict) and result.response_body.get("success"):
                    injection_vulnerabilities.append(f"SQL Injection vulnerability: {sql_payload}")
        
        # Payloads de injeção NoSQL
        for nosql_payload in nosql_injection_payloads:
            if isinstance(nosql_payload, dict):
                payload = {
                    "coupon_code": nosql_payload,
                    "amount": 100
                }
            else:
                payload = {
                    "coupon_code": nosql_payload,
                    "amount": 100
                }
            result = fuzz_tester.test_with_payload(payload, with_auth=True)
            
            if result.response_status == 200 and result.response_body:
                if isinstance(result.response_body, dict) and result.response_body.get("success"):
                    injection_vulnerabilities.append(f"NoSQL Injection vulnerability: {str(nosql_payload)[:50]}")
        
        assert len(injection_vulnerabilities) == 0, \
            f"Injection vulnerabilities detected: {injection_vulnerabilities}"
    
    def test_contact_mechanic_ssrf(self, authenticated_workshop_client,
                                  ssrf_payloads):
        """
        Challenge 11: Teste de SSRF no endpoint de contato com mecânico
        
        Expected: SSRF attempts should fail or be rejected (not execute internal requests)
        """
        fuzz_tester = GenericFuzzTester(
            authenticated_workshop_client,
            "/api/merchant/contact_mechanic",
            method="POST"
        )
        
        ssrf_vulnerabilities = []
        
        for ssrf_url in ssrf_payloads:
            payload = {
                "mechanic_id": 1,
                "service_request_id": 1,
                "message": "test",
                "attachment_url": ssrf_url  # Campo vulnerável a SSRF
            }
            result = fuzz_tester.test_with_payload(payload, with_auth=True)
            
            # Vulnerable if SSRF URL accepted and executed
            if result.response_status == 200:
                if result.response_body and isinstance(result.response_body, dict):
                    # Check if response contains fetched data (indicates SSRF worked)
                    if any(key in str(result.response_body).lower() for key in 
                           ["metadata", "password", "secret", "token", "<!doctype", "html"]):
                        ssrf_vulnerabilities.append(f"SSRF vulnerability: {ssrf_url}")
        
        assert len(ssrf_vulnerabilities) == 0, \
            f"SSRF vulnerabilities detected: {ssrf_vulnerabilities}"


class TestWorkshopMassAssignmentFuzzing:
    """Testes para vulnerabilidades de mass assignment"""
    
    def test_order_mass_assignment(self, authenticated_workshop_client,
                                  mass_assignment_payloads):
        """
        Challenge 8-9: Teste de mass assignment em pedidos
        Tenta modificar campos internos via request
        
        Expected: Extra fields should be ignored, not assigned
        """
        fuzz_tester = GenericFuzzTester(
            authenticated_workshop_client,
            "/api/shop/orders",
            method="POST"
        )
        
        base_payload = {
            "product_id": 1,
            "quantity": 1
        }
        
        mass_assignment_vulnerabilities = []
        
        for extra_field in mass_assignment_payloads:
            payload = {**base_payload, **extra_field}
            result = fuzz_tester.test_with_payload(payload, with_auth=True)
            
            # Verificar se o field extra foi aceito e atribuído
            if result.response_status == 200 and result.response_body:
                if isinstance(result.response_body, dict):
                    for key in extra_field.keys():
                        if key in result.response_body:
                            actual_value = result.response_body.get(key)
                            expected_value = extra_field[key]
                            if actual_value == expected_value:
                                mass_assignment_vulnerabilities.append(
                                    f"Mass Assignment: Campo '{key}' foi atribuído com valor {actual_value}"
                                )
        
        assert len(mass_assignment_vulnerabilities) == 0, \
            f"Mass Assignment vulnerabilities: {mass_assignment_vulnerabilities}"
    
    def test_return_order_credit_manipulation(self, authenticated_workshop_client):
        """
        Challenge 8-9: Teste de manipulação de crédito em devolução
        """
        fuzz_tester = GenericFuzzTester(
            authenticated_workshop_client,
            "/api/shop/orders/return_order",
            method="POST"
        )
        
        # Tenta manipular quantidade de crédito reembolsado
        return_payloads = [
            {"order_id": 1, "return_quantity": 1, "refund_amount": 999999},
            {"order_id": 1, "return_quantity": 999, "refund_amount": 999999},
            {"order_id": 1, "return_quantity": -1, "refund_amount": -999999},
            {"order_id": 1, "return_quantity": 0, "refund_amount": 0},
            {"order_id": 1, "return_quantity": "9" * 100},  # String grande
            {"order_id": 1, "return_quantity": 2**31},  # Overflow
        ]
        
        for payload in return_payloads:
            result = fuzz_tester.test_with_payload(payload, with_auth=True)
            if result.response_status == 200:
                logger.info(f"Return order accepted with payload: {payload}")


class TestWorkshopBusinessLogicFuzzing:
    """Testes para vulnerabilidades de lógica de negócio"""
    
    def test_order_with_negative_quantity(self, authenticated_workshop_client):
        """Teste de quantidade negativa em pedido"""
        payload = {
            "product_id": 1,
            "quantity": -10
        }
        response = authenticated_workshop_client.post(
            "/api/shop/orders",
            json_data=payload,
            with_auth=True
        )
        
        if response.status_code == 200:
            logger.warning("⚠️ Pedido criado com quantidade negativa!")
    
    def test_order_with_zero_quantity(self, authenticated_workshop_client):
        """Teste de quantidade zero em pedido"""
        payload = {
            "product_id": 1,
            "quantity": 0
        }
        response = authenticated_workshop_client.post(
            "/api/shop/orders",
            json_data=payload,
            with_auth=True
        )
        
        if response.status_code == 200:
            logger.warning("⚠️ Pedido criado com quantidade zero!")
    
    def test_order_with_extreme_quantity(self, authenticated_workshop_client):
        """Teste de quantidade extrema em pedido"""
        extreme_quantities = [
            2**31 - 1,
            2**63 - 1,
            float('inf'),
            -2**31,
            999999999999,
        ]
        
        for qty in extreme_quantities:
            payload = {
                "product_id": 1,
                "quantity": qty
            }
            response = authenticated_workshop_client.post(
                "/api/shop/orders",
                json_data=payload,
                with_auth=True
            )
            
            if response.status_code == 200:
                logger.warning(f"⚠️ Pedido aceito com quantidade extrema: {qty}")


class TestWorkshopPaginationFuzzing:
    """Testes para fuzzing de paginação"""
    
    def test_pagination_with_extreme_offsets(self, authenticated_workshop_client):
        """Teste de paginação com offsets extremos"""
        fuzz_tester = GenericFuzzTester(
            authenticated_workshop_client,
            "/api/shop/orders/all",
            method="GET"
        )
        
        limit_offset_payloads = [
            {"limit": -1, "offset": 0},
            {"limit": 0, "offset": 0},
            {"limit": 2**31, "offset": 0},
            {"limit": 1, "offset": -1},
            {"limit": 1, "offset": 2**31},
            {"limit": "1", "offset": "0"},
            {"limit": "abc", "offset": "xyz"},
            {"limit": "", "offset": ""},
            {"limit": None, "offset": None},
        ]
        
        for params in limit_offset_payloads:
            result = fuzz_tester.test_with_payload(None, with_auth=True)


class TestWorkshopConcurrencyFuzzing:
    """Testes para race conditions"""
    
    def test_concurrent_order_creation(self, authenticated_workshop_client):
        """
        Teste básico de concorrência
        Em um ambiente real, usaria threading/async
        """
        import concurrent.futures
        
        payload = {
            "product_id": 1,
            "quantity": 1
        }
        
        # Simular múltiplas requisições concorrentes
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(
                    authenticated_workshop_client.post,
                    "/api/shop/orders",
                    json_data=payload,
                    with_auth=True
                )
                for _ in range(5)
            ]
            
            results = [f.result() for f in futures]
            
            # Verificar se todos foram processados
            success_count = sum(1 for r in results if r.status_code == 200)
            logger.info(f"Concurrent orders created: {success_count}/5")
