function drawSparkline(container, payload) {
    if (!payload || !payload.values || !payload.values.length) return;
    const canvas = document.createElement("canvas");
    const width = container.clientWidth || 320;
    const height = container.classList.contains("large-chart") ? 240 : 160;
    canvas.width = width;
    canvas.height = height;
    container.innerHTML = "";
    container.appendChild(canvas);

    const ctx = canvas.getContext("2d");
    const values = payload.values;
    const min = Math.min(...values);
    const max = Math.max(...values);
    const step = width / Math.max(values.length - 1, 1);

    ctx.strokeStyle = "#25c48a";
    ctx.lineWidth = 3;
    ctx.beginPath();
    values.forEach((value, index) => {
        const x = index * step;
        const y = height - ((value - min) / Math.max(max - min, 1)) * (height - 30) - 15;
        if (index === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
    });
    ctx.stroke();

    ctx.fillStyle = "rgba(37,196,138,0.12)";
    ctx.lineTo(width, height);
    ctx.lineTo(0, height);
    ctx.closePath();
    ctx.fill();
}

document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".mini-chart, .line-chart").forEach((element) => {
        const payload = element.dataset.chart ? JSON.parse(element.dataset.chart) : null;
        drawSparkline(element, payload);
    });
});
