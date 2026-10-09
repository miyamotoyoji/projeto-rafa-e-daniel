# Especificação do DOIS

Projeto de estudo de Rafael e Daniel. Este documento descreve a primeira versão implementada do site de campeonatos amadores de Valorant 2 contra 2.

## Objetivo e escopo

Reunir inscrições, formação de duplas por nível, classificação em grupos e resultados do mata-mata. O site organiza o campeonato; as partidas são realizadas no Valorant e os resultados são informados pelo organizador.

| Formato | Jogadores | Grupos | Classificados | Mata-mata | Total de partidas |
| --- | --- | --- | --- | --- | --- |
| 8 duplas | 16 | 2 grupos de 4 | 4 duplas | Semifinais e final | 15 |
| 16 duplas | 32 | 4 grupos de 4 | 8 duplas | Quartas, semifinais e final | 31 |

## Pessoas e permissões

- **Visitante/jogador:** acompanha o campeonato e se inscreve sem criar conta. Vê nomes e ranks, mas não os Riot IDs de outros inscritos.
- **Organizador:** acessa uma área com usuário e senha. Cria o campeonato, consulta Riot IDs, remove inscrições antes do sorteio, sorteia duplas, lança ou corrige placares da fase atual e confirma o avanço das fases.

## Requisitos funcionais

| ID | Requisito | Critério de aceite |
| --- | --- | --- |
| RF01 | Criar campeonato | Organizador escolhe nome de 3 a 70 caracteres e capacidade de 8 ou 16 duplas. A instalação mantém um campeonato. |
| RF02 | Inscrever jogador | Solicita nome de 2 a 40 caracteres, Riot ID e rank. Recusa inscrição fora da fase de inscrições ou com todas as vagas preenchidas. |
| RF03 | Validar Riot ID | Aceita o formato Nome#TAG, com nome de 3 a 16 caracteres e tag de 3 a 5 letras ou números. Recusa duplicatas sem distinguir maiúsculas de minúsculas. É uma validação local de formato, sem consulta à Riot. |
| RF04 | Remover inscrição | Apenas o organizador pode remover um inscrito e somente antes do sorteio. |
| RF05 | Sortear duplas | Exige exatamente 16 ou 32 jogadores. Cada jogador aparece em uma única dupla, que permanece fixa até o fim. |
| RF06 | Gerar grupos | Distribui as duplas em grupos de quatro e cria seis confrontos por grupo, sem confrontos repetidos. |
| RF07 | Registrar resultados | Apenas o organizador informa placares inteiros de 0 a 99, sem empate. Pode corrigir resultados enquanto a fase ou rodada estiver aberta. |
| RF08 | Calcular classificação | Atualiza jogos, vitórias, derrotas, pontos, rounds feitos, rounds sofridos e saldo a partir dos resultados. |
| RF09 | Classificar duplas | Avança as duas melhores de cada grupo somente depois de todos os resultados dos grupos estarem preenchidos. |
| RF10 | Gerar mata-mata | Usa os cruzamentos definidos abaixo e promove vencedores após a confirmação de cada rodada completa. |
| RF11 | Encerrar campeonato | Ao confirmar a final, registra a dupla campeã e bloqueia alterações nos placares encerrados. |
| RF12 | Persistir dados | Inscrições e resultados continuam disponíveis depois de reiniciar o servidor; navegadores usam o mesmo banco. |

## Regras de competição

### Formação das duplas

Ranks recebem valores de 1 a 9: Ferro, Bronze, Prata, Ouro, Platina, Diamante, Ascendente, Imortal e Radiante.

A lista é embaralhada e ordenada por nível. O jogador de menor nível forma dupla com o de maior nível, o segundo menor com o segundo maior e assim por diante. O embaralhamento define a ordem entre jogadores com o mesmo rank. Depois, as duplas são sorteadas entre os grupos.

O equilíbrio é uma estimativa baseada no rank autodeclarado. Não considera divisões, desempenho recente ou histórico de partidas, nem garante duplas de habilidade idêntica.

### Grupos e desempates

Cada dupla enfrenta as outras três de seu grupo uma vez. Vitória vale três pontos e derrota vale zero. A classificação considera, nesta ordem:

1. Mais pontos.
2. Maior saldo de rounds.
3. Mais rounds vencidos.
4. Ordem sorteada da dupla no grupo.

### Cruzamentos

- **8 duplas:** A1 × B2 e B1 × A2; os vencedores disputam a final.
- **16 duplas:** A1 × B2, C1 × D2, B1 × A2 e D1 × C2, nessa ordem. Vencedores de confrontos adjacentes se enfrentam nas semifinais. Duplas do mesmo grupo só podem se reencontrar na final.

Não há disputa de terceiro lugar. O organizador combina as regras da sala personalizada com os participantes; o sistema não impõe o placar de uma partida ranqueada oficial.

## Estados e transições

Antes da criação, as páginas mostram o estado vazio. Depois da criação:

| Estado | Ações permitidas | Condição para avançar |
| --- | --- | --- |
| Inscrições abertas (`registration`) | Inscrever, remover inscrição e sortear | Todas as vagas preenchidas; organizador confirma o sorteio |
| Grupos (`groups`) | Registrar e corrigir placares dos grupos | Todos os confrontos dos grupos têm resultado |
| Mata-mata (`knockout`) | Registrar e corrigir a rodada atual | Todos os confrontos da rodada têm resultado |
| Encerrado (`finished`) | Consultar resultados e campeões | Estado final |

Cada avanço depende de uma ação do organizador. Resultados de fases e rodadas anteriores ficam bloqueados.

## Páginas e direção visual

| Página | Endereço | Conteúdo principal |
| --- | --- | --- |
| Início | `/` | Nome, fase atual, inscrição, partidas ou resultados |
| Inscrição | `/inscricao` | Nome, Riot ID, rank e validação do formulário |
| Duplas | `/duplas` | Jogadores, ranks e duplas formadas |
| Grupos | `/grupos` | Classificação e confrontos por grupo |
| Mata-mata | `/mata-mata` | Rodadas, conexões e campeão |
| Entrada do organizador | `/organizador/entrar` | Login |
| Organização | `/organizador` | Controles do campeonato e resultados |

Interface em português do Brasil, inspirada na direção de arte de Valorant e Riot Games, com identidade própria: fundo escuro, branco levemente quente, vermelho pontual, títulos condensados, números de placar expressivos e uso de linhas e tabelas. Evitar neon, gradientes decorativos, vidro translúcido, excesso de cartões e frases publicitárias genéricas.

O campeonato deve conduzir a primeira tela. Estados vazios não devem inventar inscritos ou resultados. No celular, tabelas e rodadas podem ter rolagem própria; o conteúdo não deve ser reduzido até ficar ilegível. Animações ficam restritas ao feedback das ações.

## Arquitetura e dados

- **Python e Flask:** recebem pedidos e renderizam HTML com Jinja.
- **`tournament.py`:** regras independentes da interface e do banco.
- **`storage.py`:** SQLite com transações; o estado do campeonato é armazenado como JSON.
- **`app.py`:** rotas, autenticação, autorização e validação dos formulários.
- **`templates/` e `static/`:** páginas, estilos, ícone e JavaScript de apoio.

O estado contém campeonato, jogadores, duplas, grupos, partidas, rodada atual e campeão. As partidas guardam os identificadores das duas duplas, grupo ou rodada e placares. A configuração de acesso do organizador fica no banco local.

## Requisitos de qualidade

- Persistência compartilhada no servidor, com transações para não ultrapassar o limite de vagas em pedidos simultâneos.
- Senha do organizador armazenada como hash, formulários protegidos por CSRF, limitação de tentativas de login e expiração da sessão em oito horas.
- Credenciais, banco e chave de sessão fora do Git; Riot IDs disponíveis apenas na organização.
- Mensagens claras para formulários inválidos, páginas indisponíveis e operações não permitidas.
- Fluxo principal funcionando sem depender de JavaScript; layout adaptado a computador e celular.
- Testes automatizados de regras e fluxo HTTP para os dois formatos. O histórico da verificação visual está em [docs/VALIDACAO.md](docs/VALIDACAO.md).

## Limites da primeira versão

Não inclui outros jogos, integração com a Riot, validação de posse do Riot ID, rank automático, múltiplos campeonatos por instalação, múltiplos organizadores, calendário, chat, premiação, transmissão ao vivo ou atualização automática sem recarregar a página. Não permite excluir ou reiniciar um campeonato pela interface.

O código está no GitHub; hospedagem pública do site é uma etapa separada. A execução local e os comandos de teste estão no [README.md](README.md). As entregas e pendências estão em [TASKS.md](TASKS.md).
