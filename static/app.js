// Os formulários funcionam sem JavaScript. Este arquivo acrescenta feedback.
document.querySelectorAll("form").forEach((form) => {
  form.addEventListener("submit", (event) => {
    if (form.dataset.confirm && !window.confirm(form.dataset.confirm)) {
      event.preventDefault();
      return;
    }
    const button = event.submitter;
    if (button) {
      button.dataset.originalText = button.textContent;
      button.textContent = form.dataset.pending || "Salvando…";
      button.disabled = true;
      form.setAttribute("aria-busy", "true");
    }
  });
});

// Ao voltar pelo histórico, o navegador pode restaurar um botão desabilitado.
window.addEventListener("pageshow", () => {
  document.querySelectorAll("button[data-original-text]").forEach((button) => {
    button.textContent = button.dataset.originalText;
    button.disabled = false;
    button.form?.removeAttribute("aria-busy");
  });
});

