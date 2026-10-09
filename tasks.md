# Tarefas atômicas e rastreabilidade

Derivadas de [spec.md](spec.md) e [plan.md](plan.md). Preparação atual: [issue #3](https://github.com/miyamotoyoji/projeto-rafa-e-daniel/issues/3), prioridade P1, Rafael com apoio do agente. A aprovação por outro integrante permanece aberta. `Implementado` descreve o produto; `concluído` no processo exige evidência e revisão.

## Baseline implementada, anterior à issue #3

Não existem issues retroativas que comprovem essas entregas. Evidência histórica: commits da aplicação até `6240c95` e [execução de testes após limpeza](https://github.com/miyamotoyoji/projeto-rafa-e-daniel/actions/runs/37935473904).

| ID | Tarefa verificável | Spec | Plano | Evidência existente |
| --- | --- | --- | --- | --- |
| B01 | Criar campeonato apenas com 8/16 duplas | RF01–RF02 | P02 | `test_only_supported_sizes`, `test_wrong_action_preserves_data` |
| B02 | Validar inscrição e duplicata | RF03–RF04 | P02 | `test_registration_validation`, `test_registration_and_privacy` |
| B03 | Remover jogador preservando IDs únicos | RF05 | P02 | `test_player_removal_preserves_unique_ids` |
| B04 | Sortear pares e seis partidas por grupo | RF06–RF08 | P02 | `test_balanced_pairs_and_groups` |
| B05 | Salvar/corrigir placar e recalcular tabela | RF09–RF11 | P02 | `test_invalid_score_does_not_change_match`, `test_corrections_recalculate_standings` |
| B06 | Avançar classificados até o campeão | RF12–RF15 | P02 | `test_full_championship_both_sizes` |
| B07 | Renderizar páginas vazias e públicas | RF16–RF17 | P03 | `test_all_empty_pages_render`, `test_complete_http_journey` |
| B08 | Proteger entrada, ações e saída | RF18–RF20 | P03 | `test_csrf_and_organizer_permission`, `test_login_rate_limit_and_logout` |
| B09 | Persistir e limitar última vaga | RNF01–RNF02 | P02 | `test_persistence_and_atomic_last_slot` |
| B10 | Proteger formulários, credenciais e HTML | RNF03–RNF06, RNF08 | P03–P04 | Testes listados em docs/TESTES.md |
| B11 | Conferir apresentação no celular | RNF07 | P04 | Registro manual em docs/VALIDACAO.md |

## Adequação documental — issue #3

Responsável pela preparação: Rafael com apoio do agente. Revisor sugerido: Daniel, a confirmar. Prioridade de todos os itens: P1. Cada item pode ser verificado independentemente no PR.

- [x] D01 — Substituir SPECS.md por `spec.md`, com personas e RN01–RN13. Aceite: domínio separado de decisões técnicas. Spec §§1–3; P05.
- [x] D02 — Escrever RF01–RF20 e RNF01–RNF08 em EARS. Aceite: condição/evento/resposta identificáveis e IDs estáveis. Spec §4; P05.
- [x] D03 — Modelar backlog, casos de uso e domínio/estados em texto. Aceite: UC01–UC07 e diagramas coerentes com as regras. Spec §§5–7; P05.
- [x] D04 — Criar `plan.md` com componentes, fluxo de dados e etapas. Aceite: cada módulo vinculado à spec; P05.
- [x] D05 — Registrar quatro ADRs retrospectivos. Aceite: contexto, decisão, consequências e estado de revisão em cada um; P05.
- [x] D06 — Mapear requisito para código e testes existentes. Aceite: nenhuma lacuna apresentada como teste realizado; docs/TESTES.md; P04–P05.
- [x] D07 — Registrar revisão multidimensional. Aceite: evidência, efeito, ação e situação por achado; docs/review; P05.
- [x] D08 — Documentar segurança/SSDLC. Aceite: limites de acesso, dados, controles e próximos passos explícitos; docs/SEGURANCA.md; P05.
- [x] D09 — Criar `.specify` e índice de documentação. Aceite: links locais válidos e README apontando para os nomes canônicos; P05.
- [ ] D10 — Revisar o PR por outro integrante. Aceite: revisão real no GitHub e correção das solicitações antes do merge; P06.
- [ ] D11 — Confirmar divisão de tarefas e operar Kanban semanalmente. Aceite: issues próprias e movimentação dos quatro estados; P06–P07.
- [ ] D12 — Ensaiar a entrega. Aceite: cada integrante executa e explica sua parte, com evidência no repositório; P07.

Itens D01–D09 marcados significam preparação dos arquivos; a issue só deve ser concluída após revisão humana. Abertura de PR ou marcação de checklist pelo agente não substitui participação individual.

## Próximas tarefas de qualidade — proposta, não executadas

Abrir uma issue individual antes de iniciar cada item abaixo, com responsável confirmado; prioridade P2, salvo decisão da equipe. Divisão sugerida ainda não aceita pelos dois.

| ID | Tarefa | Responsável proposto | Critério de aceite | Rastreabilidade |
| --- | --- | --- | --- | --- |
| Q01 | Testar desempate por rounds feitos com pontos e saldo iguais | Daniel | Fixture força o terceiro critério e verifica ordem | RN07, RF11; revisão R02 |
| Q02 | Testar erro de partida inexistente | Daniel | Recusa preserva todos os resultados | RF10; revisão R02 |
| Q03 | Testar expiração da janela de bloqueio de login | Rafael | Tempo controlado libera nova tentativa após janela | RNF05; revisão R02 |
| Q04 | Testar privacidade em todas as páginas públicas depois do sorteio | Rafael | Nenhuma resposta pública contém o Riot ID usado no teste | RF17, RN13; revisão R02 |
| Q05 | Ensaiar backup e restauração de uma cópia de teste | Daniel | Nova cópia mantém inscrições, fase e placares | RNF01; revisão R04 |
| Q06 | Definir requisitos de auditoria antes de implementar logs de placar | Ambos | Nova spec/ADR define evento, dados mínimos e retenção | revisão R03; melhoria fora da baseline |

## Convenção de fluxo

A fazer → Em andamento → Em revisão → Concluído. Concluído exige aceite, evidência e revisão humana quando houver PR. Usar IDs das tarefas e requisitos na descrição da issue/PR; não alterar datas nem criar commits em nome do colega. A lista não inventa conclusão de tarefas futuras nem participação anterior.
