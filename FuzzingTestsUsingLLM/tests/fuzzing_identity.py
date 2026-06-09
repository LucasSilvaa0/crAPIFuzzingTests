"""
Testes de fuzzing especializados para Identity Service
Fase 4: Fuzzing Direcionado - Autenticação e JWT
"""
import pytest
import json
import logging
from fuzzing_generic import GenericFuzzTester

logger = logging.getLogger(__name__)


class TestIdentityAuthenticationFuzzing:
    """Testes de fuzzing para vulnerabilidades de autenticação"""
    
    def test_login_with_malformed_credentials(self, identity_client,
                                              authentication_bypass_payloads):
        """
        Teste de login com credenciais malformadas/contornáveis
        Challenge 3: Reset de senha de outro usuário
        
        Expected: Malformed credentials should be rejected
        """
        fuzz_tester = GenericFuzzTester(
            identity_client,
            "/identity/api/auth/login",
            method="POST"
        )
        
        auth_bypass_vulnerabilities = []
        
        # Payloads de contorno de autenticação
        for payload in authentication_bypass_payloads:
            result = fuzz_tester.test_with_payload(payload, with_auth=False)
            
            if result.response_status == 200:
                # If login succeeds with bypass payload, it's a vulnerability
                if result.response_body and isinstance(result.response_body, dict):
                    if "token" in result.response_body:
                        auth_bypass_vulnerabilities.append(f"Auth bypass: {payload}")
        
        assert len(auth_bypass_vulnerabilities) == 0, \
            f"Authentication bypass vulnerabilities: {auth_bypass_vulnerabilities}"
    
    def test_signup_registration_bypass(self, identity_client):
        """
        Teste de bypass no registro
        
        Expected: Invalid registrations should be rejected
        """
        validation_vulnerabilities = []
        
        # Tentativas de bypass de validação
        signup_payloads = [
            # Email inválido
            ("empty_email", {"email": "", "password": "test123", "name": "test", "number": "123"}),
            ("invalid_email", {"email": "not_email", "password": "test123", "name": "test", "number": "123"}),
            ("admin_email", {"email": "admin@example.com", "password": "test123", "name": "test", "number": "123"}),
            # Password fraca
            ("empty_password", {"email": "test@example.com", "password": "", "name": "test", "number": "123"}),
            ("weak_password", {"email": "test@example.com", "password": "123", "name": "test", "number": "123"}),
            # SQL Injection
            ("sql_injection", {"email": "admin' OR '1'='1", "password": "test123", "name": "test", "number": "123"}),
            # Nome inválido
            ("empty_name", {"email": "test@example.com", "password": "test123", "name": "", "number": "123"}),
            ("huge_name", {"email": "test@example.com", "password": "test123", "name": "A" * 10000, "number": "123"}),
            # Number inválido
            ("empty_number", {"email": "test@example.com", "password": "test123", "name": "test", "number": ""}),
            ("invalid_number", {"email": "test@example.com", "password": "test123", "name": "test", "number": "invalid"}),
        ]
        
        for label, payload in signup_payloads:
            response = identity_client.post(
                "/identity/api/auth/signup",
                json_data=payload,
                with_auth=False
            )
            
            if response.status_code == 200:
                validation_vulnerabilities.append(f"Signup accepted: {label}")
        
        assert len(validation_vulnerabilities) == 0, \
            f"Signup validation vulnerabilities: {validation_vulnerabilities}"


class TestIdentityJWTFuzzing:
    """Testes para vulnerabilidades de JWT"""
    
    def test_jwt_verification_bypass(self, identity_client,
                                    jwt_bypass_payloads):
        """
        Challenge 15: Teste de forjamento de JWT
        Testa diferentes formas de bypass de verificação
        
        Expected: Invalid/forged JWTs should be rejected
        """
        fuzz_tester = GenericFuzzTester(
            identity_client,
            "/identity/api/auth/verify",
            method="POST"
        )
        
        jwt_vulnerabilities = []
        
        for jwt_payload in jwt_bypass_payloads:
            payload = {"token": jwt_payload}
            result = fuzz_tester.test_with_payload(payload, with_auth=False)
            
            if result.response_status == 200:
                if result.response_body and isinstance(result.response_body, dict):
                    # Check if verification claims token is valid
                    if result.response_body.get("valid") or result.response_body.get("verified"):
                        jwt_vulnerabilities.append(f"JWT bypass: {jwt_payload[:50]}")
        
        assert len(jwt_vulnerabilities) == 0, \
            f"JWT bypass vulnerabilities: {jwt_vulnerabilities}"
    
    def test_jwt_manipulation(self, identity_client):
        """
        Teste de manipulação de JWT
        
        Expected: Manipulated tokens should be rejected
        """
        jwt_vulnerabilities = []
        
        # Obter um JWT válido primeiro
        login_response = identity_client.post(
            "/identity/api/auth/login",
            json_data={"email": "test@example.com", "password": "test123"},
            with_auth=False
        )
        
        if login_response.status_code == 200:
            valid_token = login_response.json().get("token")
            
            if valid_token:
                # Manipulações de JWT
                jwt_manipulations = [
                    ("appended_char", valid_token + "x"),
                    ("removed_char", valid_token[:-1]),
                    ("uppercase", valid_token.upper()),
                    ("changed_separator", valid_token.replace(".", "-")),
                    ("removed_parts", valid_token.split(".")[0] + ".payload.signature"),
                    ("algorithm_change", "eyJhbGciOiJub25lIn0." + valid_token.split(".")[1] + ".fake"),
                ]
                
                for label, manipulated_token in jwt_manipulations:
                    payload = {"token": manipulated_token}
                    response = identity_client.post(
                        "/identity/api/auth/verify",
                        json_data=payload,
                        with_auth=False
                    )
                    
                    if response.status_code == 200:
                        if response.json().get("valid") or response.json().get("verified"):
                            jwt_vulnerabilities.append(f"JWT manipulation accepted: {label}")
        
        assert len(jwt_vulnerabilities) == 0, \
            f"JWT manipulation vulnerabilities: {jwt_vulnerabilities}"


class TestIdentityPasswordRecoveryFuzzing:
    """Testes para vulnerabilidades em recuperação de senha"""
    
    def test_forgot_password_enumeration(self, identity_client):
        """
        Challenge 3: Teste de reset de senha de outro usuário
        Enumerar usuários e tentar reset
        
        Expected: Should not reveal whether email exists (consistent response)
        """
        enumeration_vulnerabilities = []
        
        # Emails para testar
        test_emails = [
            "admin@example.com",
            "user@example.com",
            "test@example.com",
            "' OR '1'='1",  # SQL injection
            "admin' --",
            "%",  # Wildcard
        ]
        
        response_codes = {}
        
        for email in test_emails:
            response = identity_client.post(
                "/identity/api/auth/forget-password",
                json_data={"email": email},
                with_auth=False
            )
            response_codes[email] = response.status_code
        
        # Check if responses vary (would indicate enumeration)
        unique_codes = set(response_codes.values())
        if len(unique_codes) > 1:
            enumeration_vulnerabilities.append("Different response codes for valid/invalid emails")
        
        assert len(enumeration_vulnerabilities) == 0, \
            f"User enumeration vulnerabilities: {enumeration_vulnerabilities}"
    
    def test_otp_brute_force(self, identity_client):
        """
        Challenge 3: Teste de brute force de OTP
        
        Expected: OTP validation should have rate limiting or strong entropy
        """
        otp_vulnerabilities = []
        
        # Primeiro fazer forgot-password
        forget_response = identity_client.post(
            "/identity/api/auth/forget-password",
            json_data={"email": "test@example.com"},
            with_auth=False
        )
        
        if forget_response.status_code == 200:
            # Tentar OTPs simples
            simple_otps = [
                "000000",
                "111111",
                "123456",
                "000001",
                "999999",
            ]
            
            for otp in simple_otps:
                response = identity_client.post(
                    "/identity/api/auth/v3/check-otp",
                    json_data={"email": "test@example.com", "otp": otp},
                    with_auth=False
                )
                
                if response.status_code == 200:
                    if response.json().get("valid"):
                        otp_vulnerabilities.append(f"Weak OTP accepted: {otp}")
        
        assert len(otp_vulnerabilities) == 0, \
            f"OTP brute force vulnerabilities: {otp_vulnerabilities}"
    
    def test_otp_timing_attack(self, identity_client):
        """
        Teste de timing attack em validação de OTP
        
        Expected: Timing should be consistent regardless of OTP correctness
        """
        import time
        
        timing_vulnerabilities = []
        
        # OTP correto (hipotético)
        correct_otp = "123456"
        wrong_otp = "000000"
        
        # Medir tempo de resposta (múltiplas tentativas para média)
        correct_times = []
        wrong_times = []
        
        for _ in range(3):
            start = time.time()
            response = identity_client.post(
                "/identity/api/auth/v3/check-otp",
                json_data={"email": "test@example.com", "otp": correct_otp},
                with_auth=False
            )
            correct_times.append(time.time() - start)
            
            start = time.time()
            response = identity_client.post(
                "/identity/api/auth/v3/check-otp",
                json_data={"email": "test@example.com", "otp": wrong_otp},
                with_auth=False
            )
            wrong_times.append(time.time() - start)
        
        # Check if timing difference is significant (>100ms)
        avg_correct = sum(correct_times) / len(correct_times)
        avg_wrong = sum(wrong_times) / len(wrong_times)
        
        if abs(avg_correct - avg_wrong) > 0.1:  # 100ms difference
            timing_vulnerabilities.append(f"Timing attack possible: diff={abs(avg_correct - avg_wrong):.4f}s")
        
        assert len(timing_vulnerabilities) == 0, \
            f"Timing attack vulnerabilities: {timing_vulnerabilities}"


class TestIdentityUserEnumerationFuzzing:
    """Testes para user enumeration"""
    
    def test_dashboard_user_enumeration(self, identity_client):
        """
        Challenge: Enumerar usuários via dashboard
        
        Expected: User data should not be accessible without authentication
        """
        enumeration_vulnerabilities = []
        
        # Tentar acessar dashboard com IDs sequenciais
        user_ids = [1, 2, 3, 100, 999]
        
        for user_id in user_ids:
            response = identity_client.get(
                f"/identity/api/v2/user/{user_id}",
                with_auth=False  # Tentar sem auth primeiro
            )
            
            # Se recebe dados, há enumeration
            if response.status_code == 200:
                enumeration_vulnerabilities.append(f"User {user_id} enumerated without auth")
        
        assert len(enumeration_vulnerabilities) == 0, \
            f"User enumeration vulnerabilities: {enumeration_vulnerabilities}"
    
    def test_profile_endpoint_fuzzing(self, identity_client):
        """
        Fuzzing de endpoint de perfil
        
        Expected: Dashboard should require authentication
        """
        authorization_vulnerabilities = []
        
        # Testes sem autenticação
        response = identity_client.get(
            "/identity/api/v2/user/dashboard",
            with_auth=False
        )
        
        if response.status_code == 200:
            authorization_vulnerabilities.append("Dashboard accessible without authentication")
        
        assert len(authorization_vulnerabilities) == 0, \
            f"Authorization vulnerabilities: {authorization_vulnerabilities}"


class TestIdentityUploadFuzzing:
    """Testes para upload de arquivos"""
    
    def test_profile_upload_bypass(self, authenticated_identity_client):
        """
        Teste de bypass em upload de perfil
        
        Expected: Only valid image files should be accepted
        """
        upload_vulnerabilities = []
        
        # Payloads maliciosos
        malicious_payloads = [
            ("php_extension", {"file": "shell.php"}),
            ("double_extension", {"file": "image.php.jpg"}),
            ("null_byte", {"file": "image.jpg\x00.php"}),
            ("path_traversal", {"file": "../../../etc/passwd"}),
            ("huge_name", {"file": "A" * 10000}),
        ]
        
        for label, payload in malicious_payloads:
            response = authenticated_identity_client.post(
                "/identity/api/v2/user/profile-picture",
                json_data=payload,
                with_auth=True
            )
            
            if response.status_code == 200:
                upload_vulnerabilities.append(f"Upload bypass: {label}")
        
        assert len(upload_vulnerabilities) == 0, \
            f"Upload vulnerabilities: {upload_vulnerabilities}"


class TestIdentityFieldValidationFuzzing:
    """Testes de validação de campos"""
    
    def test_email_field_validation(self, identity_client):
        """
        Teste de validação do campo email
        
        Expected: Invalid emails should be rejected
        """
        validation_vulnerabilities = []
        
        invalid_emails = [
            "",
            " ",
            "not_email",
            "user@",
            "@domain.com",
            "user@domain",
            "user..name@domain.com",
            "user+tag@domain.com",
            "user@domain.123",
            "A" * 100 + "@domain.com",
        ]
        
        for email in invalid_emails:
            payload = {
                "email": email,
                "password": "test123",
                "name": "test",
                "number": "123"
            }
            response = identity_client.post(
                "/identity/api/auth/signup",
                json_data=payload,
                with_auth=False
            )
            
            if response.status_code == 200:
                validation_vulnerabilities.append(f"Invalid email accepted: {email}")
        
        assert len(validation_vulnerabilities) == 0, \
            f"Email validation vulnerabilities: {validation_vulnerabilities}"
    
    def test_phone_field_validation(self, identity_client):
        """
        Teste de validação do campo telefone
        
        Expected: Invalid phone numbers should be rejected
        """
        validation_vulnerabilities = []
        
        invalid_phones = [
            "",
            " ",
            "123",
            "abc",
            "a" * 100,
            "+1234567890",
            "-1234567890",
            "+00000000000",
            "(" + "1" * 50 + ")",
        ]
        
        for phone in invalid_phones:
            payload = {
                "email": "test@example.com",
                "password": "test123",
                "name": "test",
                "number": phone
            }
            response = identity_client.post(
                "/identity/api/auth/signup",
                json_data=payload,
                with_auth=False
            )
            
            if response.status_code == 200:
                validation_vulnerabilities.append(f"Invalid phone accepted: {phone}")
        
        assert len(validation_vulnerabilities) == 0, \
            f"Phone field validation vulnerabilities: {validation_vulnerabilities}"
