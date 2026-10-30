# ADR 005 — Contas de usuário opcionais no SQLite

Data do registro: 30/10/2026. Estado: proposta implementada, ratificação da equipe pendente. Complementa o [ADR 003](003-acesso-organizador.md) na parte "não criar contas para jogadores"; a credencial única do organizador e as demais decisões do ADR 003 continuam valendo.

## Contexto

O sistema só guardava o campeonato (agregado JSON) e uma credencial de organizador. Não havia como armazenar usuários diferentes, nem ligar uma inscrição a uma pessoa. A equipe pediu originalmente inscrição sem conta; essa possibilidade deve continuar existindo.

## Decisão

Criar a tabela `user` (id, username único sem distinção de maiúsculas, nome de exibição, hash de senha, data de criação) no mesmo SQLite. Usuário e organizador são sessões independentes (`session["user"]` e `session["organizer"]`). A conta é opcional: quem estiver autenticado tem a inscrição gravada com `user_id` e limitada a uma por conta; quem não estiver continua se inscrevendo como antes. Senha com 12 a 1024 caracteres, guardada com hash de Werkzeug; limite de cinco falhas em 15 minutos por endereço, em chave separada da do organizador; verificação de hash também para usuário inexistente. Páginas: `/conta/criar`, `/conta/entrar`, `/conta`, `/conta/sair`.

## Consequências

Permite acompanhar inscrição e dupla por conta e abre caminho para papéis e histórico. Aumenta a superfície de segurança: há senhas de terceiros para proteger, e ainda não existem recuperação de senha, troca de senha, confirmação de e-mail nem exclusão de conta. O vínculo `user_id` fica dentro do JSON do campeonato, sem chave estrangeira imposta pelo banco (ver ADR 002). Se a conta passar a ser obrigatória ou se houver vários campeonatos, o modelo relacional normalizado deve ser reavaliado.

## Rastreabilidade

RF21–RF24, RNF09–RNF10. Evidências: storage.py, app.py, tests/test_app.py (`test_accounts_*`, `test_account_*`, `test_registration_links_to_account_and_blocks_second_entry`). Mudança nesta decisão demanda novo ADR que indique qual substitui.
