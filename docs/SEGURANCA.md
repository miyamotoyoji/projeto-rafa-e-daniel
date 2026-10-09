# Segurança e SSDLC

Escopo: aplicação acadêmica local descrita em [spec.md](../spec.md). Este documento descreve controles e processo; não é certificação, auditoria exaustiva ou comprovação de ausência de vulnerabilidades.

## Dados, atores e limites de confiança

Públicos: nome, rank, dupla e resultados. Restritos: Riot ID, credencial de organização, chave de sessão e banco completo. O navegador é uma entrada não confiável, incluindo campos ocultos. O servidor é responsável pela autorização e pelas regras. Arquivos de instance/ não devem ser servidos como estáticos ou enviados ao GitHub.

| Situação | Controle existente | Limite/verificação |
| --- | --- | --- |
| Visitante tenta alterar resultado | Decorador protected e checagem de versão da sessão | Teste de POST sem organização; não há múltiplos administradores |
| Formulário forjado | Token CSRF em todo POST e comparação segura | tests/test_app.py::test_csrf_and_organizer_permission |
| Tentativas repetidas de senha | Cinco falhas por endereço em janela de 15 minutos | Bloqueio testado; expiração da janela ainda sem teste específico |
| Nome contém script | Escape de template e CSP restritiva | test_html_escaping; não substitui revisão de toda futura interpolação |
| Senha ou sessão exposta em Git | Hash de senha, dados ignorados, arquivo de chave privado | Revisar diffs antes de cada commit; nunca versionar ACESSO-LOCAL.txt |
| Pedidos simultâneos pela última vaga | Transação BEGIN IMMEDIATE | Teste concorrente garante capacidade; não é ensaio de carga |
| Interceptação na internet | Operação atual restrita a localhost | Hospedagem requer HTTPS e COOKIE_SECURE=1; não foi implantada |
| Falsa declaração de rank/identidade | Conferência manual pelo organizador | Não há validação de posse Riot; limitação aceita do escopo |

Sessão tem validade configurada de oito horas, cookie HttpOnly e SameSite=Lax. Troca de credencial invalida versões antigas. SQL usa parâmetros. Respostas incluem CSP, proteção de enquadramento e nosniff. Esses controles são constatados no código, sem assumir que cada combinação tem teste dedicado.

## Ciclo de desenvolvimento seguro

1. **Especificar:** identificar dados e permissões no requisito; atualizar RN/RF/RNF e critérios de abuso relevantes.
2. **Projetar:** registrar mudanças de autenticação, armazenamento ou integrações em ADR, com riscos e alternativas.
3. **Implementar:** validar no servidor; não confiar em controles visuais; separar segredo de configuração pública.
4. **Verificar:** testar acesso, entrada inválida, preservação de dados e regressões afetadas; examinar diff e dependências alteradas.
5. **Revisar:** outro integrante verifica código, spec, evidência e quatro dimensões da revisão antes do merge.
6. **Operar:** restringir acesso ao banco, guardar backup com servidor parado, ensaiar restauração e atualizar dependências após testes.

## Pendências explícitas

- Não foi executada análise automatizada de dependências nem auditoria independente.
- Não existe trilha persistente de alterações de placar; requisito deve ser definido antes de implementar.
- Não há procedimento de retenção de inscrições para hospedagem pública; definir se o escopo mudar.
- Backup/restauração precisa de ensaio por um integrante com dados de teste (Q05).
- Proxy, múltiplos processos e limitação por IP precisam de validação no ambiente de hospedagem escolhido.

Achados e ações: [docs/review](review/README.md). Testes e lacunas: [TESTES.md](TESTES.md).
