let chart;

function updateDashboard(data) {
  if (!data.kpi) return; // bootstrap state

  // KPI widgets
  set(
    "profit",
    data.kpi.total_profit_sc.toLocaleString(undefined, {
      maximumFractionDigits: 2,
    })
  );
  set("buys",   data.kpi.total_buys.toLocaleString());
  set("sells",  data.kpi.total_sells.toLocaleString());
  document.getElementById("last-update").textContent =
    `Updated ${new Date().toLocaleTimeString()}`;

  // Chart (create once, then update datasets)
  if (!chart) {
    chart = new Chart(document.getElementById("profitChart"), {
      type: "line",
      data: {
        labels: data.daily_profit.labels,
        datasets: [{
          label: "Daily Profit (SC)",
          data: data.daily_profit.values,
          tension: 0.25,
          fill: false,
        }]
      },
      options: { responsive: true, maintainAspectRatio: false }
    });
  } else {
    chart.data.labels = data.daily_profit.labels;
    chart.data.datasets[0].data = data.daily_profit.values;
    chart.update();
  }

  // Tables helper
  populateTable("buyTable",    data.buy_summary);
  populateTable("sellTable",   data.sell_summary);
  populateTable("routeTable",  data.best_routes);
  populateTable("pendingTable", data.pending_goods);
}

const initEl = document.getElementById('init-data');
if (initEl) {
  updateDashboard(JSON.parse(initEl.textContent));
} else {
  const wsUrl = `${location.protocol === 'https:' ? 'wss' : 'ws'}://${location.host}/ws`;
  const ws = new WebSocket(wsUrl);
  ws.onmessage = evt => updateDashboard(JSON.parse(evt.data));
}

function set(id, txt) { document.getElementById(id).textContent = txt; }

function populateTable(id, rows) {
  const tbl = document.getElementById(id);
  tbl.innerHTML = "";
  if (!rows.length) return;
  // header
  const thead = tbl.createTHead();
  const hdrRow = thead.insertRow();
  Object.keys(rows[0]).forEach(col => hdrRow.insertCell().textContent = col);
  // body
  const tbody = tbl.createTBody();
  rows.forEach(r => {
    const tr = tbody.insertRow();
    Object.values(r).forEach(v => {
      const cell = tr.insertCell();
      cell.textContent =
        typeof v === "number"
          ? v.toLocaleString(undefined, { maximumFractionDigits: 2 })
          : v;
    });
  });
}
