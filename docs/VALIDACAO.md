# Validação da primeira versão

Verificação local em 9 de outubro de 2026.

- 20 testes automatizados passaram com Python 3.12.
- Campeonatos de 8 e 16 duplas percorreram o fluxo HTTP completo até o campeão.
- Um campeonato de 8 duplas foi percorrido também no navegador: inscrição, login, sorteio, 15 placares, semifinais e final.
- As páginas públicas e de organização foram verificadas em larguras de 320, 390, 768 e 1440 pixels, sem rolagem horizontal da página inteira. Tabelas, navegação e chaveamento têm rolagem própria quando necessário.
- Início, duplas, grupos e mata-mata foram conferidos com texto a 200% em tela pequena.
- Capturas das telas de computador e celular foram inspecionadas durante a implementação.
- Os testes de concorrência confirmaram que dois pedidos pela última vaga não ultrapassam o limite.
- Os dados de teste ficaram em bancos temporários, separados da aplicação de entrega.

O workflow de GitHub Actions executa a mesma suíte em cada push e pull request. Consulte a aba Actions do repositório para verificar o resultado correspondente a cada commit.
