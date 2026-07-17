(() => {
  "use strict";

  const NIVEL_COLOR = {
    verde:    "#2ECC71",
    amarillo: "#F4B740",
    naranja:  "#FF8C42",
    rojo:     "#E74C3C",
  };
  const NIVEL_ORDEN = { verde: 0, amarillo: 1, naranja: 2, rojo: 3 };
  const RING_CIRC = 326.7; // 2 * PI * 52 (radio del SVG del anillo de estado)

  /* -----------------------------------------------------------------
     Reloj
     ----------------------------------------------------------------- */
  function tickClock() {
    const el = document.getElementById("clock");
    if (!el) return;
    const now = new Date();
    el.textContent = now.toLocaleTimeString("es-PE", { hour12: false });
  }
  tickClock();
  setInterval(tickClock, 1000);

  /* -----------------------------------------------------------------
     Tarjeta de estado
     ----------------------------------------------------------------- */
  async function cargarEstado() {
    try {
      const res = await fetch("/api/status");
      const data = await res.json();

      document.getElementById("statusZona").textContent = data.zona_critica;
      document.getElementById("statusZonasCount").textContent = data.zonas_monitoreadas;
      document.getElementById("statusSensores").textContent = data.sensores_activos;
      document.getElementById("statusUpdated").textContent = data.actualizado;

      const badge = document.getElementById("statusBadge");
      badge.textContent = data.label.toUpperCase();

      const levelEl = document.getElementById("statusLevel");
      levelEl.textContent = data.label;

      const color = NIVEL_COLOR[data.nivel] || "#6C87A8";
      const ring = document.getElementById("ringFg");
      const pct = (NIVEL_ORDEN[data.nivel] + 1) / 4; // 25% a 100%
      ring.style.stroke = color;
      ring.style.color = color;
      ring.style.strokeDashoffset = String(RING_CIRC * (1 - pct));

      document.documentElement.style.setProperty("--current-level-color", color);
    } catch (err) {
      console.error("No se pudo cargar el estado:", err);
    }
  }

  /* -----------------------------------------------------------------
     Panel de alertas
     ----------------------------------------------------------------- */
  async function cargarAlertas() {
    const list = document.getElementById("alertList");
    const count = document.getElementById("alertsCount");
    try {
      const res = await fetch("/api/alertas");
      const data = await res.json();
      count.textContent = data.alertas.length;

      if (!data.alertas.length) {
        list.innerHTML = '<li class="alert-list__empty">Sin alertas activas por el momento.</li>';
        return;
      }

      list.innerHTML = data.alertas.map((a) => {
        const color = NIVEL_COLOR[a.nivel] || "#6C87A8";
        return `
          <li class="alert-item" style="--nivel-color:${color}">
            <span class="alert-item__bar"></span>
            <div class="alert-item__body">
              <p class="alert-item__title">${escapeHtml(a.titulo)}</p>
              <p class="alert-item__detail">${escapeHtml(a.detalle)}</p>
            </div>
            <span class="alert-item__time">${a.hora}</span>
          </li>`;
      }).join("");
    } catch (err) {
      list.innerHTML = '<li class="alert-list__empty">No se pudieron cargar las alertas.</li>';
      console.error(err);
    }
  }

  /* -----------------------------------------------------------------
     Mapa Leaflet
     ----------------------------------------------------------------- */
  async function inicializarMapa() {
    const mapEl = document.getElementById("map");
    if (!mapEl || typeof L === "undefined") return;

    const map = L.map(mapEl, {
      zoomControl: true,
      attributionControl: true,
    }).setView([-12.0096, -76.8894], 14);

    L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", {
      attribution: '&copy; OpenStreetMap &copy; CARTO',
      maxZoom: 19,
    }).addTo(map);

    try {
      const res = await fetch("/api/zonas");
      const data = await res.json();

      L.circle([data.center.lat, data.center.lng], {
        radius: 900,
        color: "#23D6FF",
        weight: 1,
        fillColor: "#23D6FF",
        fillOpacity: 0.05,
      }).addTo(map);

      data.zonas.forEach((z) => {
        const color = NIVEL_COLOR[z.nivel] || "#6C87A8";
        const icon = L.divIcon({
          className: "",
          html: `<span class="siatd-marker" style="width:14px;height:14px;background:${color};color:${color}"></span>`,
          iconSize: [14, 14],
          iconAnchor: [7, 7],
        });

        L.marker([z.lat, z.lng], { icon }).addTo(map).bindPopup(`
          <b>${escapeHtml(z.nombre)}</b><br/>
          Tipo: ${escapeHtml(z.tipo)}<br/>
          ${escapeHtml(z.sensor)}<br/>
          <em>${escapeHtml(z.ultima_lectura)}</em>
        `);
      });
    } catch (err) {
      console.error("No se pudieron cargar las zonas:", err);
    }

    // Asegura que el mapa recalcule su tamaño tras el layout inicial
    setTimeout(() => map.invalidateSize(), 200);
    window.addEventListener("resize", () => map.invalidateSize());
  }

  /* -----------------------------------------------------------------
     Asistente / chat
     ----------------------------------------------------------------- */
  function initChat() {
    const form = document.getElementById("chatForm");
    const input = document.getElementById("chatInput");
    const messages = document.getElementById("chatMessages");

    function addMessage(text, from) {
      const div = document.createElement("div");
      div.className = `msg msg--${from}`;
      div.textContent = text;
      messages.appendChild(div);
      messages.scrollTop = messages.scrollHeight;
      return div;
    }

    function addTyping() {
      const div = document.createElement("div");
      div.className = "msg msg--bot msg--typing";
      div.innerHTML = "<span></span><span></span><span></span>";
      messages.appendChild(div);
      messages.scrollTop = messages.scrollHeight;
      return div;
    }

    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const texto = input.value.trim();
      if (!texto) return;

      addMessage(texto, "user");
      input.value = "";
      const typing = addTyping();

      try {
        const res = await fetch("/api/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ mensaje: texto }),
        });
        const data = await res.json();
        typing.remove();
        addMessage(data.respuesta, "bot");
      } catch (err) {
        typing.remove();
        addMessage("No pude conectarme con el servidor. Intenta nuevamente.", "bot");
        console.error(err);
      }
    });
  }

  /* -----------------------------------------------------------------
     Navegación: sidebar / tabbar móvil + panel del asistente
     ----------------------------------------------------------------- */
  function initNav() {
    const content = document.querySelector(".content");
    const sidebarItems = document.querySelectorAll(".sidebar__nav li");
    const tabbarItems = document.querySelectorAll(".tabbar__item[data-tab]");
    const assistant = document.getElementById("assistant");
    const fab = document.getElementById("assistantFab");
    const closeBtn = document.getElementById("assistantClose");
    const tabbarChat = document.getElementById("tabbarChat");

    function setTab(tab) {
      content.className = `content tab-${tab}`;
      sidebarItems.forEach((li) => li.classList.toggle("active", li.dataset.tab === tab));
      tabbarItems.forEach((btn) => btn.classList.toggle("active", btn.dataset.tab === tab));
    }
    setTab("panel");

    sidebarItems.forEach((li) => li.addEventListener("click", () => {
      if (li.dataset.tab === "chat") { openAssistant(); return; }
      setTab(li.dataset.tab);
    }));
    tabbarItems.forEach((btn) => btn.addEventListener("click", () => setTab(btn.dataset.tab)));

    function openAssistant() {
      assistant.classList.add("is-open");
    }
    function closeAssistant() {
      assistant.classList.remove("is-open");
    }

    fab && fab.addEventListener("click", openAssistant);
    closeBtn && closeBtn.addEventListener("click", closeAssistant);
    tabbarChat && tabbarChat.addEventListener("click", openAssistant);
  }

  /* -----------------------------------------------------------------
     Utilidades
     ----------------------------------------------------------------- */
  function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str ?? "";
    return div.innerHTML;
  }

  /* -----------------------------------------------------------------
     Arranque
     ----------------------------------------------------------------- */
  document.addEventListener("DOMContentLoaded", () => {
    initNav();
    initChat();
    inicializarMapa();
    cargarEstado();
    cargarAlertas();

    setInterval(cargarEstado, 30000);
    setInterval(cargarAlertas, 30000);
  });
})();
