# Documentação do projeto

Projeto final de Modelagem de Software, semestre 2026-2, turma 04G. Tema: organização de campeonatos amadores de Valorant 2 contra 2.

## Leitura principal

1. [spec.md](../spec.md): fonte de verdade, personas, EARS, regras, backlog, casos de uso e modelos textuais.
2. [plan.md](../plan.md): arquitetura, dados, etapas e proposta de divisão de trabalho.
3. [tasks.md](../tasks.md): tarefas atômicas, evidências e pendências.
4. [Conformidade com o enunciado](CONFORMIDADE.md): requisitos acadêmicos e situação real.

## Decisões e qualidade

- [ADR 001 — Monólito Flask](adr/001-monolito-flask.md).
- [ADR 002 — SQLite e agregado JSON](adr/002-sqlite-agregado.md).
- [ADR 003 — Acesso de organização](adr/003-acesso-organizador.md).
- [ADR 004 — Sem IA no produto](adr/004-sem-ia-no-produto.md).
- [Revisão multidimensional](review/README.md): arquitetura, performance, segurança e observabilidade.
- [Segurança e SSDLC](SEGURANCA.md).
- [Estratégia de testes e rastreabilidade](TESTES.md).
- [Validação anterior da interface](VALIDACAO.md).
- [Roteiro de apresentação](APRESENTACAO.md).
- [Orientações ao agente](../.specify/README.md).

## Processo e autoria

A [issue #3](https://github.com/miyamotoyoji/projeto-rafa-e-daniel/issues/3) registra esta adequação. O código anterior foi preparado com apoio de agente e enviado em commits diretos; a documentação atual não inventa um fluxo de revisão retroativo. A participação individual de Rafael e Daniel, o uso contínuo de Kanban e a revisão humana precisam de evidências reais.

Fonte de requisitos acadêmicos: `ProjetoFinal_ModelagemDeSoftware_2026-2.pdf`, fornecido por Rafael, seis páginas. O documento do professor não foi republicado no repositório; esta pasta contém a aplicação dos requisitos ao projeto.
