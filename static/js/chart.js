(() => {
  const canvas = document.querySelector("#temperatureChart");
  const source = document.querySelector("#forecast-data");
  if (!canvas || !source) return;

  const data = JSON.parse(source.textContent);
  const labels = data.labels.map((value) => value.slice(5, 10).replace("-", "/"));
  const mins = data.mins.map((value) => value == null ? NaN : Number(value));
  const maxs = data.maxs.map((value) => value == null ? NaN : Number(value));
  const values = [...mins, ...maxs].filter(Number.isFinite);
  if (!values.length) {
    canvas.setAttribute("aria-label", "目前沒有足夠的溫度資料可繪製圖表");
    return;
  }

  const ratio = Math.max(1, window.devicePixelRatio || 1);
  const width = canvas.clientWidth || 520;
  const height = 270;
  canvas.width = width * ratio;
  canvas.height = height * ratio;
  const ctx = canvas.getContext("2d");
  ctx.scale(ratio, ratio);

  const pad = { top: 34, right: 22, bottom: 36, left: 30 };
  const minValue = Math.min(...values) - 2;
  const maxValue = Math.max(...values) + 2;
  const x = (index) => pad.left + index * ((width - pad.left - pad.right) / Math.max(1, labels.length - 1));
  const y = (value) => pad.top + (maxValue - value) * ((height - pad.top - pad.bottom) / Math.max(1, maxValue - minValue));

  ctx.font = "11px sans-serif";
  ctx.textAlign = "center";
  labels.forEach((label, index) => {
    ctx.fillStyle = "#708999";
    ctx.fillText(label, x(index), height - 10);
    ctx.strokeStyle = "rgba(200,225,236,.08)";
    ctx.beginPath(); ctx.moveTo(x(index), pad.top); ctx.lineTo(x(index), height - pad.bottom); ctx.stroke();
  });

  const draw = (series, color) => {
    ctx.strokeStyle = color;
    ctx.lineWidth = 2.5;
    ctx.lineJoin = "round";
    ctx.beginPath();
    series.forEach((value, index) => {
      if (!Number.isFinite(value)) return;
      index === 0 ? ctx.moveTo(x(index), y(value)) : ctx.lineTo(x(index), y(value));
    });
    ctx.stroke();
    series.forEach((value, index) => {
      if (!Number.isFinite(value)) return;
      ctx.fillStyle = color;
      ctx.beginPath(); ctx.arc(x(index), y(value), 4, 0, Math.PI * 2); ctx.fill();
      ctx.fillStyle = "#dce8ed";
      ctx.fillText(`${value}°`, x(index), y(value) - 11);
    });
  };
  draw(mins, "#70c8eb");
  draw(maxs, "#f1c96b");
})();
