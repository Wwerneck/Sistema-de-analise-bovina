const fmt = new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 1 });
const full = new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 0 });
const decimal = new Intl.NumberFormat("pt-BR", { minimumFractionDigits: 1, maximumFractionDigits: 1 });
let charts = [];
const palette = ["#7dd3fc", "#f8c471", "#8bd3c7", "#b7a6f6", "#f2a7b5", "#94a3b8"];

Chart.defaults.animation = { duration: 450, easing: "easeOutQuart" };
Chart.defaults.font.family = 'Inter, Manrope, "Segoe UI", Arial, sans-serif';
Chart.defaults.color = "#aab7c4";

fetch("data/bovintel_dashboard.json", { cache: "no-store" })
  .then(r => r.json())
  .then(init)
  .catch(() => {
    document.querySelector("main").innerHTML = '<section class="panel"><h2>Dados nao encontrados</h2><p>Execute make transform, make analyze, make forecast e make dashboard para gerar dashboard/data/bovintel_dashboard.json.</p></section>';
  });

function group(rows, key, val) {
  const out = {};
  rows.forEach(r => { out[r[key]] = (out[r[key]] || 0) + Number(r[val] || 0); });
  return out;
}

function lastRows(rows, n) {
  return rows.slice(Math.max(rows.length - n, 0));
}

function init(data) {
  const meta = data.metadata || {};
  const k = data.indicators || {};
  document.getElementById("lastUpdate").textContent = k.latest_export_period || meta.exports_period || "n/d";
  document.getElementById("sourceDetails").innerHTML = `
    <strong>${meta.sources || "Fontes oficiais"}</strong>
    <span>Rebanho: ${meta.herd_period || "n/d"}</span>
    <span>Abate: ${meta.slaughter_period || "n/d"}</span>
    <span>Exportacoes: ${meta.exports_period || "n/d"}</span>
  `;
  document.getElementById("footerSources").textContent = `Fontes: ${meta.sources || "IBGE SIDRA PPM, IBGE SIDRA Abate e Comex Stat/MDIC."}`;

  renderConcentration(data.concentration || {});
  renderQuality(data.data_quality || []);
  renderCorrelation(data.correlation || []);

  const years = [...new Set(data.herd_year.map(d => d.year))].sort();
  const select = document.getElementById("yearFilter");
  years.forEach(y => select.add(new Option(y, y)));
  select.value = years.at(-1);
  select.addEventListener("change", () => render(data, Number(select.value)));
  render(data, Number(select.value));
}

function signed(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "n/d";
  const sign = Number(value) > 0 ? "+" : "";
  return `${sign}${fmt.format(value)}%`;
}

function percentChange(current, previous) {
  const curr = Number(current || 0);
  const prev = Number(previous || 0);
  if (!prev) return null;
  return ((curr - prev) / prev) * 100;
}

function sortedByPeriod(rows) {
  return [...rows].sort((a, b) => String(a.period).localeCompare(String(b.period)));
}

function latestPeriodInYear(rows, year) {
  const matches = sortedByPeriod(rows).filter(row => Number(String(row.period).slice(0, 4)) === year);
  return matches.at(-1) || {};
}

function previousPeriodRow(rows, currentPeriod) {
  const sorted = sortedByPeriod(rows);
  const index = sorted.findIndex(row => String(row.period) === String(currentPeriod));
  return index > 0 ? sorted[index - 1] : {};
}

function deltaClass(value) {
  if (Number(value) < 0) return "delta negative";
  if (Number(value) === 0) return "delta neutral";
  return "delta";
}

function deltaIcon(value) {
  if (Number(value) < 0) return "DOWN";
  if (Number(value) === 0) return "STABLE";
  return "UP";
}

function compactBr(value, unit = "") {
  const n = Number(value || 0);
  const abs = Math.abs(n);
  let formatted = full.format(n);
  if (abs >= 1_000_000_000) formatted = `${decimal.format(n / 1_000_000_000)} bi`;
  else if (abs >= 1_000_000) formatted = `${decimal.format(n / 1_000_000)} mi`;
  else if (abs >= 1_000) formatted = `${decimal.format(n / 1_000)} mil`;
  return `${formatted}${unit ? ` ${unit}` : ""}`;
}

function usdBr(value) {
  const n = Number(value || 0);
  const abs = Math.abs(n);
  if (abs >= 1_000_000_000) return `US$ ${new Intl.NumberFormat("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(n / 1_000_000_000)} bi`;
  if (abs >= 1_000_000) return `US$ ${decimal.format(n / 1_000_000)} mi`;
  return `US$ ${full.format(n)}`;
}

function absoluteTitle(value, unit = "") {
  return `${full.format(Number(value || 0))}${unit ? ` ${unit}` : ""}`;
}

function renderConcentration(c) {
  const classification = c.classification || "classificacao nao informada";
  document.getElementById("concentrationDescription").textContent =
    `A carteira de exportacao apresenta ${classification}. A leitura combina dependencia dos principais compradores, dispersao dos destinos e quantidade de mercados necessaria para sustentar a maior parte do volume.`;
  document.getElementById("concentration").innerHTML = [
    ["Top 3 destinos", `${fmt.format(c.cr3_percent || 0)}%`, "Participacao concentrada nos tres maiores mercados compradores."],
    ["Top 5 destinos", `${fmt.format(c.cr5_percent || 0)}%`, "Peso acumulado dos cinco principais destinos na pauta exportadora."],
    ["Indice HHI", fmt.format(c.hhi || 0), "Mede concentracao de mercado; quanto maior, maior a dependencia comercial."],
    ["Pareto do volume", `${c.pareto_80_count || 0} destinos`, "Numero de destinos necessarios para explicar aproximadamente 80% do volume."]
  ].map(([k, v, note]) => `<div><span>${k}</span><strong>${v}</strong><small>${note}</small></div>`).join("");
}

function renderCorrelation(rows) {
  const valid = rows.filter(r => r.correlation !== null && r.correlation !== undefined);
  const cards = valid.length
    ? valid.map(r => `
      <div class="stat-card">
        <span>${r.method}</span>
        <strong>r=${fmt.format(r.correlation)}</strong>
        <small>p=${fmt.format(r.p_value)} | n=${r.n}</small>
      </div>
    `).join("")
    : '<div class="stat-card"><span>Status</span><strong>Amostra insuficiente</strong><small>Sem correlacao calculavel.</small></div>';
  document.getElementById("correlation").innerHTML =
    `<p class="eyebrow">Leitura estatistica</p>
     <h3>Associacao abate-exportacao</h3>
     <p>Avaliacao da relacao estatistica entre abate e volume exportado, considerando intensidade da associacao e significancia da amostra.</p>
     <div class="stat-grid">${cards}</div>
     <p class="method-note">Correlacao mede associacao entre series historicas e nao demonstra causalidade.</p>`;
}

function renderQuality(rows) {
  const totals = rows.reduce((acc, row) => {
    acc.zeros += Number(row.zero_numeric_cells || 0);
    acc.missing += Number(row.missing_cells || 0);
    acc.suppressed += Number(row.raw_suppressed_symbols || 0);
    acc.unavailable += Number(row.raw_unavailable_symbols || 0);
    return acc;
  }, { zeros: 0, missing: 0, suppressed: 0, unavailable: 0 });
  const availabilityIssues = totals.suppressed + totals.unavailable;
  const status = availabilityIssues === 0
    ? "sem registros suprimidos ou indisponiveis nas bases processadas"
    : `${fmt.format(availabilityIssues)} registros com restricao de disponibilidade`;
  document.getElementById("qualityDescription").textContent =
    `Resumo de consistencia das bases tratadas: ${fmt.format(totals.missing)} ausencias processadas, ${fmt.format(totals.zeros)} zeros numericos e ${status}.`;
  document.getElementById("quality").innerHTML = [
    ["Zeros numericos", fmt.format(totals.zeros), "Celulas numericas zeradas"],
    ["Ausencias", fmt.format(totals.missing), "Campos tratados como ausentes"],
    ["Disponibilidade", `${fmt.format(totals.suppressed)} / ${fmt.format(totals.unavailable)}`, "Suprimidos / indisponiveis"]
  ].map(([k, v, note]) => `<div><span>${k}</span><strong>${v}</strong><small>${note}</small></div>`).join("");
}

function render(data, year) {
  charts.forEach(c => c.destroy());
  charts = [];

  const herdTotal = data.herd_year.find(d => d.year === year) || {};
  const previousHerdTotal = data.herd_year.find(d => d.year === year - 1) || {};
  const herdYoY = percentChange(herdTotal.bovine_herd_heads, previousHerdTotal.bovine_herd_heads);
  const herdUf = data.herd_state_year.filter(d => d.year === year);
  const latestSlaughter = latestPeriodInYear(data.slaughter_quarter, year);
  const previousSlaughter = previousPeriodRow(data.slaughter_quarter, latestSlaughter.period);
  const latestExports = latestPeriodInYear(data.exports_month, year);
  const previousExports = previousPeriodRow(data.exports_month, latestExports.period);
  const latestExportYear = latestExports.period ? Number(String(latestExports.period).slice(0, 4)) : year;
  const latestExportMonth = latestExports.period ? String(latestExports.period).slice(0, 7) : "n/d";
  const latestSlaughterPeriod = latestSlaughter.period ? String(latestSlaughter.period).slice(0, 10) : "n/d";
  const destRows = data.destination_year.filter(d => d.year === latestExportYear);
  const dest = group(destRows, "destination_country", "net_weight_kg");
  const topDest = Object.entries(dest).sort((a, b) => b[1] - a[1])[0] || ["n/d", 0];
  const topUf = [...herdUf].sort((a, b) => Number(b.bovine_herd_heads || 0) - Number(a.bovine_herd_heads || 0))[0] || {};
  const k = data.indicators || {};
  const ufShare = herdTotal.bovine_herd_heads ? (Number(topUf.bovine_herd_heads || 0) / Number(herdTotal.bovine_herd_heads)) * 100 : 0;
  const slaughterQoQ = percentChange(latestSlaughter.slaughtered_heads, previousSlaughter.slaughtered_heads);
  const exportMoM = percentChange(latestExports.net_weight_kg, previousExports.net_weight_kg);

  document.getElementById("filterContext").textContent =
    `Recorte ativo: ${year}. Lideranca no rebanho: ${topUf.state_name || "n/d"} com ${fmt.format(ufShare)}% do total nacional.`;
  document.getElementById("ufShareDescription").textContent =
    `Em ${year}, ${topUf.state_name || "a UF lider"} concentra ${fmt.format(ufShare)}% do rebanho nacional. O grafico compara as cinco maiores UFs com o restante do pais para evidenciar concentracao territorial.`;
  document.getElementById("heroMetrics").innerHTML = [
    ["Recorte ativo", String(year), "Ano base dos indicadores filtraveis"],
    ["UF lider", topUf.state_name || "n/d", `${fmt.format(ufShare)}% do rebanho nacional`],
    ["Destino lider", topDest[0], `Ano ${latestExportYear}`],
    ["Tendencia exportacao", signed(exportMoM), `${latestExportMonth} vs. mes anterior`]
  ].map(([label, value, detail]) => `
    <div class="hero-metric">
      <span>${label}</span>
      <strong>${value}</strong>
      <small>${detail}</small>
    </div>
  `).join("");

  document.getElementById("cards").innerHTML = [
    ["Rebanho bovino", compactBr(herdTotal.bovine_herd_heads, "cabecas"), absoluteTitle(herdTotal.bovine_herd_heads, "cabecas"), `Ano ${year}`, signed(herdYoY), herdYoY],
    ["Abate no ano", compactBr(latestSlaughter.slaughtered_heads, "cabecas"), absoluteTitle(latestSlaughter.slaughtered_heads, "cabecas"), `${latestSlaughterPeriod} vs. periodo anterior`, signed(slaughterQoQ), slaughterQoQ],
    ["Peso medio carcaca", `${decimal.format(latestSlaughter.avg_carcass_weight_kg_per_head || 0)} kg/cabeca`, absoluteTitle(latestSlaughter.avg_carcass_weight_kg_per_head, "kg/cabeca"), latestSlaughterPeriod],
    ["Valor exportado", usdBr(latestExports.export_value_usd_fob || 0), `US$ ${full.format(latestExports.export_value_usd_fob || 0)}`, latestExportMonth],
    ["Volume exportado", compactBr(latestExports.net_weight_kg, "kg"), absoluteTitle(latestExports.net_weight_kg, "kg"), `${latestExportMonth} vs. mes anterior`, signed(exportMoM), exportMoM],
    ["Principal destino", topDest[0], absoluteTitle(topDest[1], "kg exportados"), `Ano ${latestExportYear}`]
  ].map(([title, value, abs, period, delta, raw]) => {
    const deltaHtml = delta ? `<small class="${deltaClass(raw)}"><span aria-hidden="true">${deltaIcon(raw)}</span>${delta}</small>` : "";
    const trendClass = raw === undefined ? "" : Number(raw) < 0 ? " trend-down" : " trend-up";
    return `<div class="card${trendClass}" title="${abs}"><span>${title}</span><strong>${value}</strong><small>${period}</small>${deltaHtml}</div>`;
  }).join("");

  doughnut("ufShareChart", shareWithOther(group(herdUf, "state_name", "bovine_herd_heads"), 5), "Cabecas");
  doughnut("destShareChart", shareWithOther(dest, 5), "Kg");
  line("herdChart", group(data.herd_year, "year", "bovine_herd_heads"), "Cabecas", year);
  bar("ufChart", group(herdUf, "state_name", "bovine_herd_heads"), "Cabecas");
  line("slaughterChart", group(lastRows(data.slaughter_quarter, 36), "period", "slaughtered_heads"), "Cabecas", null, { compactTime: true });
  line("exportsChart", group(lastRows(data.exports_month, 36), "period", "net_weight_kg"), "Kg", null, { compactTime: true });
  bar("destChart", dest, "Kg");
  const forecastRows = (data.forecast || []).filter(r => r.forecast_net_weight_kg !== null);
  line("forecastChart", group(forecastRows, "period", "forecast_net_weight_kg"), "Kg previstos");
}

function shareWithOther(obj, limit) {
  const entries = Object.entries(obj).sort((a, b) => b[1] - a[1]);
  const top = entries.slice(0, limit);
  const other = entries.slice(limit).reduce((acc, row) => acc + row[1], 0);
  if (other > 0) top.push(["Demais", other]);
  return Object.fromEntries(top);
}

function shortPeriodLabel(value) {
  const text = String(value || "");
  if (/^\d{4}-\d{2}/.test(text)) return `${text.slice(5, 7)}/${text.slice(2, 4)}`;
  return text;
}

function line(id, obj, label, selectedLabel = null, config = {}) {
  setChartState(id, Object.keys(obj).length ? "" : "empty");
  if (!Object.keys(obj).length) return;
  const labels = Object.keys(obj);
  const displayLabels = config.compactTime ? labels.map(shortPeriodLabel) : labels;
  const pointRadius = config.compactTime ? 0 : 3;
  const selectedRadius = config.compactTime ? 4 : 7;
  charts.push(new Chart(document.getElementById(id), {
    type: "line",
    data: {
      labels: displayLabels,
      datasets: [{
        label,
        data: Object.values(obj),
        borderColor: "#7dd3fc",
        backgroundColor: "rgba(125, 211, 252, .12)",
        pointBackgroundColor: "#ffffff",
        pointBorderColor: labels.map(item => String(item) === String(selectedLabel) ? "#f8c471" : "#7dd3fc"),
        pointRadius: labels.map(item => String(item) === String(selectedLabel) ? selectedRadius : pointRadius),
        pointHoverRadius: 5,
        borderWidth: 2.5,
        tension: config.compactTime ? 0.34 : 0.28,
        fill: true
      }]
    },
    options: lineOptions(config)
  }));
}

function doughnut(id, obj, label) {
  const entries = Object.entries(obj).filter(([, value]) => Number(value) > 0);
  setChartState(id, entries.length ? "" : "empty");
  if (!entries.length) return;
  charts.push(new Chart(document.getElementById(id), {
    type: "doughnut",
    data: {
      labels: entries.map(e => e[0]),
      datasets: [{
        label,
        data: entries.map(e => e[1]),
        backgroundColor: entries.map((_, i) => palette[i % palette.length]),
        borderColor: "#101925",
        borderWidth: 2,
        hoverOffset: 6
      }]
    },
    options: doughnutOptions()
  }));
}

function bar(id, obj, label) {
  const entries = Object.entries(obj).sort((a, b) => b[1] - a[1]).slice(0, 10);
  setChartState(id, entries.length ? "" : "empty");
  if (!entries.length) return;
  charts.push(new Chart(document.getElementById(id), {
    type: "bar",
    data: {
      labels: entries.map(e => e[0]),
      datasets: [{
        label,
        data: entries.map(e => e[1]),
        backgroundColor: entries.map((_, i) => i === 0 ? "#7dd3fc" : "#607085"),
        hoverBackgroundColor: "#f8c471",
        borderRadius: 8,
        barThickness: "flex",
        maxBarThickness: 34
      }]
    },
    options: barOptions()
  }));
}

function doughnutOptions() {
  return {
    responsive: true,
    maintainAspectRatio: false,
    cutout: "68%",
    plugins: {
      legend: {
        position: "right",
        labels: {
          boxWidth: 10,
          boxHeight: 10,
          color: "#d7e2ea",
          font: { size: 11, weight: "700" },
          padding: 12
        }
      },
      tooltip: {
        backgroundColor: "#07111f",
        padding: 12,
        displayColors: false,
        callbacks: {
          label: ctx => {
            const total = ctx.dataset.data.reduce((acc, value) => acc + Number(value || 0), 0);
            const value = Number(ctx.parsed || 0);
            const share = total ? (value / total) * 100 : 0;
            return `${ctx.label}: ${full.format(value)} (${fmt.format(share)}%)`;
          }
        }
      }
    }
  };
}

function setChartState(id, state) {
  const box = document.getElementById(id).closest(".chart-box");
  box.dataset.state = state;
  box.dataset.message = state === "empty" ? "Sem dados para o recorte selecionado." : "";
}

function parsedValue(ctx) {
  if (typeof ctx.parsed === "number") return ctx.parsed;
  if (ctx.parsed && typeof ctx.parsed.x === "number") return ctx.parsed.x;
  if (ctx.parsed && typeof ctx.parsed.y === "number") return ctx.parsed.y;
  return 0;
}

function basePlugins(showLegend = false) {
  return {
    legend: {
      display: showLegend,
      position: "bottom",
      labels: {
        boxWidth: 10,
        boxHeight: 10,
        color: "#d7e2ea",
        font: { size: 12, weight: "700" },
        padding: 16,
        usePointStyle: true
      }
    },
    tooltip: {
      backgroundColor: "#07111f",
      borderColor: "rgba(255,255,255,.12)",
      borderWidth: 1,
      padding: 12,
      displayColors: false,
      callbacks: { label: ctx => `${ctx.dataset.label}: ${full.format(parsedValue(ctx))}` }
    }
  };
}

function lineOptions(config = {}) {
  const compactTime = Boolean(config.compactTime);
  return {
    responsive: true,
    maintainAspectRatio: false,
    resizeDelay: 100,
    interaction: { mode: "index", intersect: false },
    plugins: basePlugins(!compactTime),
    scales: {
      x: {
        title: { display: !compactTime, text: "Ano / periodo", color: "#d7e2ea" },
        ticks: {
          color: "#aab7c4",
          maxRotation: compactTime ? 0 : 45,
          minRotation: 0,
          maxTicksLimit: compactTime ? 6 : 10,
          autoSkip: true
        },
        grid: { display: false },
        border: { display: false }
      },
      y: { ticks: { color: "#aab7c4", callback: value => compactBr(value) }, grid: { color: "rgba(148, 163, 184, .18)" }, border: { display: false } }
    }
  };
}

function barOptions() {
  return {
    responsive: true,
    maintainAspectRatio: false,
    resizeDelay: 100,
    indexAxis: "y",
    plugins: basePlugins(true),
    scales: {
      x: {
        title: { display: true, text: "Volume", color: "#d7e2ea" },
        ticks: { color: "#aab7c4", callback: value => compactBr(value), maxTicksLimit: 6 },
        grid: { color: "rgba(148, 163, 184, .18)" },
        border: { display: false }
      },
      y: {
        title: { display: true, text: "Categoria", color: "#d7e2ea" },
        ticks: { color: "#d7e2ea", font: { size: 12, weight: "700" } },
        grid: { display: false },
        border: { display: false }
      }
    }
  };
}
