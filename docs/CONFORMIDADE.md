# Conformidade com o enunciado de Modelagem de Software

Fonte: `ProjetoFinal_ModelagemDeSoftware_2026-2.pdf`, seis páginas, fornecido por Rafael. Conferência em 09/10/2026. Os números abaixo referem-se às seções do PDF; critérios e pesos apresentados em aula não constam no arquivo e precisam ser conferidos pela equipe.

## Matriz de atendimento

| Exigência | Evidência/ação | Situação |
| --- | --- | --- |
| §§1, 5 — Problema real e tema aprovado | spec.md §§1–2; Rafael confirmou aprovação pelo professor | Tema aprovado por relato do integrante; personas são hipóteses, não entrevistas |
| §4 — Até três integrantes e participação visível | Rafael e Daniel; proposta em plan.md | Dupla definida; participação individual contínua ainda exige evidências próprias |
| §6.1 — Dois perfis | Participante público e organizador autenticado, com permissões distintas | Implementado; ausência de conta de jogador é explícita |
| §6.2 — Persistência | SQLite e teste de reabertura | Implementado |
| §6.3 — Fluxo não trivial | Inscrição, pareamento, grupos, classificação, mata-mata e campeão | Implementado |
| §6.4 — Regras explícitas | RN01–RN13 em spec.md | Documentado |
| §6.5 — IA estruturada quando usada no produto | ADR 004: produto não usa IA/LLM | Não aplicável ao produto; agente auxilia desenvolvimento |
| §7 — README, EARS, personas, backlog, casos de uso e domínio | README.md; spec.md; diagramas Mermaid versionados | Preparados; revisão humana pendente |
| §§7–8 — Plano, tarefas e 3 a 5 ADRs | plan.md, tasks.md e quatro registros em docs/adr | Preparados retrospectivamente; ratificação pendente |
| §7 — Revisão multidimensional e SSDLC | docs/review/README.md e docs/SEGURANCA.md | Leitura e registro realizados; achados abertos explícitos |
| §7 — Estratégia e evidências de testes | docs/TESTES.md, testes e CI | Evidências reais; lacunas específicas documentadas |
| §9.1 — docs, src ou equivalente, tests e .specify | docs/, tests/, .specify/; módulos Python na raiz equivalem a src | Estrutura documentada; não há obrigação de renomear a raiz |
| §9.2 — Issues com responsável, prioridade e aceite | Issue #3 registra esta preparação | Adotado para a entrega atual; não corrige ausência histórica |
| §9.2 — Project/Kanban com quatro estados | A fazer, Em andamento, Em revisão, Concluído | Quadro criado na conta de Rafael, issue #3 em revisão; manutenção semanal e acesso de edição de Daniel pendentes |
| §§9.2, 9.5 — Distribuição equilibrada e progresso semanal | Proposta em plan.md; D11–D12 | Pendente de confirmação e trabalho real dos dois |
| §9.3 — Branch, PR e revisão por colega | Branch codex/adequacao-modelagem; PR vinculado à issue #3 | Entrega preparada para revisão; não integrar antes da revisão humana |
| §9.4 — Referências issue/commit/PR e agente | Issue #3, IDs em tasks.md e .specify/README.md | A partir desta adequação; MCP é opcional no enunciado |
| §§10–11 — Coerência e produto funcional | Matriz em docs/TESTES.md, ADRs e app | Revisão final da equipe e avaliação do professor ainda necessárias |

## Kanban

[DOIS — Projeto Final de Modelagem](https://github.com/users/rcosta2702/projects/1) é um Project público na conta de Rafael, com os quatro estados e a issue #3 em revisão. O seletor de vínculo na aba Projects do repositório de miyamotoyoji não ofereceu esse quadro de outra conta; o acesso é pelo link. Daniel pode consultar o quadro público; seu acesso de edição ainda precisa ser configurado. Não houve convite enviado em nome de Rafael.

## O que não pode ser fabricado

Não transformar uploads antigos em supostos PRs revisados; não inventar issues antigas, entrevistas, aprovação do colega ou commits feitos por ele. O histórico atual mostra contribuições técnicas com apoio de agente, mas a avaliação exige demonstração de entendimento e participação de cada integrante.

## Próxima revisão humana

1. Confirmar personas/regras e a proposta de divisão.
2. Conferir spec, código e os achados da revisão; executar o projeto em uma cópia de teste.
3. Registrar revisão do PR com os testes realmente executados, solicitar ajustes e integrar após resolução.
4. Manter issues próprias no Project e apresentar os próprios commits durante os checkpoints.

O repositório não deve ser apresentado como integralmente conforme só porque os arquivos existem. Processo colaborativo é evidência de trabalho contínuo, não um checklist preenchido pelo agente.
