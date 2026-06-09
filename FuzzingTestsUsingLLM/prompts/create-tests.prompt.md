# IA Especializada em Fuzz Testing para APIs REST

Você já analisou previamente a documentação, arquitetura e estrutura do repositório.

Agora seu objetivo é identificar, criar e integrar testes de fuzzing para APIs REST existentes no projeto.

---

# Objetivo Principal

Criar uma estratégia de fuzz testing para as APIs REST do repositório, cobrindo:

- testes genéricos automatizados;
- entradas inválidas;
- entradas malformadas;
- valores extremos;
- payloads inesperados;
- exploração de edge cases;
- pontos críticos da aplicação;
- possíveis vulnerabilidades;
- falhas de validação;
- problemas de estabilidade.

O objetivo é aumentar a robustez, segurança e confiabilidade da aplicação.

---

# Fase 1 — Descoberta das APIs

Primeiro:

1. Localize todas as APIs REST do projeto.
2. Identifique:
   - rotas;
   - métodos HTTP;
   - payloads esperados;
   - autenticação;
   - middlewares;
   - validações;
   - schemas;
   - integrações externas.

Mapeie:

- endpoints públicos;
- endpoints autenticados;
- endpoints administrativos;
- uploads;
- filtros;
- paginação;
- buscas;
- operações críticas.

---

# Fase 2 — Identificação de Pontos Críticos

Após mapear as APIs, identifique endpoints potencialmente críticos.

Priorize APIs que envolvam:

- autenticação;
- autorização;
- upload de arquivos;
- manipulação financeira;
- persistência de dados;
- queries complexas;
- execução assíncrona;
- processamento pesado;
- serialização/deserialização;
- parsing;
- filtros dinâmicos;
- geração de relatórios;
- importação/exportação;
- integrações externas;
- operações destrutivas;
- concorrência;
- manipulação de permissões.

Também procure:

- ausência de validação;
- validações inconsistentes;
- trust excessivo no client;
- uso perigoso de parâmetros;
- possíveis gargalos;
- endpoints sem rate limit;
- uso inseguro de parsing JSON/XML;
- comportamento indefinido para entradas inválidas.

---

# Fase 3 — Criação de Fuzz Tests Genéricos

Crie fuzz tests reutilizáveis para APIs REST.

Os testes devem tentar:

- strings extremamente grandes;
- caracteres especiais;
- Unicode inválido;
- JSON malformado;
- tipos inesperados;
- números extremos;
- arrays gigantes;
- objetos profundamente aninhados;
- payloads vazios;
- campos ausentes;
- campos extras;
- valores null;
- payloads aleatórios;
- combinações inesperadas de parâmetros;
- headers inválidos;
- query params inválidos;
- tokens corrompidos;
- formatos incorretos;
- boundary values.

Os testes devem verificar:

- crashes;
- exceptions não tratadas;
- timeouts;
- memory leaks aparentes;
- respostas inconsistentes;
- falhas 500;
- stack traces expostos;
- comportamento inesperado;
- corrupção de estado;
- falhas de autenticação/autorização.

---

# Fase 4 — Fuzzing Direcionado para Pontos Críticos

Além dos testes genéricos, crie fuzz tests específicos para endpoints críticos identificados.

Os testes devem explorar:

## Autenticação

- tokens inválidos;
- JWTs malformados;
- expiração;
- bypass;
- headers manipulados.

---

## Uploads

- arquivos gigantes;
- extensões inválidas;
- MIME incorreto;
- conteúdo corrompido;
- payloads binários inesperados.

---

## Banco de Dados

- filtros inesperados;
- injeções;
- payloads complexos;
- queries degenerativas;
- paginação extrema.

---

## Parsing

- JSON profundamente aninhado;
- estruturas circulares;
- payloads truncados;
- encoding inválido.

---

## Concorrência

- múltiplas requisições simultâneas;
- race conditions;
- duplicação de requests;
- retries inesperados.

---

# Regras Importantes

## Respeitar a Stack do Projeto

Utilize as ferramentas e frameworks já presentes no repositório sempre que possível.

Exemplos:

- Jest
- Vitest
- Pytest
- Supertest
- Cypress
- Playwright
- REST Assured
- Hypothesis
- fast-check
- AFL wrappers
- fuzzing nativo da linguagem

---

## Manter Consistência Arquitetural

Os testes devem seguir:

- estrutura existente;
- convenções do projeto;
- organização atual de testes;
- padrões de nomenclatura.

---

## Evitar Testes Desnecessariamente Destrutivos

Não gerar:

- loops infinitos;
- ataques reais;
- negação de serviço agressiva;
- cargas perigosas para ambientes produtivos.

Os fuzz tests devem ser seguros para ambiente de desenvolvimento e CI.

---

# Estrutura Esperada dos Testes

Os testes devem:

- ser reutilizáveis;
- possuir boa cobertura;
- ter logs claros;
- identificar facilmente o endpoint problemático;
- permitir reprodução do erro;
- ser parametrizados quando possível.

---

# Resultado Esperado

Ao finalizar:

1. Gere fuzz tests genéricos para APIs REST.
2. Gere fuzz tests especializados para pontos críticos.
3. Explique:
   - quais endpoints foram priorizados;
   - quais riscos foram identificados;
   - quais estratégias de fuzzing foram usadas.
4. Aponte possíveis fragilidades descobertas.
5. Sugira melhorias de validação e segurança quando apropriado.

---

# Regras de Análise

Durante a implementação:

- não assuma validações inexistentes;
- leia o código antes de testar;
- identifique comportamentos implícitos;
- respeite autenticação existente;
- considere edge cases reais;
- considere limitações da infraestrutura.

---

# Início da Execução

Comece agora:

1. localizando todas as APIs REST;
2. identificando endpoints críticos;
3. analisando validações existentes;
4. criando fuzz tests genéricos;
5. criando fuzz tests especializados para pontos sensíveis do sistema.

---

# LOCAL DOS TESTES

pasta "./../tests"