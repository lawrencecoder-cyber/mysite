const WS_URL = `wss://${window.location.host}/ws/stocks/`;

let socket;
let reconnectDelay = 1000;
let maxReconnectDelay = 10000;

const stockCache = {};
let renderScheduled = false;

const charts = {};

function updateChart(symbol, price) {
  if (!charts[symbol]) {
    const ctx = document.createElement("canvas");
    document.body.appendChild(ctx);

    charts[symbol] = new Chart(ctx, {
      type: "line",
      data: {
        labels: [],
        datasets: [{
          label: symbol,
          data: []
        }]
      }
    });
  }

  const chart = charts[symbol];
  chart.data.labels.push("");
  chart.data.datasets[0].data.push(price);

  if (chart.data.labels.length > 20) {
    chart.data.labels.shift();
    chart.data.datasets[0].data.shift();
  }

  chart.update();
}
/* =========================
   CONNECTION STATUS UI
========================= */
const statusEl = document.createElement("div");
statusEl.className = "connection-status disconnected";
statusEl.innerText = "Disconnected";
document.body.appendChild(statusEl);

function setStatus(connected) {
  statusEl.className = "connection-status " + (connected ? "connected" : "disconnected");
  statusEl.innerText = connected ? "Connected" : "Disconnected";
}

/* =========================
   CREATE SOCKET
========================= */
function connectWebSocket() {
  socket = new WebSocket(WS_URL);

  socket.onopen = () => {
    console.log("WS connected");
    setStatus(true);
    reconnectDelay = 1000;
  };

  socket.onmessage = (event) => {
    const data = JSON.parse(event.data);

    // Merge incoming batch
    Object.assign(stockCache, data);
    Object.entries(data).forEach(([symbol, value]) => {
    updateChart(symbol, value.c); // 'c' = current price from Finnhub
  });

    scheduleRender();
  };

  socket.onclose = () => {
    console.log("WS disconnected");
    setStatus(false);
    reconnect();
  };

  socket.onerror = (err) => {
    console.error("WS error", err);
    socket.close();
  };
}

/* =========================
   RECONNECT LOGIC
========================= */
function reconnect() {
  setTimeout(() => {
    reconnectDelay = Math.min(reconnectDelay * 2, maxReconnectDelay);
    connectWebSocket();
  }, reconnectDelay);
}

/* =========================
   RENDER (BATCHED)
========================= */
function scheduleRender() {
  if (!renderScheduled) {
    renderScheduled = true;
    requestAnimationFrame(renderStocks);
  }
}

function renderStocks() {
  renderScheduled = false;

  const container = document.getElementById("stocks");
  container.innerHTML = "";

  Object.entries(stockCache).forEach(([symbol, data]) => {
    const price = data.c || 0;
    const change = data.d || 0;

    const card = document.createElement("div");
    card.className = "stock-card";

    card.innerHTML = `
      <div class="stock-symbol">${symbol}</div>
      <div class="stock-price">$${price.toFixed(2)}</div>
      <div class="stock-change ${change >= 0 ? "up" : "down"}">
        ${change.toFixed(2)}
      </div>
    `;

    container.appendChild(card);
  });
}

/* =========================
   INIT
========================= */
document.addEventListener("DOMContentLoaded", () => {
  connectWebSocket();
});
