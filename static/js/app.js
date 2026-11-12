const sidebarToggle = document.querySelector(".sidebar-toggle");
const sidebarOverlay = document.querySelector(".sidebar-overlay");
const appShell = document.querySelector(".app-shell");

function setNavigationOpen(isOpen) {
  document.body.classList.toggle("nav-open", isOpen);
  sidebarToggle?.setAttribute("aria-expanded", String(isOpen));
}

sidebarToggle?.addEventListener("click", () => {
  if (window.matchMedia("(max-width: 760px)").matches) {
    setNavigationOpen(!document.body.classList.contains("nav-open"));
  } else {
    const isCollapsed = appShell.classList.toggle("sidebar-collapsed");
    sidebarToggle.setAttribute("aria-expanded", String(!isCollapsed));
  }
});

sidebarOverlay?.addEventListener("click", () => setNavigationOpen(false));

document.querySelectorAll(".nav-link").forEach((link) => {
  link.addEventListener("click", () => setNavigationOpen(false));
});

window.addEventListener("resize", () => {
  if (!window.matchMedia("(max-width: 760px)").matches) {
    setNavigationOpen(false);
  }
});

document.querySelectorAll("[data-open-dialog]").forEach((trigger) => {
  trigger.addEventListener("click", () => {
    const dialog = document.getElementById(trigger.dataset.openDialog);
    if (dialog instanceof HTMLDialogElement && !dialog.open) {
      dialog.showModal();
      dialog.querySelector("input:not([type='hidden'])")?.focus();
    }
  });
});

document.querySelectorAll(".profile-dialog").forEach((dialog) => {
  dialog.querySelectorAll("[data-close-dialog]").forEach((button) => {
    button.addEventListener("click", () => dialog.close());
  });
  dialog.addEventListener("click", (event) => {
    if (event.target === dialog) dialog.close();
  });

  if (dialog.hasAttribute("data-reopen")) {
    const flashStack = document.querySelector(".flash-stack");
    if (flashStack) dialog.prepend(flashStack);
    dialog.showModal();
  }
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") {
    document.querySelectorAll(".profile-dialog[open]").forEach((dialog) => dialog.close());
  }
});

function filterTable(tableId) {
  const table = document.getElementById(tableId);
  if (!table) return;

  const query = document.querySelector(`[data-table-search="${tableId}"]`)?.value.trim().toLocaleLowerCase() ?? "";
  const filter = document.querySelector(`[data-table-filter="${tableId}"]`);
  const filterField = filter?.dataset.filterField;
  const filterValue = filter?.value.toLocaleLowerCase() ?? "";
  const fromDate = document.querySelector(`[data-date-from="${tableId}"]`)?.value ?? "";
  const toDate = document.querySelector(`[data-date-to="${tableId}"]`)?.value ?? "";
  const rows = [...table.querySelectorAll("tbody tr[data-search]")];
  let visibleRows = 0;

  rows.forEach((row) => {
    const matchesQuery = row.dataset.search.includes(query);
    const matchesFilter = !filterValue || row.dataset[filterField] === filterValue;
    const matchesFromDate = !fromDate || row.dataset.date >= fromDate;
    const matchesToDate = !toDate || row.dataset.date <= toDate;
    const isVisible = matchesQuery && matchesFilter && matchesFromDate && matchesToDate;
    row.hidden = !isVisible;
    if (isVisible) visibleRows += 1;
  });

  const noResults = table.querySelector(".no-results");
  if (noResults) noResults.hidden = visibleRows !== 0 || rows.length === 0;
}

document.querySelectorAll("[data-table-search]").forEach((input) => {
  input.addEventListener("input", () => filterTable(input.dataset.tableSearch));
});

document.querySelectorAll("[data-table-filter]").forEach((select) => {
  select.addEventListener("change", () => filterTable(select.dataset.tableFilter));
});

document.querySelectorAll("[data-date-from], [data-date-to]").forEach((input) => {
  input.addEventListener("change", () => {
    filterTable(input.dataset.dateFrom ?? input.dataset.dateTo);
  });
});

const confirmDialog = document.querySelector("#confirm-dialog");
const confirmMessage = confirmDialog?.querySelector(".dialog-message");
const confirmButton = confirmDialog?.querySelector(".dialog-confirm");
let pendingDeleteForm = null;

document.addEventListener("submit", (event) => {
  const form = event.target;
  if (!(form instanceof HTMLFormElement)) return;

  if (form.matches("form[data-confirm]") && form.dataset.confirmed !== "true") {
    event.preventDefault();
    pendingDeleteForm = form;
    if (confirmDialog?.showModal) {
      confirmMessage.textContent = form.dataset.confirm;
      confirmDialog.showModal();
    } else if (window.confirm(form.dataset.confirm)) {
      form.dataset.confirmed = "true";
      form.requestSubmit();
    }
    return;
  }

  const submitButton = form.querySelector('button[type="submit"], input[type="submit"]');
  if (submitButton instanceof HTMLButtonElement) {
    submitButton.classList.add("is-loading");
    submitButton.disabled = true;
    submitButton.setAttribute("aria-busy", "true");
  }
});

confirmButton?.addEventListener("click", (event) => {
  event.preventDefault();
  if (!pendingDeleteForm) return;

  const formToSubmit = pendingDeleteForm;
  pendingDeleteForm = null;
  formToSubmit.dataset.confirmed = "true";
  confirmDialog.close();
  formToSubmit.requestSubmit();
});

confirmDialog?.addEventListener("close", () => {
  pendingDeleteForm = null;
});

document.querySelectorAll(".flash").forEach((toast, index) => {
  window.setTimeout(() => {
    toast.classList.add("is-dismissed");
    window.setTimeout(() => toast.remove(), 220);
  }, 4500 + index * 250);
});
