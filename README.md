# DOIS / Projeto Rafa e Daniel

Site de campeonatos amadores de **Valorant 2 contra 2**, feito com Python, Flask, SQLite, HTML, CSS e um pequeno arquivo JavaScript.

A interface usa tipografia condensada, fundo escuro, divisórias e vermelho pontual. Não depende de bibliotecas de interface, fontes externas, imagens de terceiros ou serviços da Riot.

## Começar

Requisito: **Python 3.11 ou superior**, com pip e venv. A instalação inicial das dependências precisa de internet.

Na pasta do projeto, execute:

~~~bash
python iniciar.py
~~~

No Windows, se necessário, use **py iniciar.py**.

O atalho prepara o ambiente, instala as dependências e pede para criar o usuário e a senha do organizador na primeira execução. A senha precisa ter de 12 a 1024 caracteres; ela não aparece enquanto é digitada.

Abra **http://127.0.0.1:5173**. Entre em **Organização**, informe a credencial criada e escolha o nome do campeonato e a quantidade de duplas.

Não há usuário nem senha padrão. Não coloque senhas no código ou em commits.

## Como usar

1. O organizador abre um campeonato de 8 ou 16 duplas.
2. Cada jogador informa nome, Riot ID e rank, sem criar conta.
3. Com 16 ou 32 inscritos, o organizador confere os dados e realiza o sorteio.
4. As duplas fixas são distribuídas em grupos de quatro. Cada dupla joga três partidas.
5. O organizador registra ou corrige os placares.
6. Ao encerrar os grupos, as duas melhores duplas de cada grupo avançam.
7. O organizador confirma cada rodada do mata-mata até definir os campeões.

Os jogadores acompanham as páginas públicas. As alterações ficam disponíveis ao atualizar a página.

## Regras implementadas

- **Níveis:** Ferro = 1, Bronze = 2, Prata = 3, Ouro = 4, Platina = 5, Diamante = 6, Ascendente = 7, Imortal = 8 e Radiante = 9.
- **Duplas:** a lista é embaralhada e ordenada por nível; o menor nível é combinado com o maior, o segundo menor com o segundo maior, e assim por diante. O embaralhamento sorteia a ordem dentro dos níveis iguais. A soma é uma aproximação para reduzir a diferença de força, não uma garantia de habilidade igual. As divisões de cada rank não são consideradas.
- **Grupos:** as duplas são sorteadas em grupos de quatro. Todos enfrentam todos uma vez.
- **Pontos:** vitória = 3; derrota = 0. Não há empate.
- **Desempates:** pontos, saldo de rounds, rounds vencidos e ordem sorteada no início.
- **Placares:** números inteiros entre 0 e 99. A duração e as regras da sala personalizada são combinadas pelo organizador; o sistema não impõe o formato oficial de uma partida ranqueada.
- **8 duplas:** semifinais A1 × B2 e B1 × A2.
- **16 duplas:** quartas A1 × B2, C1 × D2, B1 × A2 e D1 × C2, nesta ordem. Duplas do mesmo grupo ficam em metades opostas e só podem se reencontrar na final.
- **Avanço:** exige todos os resultados da fase. Depois de avançar, os placares anteriores ficam bloqueados.
- **Inscrições:** Riot IDs duplicados são recusados, sem diferenciar maiúsculas de minúsculas. Apenas o organizador pode remover inscrições antes do sorteio.

O Riot ID é validado apenas por formato. Não há consulta à API da Riot, verificação de posse de conta nem checagem automática do rank.

## Organização do código

| Arquivo | Responsabilidade |
| --- | --- |
| tournament.py | Inscrições, sorteio, classificação e mata-mata; não depende de Flask. |
| storage.py | Leitura e gravação em SQLite com transações. |
| app.py | Rotas, login do organizador, validação dos formulários e páginas. |
| templates/ | HTML com Jinja; os componentes repetidos ficam em _macros.html. |
| static/style.css | Identidade visual e adaptação ao celular. |
| static/app.js | Confirmações e feedback de envio; o restante funciona sem JavaScript. |
| iniciar.py | Prepara e inicia o projeto. |
| tests/ | Testes das regras e do fluxo HTTP. |
| .github/workflows/tests.yml | Executa os testes no GitHub Actions em pushes e pull requests. |

O banco guarda um único campeonato como JSON. Essa escolha mantém o projeto pequeno e facilita entender suas mudanças de estado. SQLite centraliza os dados para todos os navegadores; não é usado localStorage para inscrições ou resultados.

## Executar manualmente

~~~bash
python -m venv .venv
~~~

Windows:

~~~powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m flask --app app init-admin
.\.venv\Scripts\python.exe -m waitress --host=127.0.0.1 --port=5173 --call app:create_app
~~~

Linux/macOS:

~~~bash
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m flask --app app init-admin
.venv/bin/python -m waitress --host=127.0.0.1 --port=5173 --call app:create_app
~~~

Para trocar o usuário ou a senha, execute **init-admin** novamente. As sessões antigas serão invalidadas. Para desenvolvimento, o comando **python -m flask --app app run** também funciona usando o Python do ambiente virtual.

## Testes

Windows:

~~~powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
~~~

Linux/macOS:

~~~bash
.venv/bin/python -m unittest discover -s tests -v
~~~

Os testes usam bancos temporários e não modificam o campeonato real. Eles cobrem os dois tamanhos de torneio, correções de placar, bloqueio das fases, duplicidade de inscrição, concorrência na última vaga, autorização e proteção de formulários.

## Dados e acesso

- Os arquivos em **instance/** são criados na execução e ignorados pelo Git.
- **championship.sqlite3** guarda o campeonato e o hash da senha.
- **secret.key** guarda a chave da sessão quando SECRET_KEY não foi definida no ambiente.
- Nomes e ranks são públicos; Riot IDs aparecem apenas na área do organizador.
- As senhas usam hash do Werkzeug; não são guardadas em texto aberto.
- Formulários usam tokens CSRF; o login limita tentativas por endereço e a sessão expira em oito horas.
- O banco usa transações para impedir inscrições além do limite em acessos simultâneos.

Faça backup de **instance/** com o servidor parado e mantenha esses arquivos privados. A primeira versão administra **um campeonato por instalação** e preserva seus resultados; não inclui exclusão ou reinicialização pelo navegador.

## GitHub e publicação

O GitHub armazena o código e executa os testes. **GitHub Pages não executa este backend Python**. Para jogadores em diferentes redes usarem os mesmos dados, a aplicação precisa de um servidor Python com armazenamento persistente.

O atalho inicia apenas no próprio computador (127.0.0.1). Se futuramente houver publicação, use HTTPS, defina uma SECRET_KEY forte e COOKIE_SECURE=1, mantenha o banco fora de diretórios públicos e configure o servidor/rede conforme o ambiente. Nenhum serviço externo é necessário para apresentar o projeto localmente.

Projeto independente de estudo, sem vínculo com a Riot Games.
