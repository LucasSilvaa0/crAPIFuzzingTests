#!/usr/bin/env python3
"""
Script de execução de testes de fuzzing para crAPI
Demonstra como usar a suíte de fuzzing
"""

import subprocess
import sys
import os
from pathlib import Path


class FuzzingExecutor:
    """Executor para testes de fuzzing do crAPI"""
    
    def __init__(self):
        self.test_dir = Path(__file__).parent
        self.results_dir = self.test_dir / "results"
        self.results_dir.mkdir(exist_ok=True)
    
    def run_command(self, cmd, description):
        """Executa comando e monitora resultado"""
        print(f"\n{'='*80}")
        print(f"🚀 {description}")
        print(f"{'='*80}")
        print(f"Executando: {' '.join(cmd)}\n")
        
        result = subprocess.run(cmd)
        
        if result.returncode != 0:
            print(f"\n❌ Falha em: {description}")
            return False
        
        print(f"\n✅ Sucesso em: {description}")
        return True
    
    def check_requirements(self):
        """Verifica se dependências estão instaladas"""
        print("🔍 Verificando dependências...")
        
        required = ["pytest", "requests", "hypothesis"]
        missing = []
        
        for pkg in required:
            try:
                __import__(pkg)
                print(f"  ✅ {pkg}")
            except ImportError:
                missing.append(pkg)
                print(f"  ❌ {pkg}")
        
        if missing:
            print(f"\n⚠️ Instalar dependências faltantes:")
            print(f"pip install -r requirements.txt")
            return False
        
        return True
    
    def run_all_tests(self):
        """Executa todos os testes"""
        cmd = [
            "pytest",
            "-v",
            "--tb=short",
            "--html=results/report.html",
            f"--log-file=results/fuzzing_results.log"
        ]
        return self.run_command(cmd, "Executando todos os testes")
    
    def run_tests_by_service(self, service):
        """Executa testes de um serviço específico"""
        file_map = {
            "workshop": "fuzzing_workshop.py",
            "identity": "fuzzing_identity.py",
            "community": "fuzzing_community.py",
            "chatbot": "fuzzing_chatbot.py",
        }
        
        if service not in file_map:
            print(f"❌ Serviço desconhecido: {service}")
            print(f"Opções: {', '.join(file_map.keys())}")
            return False
        
        cmd = [
            "pytest",
            "-v",
            "-m", service,
            file_map[service],
            f"--log-file=results/fuzzing_{service}.log"
        ]
        
        return self.run_command(
            cmd,
            f"Executando testes do serviço: {service}"
        )
    
    def run_critical_tests(self):
        """Executa apenas endpoints críticos"""
        cmd = [
            "pytest",
            "-v",
            "-m", "critical",
            "--tb=short",
            "--log-file=results/critical_tests.log"
        ]
        return self.run_command(cmd, "Executando testes de endpoints críticos")
    
    def run_injection_tests(self):
        """Executa apenas testes de injeção"""
        cmd = [
            "pytest",
            "-v",
            "-m", "injection",
            "--tb=short",
            "--log-file=results/injection_tests.log"
        ]
        return self.run_command(cmd, "Executando testes de injeção")
    
    def run_authorization_tests(self):
        """Executa apenas testes de autorização"""
        cmd = [
            "pytest",
            "-v",
            "-m", "authorization",
            "--tb=short",
            "--log-file=results/authorization_tests.log"
        ]
        return self.run_command(cmd, "Executando testes de autorização (BOLA/BFLA)")
    
    def run_parallel_tests(self, workers=4):
        """Executa testes em paralelo"""
        cmd = [
            "pytest",
            "-v",
            "-n", str(workers),
            "--tb=short",
            "--html=results/parallel_report.html",
            f"--log-file=results/parallel_fuzzing.log"
        ]
        return self.run_command(cmd, f"Executando testes em paralelo ({workers} workers)")
    
    def run_specific_test(self, test_path):
        """Executa um teste específico"""
        cmd = [
            "pytest",
            "-v",
            "-s",
            test_path,
            "--tb=short"
        ]
        return self.run_command(cmd, f"Executando teste específico: {test_path}")
    
    def run_with_coverage(self):
        """Executa com cobertura de código"""
        cmd = [
            "pytest",
            "-v",
            "--cov=fuzzing_generic",
            "--cov-report=html:results/coverage",
            "--cov-report=term",
            "--log-file=results/coverage_test.log"
        ]
        return self.run_command(cmd, "Executando com cobertura de código")
    
    def list_available_tests(self):
        """Lista testes disponíveis"""
        cmd = ["pytest", "--collect-only", "-q"]
        print("\n📋 Testes disponíveis:")
        subprocess.run(cmd)
    
    def print_menu(self):
        """Imprime menu de opções"""
        menu = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                 CRAPI FUZZING TEST SUITE - MENU PRINCIPAL                    ║
╚══════════════════════════════════════════════════════════════════════════════╝

Opções de Execução:

1. Executar TODOS os testes
2. Testes do Workshop Service
3. Testes do Identity Service
4. Testes do Community Service
5. Testes do Chatbot Service
6. Apenas testes CRÍTICOS
7. Apenas testes de INJEÇÃO
8. Apenas testes de AUTORIZAÇÃO
9. Testes em PARALELO (4 workers)
10. Teste ESPECÍFICO (via input)
11. Com COBERTURA de código
12. Listar testes disponíveis
13. Sair

────────────────────────────────────────────────────────────────────────────────
Exemplo: Executar tudo com relatório HTML
  pytest -v --html=results/report.html

Exemplo: Apenas testes críticos do Workshop
  pytest -v -m "workshop and critical" fuzzing_workshop.py

Exemplo: Com seed reproduzível
  pytest -v --hypothesis-seed=12345
────────────────────────────────────────────────────────────────────────────────
"""
        print(menu)
    
    def interactive_menu(self):
        """Menu interativo"""
        while True:
            self.print_menu()
            
            try:
                choice = input("Escolha uma opção (1-13): ").strip()
                
                if choice == "1":
                    self.run_all_tests()
                elif choice == "2":
                    self.run_tests_by_service("workshop")
                elif choice == "3":
                    self.run_tests_by_service("identity")
                elif choice == "4":
                    self.run_tests_by_service("community")
                elif choice == "5":
                    self.run_tests_by_service("chatbot")
                elif choice == "6":
                    self.run_critical_tests()
                elif choice == "7":
                    self.run_injection_tests()
                elif choice == "8":
                    self.run_authorization_tests()
                elif choice == "9":
                    workers = input("Número de workers (default 4): ").strip() or "4"
                    self.run_parallel_tests(int(workers))
                elif choice == "10":
                    test_path = input("Caminho do teste: ").strip()
                    self.run_specific_test(test_path)
                elif choice == "11":
                    self.run_with_coverage()
                elif choice == "12":
                    self.list_available_tests()
                elif choice == "13":
                    print("\n👋 Até logo!")
                    break
                else:
                    print("❌ Opção inválida")
                
                input("\nPressione ENTER para continuar...")
            except KeyboardInterrupt:
                print("\n\n👋 Execução cancelada")
                break
            except Exception as e:
                print(f"❌ Erro: {e}")
                input("\nPressione ENTER para continuar...")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Executor de testes de fuzzing para crAPI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  %(prog)s --all                    # Executar todos os testes
  %(prog)s --service workshop       # Testes do Workshop
  %(prog)s --critical              # Apenas críticos
  %(prog)s --injection             # Apenas injeção
  %(prog)s --parallel 8            # Paralelo com 8 workers
  %(prog)s --coverage              # Com cobertura
  %(prog)s --test fuzzing_identity.py::TestIdentityAuthenticationFuzzing::test_login_with_malformed_credentials
  %(prog)s --interactive           # Menu interativo
        """
    )
    
    parser.add_argument("--all", action="store_true", help="Executar todos os testes")
    parser.add_argument("--service", choices=["workshop", "identity", "community", "chatbot"],
                       help="Executar testes de um serviço específico")
    parser.add_argument("--critical", action="store_true", help="Apenas endpoints críticos")
    parser.add_argument("--injection", action="store_true", help="Apenas testes de injeção")
    parser.add_argument("--authorization", action="store_true", help="Apenas testes de autorização")
    parser.add_argument("--parallel", type=int, metavar="N", help="Executar em paralelo (N workers)")
    parser.add_argument("--coverage", action="store_true", help="Com cobertura de código")
    parser.add_argument("--test", metavar="PATH", help="Teste específico")
    parser.add_argument("--list", action="store_true", help="Listar testes disponíveis")
    parser.add_argument("--interactive", action="store_true", help="Menu interativo")
    parser.add_argument("--check", action="store_true", help="Verificar dependências")
    
    args = parser.parse_args()
    
    executor = FuzzingExecutor()
    
    # Verificar se nenhuma opção foi fornecida
    if not any(vars(args).values()):
        args.interactive = True
    
    # Verificar dependências
    if args.check:
        return 0 if executor.check_requirements() else 1
    
    if args.interactive:
        executor.interactive_menu()
    elif args.all:
        executor.run_all_tests()
    elif args.service:
        executor.run_tests_by_service(args.service)
    elif args.critical:
        executor.run_critical_tests()
    elif args.injection:
        executor.run_injection_tests()
    elif args.authorization:
        executor.run_authorization_tests()
    elif args.parallel:
        executor.run_parallel_tests(args.parallel)
    elif args.coverage:
        executor.run_with_coverage()
    elif args.test:
        executor.run_specific_test(args.test)
    elif args.list:
        executor.list_available_tests()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
