(() => {
  const form = document.querySelector("[data-weather-form]");
  const input = document.querySelector("#cityInput");
  const geolocateButton = document.querySelector("[data-geolocate]");
  const locationStatus = document.querySelector("[data-location-status]");
  const radar = document.querySelector("[data-radar]");
  const clock = document.querySelector("[data-clock]");
  const results = document.querySelector("[data-weather-results]");

  const updateClock = () => {
    if (!clock) return;
    clock.textContent = new Intl.DateTimeFormat("zh-TW", {
      hour: "2-digit", minute: "2-digit", hour12: false,
    }).format(new Date());
  };
  updateClock();
  window.setInterval(updateClock, 30000);

  form?.addEventListener("submit", async (event) => {
    if (!results || !input.value.trim()) return;
    event.preventDefault();
    const button = form.querySelector("button[type='submit']");
    button.disabled = true;
    button.textContent = "正在查詢…";
    locationStatus.classList.remove("is-error");
    locationStatus.textContent = "正在取得最新預報…";
    try {
      const response = await fetch(`/api/v1/weather?city=${encodeURIComponent(input.value.trim())}`, {
        headers: { Accept: "application/json" },
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.error?.message || "暫時無法取得天氣。請稍後再試。");
      renderWeather(payload.data);
      locationStatus.textContent = `已更新 ${payload.data.location} 天氣`;
      history.replaceState(null, "", `/?city=${encodeURIComponent(input.value.trim())}`);
    } catch (error) {
      locationStatus.textContent = error.message;
      locationStatus.classList.add("is-error");
    } finally {
      button.disabled = false;
      button.innerHTML = "查看天氣 <span aria-hidden='true'>→</span>";
    }
  });

  const valueOrDash = (value, suffix = "") => value == null ? "—" : `${value}${suffix}`;
  const weatherIcon = (summary = "") => {
    if (summary.includes("雷")) return "⛈";
    if (summary.includes("雨")) return "☂";
    if (summary.includes("晴") && (summary.includes("雲") || summary.includes("陰"))) return "⛅";
    if (summary.includes("晴")) return "☀";
    return "☁";
  };
  const formatDateTime = (value) => new Intl.DateTimeFormat("zh-TW", {
    month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit", hour12: false,
  }).format(new Date(value));
  const setText = (selector, value) => {
    const node = results.querySelector(selector);
    if (node) node.textContent = value;
  };

  const renderWeather = (report) => {
    const current = report.current;
    setText("[data-result-location]", report.location);
    setText("[data-result-updated]", `${formatDateTime(report.updated_at)} 更新`);
    setText("[data-result-icon]", weatherIcon(current.summary));
    setText("[data-result-temperature]", valueOrDash(current.max_temp_c ?? current.min_temp_c, "°"));
    setText("[data-result-summary]", current.summary);
    setText("[data-result-min]", valueOrDash(current.min_temp_c, "°"));
    setText("[data-result-max]", valueOrDash(current.max_temp_c, "°"));
    setText("[data-result-rain]", valueOrDash(current.rain_probability, "%"));

    const detail = results.querySelector("[data-result-detail]");
    detail.href = `/weather?city=${encodeURIComponent(report.location)}`;
    const hourly = results.querySelector("[data-result-hourly]");
    hourly.replaceChildren(...report.hourly.map((period) => {
      const card = document.createElement("article");
      card.className = "api-hourly-card";
      const time = document.createElement("time");
      time.dateTime = period.start_time;
      time.textContent = formatDateTime(period.start_time);
      const icon = document.createElement("span");
      icon.className = "api-hourly-icon";
      icon.textContent = weatherIcon(period.summary);
      icon.setAttribute("aria-hidden", "true");
      const summary = document.createElement("p");
      summary.textContent = period.summary;
      const metrics = document.createElement("div");
      metrics.textContent = `${valueOrDash(period.min_temp_c, "°")} / ${valueOrDash(period.max_temp_c, "°")} · 降雨 ${valueOrDash(period.rain_probability, "%")}`;
      card.append(time, icon, summary, metrics);
      return card;
    }));
    results.hidden = false;
    results.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  geolocateButton?.addEventListener("click", () => {
    if (!navigator.geolocation) {
      locationStatus.textContent = "此瀏覽器不支援定位功能。";
      return;
    }
    geolocateButton.disabled = true;
    locationStatus.textContent = "正在取得位置…";
    navigator.geolocation.getCurrentPosition(
      async ({ coords }) => {
        try {
          const url = new URL("https://nominatim.openstreetmap.org/reverse");
          url.searchParams.set("format", "jsonv2");
          url.searchParams.set("lat", coords.latitude);
          url.searchParams.set("lon", coords.longitude);
          url.searchParams.set("accept-language", "zh-TW");
          const response = await fetch(url, { headers: { Accept: "application/json" } });
          if (!response.ok) throw new Error("reverse geocoding failed");
          const { address = {} } = await response.json();
          const city = address.city || address.county || address.state || address.town;
          if (!city) throw new Error("city not found");
          input.value = city.replace("台", "臺");
          locationStatus.textContent = `已找到 ${input.value}`;
          form.requestSubmit();
        } catch {
          locationStatus.textContent = "無法辨識所在縣市，請改用文字搜尋。";
          geolocateButton.disabled = false;
        }
      },
      (error) => {
        locationStatus.textContent = error.code === 1
          ? "未取得定位權限，請改用文字搜尋。"
          : "暫時無法取得位置，請稍後再試。";
        geolocateButton.disabled = false;
      },
      { enableHighAccuracy: false, timeout: 8000, maximumAge: 300000 },
    );
  });

  if (radar) {
    const refreshRadar = () => {
      const url = new URL(radar.src);
      url.searchParams.set("updated", Date.now());
      radar.src = url.toString();
    };
    window.setInterval(refreshRadar, 120000);
    radar.addEventListener("error", () => {
      radar.alt = "雷達回波圖目前無法載入";
    });
  }

  if ("serviceWorker" in navigator) {
    window.addEventListener("load", () => navigator.serviceWorker.register("/static/sw.js"));
  }
})();
