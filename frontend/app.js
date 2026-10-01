// Frontend client logic for SIG-UOIT incident classifier
const form = document.querySelector("#ticket-form");
const titleInput = document.querySelector("#title");
const descriptionInput = document.querySelector("#initial-description");
const button = document.querySelector("#classify-button");

// 3 Preloaded scenarios for the 5-minute defense
const scenarios = {
  clear: {
    title: "Agotamiento del pool de conexiones en base de datos PostgreSQL",
    description: "Alerta de monitoreo Zabbix: El cluster PostgreSQL alcanzo el limite de max_connections y las aplicaciones no pueden abrir nuevas sesiones. Se solicita intervencion de la guardia tecnica.",
  },
  ambiguous: {
    title: "Error 500 al consultar reportes contables y timeout intermitente",
    description: "Reporte de turno de guardia: La aplicacion web lanza errores HTTP 500 y timeout al solicitar liquidaciones. No se identifica si la falla se origina en la logica de la aplicacion o en saturacion del motor relacional.",
  },
  outside: {
    title: "Menu de almuerzo y opciones vegetarianas en la cafeteria",
    description: "Quisiera consultar que platos vegetarianos y opciones de almuerzo ofrece el casino de la institucion para el dia de manana.",
  },
};

let categories = {};
let inputRevision = 0;

function setText(selector, value) {
  const el = document.querySelector(selector);
  if (el) el.textContent = value;
}

function percent(value) {
  return new Intl.NumberFormat("es", { style: "percent", maximumFractionDigits: 1 }).format(value);
}

function showError(selector, message) {
  const element = document.querySelector(selector);
  if (!element) return;
  element.textContent = message;
  element.hidden = !message;
}

async function requestJson(url, options = {}) {
  const response = await fetch(url, { ...options, signal: AbortSignal.timeout(15000) });
  const data = await response.json();
  if (!response.ok) {
    if (response.status === 422) {
      throw new Error("El título (mín. 5 caracteres) o la descripción (mín. 15 caracteres y 10 letras) no cumplen las reglas de validación.");
    }
    if (response.status === 503) {
      throw new Error("El modelo operativo no está disponible en memoria. Ejecuta python -m app.train y reinicia el servidor.");
    }
    throw new Error("No se pudo completar la consulta con el servidor de inferencia.");
  }
  return data;
}

function inputChanged() {
  inputRevision += 1;
  const len = descriptionInput.value.length;
  setText("#character-count", `${len.toLocaleString("es")} / 2.000`);
  document.querySelector("#classification-result").hidden = true;
  document.querySelector("#empty-result").hidden = false;
  showError("#form-error", "");
}

titleInput.addEventListener("input", inputChanged);
descriptionInput.addEventListener("input", inputChanged);

document.querySelectorAll("[data-scenario]").forEach((control) => {
  control.addEventListener("click", () => {
    const sc = scenarios[control.dataset.scenario];
    if (sc) {
      titleInput.value = sc.title;
      descriptionInput.value = sc.description;
      inputChanged();
    }
  });
});

document.querySelectorAll("[data-panel]").forEach((control) => {
  control.addEventListener("click", () => {
    document.querySelectorAll("[data-panel]").forEach((item) =>
      item.setAttribute("aria-pressed", String(item === control))
    );
    document.querySelectorAll(".panel").forEach((panel) => {
      panel.hidden = panel.id !== control.dataset.panel;
    });
  });
});

function renderClassification(result) {
  document.querySelector("#empty-result").hidden = true;
  document.querySelector("#classification-result").hidden = false;

  setText("#model-badge", result.model || "Línea Base Lineal (C=1.0)");
  setText("#latency-tag", `Latencia: ${result.latency_ms} ms`);
  setText("#category-name", result.category_name);

  const reviewStatus = document.querySelector("#review-status");
  reviewStatus.textContent = result.requires_review
    ? "Revisión técnica recomendada · Confianza moderada"
    : "Sugerencia de alta confianza para el operador";
  reviewStatus.classList.toggle("review", result.requires_review);

  const descriptions = {
    unknown_vocabulary: "No se reconocieron n-gramas específicos del entrenamiento. Conviene verificar manualmente el texto antes de asignar.",
    below_threshold: "El puntaje relativo no superó el umbral de calibración de validación. Se recomienda contrastar las alternativas Top-3.",
    above_threshold: "El puntaje relativo supera el umbral de validación. Confirma la asignación técnica correspondiente.",
  };
  setText("#review-description", descriptions[result.review_reason] || "");

  const ranking = document.querySelector("#ranking");
  ranking.replaceChildren();

  result.ranking.forEach((item, idx) => {
    const row = document.createElement("div");
    row.className = "rank-row";

    const heading = document.createElement("div");
    heading.className = "rank-heading";

    const name = document.createElement("span");
    name.textContent = `${idx < 3 ? `[Top-${idx + 1}] ` : ""}${item.name}`;

    const score = document.createElement("strong");
    score.textContent = percent(item.score);
    heading.append(name, score);

    const track = document.createElement("div");
    track.className = "rank-track";
    track.setAttribute("aria-hidden", "true");

    const fill = document.createElement("div");
    fill.className = "rank-fill";
    fill.style.width = `${Math.max(2, item.score * 100)}%`;
    track.append(fill);

    row.append(heading, track);
    ranking.append(row);
  });

  const baselineCatName = (result.baseline && categories[result.baseline.category])
    ? categories[result.baseline.category].name
    : "Sin coincidencia";
  setText("#baseline-category", baselineCatName);

  const threshVal = result.review_threshold !== undefined
    ? (result.review_threshold > 1 ? "Revisión en todos los casos" : `Puntaje ≥ ${percent(result.review_threshold)}`)
    : "N/A";
  setText("#threshold-label", threshVal);

  const signals = document.querySelector("#signals");
  signals.replaceChildren();
  if (result.signals && result.signals.length > 0) {
    result.signals.forEach((signal) => {
      const chip = document.createElement("span");
      chip.textContent = `${signal.term} (+${signal.contribution})`;
      signals.append(chip);
    });
  } else {
    signals.textContent = "Sin señales léxicas dominantes identificadas.";
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const title = titleInput.value.replace(/\s+/g, " ").trim();
  const initial_description = descriptionInput.value.replace(/\s+/g, " ").trim();
  const letterCount = (initial_description.match(/\p{L}/gu) || []).length;

  if (title.length < 5 || title.length > 200) {
    showError("#form-error", "El título debe contener entre 5 y 200 caracteres.");
    return;
  }
  if (initial_description.length < 15 || initial_description.length > 2000 || letterCount < 10) {
    showError("#form-error", "La descripción debe contener al menos 15 caracteres y 10 letras.");
    return;
  }

  const submittedRevision = inputRevision;
  button.disabled = true;
  button.textContent = "Clasificando…";
  showError("#form-error", "");

  try {
    const result = await requestJson("/api/classify", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title, initial_description }),
    });
    if (submittedRevision === inputRevision) {
      renderClassification(result);
    }
  } catch (error) {
    showError("#form-error", error.name === "TimeoutError" ? "La consulta demoró demasiado. Reintenta." : error.message);
  } finally {
    button.disabled = false;
    button.textContent = "Clasificar incidente ↗";
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
  const bTest = report.test.linear_baseline;
  const tTest = report.test.proposed_transformer;
  const policy = report.test.review_policy;

  setText("#metric-model", bTest.macro_f1.toFixed(4));
  setText("#metric-transformer", tTest.macro_f1.toFixed(4));
  setText("#metric-top3", percent(bTest.top_3_accuracy || 1.0));

  const verdict = bTest.macro_f1 >= tTest.macro_f1
    ? `En la evaluación congelada sobre TEST, la Línea Base Lineal (Macro-F1 ${bTest.macro_f1.toFixed(4)}) superó al Modelo Propuesto Transformer (${tTest.macro_f1.toFixed(4)}), confirmando la decisión tomada en validación.`
    : `En TEST, el Modelo Propuesto Transformer obtuvo mayor Macro-F1 que la Línea Base.`;
  setText("#comparison-verdict", verdict);

  const catTable = document.querySelector("#category-metrics");
  catTable.replaceChildren();
  bTest.by_category.forEach((row) => {
    const catName = categories[row.category] ? categories[row.category].name : row.category;
    addRow(catTable, [catName, percent(row.precision), percent(row.recall), row.f1.toFixed(4), row.support]);
  });

  setText("#accuracy-note", `Accuracy global en TEST: ${percent(bTest.accuracy)}. F1 Ponderado: ${bTest.weighted_f1.toFixed(4)}. Top-3 Accuracy: ${percent(bTest.top_3_accuracy || 1.0)}.`);
  setText("#accepted-count", `${policy.accepted_count} de 180 incidentes (${percent(policy.coverage)})`);
  setText("#review-count", `${policy.review_count} incidentes`);
  setText("#accepted-accuracy", policy.accepted_accuracy !== null ? percent(policy.accepted_accuracy) : "N/A");
  setText("#policy-note", `El umbral de revisión (${report.review_threshold.toFixed(4)}) fue calibrado exclusivamente en VALIDACIÓN para lograr al menos 90% de exactitud.`);

  // Confusion matrix
  const headerRow = document.createElement("tr");
  ["Real / Predicha", ...report.labels.map((l) => (categories[l] ? categories[l].name : l))].forEach((name) => {
    const cell = document.createElement("th");
    cell.scope = "col";
    cell.textContent = name;
    headerRow.append(cell);
  });
  const confHead = document.querySelector("#confusion-head");
  confHead.replaceChildren();
  confHead.append(headerRow);

  const confBody = document.querySelector("#confusion-body");
  confBody.replaceChildren();
  const maxVal = Math.max(1, ...bTest.confusion_matrix.flat());

  bTest.confusion_matrix.forEach((values, rIdx) => {
    const row = document.createElement("tr");
    const label = document.createElement("th");
    label.scope = "row";
    label.textContent = categories[report.labels[rIdx]] ? categories[report.labels[rIdx]].name : report.labels[rIdx];
    row.append(label);

    values.forEach((val, cIdx) => {
      const cell = document.createElement("td");
      cell.textContent = val;
      cell.style.backgroundColor = rIdx === cIdx
        ? `rgba(108, 89, 153, ${0.05 + (val / maxVal) * 0.35})`
        : val > 0 ? "#fbf0df" : "transparent";
      row.append(cell);
    });
    confBody.append(row);
  });

  // Split timeline
  const splitNames = { train: "Entrenamiento", validation: "Validación", test: "Prueba Final" };
  const splitTimeline = document.querySelector("#split-timeline");
  splitTimeline.replaceChildren();
  for (const [name, split] of Object.entries(report.splits)) {
    const block = document.createElement("div");
    block.className = "split";
    const title = document.createElement("h4");
    title.textContent = splitNames[name] || name;
    const p = document.createElement("p");
    p.textContent = `${split.rows} incidentes · ${split.families} familias`;
    block.append(title, p);
    splitTimeline.append(block);
  }

  setText("#dataset-summary", `${report.total_incidents} incidentes sintéticos en 40 familias. 5 categorías de infraestructura.`);
  setText("#selection-summary", `La línea base lineal alcanzó Macro-F1 de ${report.validation.linear_baseline.macro_f1.toFixed(4)} en VALIDACIÓN y fue seleccionada para operar el sistema.`);
}

async function initialize() {
  inputChanged();
  try {
    const [catalog, report] = await Promise.all([
      requestJson("/api/categories"),
      requestJson("/api/metrics"),
    ]);
    categories = catalog.categories;

    const cardsContainer = document.querySelector("#category-cards");
    cardsContainer.replaceChildren();
    Object.values(categories).forEach((cat) => {
      const card = document.createElement("article");
      card.className = "category-card";
      const title = document.createElement("h4");
      title.textContent = cat.name;
      const desc = document.createElement("p");
      desc.textContent = cat.description;
      card.append(title, desc);
      cardsContainer.append(card);
    });

    renderMetrics(report);
    button.disabled = false;
    setText("#connection-status", "● Inferencia activa (Línea Base)");
  } catch (error) {
    setText("#connection-status", "Modelo no disponible");
    showError("#global-error", error.message);
  }
}

initialize();
