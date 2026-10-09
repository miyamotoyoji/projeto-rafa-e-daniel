# Tarefas do projeto

Lista de acompanhamento do DOIS, projeto de estudo de Rafael e Daniel. Os itens marcados representam funcionalidades já implementadas ou verificações registradas. As pendências de apresentação dependem da revisão dos autores.

Especificação: [SPECS.md](SPECS.md). Instalação e uso: [README.md](README.md).

## Escopo e regras

- [x] Definir Valorant 2 contra 2, com 8 ou 16 duplas.
- [x] Definir inscrição individual com nome, Riot ID e rank.
- [x] Implementar validação de dados, duplicatas e limite de vagas.
- [x] Formar duplas fixas combinando níveis altos e baixos (RF05).
- [x] Sortear grupos de quatro e gerar todos os confrontos (RF06).
- [x] Calcular classificação e critérios de desempate (RF08).
- [x] Classificar duas duplas por grupo e gerar o mata-mata (RF09–RF10).
- [x] Registrar campeão e bloquear fases encerradas (RF11).

## Aplicação e dados

- [x] Separar regras, persistência e rotas em módulos Python.
- [x] Salvar campeonato em SQLite com transações (RF12).
- [x] Criar área protegida do organizador.
- [x] Permitir remover inscrições antes do sorteio (RF04).
- [x] Permitir lançar e corrigir resultados da fase atual (RF07).
- [x] Proteger formulários com CSRF e limitar tentativas de login.
- [x] Manter Riot IDs restritos à organização e credenciais fora do repositório.
- [x] Criar atalho de execução e configuração inicial com `iniciar.py`.

## Interface

- [x] Criar início, inscrição, duplas, grupos, mata-mata e organização.
- [x] Aplicar identidade visual escura, tipografia condensada e vermelho pontual.
- [x] Criar estados vazios e mensagens de validação em português.
- [x] Adaptar navegação, tabelas e chaveamento para celular.
- [x] Adicionar feedback de envio e confirmações das ações.

## Verificação e repositório

- [x] Implementar e executar os 20 testes de regras e aplicação.
- [x] Verificar o fluxo HTTP completo de campeonatos de 8 e 16 duplas.
- [x] Verificar concorrência na última vaga, acesso e proteção de formulários.
- [x] Percorrer um campeonato de 8 duplas no navegador até o campeão.
- [x] Conferir larguras de 320, 390, 768 e 1440 pixels e texto ampliado.
- [x] Configurar testes no GitHub Actions e confirmar execução com sucesso.
- [x] Remover rascunhos e configurações locais do editor do repositório.
- [x] Documentar especificação, instalação, apresentação e validação.

Evidências e limites dessas verificações: [docs/VALIDACAO.md](docs/VALIDACAO.md).

## Antes da entrega do trabalho

- [ ] Rafael e Daniel revisarem as regras e os critérios de aceite de [SPECS.md](SPECS.md).
- [ ] Conferir as exigências do professor e acrescentar capa, relatório ou outros materiais, se solicitados.
- [ ] Combinar quem apresenta cada parte do projeto, sem atribuições presumidas.
- [ ] Instalar e executar no computador que será usado na apresentação.
- [ ] Ensaiar o [roteiro de demonstração](docs/APRESENTACAO.md) em uma cópia separada, com dados identificados como teste.
- [ ] Conferir os testes do commit escolhido para a entrega e registrar esse commit no material apresentado.

## Melhorias futuras — fora do escopo atual

Estas ideias ainda não estão implementadas nem são necessárias para executar a primeira versão.

- [ ] Publicar em servidor Python com HTTPS e armazenamento persistente, caso seja necessário acesso pela internet.
- [ ] Permitir criar novos campeonatos e consultar o histórico dos anteriores.
- [ ] Exportar classificação e resultados.
- [ ] Atualizar placares automaticamente sem recarregar a página.
- [ ] Avaliar integração com a Riot para dados de conta e rank, conforme disponibilidade e requisitos do serviço.
