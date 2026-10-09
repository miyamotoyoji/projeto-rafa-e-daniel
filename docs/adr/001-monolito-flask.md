# ADR 001 — Monólito Flask e páginas no servidor

Data do registro: 09/10/2026. Estado: decisão já implementada, documentada retrospectivamente; ratificação da equipe pendente. Preparação: agente sob orientação de Rafael, issue #3. Não atribui aprovação prévia a Daniel.

## Contexto

Uma equipe de estudo precisa demonstrar regras, persistência e interface com execução local simples. Uma aplicação distribuída ou uma SPA adicionaria infraestrutura e contratos desnecessários para 16/32 jogadores.

## Decisão

Usar Python/Flask para rotas e HTML/Jinja, CSS e JavaScript de apoio. Manter regras em tournament.py e persistência em storage.py, separadas da aplicação web. O código na raiz é o equivalente de src permitido pelo enunciado.

## Consequências

Instalação pequena, testes das regras sem servidor e formulários funcionais sem JavaScript. Em contrapartida, a interface recarrega páginas e não oferece atualizações em tempo real; a implantação é uma unidade única. Uma SPA foi considerada desnecessária para este escopo. Evidências: app.py, tournament.py, storage.py e templates/.

## Rastreabilidade

RF01–RF20, RNF07; plan.md P02–P03. Consulte [spec.md](../../spec.md), [plan.md](../../plan.md) e a [revisão](../review/README.md). Mudança nesta decisão demanda novo ADR que indique qual substitui.
