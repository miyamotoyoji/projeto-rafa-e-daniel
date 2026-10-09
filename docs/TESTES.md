# Estratégia de testes e rastreabilidade

Baseline: 20 testes unittest em [tests/test_tournament.py](../tests/test_tournament.py) e [tests/test_app.py](../tests/test_app.py). Esta suíte cobre regras isoladas e integração HTTP/SQLite com bancos temporários. Não há porcentagem de cobertura medida nem teste de carga.

Execução local: `.venv/Scripts/python.exe -m unittest discover -s tests -v` no Windows; `.venv/bin/python -m unittest discover -s tests -v` no Linux/macOS. O workflow [tests.yml](../.github/workflows/tests.yml) executa a mesma suíte em push e PR. Os dados dos testes são temporários e não modificam o campeonato real.

## Matriz requisito → código → teste → tarefa

Nomes abreviados abaixo são métodos dos dois arquivos de teste. Uma linha demonstra cobertura relevante, não todas as combinações de entradas do requisito.

| Requisitos | Código | Evidência automatizada | Tarefa |
| --- | --- | --- | --- |
| RF01–RF02 | tournament.create; app.admin_action | test_only_supported_sizes; test_wrong_action_preserves_data; test_complete_http_journey | B01 |
| RF03–RF04 | tournament.register; app.signup | test_registration_validation; test_capacity_and_incomplete_draw; test_draw_is_locked_and_signup_closes; test_registration_and_privacy | B02 |
| RF05 | tournament.remove_player | test_player_removal_preserves_unique_ids; test_draw_is_locked_and_signup_closes | B03 |
| RF06–RF07 | tournament.draw | test_balanced_pairs_and_groups | B04 |
| RF08 | tournament.draw | test_capacity_and_incomplete_draw; test_draw_is_locked_and_signup_closes; test_wrong_action_preserves_data | B04 |
| RF09 | tournament.set_score | test_corrections_recalculate_standings; test_complete_http_journey | B05 |
| RF10 | tournament.set_score; app.admin_action | test_invalid_score_does_not_change_match; test_full_championship_both_sizes; falta teste específico de ID inexistente | B05, Q02 |
| RF11 | tournament.standings | test_points_and_tie_order; test_corrections_recalculate_standings; falta isolar terceiro desempate | B05, Q01 |
| RF12–RF15 | tournament.advance | test_full_championship_both_sizes; test_complete_http_journey; test_wrong_action_preserves_data | B06 |
| RF16 | app.render; templates | test_all_empty_pages_render | B07 |
| RF17 | páginas públicas; template admin | test_registration_and_privacy; test_complete_http_journey; privacidade pós-sorteio em todas as páginas ainda não isolada | B07, Q04 |
| RF18–RF20 | app.login/protected/logout | test_csrf_and_organizer_permission; test_login_rate_limit_and_logout; test_admin_command | B08 |
| RNF01–RNF02 | storage.transaction/read/save | test_persistence_and_atomic_last_slot | B09, Q05 |
| RNF03 | app.protect_forms | test_csrf_and_organizer_permission | B10 |
| RNF04 | app.init_admin; Werkzeug | test_admin_command verifica credencial configurada e login; armazenamento hash também conferido por leitura, sem teste de algoritmo específico | B10 |
| RNF05 | app.login; login_attempt | test_login_rate_limit_and_logout; expiração da janela ainda não isolada | B10, Q03 |
| RNF06 | app.is_organizer/init_admin | test_password_change_invalidates_session | B10 |
| RNF07 | templates; static/style.css | Evidência manual em VALIDACAO.md; não há teste visual automatizado versionado | B11 |
| RNF08 | Jinja; app.headers | test_html_escaping | B10 |

## Regras e critérios de aceite

CA01/CA03: jornadas completas e teste de sorteio nos dois tamanhos. CA02/CA04: entradas inválidas, avanço incompleto, correção e bloqueio de fases. CA05/CA07: permissão, privacidade de inscrição, CSRF, escape e revogação. CA06: nova instância da aplicação sobre o mesmo banco e disputa da última vaga. CA08: verificação manual registrada. Testes existentes não esgotam todos os limites de tamanho de nome, combinações de desempate ou cenários operacionais.

O teste de equilíbrio usa ranks de uma fixture específica e afirma diferença de força de no máximo 1 nessa fixture. Isso não é garantia universal do produto para qualquer distribuição de ranks.

## Evidências e reprodução

- A [execução de CI após a limpeza](https://github.com/miyamotoyoji/projeto-rafa-e-daniel/actions/runs/37935473904) passou; corresponde ao commit `09c7733`, anterior à adequação documental.
- A execução local desta adequação será registrada em `docs/review/testes-2026-10-09.txt`; o arquivo contém o resultado real do comando, sem senhas ou dados do campeonato.
- A CI do PR é a evidência correspondente à versão proposta; consultar os checks antes da integração.
- [VALIDACAO.md](VALIDACAO.md) descreve o ensaio visual anterior. Não existem capturas desse ensaio versionadas no repositório; não tratá-lo como nova execução por Rafael ou Daniel.

## Estratégia para mudanças

Executar primeiro os testes das regras afetadas e a suíte completa antes de integrar mudança funcional. Para interface, conferir estados vazio, preenchido, erro e telas pequenas. Para documentação, validar links/IDs e correspondência com código; não criar testes que apenas repitam texto. Q01–Q05 são melhorias propostas com aceite próprio em [tasks.md](../tasks.md).
