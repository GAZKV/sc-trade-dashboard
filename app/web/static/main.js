let chart;
let lastData;

const resourceNames = {
  // Predefined mappings for common resources
  "res1": "Test Resource"
};

const shopNames = {
  // Predefined mappings for common shops
  "ID1": "Test Shop"
};

Object.assign(resourceNames, JSON.parse(localStorage.getItem("resourceNames") || "{}"));
Object.assign(shopNames, JSON.parse(localStorage.getItem("shopNames") || "{}"));

function saveResourceName(guid, name) {
  if (!name) return;
  resourceNames[guid] = name;
  localStorage.setItem("resourceNames", JSON.stringify(resourceNames));
  if (lastData) updateDashboard(lastData);
}

function saveShopName(id, name) {
  if (!name) return;
  shopNames[id] = name;
  localStorage.setItem("shopNames", JSON.stringify(shopNames));
  if (lastData) updateDashboard(lastData);
}

function enableEdit(cell, idValue, currentName, saveFn) {
  cell.ondblclick = () => {
    cell.innerHTML = "";

    const group = document.createElement("div");
    group.className = "input-group input-group-sm";

    const input = document.createElement("input");
    input.type = "text";
    input.placeholder = idValue;
    input.value = currentName || "";
    input.className = "form-control";

    const btn = document.createElement("button");
    btn.textContent = "Apply";
    btn.className = "btn btn-success";
    btn.onclick = () => {
      const val = input.value.trim();
      if (val && val !== currentName && val !== idValue) {
        saveFn(idValue, val);
      } else {
        cell.textContent = currentName || idValue;
        enableEdit(cell, idValue, currentName, saveFn);
      }
    };

    group.appendChild(input);
    group.appendChild(btn);
    cell.appendChild(group);

    input.focus();
  };
}

function updateDashboard(data) {
  lastData = data;
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
  if (data.log_info) {
    document.getElementById("log-summary").textContent = `${data.log_info.count} logs from ${data.log_info.path}`;
  }

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
  populateTable("lastTransTable", data.last_transactions);
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

function populateTable(id, rows, perPage = 10) {
  const tbl = document.getElementById(id);
  const container = tbl.parentNode;
  tbl.innerHTML = "";
  const oldNav = container.querySelector('.pagination-controls');
  if (oldNav) oldNav.remove();
  if (!rows.length) return;

  const sortRows = rows.slice();
  if (rows[0].timestamp) {
    sortRows.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
  }

  const totalPages = Math.ceil(sortRows.length / perPage);

  function render(page) {
    tbl.innerHTML = "";
    const thead = tbl.createTHead();
    const hdrRow = thead.insertRow();
    Object.keys(sortRows[0]).forEach(col => hdrRow.insertCell().textContent = col);
    const tbody = tbl.createTBody();
    sortRows.slice((page - 1) * perPage, page * perPage).forEach(r => {
      const tr = tbody.insertRow();
      Object.entries(r).forEach(([key, v]) => {
        const cell = tr.insertCell();
      if (key === "resourceGUID") {
        const mapped = resourceNames[v];
        if (mapped) {
          cell.textContent = mapped;
          enableEdit(cell, v, mapped, saveResourceName);
        } else if (id === "pendingTable") {
          const group = document.createElement("div");
          group.className = "input-group input-group-sm";

          const input = document.createElement("input");
          input.type = "text";
          input.placeholder = v;
          input.className = "form-control";

          const btn = document.createElement("button");
          btn.textContent = "Apply";
          btn.className = "btn btn-success";
          btn.onclick = () => saveResourceName(v, input.value || v);

          group.appendChild(input);
          group.appendChild(btn);
          cell.appendChild(group);
        } else {
          cell.textContent = v;
          enableEdit(cell, v, "", saveResourceName);
        }
      } else if (key === "shopId") {
        const mapped = shopNames[v];
        if (mapped) {
          cell.textContent = mapped;
          enableEdit(cell, v, mapped, saveShopName);
        } else if (id === "lastTransTable") {
          const group = document.createElement("div");
          group.className = "input-group input-group-sm";

          const input = document.createElement("input");
          input.type = "text";
          input.placeholder = v;
          input.className = "form-control";

          const btn = document.createElement("button");
          btn.textContent = "Apply";
          btn.className = "btn btn-success";
          btn.onclick = () => saveShopName(v, input.value || v);

          group.appendChild(input);
          group.appendChild(btn);
          cell.appendChild(group);
        } else {
          cell.textContent = v;
          enableEdit(cell, v, "", saveShopName);
        }
      } else {
        cell.textContent =
          typeof v === "number"
            ? v.toLocaleString(undefined, { maximumFractionDigits: 2 })
            : v;
      }
      });
    });
  }

  function addPagination() {
    if (totalPages <= 1) return;
    const nav = document.createElement('div');
    nav.className = 'pagination-controls';
    for (let i = 1; i <= totalPages; i++) {
      const btn = document.createElement('button');
      btn.textContent = i;
      btn.className = 'btn btn-sm btn-secondary mx-1';
      btn.onclick = () => render(i);
      nav.appendChild(btn);
    }
    container.appendChild(nav);
  }

  render(1);
  addPagination();
}
