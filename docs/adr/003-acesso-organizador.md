# ADR 003 — Participação pública e acesso restrito à organização

Data do registro: 09/10/2026. Estado: decisão já implementada, documentada retrospectivamente; ratificação da equipe pendente. Preparação: agente sob orientação de Rafael, issue #3. Não atribui aprovação prévia a Daniel.

## Contexto

Jogadores precisam de inscrição simples; apenas a organização deve alterar sorteio, placares e fases. Riot ID não deve aparecer nas listas públicas. A equipe solicitou inscrição sem criação de conta.

## Decisão

Não criar contas para jogadores. Configurar uma credencial de organização via comando local, armazenar hash, usar sessão assinada com versão de credencial, CSRF nos POSTs e limitação de falhas por endereço. Publicar nomes e ranks; restringir Riot IDs ao painel.

## Consequências

Reduz esforço de cadastro e separa permissões. Não comprova posse da conta Riot ou rank; outra pessoa pode tentar inscrever um ID alheio. Há somente um organizador e nenhuma atribuição de ações a múltiplos administradores. Bloqueio por endereço pode afetar pessoas na mesma rede; publicação com proxy exige análise. Evidências: app.py, tests/test_app.py. Não existem senhas padrão no produto.

## Rastreabilidade

RF03–RF05, RF18–RF20, RNF03–RNF06, RN13; plan.md P03. Consulte [spec.md](../../spec.md), [plan.md](../../plan.md) e a [revisão](../review/README.md). Mudança nesta decisão demanda novo ADR que indique qual substitui.
