# ADR 002 — SQLite com campeonato em agregado JSON

Data do registro: 09/10/2026. Estado: decisão já implementada, documentada retrospectivamente; ratificação da equipe pendente. Preparação: agente sob orientação de Rafael, issue #3. Não atribui aprovação prévia a Daniel.

## Contexto

Inscrições e resultados devem sobreviver ao reinício e ser compartilhados entre navegadores. É preciso impedir duas inscrições na última vaga. A primeira versão tem um campeonato com no máximo 32 jogadores.

## Decisão

Gravar um agregado JSON na tabela tournament do SQLite. Ler, validar e salvar dentro de BEGIN IMMEDIATE, com commit ou rollback. Guardar credencial e tentativas de login em tabelas próprias. Manter dados em instance/.

## Consequências

Evita um servidor de banco separado e mantém atualizações do campeonato atômicas. O JSON não tem integridade referencial interna imposta pelo banco e não favorece consultas analíticas ou múltiplos torneios. Escritas são serializadas e cada atualização regrava o agregado. Um modelo relacional normalizado passa a ser alternativa se houver expansão de escopo. Evidências: storage.py e test_persistence_and_atomic_last_slot.

## Rastreabilidade

RNF01–RNF02, RN01; plan.md P02. Consulte [spec.md](../../spec.md), [plan.md](../../plan.md) e a [revisão](../review/README.md). Mudança nesta decisão demanda novo ADR que indique qual substitui.
