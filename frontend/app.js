// The browser sends one initial message; the server owns the trained pipeline.
const form = document.querySelector("#ticket-form");
const messageInput = document.querySelector("#message");
const button = document.querySelector("#classify-button");
const scenarios = {
  access: "Mi cuenta está bloqueada y no puedo iniciar sesión. Necesito recuperar el acceso al portal de trabajo.",
  network: "La conexión wifi se corta a cada rato y no podemos abrir páginas de internet en varios equipos.",
  email: "Mis correos quedan en la bandeja de salida y los destinatarios no reciben los mensajes con adjuntos.",
  hardware: "El teclado físico dejó de responder y varias teclas están dañadas. Ya probé conectarlo nuevamente.",
  ambiguous: "No puedo entrar y todo dejó de funcionar. Necesito ayuda para continuar con mi trabajo.",
  outside: "Quisiera saber qué platos vegetarianos ofrece la cafetería para el almuerzo de mañana.",
};
let categories = {};
let inputRevision = 0;

function setText(selector, value) {
  document.querySelector(selector).textContent = value;
}

function percent(value) {
  return new Intl.NumberFormat("es", { style: "percent", maximumFractionDigits: 1 }).format(value);
}

function showError(selector, message) {
  const element = document.querySelector(selector);
  element.textContent = message;
  element.hidden = !message;
}

async function requestJson(url, options = {}) {
  const response = await fetch(url, { ...options, signal: AbortSignal.timeout(15000) });
  const data = await response.json();
  if (!response.ok) {
    if (response.status === 422) throw new Error("Describe la solicitud con entre 20 y 2.000 caracteres y al menos 10 letras.");
    if (response.status === 503) throw new Error("El modelo no está disponible. Genera datos, entrena y reinicia el servidor; consulta README.md.");
    throw new Error("No se pudo completar la consulta. Revisa que el servidor esté funcionando.");
  }
  return data;
}

function messageChanged() {
  inputRevision += 1;
  setText("#character-count", `${messageInput.value.length.toLocaleString("es")} / 2.000`);
  document.querySelector("#classification-result").hidden = true;
  document.querySelector("#empty-result").hidden = false;
  showError("#form-error", "");
}

messageInput.addEventListener("input", messageChanged);
document.querySelectorAll("[data-scenario]").forEach((control) => {
  control.addEventListener("click", () => {
    messageInput.value = scenarios[control.dataset.scenario];
    messageChanged();
  });
});
document.querySelectorAll("[data-panel]").forEach((control) => {
  control.addEventListener("click", () => {
    document.querySelectorAll("[data-panel]").forEach((item) => item.setAttribute("aria-pressed", String(item === control)));
    document.querySelectorAll(".panel").forEach((panel) => { panel.hidden = panel.id !== control.dataset.panel; });
  });
});

function renderClassification(result) {
  document.querySelector("#empty-result").hidden = true;
  document.querySelector("#classification-result").hidden = false;
  setText("#category-name", result.category_name);
  setText("#review-status", result.needs_review ? "Revisión necesaria · Sugerencia tentativa" : "Sugerencia disponible para revisión");
  document.querySelector("#review-status").classList.toggle("review", result.needs_review);
  const descriptions = {
    unknown_vocabulary: "No se reconoció vocabulario del entrenamiento. La categoría mostrada no es una orientación fiable para este texto.",
    below_threshold: "El puntaje no alcanza el criterio elegido en validación. Conviene aclarar la solicitud antes de asignarla.",
    above_threshold: "El puntaje supera el criterio de validación. Confirma que la categoría corresponda al problema descrito.",
  };
  setText("#review-description", descriptions[result.review_reason]);
  const ranking = document.querySelector("#ranking");
  ranking.replaceChildren();
  result.ranking.forEach((item) => {
    const row = document.createElement("div");
    row.className = "rank-row";
    const heading = document.createElement("div");
    heading.className = "rank-heading";
    const name = document.createElement("span");
    name.textContent = item.name;
    const score = document.createElement("strong");
    score.textContent = percent(item.score);
    heading.append(name, score);
    const track = document.createElement("div");
    track.className = "rank-track";
    track.setAttribute("aria-hidden", "true");
    const fill = document.createElement("div");
    fill.className = "rank-fill";
    fill.style.width = `${item.score * 100}%`;
    track.append(fill);
    row.append(heading, track);
    ranking.append(row);
  });
  setText("#baseline-category", categories[result.baseline.category].name);
  setText("#threshold-label", result.review_threshold > 1 ? "Revisión para todos" : `Puntaje ≥ ${percent(result.review_threshold)}`);
  document.querySelector("#fallback-note").hidden = !result.baseline.used_fallback;
  const signals = document.querySelector("#signals");
  signals.replaceChildren();
  result.signals.forEach((signal) => {
    const chip = document.createElement("span");
    chip.textContent = signal.term;
    signals.append(chip);
  });
  if (!result.signals.length) signals.textContent = "No hay términos positivos reconocidos para destacar.";
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = messageInput.value.replace(/\s+/g, " ").trim();
  const letterCount = (message.match(/\p{L}/gu) || []).length;
  if (message.length < 20 || message.length > 2000 || letterCount < 10) {
    showError("#form-error", "Escribe una descripción de al menos 20 caracteres y 10 letras, sin contar espacios repetidos.");
    return;
  }
  const submittedRevision = inputRevision;
  button.disabled = true;
  button.textContent = "Analizando…";
  showError("#form-error", "");
  try {
    const result = await requestJson("/api/classify", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ message }) });
    if (submittedRevision === inputRevision) renderClassification(result);
  } catch (error) {
    showError("#form-error", error.name === "TimeoutError" ? "La consulta tardó demasiado. Intenta nuevamente." : error.message);
  } finally {
    button.disabled = false;
    button.textContent = "Analizar solicitud ↗";
  }
});

function addRow(body, values) {
  const row = document.createElement("tr");
  values.forEach((value, index) => {
    const cell = document.createElement(index === 0 ? "th" : "td");
    if (index === 0) cell.scope = "row";
    cell.textContent = value;
    row.append(cell);
  });
  body.append(row);
}

function renderMetrics(report) {
  const { model, baseline, review_policy: policy } = report.test;
  setText("#metric-model", model.macro_f1.toFixed(3));
  setText("#metric-baseline", baseline.macro_f1.toFixed(3));
  setText("#metric-coverage", percent(policy.coverage));
  setText("#comparison-verdict", baseline.macro_f1 >= model.macro_f1 ? "En esta prueba, las reglas superan al modelo. El resultado no justifica reemplazar la regla sencilla; sirve para identificar qué datos y categorías necesitan mejorar." : "En esta prueba sintética, el modelo supera a las reglas. Esto todavía no demuestra utilidad en una mesa de ayuda real.");
  model.by_category.forEach((row) => addRow(document.querySelector("#category-metrics"), [categories[row.category].name, percent(row.precision), percent(row.recall), row.f1.toFixed(3), row.support]));
  setText("#accuracy-note", `Exactitud en todos los mensajes: ${percent(model.accuracy)}. F1 ponderado: ${model.weighted_f1.toFixed(3)}. Estas métricas no excluyen los mensajes marcados para revisión.`);
  setText("#accepted-count", policy.accepted_count);
  setText("#review-count", policy.review_count);
  setText("#accepted-accuracy", policy.accepted_accuracy === null ? "No definida" : percent(policy.accepted_accuracy));
  const targetNote = policy.accepted_accuracy !== null && policy.accepted_accuracy < report.target_accepted_accuracy ? " En prueba no se alcanzó ese objetivo; el umbral se conserva sin reajustarlo." : " No es una garantía para textos futuros.";
  setText("#policy-note", `Se buscó al menos ${percent(report.target_accepted_accuracy)} de exactitud en un mínimo de ${report.minimum_accepted_cases} casos de validación, con la mayor cobertura posible.${targetNote}`);
  const headerRow = document.createElement("tr");
  ["Real / predicha", ...report.labels.map((label) => categories[label].name)].forEach((name) => {
    const cell = document.createElement("th");
    cell.scope = "col";
    cell.textContent = name;
    headerRow.append(cell);
  });
  document.querySelector("#confusion-head").append(headerRow);
  const maximum = Math.max(1, ...model.confusion_matrix.flat());
  model.confusion_matrix.forEach((values, index) => {
    const row = document.createElement("tr");
    const label = document.createElement("th");
    label.scope = "row";
    label.textContent = categories[report.labels[index]].name;
    row.append(label);
    values.forEach((value, column) => {
      const cell = document.createElement("td");
      cell.textContent = value;
      cell.style.backgroundColor = index === column ? `rgba(108, 89, 153, ${0.04 + value / maximum * 0.25})` : value ? "#fbf0df" : "transparent";
      row.append(cell);
    });
    document.querySelector("#confusion-body").append(row);
  });
  const names = { train: "Entrenamiento", validation: "Validación", test: "Prueba final" };
  for (const [name, split] of Object.entries(report.splits)) {
    const block = document.createElement("div");
    block.className = "split";
    const title = document.createElement("h4");
    title.textContent = names[name];
    const text = document.createElement("p");
    text.textContent = `${split.rows} mensajes · ${split.families} familias`;
    block.append(title, text);
    document.querySelector("#split-timeline").append(block);
  }
  const total = Object.values(report.splits).reduce((sum, split) => sum + split.rows, 0);
  setText("#dataset-summary", `${total.toLocaleString("es")} mensajes en 60 familias de frases. Cinco categorías con diferentes cantidades de ejemplos.`);
  setText("#selection-summary", `Se comparan dos niveles de regularización y se elige C = ${report.selected_c} por Macro-F1 de validación.`);
}

async function initialize() {
  messageChanged();
  try {
    const [catalog, report] = await Promise.all([requestJson("/api/categories"), requestJson("/api/metrics")]);
    categories = catalog.categories;
    Object.values(categories).forEach((category) => {
      const card = document.createElement("article");
      card.className = "category-card";
      const title = document.createElement("h4");
      title.textContent = category.name;
      const description = document.createElement("p");
      description.textContent = category.description;
      card.append(title, description);
      document.querySelector("#category-cards").append(card);
    });
    renderMetrics(report);
    button.disabled = false;
    setText("#connection-status", "● Modelo conectado");
  } catch (error) {
    setText("#connection-status", "Modelo no disponible");
    showError("#global-error", error.message);
  }
}

initialize();
