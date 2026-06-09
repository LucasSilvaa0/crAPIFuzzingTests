"""
Testes de fuzzing especializados para Community Service
Fase 4: Fuzzing Direcionado - Posts, Comentários, Cupons
"""
import pytest
import logging
from fuzzing_generic import GenericFuzzTester

logger = logging.getLogger(__name__)


class TestCommunityPostsFuzzing:
    """Testes de fuzzing para endpoints de posts"""
    
    def test_post_id_tampering(self, authenticated_community_client):
        """
        Teste de acesso a posts de outros usuários
        Challenge: Enumerar e acessar posts
        
        Expected: Unauthorized access should be denied
        """
        fuzz_tester = GenericFuzzTester(
            authenticated_community_client,
            "/community/api/v2/community/posts/1",
            method="GET"
        )
        
        # Valores de ID para fuzzing
        post_ids = [
            1,
            -1,
            0,
            999999,
            2**31 - 1,
        ]
        
        bola_vulnerabilities = []
        
        for post_id in post_ids:
            fuzz_tester.endpoint = f"/community/api/v2/community/posts/{post_id}"
            result = fuzz_tester.test_with_payload(None, with_auth=True)
            
            # BOLA vulnerability if accessing other user's post with 200
            if result.response_status == 200:
                # Verify if we got another user's post (would indicate BOLA)
                if result.response_body and isinstance(result.response_body, dict):
                    post_data = result.response_body.get("post", result.response_body)
                    # If we can fetch a post by random ID, it's BOLA
                    bola_vulnerabilities.append(f"BOLA in posts: ID {post_id} returned data")
        
        assert len(bola_vulnerabilities) == 0, \
            f"BOLA vulnerabilities in posts: {bola_vulnerabilities}"
    
    def test_create_post_xss(self, authenticated_community_client,
                            xss_payloads):
        """
        Challenge 4: Teste de XSS em criação de post
        
        Expected: XSS payloads should be sanitized/rejected
        """
        fuzz_tester = GenericFuzzTester(
            authenticated_community_client,
            "/community/api/v2/community/posts",
            method="POST"
        )
        
        xss_vulnerabilities = []
        
        for xss_payload in xss_payloads:
            payload = {
                "title": "Test Post",
                "body": xss_payload
            }
            result = fuzz_tester.test_with_payload(payload, with_auth=True)
            
            if result.response_status == 200:
                # Check if XSS payload was stored unescaped
                if result.response_body and isinstance(result.response_body, dict):
                    stored_body = result.response_body.get("post", {}).get("body", "")
                    if xss_payload in stored_body:  # Payload stored unescaped = XSS vulnerability
                        xss_vulnerabilities.append(f"XSS vulnerability: {xss_payload[:50]}")
        
        assert len(xss_vulnerabilities) == 0, \
            f"XSS vulnerabilities in posts: {xss_vulnerabilities}"
    
    def test_post_search_injection(self, authenticated_community_client,
                                   sql_injection_payloads):
        """
        Teste de injeção em busca de posts
        
        Expected: Injection attempts should be rejected or sanitized
        """
        injection_vulnerabilities = []
        
        for sql_payload in sql_injection_payloads:
            # Testar com query params
            response = authenticated_community_client.get(
                "/community/api/v2/community/posts/search",
                params={"q": sql_payload},
                with_auth=True
            )
            
            if response.status_code == 200:
                response_str = str(response.content).lower()
                if any(keyword in response_str for keyword in ["syntax", "database", "sql", "query"]):
                    injection_vulnerabilities.append(f"SQL Injection: {sql_payload[:50]}")
        
        assert len(injection_vulnerabilities) == 0, \
            f"Injection vulnerabilities: {injection_vulnerabilities}"


class TestCommunityCommentsFuzzing:
    """Testes de fuzzing para comentários"""
    
    def test_comment_id_tampering(self, authenticated_community_client):
        """
        Teste de acesso a comentários de outros usuários
        
        Expected: Unauthorized access should be denied
        """
        bola_vulnerabilities = []
        
        # Tenta acessar comentários com IDs extremos
        comment_ids = [1, -1, 0, 999999, 2**31 - 1]
        
        for comment_id in comment_ids:
            response = authenticated_community_client.get(
                f"/community/api/v2/community/posts/1/comment/{comment_id}",
                with_auth=True
            )
            
            if response.status_code == 200:
                bola_vulnerabilities.append(f"BOLA in comments: comment ID {comment_id} returned data")
        
        assert len(bola_vulnerabilities) == 0, \
            f"BOLA vulnerabilities in comments: {bola_vulnerabilities}"
    
    def test_comment_xss_injection(self, authenticated_community_client,
                                  xss_payloads):
        """
        Teste de XSS em comentários
        
        Expected: XSS payloads should be sanitized/rejected
        """
        xss_vulnerabilities = []
        
        for xss_payload in xss_payloads:
            payload = {
                "body": xss_payload,
                "post_id": 1
            }
            response = authenticated_community_client.post(
                "/community/api/v2/community/posts/1/comment",
                data=payload,
                with_auth=True
            )
            
            if response.status_code == 200:
                stored_body = response.json().get("comment", {}).get("body", "")
                if xss_payload in stored_body:
                    xss_vulnerabilities.append(f"XSS in comment: {xss_payload[:50]}")
        
        assert len(xss_vulnerabilities) == 0, \
            f"XSS vulnerabilities in comments: {xss_vulnerabilities}"
    
    def test_comment_author_bypass(self, authenticated_community_client):
        """
        Challenge: Tentar apagar/editar comentário de outro usuário
        
        Expected: Only comment author should be able to delete/edit
        """
        authorization_vulnerabilities = []
        
        # Tentar deletar comentário com ID de outro usuário
        response = authenticated_community_client.delete(
            "/community/api/v2/community/comments/999",
            with_auth=True
        )
        
        if response.status_code == 200:
            authorization_vulnerabilities.append("User could delete comment from other user")
        
        assert len(authorization_vulnerabilities) == 0, \
            f"Authorization bypasses: {authorization_vulnerabilities}"


class TestCommunityCouponFuzzing:
    """Testes para cupons"""
    
    def test_coupon_code_injection(self, authenticated_community_client,
                                   sql_injection_payloads,
                                   nosql_injection_payloads):
        """
        Challenge 12: Teste de injeção em código de cupom
        
        Expected: Injection attempts should be rejected/sanitized
        """
        injection_vulnerabilities = []
        
        # SQL injection
        for sql_payload in sql_injection_payloads:
            payload = {"coupon_code": sql_payload}
            response = authenticated_community_client.post(
                "/community/api/v2/coupon/validate-coupon",
                data=payload,
                with_auth=True
            )
            
            if response.status_code == 200:
                response_str = str(response.content).lower()
                if any(keyword in response_str for keyword in ["syntax", "database", "sql"]):
                    injection_vulnerabilities.append(f"SQL Injection: {sql_payload[:50]}")
        
        # NoSQL injection
        for nosql_payload in nosql_injection_payloads:
            if isinstance(nosql_payload, dict):
                payload = {"coupon_code": nosql_payload}
            else:
                payload = {"coupon_code": str(nosql_payload)}
            
            response = authenticated_community_client.post(
                "/community/api/v2/coupon/validate-coupon",
                data=payload,
                with_auth=True
            )
            
            if response.status_code == 200:
                response_str = str(response.content).lower()
                if any(keyword in response_str for keyword in ["bson", "mongodb"]):
                    injection_vulnerabilities.append(f"NoSQL Injection: {str(nosql_payload)[:50]}")
        
        assert len(injection_vulnerabilities) == 0, \
            f"Coupon injection vulnerabilities: {injection_vulnerabilities}"
    
    def test_coupon_bypass(self, authenticated_community_client):
        """
        Teste de bypass de validação de cupom
        
        Expected: Invalid coupons should be rejected (non-200 responses)
        """
        bypass_vulnerabilities = []
        
        bypass_payloads = [
            {"coupon_code": ""},
            {"coupon_code": " "},
            {"coupon_code": None},
            {"coupon_code": "123"},
            {"coupon_code": "A" * 1000},
            {"coupon_code": "' OR '1'='1"},
            {"coupon_code": {"$ne": None}},
        ]
        
        for payload in bypass_payloads:
            response = authenticated_community_client.post(
                "/community/api/v2/coupon/validate-coupon",
                json_data=payload,
                with_auth=True
            )
            
            if response.status_code == 200:
                bypass_vulnerabilities.append(f"Coupon bypass: {payload}")
        
        assert len(bypass_vulnerabilities) == 0, \
            f"Coupon bypass vulnerabilities: {bypass_vulnerabilities}"
    
    def test_create_coupon_mass_assignment(self, authenticated_community_client,
                                          mass_assignment_payloads):
        """
        Challenge: Tentar criar cupom gratuito ou com desconto alto
        
        Expected: Extra fields should be ignored/rejected
        """
        mass_assignment_vulnerabilities = []
        
        base_payload = {
            "code": "TEST123",
            "discount": 10
        }
        
        for extra_field in mass_assignment_payloads:
            payload = {**base_payload, **extra_field}
            response = authenticated_community_client.post(
                "/community/api/v2/coupon/new-coupon",
                json_data=payload,
                with_auth=True
            )
            
            if response.status_code == 200:
                if response.json().get("discount") != 10:  # Verify discount wasn't modified
                    mass_assignment_vulnerabilities.append(
                        f"Mass assignment on coupon discount: {response.json().get('discount')}"
                    )
        
        assert len(mass_assignment_vulnerabilities) == 0, \
            f"Coupon mass assignment vulnerabilities: {mass_assignment_vulnerabilities}"


class TestCommunityRateLimitFuzzing:
    """Testes para rate limiting"""
    
    def test_excessive_requests(self, authenticated_community_client):
        """
        Challenge 6: Teste de DoS via requests excessivos
        """
        import threading
        import time
        
        # Fazer múltiplas requisições
        responses = []
        
        def make_request():
            response = authenticated_community_client.get(
                "/community/api/v2/community/posts/recent",
                with_auth=True
            )
            responses.append(response.status_code)
        
        threads = []
        for _ in range(50):
            thread = threading.Thread(target=make_request)
            thread.start()
            threads.append(thread)
        
        for thread in threads:
            thread.join()
        
        # Verificar se houve rate limiting
        too_many_requests = sum(1 for r in responses if r == 429)
        if too_many_requests == 0:
            logger.warning("⚠️ Nenhuma resposta 429 (Too Many Requests) detectada")
    
    def test_rate_limit_bypass_headers(self, authenticated_community_client):
        """Tentar bypass de rate limiting com headers"""
        bypass_headers = [
            {"X-Forwarded-For": "127.0.0.1"},
            {"X-Client-IP": "127.0.0.1"},
            {"X-Real-IP": "127.0.0.1"},
            {"CF-Connecting-IP": "127.0.0.1"},
        ]
        
        for _ in range(10):  # Múltiplas requisições
            response = authenticated_community_client.session.get(
                f"{authenticated_community_client.base_url}/community/api/v2/community/posts/recent",
                headers={
                    **authenticated_community_client.get_headers(),
                    **bypass_headers[0]
                },
                timeout=10
            )
            
            if response.status_code == 429:
                logger.info("Rate limit detectado")
