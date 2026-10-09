# ADR 004 — Regras explícitas sem IA no produto

Data do registro: 09/10/2026. Estado: decisão já implementada, documentada retrospectivamente; ratificação da equipe pendente. Preparação: agente sob orientação de Rafael, issue #3. Não atribui aprovação prévia a Daniel.

## Contexto

Sorteio, classificação e avanço precisam de decisões verificáveis, com dados disponíveis durante o semestre. O projeto não precisa analisar linguagem natural ou depender de dados pagos/externos.

## Decisão

Usar código explícito para pareamento, pontuação e transições; não chamar LLM ou API Riot no produto. Embaralhamento é aleatório em uso normal e recebe gerador controlado nos testes. Usar agente somente como apoio ao desenvolvimento, com validação e revisão humana.

## Consequências

Regras são explicáveis e testáveis sem respostas probabilísticas externas. Rank é autodeclarado, e o equilíbrio é aproximação. O uso de agente para programar não é um componente de IA do sistema e não aciona o requisito de saída estruturada de LLM do domínio (§6.5). Uma futura integração exigirá nova análise, spec, ADR e testes.

## Rastreabilidade

RN04–RN12, RF06–RF15; enunciado §6.5; plan.md P02–P05. Consulte [spec.md](../../spec.md), [plan.md](../../plan.md) e a [revisão](../review/README.md). Mudança nesta decisão demanda novo ADR que indique qual substitui.
