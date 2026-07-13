(() => {
  const form = document.querySelector("[data-weather-form]");
  const input = document.querySelector("#cityInput");
  const geolocateButton = document.querySelector("[data-geolocate]");
  const locationStatus = document.querySelector("[data-location-status]");
  const radar = document.querySelector("[data-radar]");
  const clock = document.querySelector("[data-clock]");

  const updateClock = () => {
    if (!clock) return;
    clock.textContent = new Intl.DateTimeFormat("zh-TW", {
      hour: "2-digit", minute: "2-digit", hour12: false,
    }).format(new Date());
  };
  updateClock();
  window.setInterval(updateClock, 30000);

  form?.addEventListener("submit", () => {
    const button = form.querySelector("button[type='submit']");
    button.disabled = true;
    button.textContent = "正在查詢…";
  });

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
