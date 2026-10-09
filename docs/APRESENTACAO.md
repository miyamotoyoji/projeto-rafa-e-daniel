# Roteiro para apresentar o projeto

## Problema

Organizar inscrições, montar duplas com níveis próximos de força e acompanhar grupos e mata-mata manualmente dá trabalho e pode gerar erros.

## Solução

O DOIS reúne essas etapas em um site. Jogadores se inscrevem sem criar conta, e o organizador controla o campeonato por uma área protegida.

## Demonstração

1. Abra a tela inicial e mostre o estado vazio, sem dados inventados.
2. Entre em Organização e crie um campeonato com 8 duplas.
3. Abra uma janela anônima para representar um jogador e faça uma inscrição.
4. Mostre que nome e rank são públicos, mas o Riot ID fica apenas na organização.
5. Complete as 16 inscrições com colegas ou dados explicitamente identificados como teste.
6. Realize o sorteio e explique a combinação de níveis altos com baixos.
7. Mostre os grupos e registre os placares.
8. Encerre os grupos, dispute as semifinais e confirme a final.

Para ensaiar, use uma cópia separada do projeto. O banco é próprio de cada cópia. Não coloque dados de teste no campeonato real.

## Explicação do código

- O navegador pede uma página ao Flask.
- app.py recebe o pedido e valida o acesso e os dados.
- tournament.py aplica as regras, sem saber nada sobre páginas.
- storage.py salva o resultado da operação em uma transação SQLite.
- O Flask preenche um template HTML com o estado atualizado.
- O CSS adapta a apresentação ao tamanho da tela.

## Exemplos que demonstram aprendizado

- **Listas e dicionários:** representam jogadores, duplas e partidas.
- **Ordenação:** forma as duplas e calcula a classificação.
- **Laços:** criam os confrontos dos grupos e as próximas rodadas.
- **Funções:** separam cada regra em uma operação testável.
- **Banco de dados:** permite que vários navegadores vejam o mesmo campeonato.
- **Validação:** impede duplicidade, empate e avanço de fases incompletas.
- **Autenticação e autorização:** identificam o organizador e limitam suas ações.

## Limitações que vale explicar

O rank é informado pelo jogador e serve como estimativa. Não há integração com a Riot. O projeto guarda um campeonato por instalação e não gerencia calendário, chat, múltiplos organizadores ou partidas dentro do jogo.

Essas limitações mantêm a primeira versão focada no problema principal.

