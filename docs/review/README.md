# Revisão multidimensional — 09/10/2026

Preparação por agente, sob orientação de Rafael, issue #3. Base examinada: `6240c95`, mais a documentação desta branch. Métodos: leitura de app.py, storage.py, tournament.py e dos testes; consulta às evidências existentes; execução da suíte nesta adequação. Não houve entrevista, benchmark de carga, auditoria independente ou revisão de outro integrante nesta etapa.

## Achados e ações

| ID | Dimensão | Evidência e impacto | Ação e situação |
| --- | --- | --- | --- |
| R01 | Arquitetura/especificação | SPECS.md não usava EARS e faltavam plan.md, ADRs e modelo textual; isso impede rastreabilidade exigida pelo enunciado | Preparados spec.md canônico, plan.md, tasks.md, quatro ADRs e matriz de testes. Resolvido na preparação documental; aguarda revisão humana |
| R02 | Qualidade transversal | Os testes exercitam fluxo completo, mas test_points_and_tie_order não isola o terceiro desempate; não há teste específico de partida inexistente, expiração do bloqueio ou privacidade em todas as páginas após sorteio | Lacunas explicitadas; Q01–Q04 propostas em tasks.md. Aberto, sem alegação de cobertura completa |
| R03 | Observabilidade | app.py::database_error registra exceção de banco e responde 503; não há log de quem alterou placar, valor anterior/novo, métricas ou identificador de correlação | Documentado o estado atual. Definir requisito de auditoria antes de codificar (Q06). Aberto; não tratado como funcionalidade existente |
| R04 | Operação/segurança | README orienta backup de instance/ com servidor parado, mas não há evidência de ensaio de restauração por integrante | Q05 proposta. Preservar credenciais fora de Git e testar em cópia descartável. Aberto |
| R05 | Performance | app.py::login executa check_password_hash dentro de storage.transaction; BEGIN IMMEDIATE mantém trava de escrita enquanto calcula hash | Registrar limite; medir contenção antes de hospedagem concorrente e avaliar leitura fora da trava com revalidação. Não alterado nesta entrega |
| R06 | Performance/arquitetura | render() recalcula tabelas em todas as páginas; storage.save regrava JSON inteiro | Compatível em dimensão com máximo de 32 jogadores, mas sem benchmark. ADR 002 explicita limite; não prometer SLA ou escala não medida |
| R07 | Segurança | CSRF, protected, escape Jinja e parâmetros SQL estão presentes; testes cobrem parte desses controles | Preservar e documentar em SEGURANCA.md. Verificado por leitura/testes indicados; não significa auditoria de segurança completa |
| R08 | Processo | Entregas anteriores foram commits diretos, sem issues e PRs correspondentes; ausência de evidência de revisão de colega | Issue #3 e branch iniciam o processo atual. PR deve aguardar revisão real. Histórico anterior preservado; pendência de participação não encerrada por documentação |

## Parecer para esta entrega

A mudança é documental: nenhum comportamento do campeonato foi alterado. A baseline atende aos quatro aspectos de domínio do enunciado: perfis distintos, persistência, fluxo com estados e regras explícitas. Ainda há pendências de processo acadêmico e de testes direcionados. Não declarar conformidade integral até revisão, validação da equipe e evidências individuais.

## Como registrar a revisão humana

O revisor registra no PR os requisitos conferidos, os testes/fluxos que executou e as correções solicitadas. Atualizar esta página com a data e o link da revisão real. Não preencher nome, aprovação ou execução em nome do colega. Tarefas: D10–D12 em [tasks.md](../../tasks.md).
