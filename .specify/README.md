# Convenções de especificação e uso do agente

Pasta de apoio ao desenvolvimento dirigido por especificação, exigida pelo enunciado. Não implica que o GitHub Spec Kit esteja instalado.

## Fontes canônicas

- [spec.md](../spec.md): comportamento e regras.
- [plan.md](../plan.md): decisões e desenho técnico.
- [tasks.md](../tasks.md): unidades de trabalho, dependências e evidências.
- [ADRs](../docs/README.md): decisões relevantes.

## Contrato de uma tarefa

Antes de implementar, associar a issue, o ID da tarefa, os requisitos afetados e o critério de aceite. Limitar a mudança a esse escopo. Se o comportamento mudar, atualizar a spec e avaliar ADR antes ou junto do código. Usar branch e PR com referência à issue; validar apenas os riscos e critérios pertinentes.

Ao concluir a preparação, registrar arquivos alterados, verificações executadas, limitações e pendências. O agente não atribui aprovação, autoria ou execução de teste a outra pessoa. Testes passados não substituem a revisão do colega. Não marcar revisão humana como realizada automaticamente.

## Modelo de pedido ao agente

```text
Issue: #<numero>
Tarefa: <ID em tasks.md>
Requisitos: <IDs em spec.md>
Objetivo: <mudanca observavel>
Aceite: <resultado verificavel>
Restricoes: <escopo e dados que devem ser preservados>
Entrega: branch, diff, evidencia de teste e PR para revisao
```

Nomes e IDs são estáveis. Mudanças de especificação devem explicar o motivo no PR e manter matriz requisito/código/teste consistente. Não enviar banco, segredo de sessão, senha nem arquivo local de acesso.
