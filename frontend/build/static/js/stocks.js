const WS_URL = `wss://${window.location.host}/ws/stocks/`;

let socket;
let reconnectDelay = 1000;
const maxReconnectDelay = 10000;

const stockCache = {};
const charts = {};
let renderScheduled = false;

const MAX_POINTS = 20;

/* =========================
   DOM CONTAINERS
========================= */
const container = document.getElementById("stocks") || createContainer();

function createContainer() {
  const el = document.createElement("div");
  el.id = "stocks";
  document.body.appendChild(el);
  return el;
}

/* =========================
   CREATE STOCK CARD
========================= */
function createStockCard(symbol) {
  const card = document.createElement("div");
  card.className = "stock-card";
  card.id = `stock-${symbol}`;

  const title = document.createElement("div");
  title.className = "stock-symbol";
  title.innerText = symbol;

  const price = document.createElement("div");
  price.className = "stock-price";

  const change = document.createElement("div");
  change.className = "stock-change";

  const canvas = document.createElement("canvas");

  card.appendChild(title);
  card.appendChild(price);
  card.appendChild(change);
  card.appendChild(canvas);

  container.appendChild(card);

  // Create chart
  charts[symbol] = new Chart(canvas, {
    type: "line",
    data: {
      labels: [],
      datasets: [{
        label: symbol,
        data: [],
        tension: 0.3
      }]
    },
    options: {
      animation: false,
      responsive: true,
      plugins: { legend: { display: false } },
      scales: { x: { display: false } }
    }
  });

  return { card, price, change };
}

/* =========================
   UPDATE CHART
========================= */
function updateChart(symbol, price) {
  const chart = charts[symbol];
  if (!chart) return;

  chart.data.labels.push("");
  chart.data.datasets[0].data.push(price);

  if (chart.data.labels.length > MAX_POINTS) {
    chart.data.labels.shift();
    chart.data.datasets[0].data.shift();
  }

  chart.update("none");
}

/* =========================
   UPDATE UI CARD
========================= */
function updateCard(symbol, data) {
  let card = document.getElementById(`stock-${symbol}`);

  if (!card) {
    createStockCard(symbol);
    card = document.getElementById(`stock-${symbol}`);
  }

  const priceEl = card.querySelector(".stock-price");
  const changeEl = card.querySelector(".stock-change");

  const price = data?.c || 0;
  const change = data?.d || 0;

  priceEl.innerText = `$${price.toFixed(2)}`;
  changeEl.innerText = change.toFixed(2);

  changeEl.className = "stock-change " + (change >= 0 ? "up" : "down");

  updateChart(symbol, price);
}

/* =========================
   CONNECTION STATUS
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
   WEBSOCKET
========================= */
function connectWebSocket() {
  socket = new WebSocket(WS_URL);

  socket.onopen = () => {
    console.log("✅ WS connected");
    setStatus(true);
    reconnectDelay = 1000;

    // heartbeat
    socket.pingInterval = setInterval(() => {
      if (socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({ type: "ping" }));
      }
    }, 20000);
  };

  socket.onmessage = (event) => {
    let payload;

    try {
      payload = JSON.parse(event.data);
    } catch {
      return;
    }

    const data = payload.data || payload;
    if (!data) return;

    Object.entries(data).forEach(([symbol, value]) => {
      stockCache[symbol] = value;
    });

    scheduleRender();
  };

  socket.onclose = () => {
    console.log("❌ WS disconnected");
    setStatus(false);
    clearInterval(socket.pingInterval);
    reconnect();
  };

  socket.onerror = () => socket.close();
}

/* =========================
   RECONNECT
========================= */
function reconnect() {
  setTimeout(() => {
    reconnectDelay = Math.min(reconnectDelay * 2, maxReconnectDelay);
    connectWebSocket();
  }, reconnectDelay);
}

/* =========================
   BATCHED RENDER
========================= */
function scheduleRender() {
  if (!renderScheduled) {
    renderScheduled = true;
    requestAnimationFrame(renderStocks);
  }
}

function renderStocks() {
  renderScheduled = false;

  Object.entries(stockCache).forEach(([symbol, data]) => {
    updateCard(symbol, data);
  });
}

/* =========================
   INIT
========================= */
document.addEventListener("DOMContentLoaded", () => {
  connectWebSocket();
});
