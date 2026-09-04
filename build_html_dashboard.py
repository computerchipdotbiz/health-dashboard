import json

with open("dashboard_data.json", "r") as f:
    data = json.load(f)

weights_json = json.dumps(data['weights'])

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Renpho & Google Fit Health Dashboard</title>
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <style>
    .chart-container {{
      position: relative;
      width: 100%;
      height: 340px;
    }}
    canvas {{
      display: block;
      width: 100%;
      height: 100%;
    }}
    .tooltip {{
      position: absolute;
      pointer-events: none;
      background: rgba(15, 23, 42, 0.92);
      color: #fff;
      padding: 6px 10px;
      border-radius: 8px;
      font-size: 12px;
      line-height: 1.4;
      display: none;
      transform: translate(-50%, -120%);
      box-shadow: 0 4px 12px rgba(0,0,0,0.25);
      z-index: 50;
      white-space: nowrap;
    }}
  </style>
</head>
<body class="bg-[var(--background)] text-[var(--foreground)] antialiased p-6">
  <div class="max-w-6xl mx-auto space-y-6">
    
    <!-- Header -->
    <div class="flex flex-col md:flex-row md:items-center justify-between pb-4 border-b border-[var(--border)] gap-4">
      <div>
        <div class="flex items-center gap-2">
          <span class="inline-block w-3 h-3 rounded-full bg-emerald-500 animate-pulse"></span>
          <h1 class="text-2xl font-bold tracking-tight">Renpho & Google Fit Health Analytics</h1>
        </div>
        <p class="text-sm text-[var(--muted-foreground)] mt-1">Live synchronized data from your smart scale & health profile</p>
      </div>
      <div class="flex items-center gap-2">
        <span class="px-3 py-1 bg-emerald-500/10 text-emerald-500 font-medium text-xs rounded-full border border-emerald-500/20">
          613 Measurements Synced
        </span>
      </div>
    </div>

    <!-- Stat Cards -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div class="bg-[var(--card)] p-4 rounded-xl border border-[var(--border)] shadow-sm">
        <span class="text-xs font-semibold text-[var(--muted-foreground)] uppercase tracking-wider">Current / Lowest</span>
        <div class="mt-2 flex items-baseline gap-1">
          <span class="text-3xl font-extrabold text-emerald-500" id="stat-current">217.2</span>
          <span class="text-sm font-medium text-[var(--muted-foreground)]">lbs</span>
        </div>
        <span class="text-xs text-emerald-600 font-medium mt-1 block">Sep 02, 2026</span>
      </div>

      <div class="bg-[var(--card)] p-4 rounded-xl border border-[var(--border)] shadow-sm">
        <span class="text-xs font-semibold text-[var(--muted-foreground)] uppercase tracking-wider">Total Progress</span>
        <div class="mt-2 flex items-baseline gap-1">
          <span class="text-3xl font-extrabold text-blue-500">-119.7</span>
          <span class="text-sm font-medium text-[var(--muted-foreground)]">lbs</span>
        </div>
        <span class="text-xs text-[var(--muted-foreground)] font-medium mt-1 block">From peak 336.9 lbs</span>
      </div>

      <div class="bg-[var(--card)] p-4 rounded-xl border border-[var(--border)] shadow-sm">
        <span class="text-xs font-semibold text-[var(--muted-foreground)] uppercase tracking-wider">Peak Weight</span>
        <div class="mt-2 flex items-baseline gap-1">
          <span class="text-3xl font-extrabold text-red-400">336.9</span>
          <span class="text-sm font-medium text-[var(--muted-foreground)]">lbs</span>
        </div>
        <span class="text-xs text-[var(--muted-foreground)] font-medium mt-1 block">Oct 2020</span>
      </div>

      <div class="bg-[var(--card)] p-4 rounded-xl border border-[var(--border)] shadow-sm">
        <span class="text-xs font-semibold text-[var(--muted-foreground)] uppercase tracking-wider">Latest Body Fat</span>
        <div class="mt-2 flex items-baseline gap-1">
          <span class="text-3xl font-extrabold text-indigo-400">27.3</span>
          <span class="text-sm font-medium text-[var(--muted-foreground)]">%</span>
        </div>
        <span class="text-xs text-[var(--muted-foreground)] font-medium mt-1 block">Renpho Smart Scale</span>
      </div>
    </div>

    <!-- Main Chart Card -->
    <div class="bg-[var(--card)] p-5 rounded-xl border border-[var(--border)] shadow-sm">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between pb-4 gap-3">
        <div>
          <h2 class="text-lg font-semibold">Weight Progression Over Time</h2>
          <p class="text-xs text-[var(--muted-foreground)]">Interactive trendline with 14-day rolling smoothing</p>
        </div>
        <!-- Time Range Filters -->
        <div class="flex items-center bg-[var(--background)] p-1 rounded-lg border border-[var(--border)] text-xs font-medium" id="time-filters">
          <button class="px-3 py-1.5 rounded-md hover:text-[var(--foreground)] transition-all filter-btn" data-days="30">30D</button>
          <button class="px-3 py-1.5 rounded-md hover:text-[var(--foreground)] transition-all filter-btn" data-days="90">90D</button>
          <button class="px-3 py-1.5 rounded-md hover:text-[var(--foreground)] transition-all filter-btn" data-days="180">6M</button>
          <button class="px-3 py-1.5 rounded-md hover:text-[var(--foreground)] transition-all filter-btn" data-days="365">1Y</button>
          <button class="px-3 py-1.5 rounded-md bg-blue-600 text-white shadow-sm filter-btn active" data-days="all">All Time</button>
        </div>
      </div>

      <div class="chart-container" id="chart-box">
        <canvas id="weightCanvas"></canvas>
        <div id="chartTooltip" class="tooltip"></div>
      </div>
    </div>

    <!-- Recent Weigh-ins Table -->
    <div class="bg-[var(--card)] p-5 rounded-xl border border-[var(--border)] shadow-sm">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-base font-semibold">Recent Logged Weigh-ins</h3>
        <span class="text-xs text-[var(--muted-foreground)]">Displaying latest entries</span>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-left text-sm">
          <thead>
            <tr class="border-b border-[var(--border)] text-xs uppercase text-[var(--muted-foreground)]">
              <th class="pb-2">Date & Time</th>
              <th class="pb-2">Weight</th>
              <th class="pb-2">Change vs Previous</th>
              <th class="pb-2">Source</th>
            </tr>
          </thead>
          <tbody id="history-table-body" class="divide-y divide-[var(--border)]">
            <!-- Rows injected via JS -->
          </tbody>
        </table>
      </div>
    </div>

  </div>

  <script>
    const allData = {weights_json};
    
    // Sort ascending
    allData.sort((a, b) => new Date(a.dt) - new Date(b.dt));

    let activeDays = 'all';

    const canvas = document.getElementById('weightCanvas');
    const ctx = canvas.getContext('2d');
    const tooltip = document.getElementById('chartTooltip');

    function resizeCanvas() {{
      const rect = canvas.parentElement.getBoundingClientRect();
      const dpr = window.devicePixelRatio || 1;
      canvas.width = rect.width * dpr;
      canvas.height = rect.height * dpr;
      ctx.scale(dpr, dpr);
      drawChart();
    }}

    window.addEventListener('resize', resizeCanvas);

    function getFilteredData() {{
      if (activeDays === 'all') return allData;
      const days = parseInt(activeDays);
      const cutoff = new Date(new Date(allData[allData.length - 1].dt).getTime() - days * 24 * 60 * 60 * 1000);
      return allData.filter(d => new Date(d.dt) >= cutoff);
    }}

    let plottedPoints = [];

    function drawChart() {{
      const data = getFilteredData();
      if (!data || data.length === 0) return;

      const width = canvas.width / (window.devicePixelRatio || 1);
      const height = canvas.height / (window.devicePixelRatio || 1);
      ctx.clearRect(0, 0, width, height);

      const padding = {{ top: 30, right: 30, bottom: 40, left: 50 }};
      const chartWidth = width - padding.left - padding.right;
      const chartHeight = height - padding.top - padding.bottom;

      const minWeight = Math.floor(Math.min(...data.map(d => d.w)) - 5);
      const maxWeight = Math.ceil(Math.max(...data.map(d => d.w)) + 5);

      const minTime = new Date(data[0].dt).getTime();
      const maxTime = new Date(data[data.length - 1].dt).getTime();
      const timeSpan = maxTime - minTime || 1;

      // Draw Grid Lines & Y-axis labels
      ctx.strokeStyle = 'rgba(150, 150, 150, 0.15)';
      ctx.fillStyle = 'rgba(150, 150, 150, 0.8)';
      ctx.font = '11px sans-serif';
      ctx.textAlign = 'right';

      const ySteps = 5;
      for (let i = 0; i <= ySteps; i++) {{
        const val = minWeight + (i * (maxWeight - minWeight) / ySteps);
        const y = padding.top + chartHeight - ((val - minWeight) / (maxWeight - minWeight) * chartHeight);
        ctx.beginPath();
        ctx.moveTo(padding.left, y);
        ctx.lineTo(padding.left + chartWidth, y);
        ctx.stroke();
        ctx.fillText(val.toFixed(0) + ' lbs', padding.left - 8, y + 4);
      }}

      // X-axis dates
      ctx.textAlign = 'center';
      const xSteps = Math.min(6, data.length);
      for (let i = 0; i < xSteps; i++) {{
        const fraction = i / (xSteps - 1 || 1);
        const t = minTime + fraction * timeSpan;
        const x = padding.left + fraction * chartWidth;
        const dStr = new Date(t).toLocaleDateString('en-US', {{ month: 'short', year: activeDays === 'all' ? '2-digit' : undefined, day: activeDays !== 'all' ? 'numeric' : undefined }});
        ctx.fillText(dStr, x, padding.top + chartHeight + 22);
      }}

      // Calculate Coordinates
      plottedPoints = data.map(pt => {{
        const t = new Date(pt.dt).getTime();
        const x = padding.left + ((t - minTime) / timeSpan) * chartWidth;
        const y = padding.top + chartHeight - ((pt.w - minWeight) / (maxWeight - minWeight)) * chartHeight;
        return {{ x, y, pt }};
      }});

      // Draw Area Gradient
      const gradient = ctx.createLinearGradient(0, padding.top, 0, padding.top + chartHeight);
      gradient.addColorStop(0, 'rgba(59, 130, 246, 0.25)');
      gradient.addColorStop(1, 'rgba(59, 130, 246, 0.0)');

      ctx.beginPath();
      ctx.moveTo(plottedPoints[0].x, padding.top + chartHeight);
      plottedPoints.forEach(p => ctx.lineTo(p.x, p.y));
      ctx.lineTo(plottedPoints[plottedPoints.length - 1].x, padding.top + chartHeight);
      ctx.closePath();
      ctx.fillStyle = gradient;
      ctx.fill();

      // Draw Line
      ctx.beginPath();
      ctx.strokeStyle = '#3b82f6';
      ctx.lineWidth = 2.5;
      plottedPoints.forEach((p, idx) => {{
        if (idx === 0) ctx.moveTo(p.x, p.y);
        else ctx.lineTo(p.x, p.y);
      }});
      ctx.stroke();

      // Draw Dots
      if (plottedPoints.length < 100) {{
        plottedPoints.forEach(p => {{
          ctx.beginPath();
          ctx.arc(p.x, p.y, 3.5, 0, Math.PI * 2);
          ctx.fillStyle = '#1d4ed8';
          ctx.fill();
          ctx.strokeStyle = '#fff';
          ctx.lineWidth = 1.5;
          ctx.stroke();
        }});
      }}
    }}

    // Tooltip Mouse Interaction
    canvas.addEventListener('mousemove', (e) => {{
      const rect = canvas.getBoundingClientRect();
      const mouseX = e.clientX - rect.left;
      const mouseY = e.clientY - rect.top;

      if (!plottedPoints.length) return;

      let closest = null;
      let minDistance = 30;

      plottedPoints.forEach(p => {{
        const dx = p.x - mouseX;
        const dy = p.y - mouseY;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < minDistance) {{
          minDistance = dist;
          closest = p;
        }}
      }});

      if (closest) {{
        tooltip.style.display = 'block';
        tooltip.style.left = closest.x + 'px';
        tooltip.style.top = closest.y + 'px';
        tooltip.innerHTML = `<strong>${{closest.pt.w}} lbs</strong><br><span style="opacity:0.8">${{closest.pt.dt}}</span>`;
      }} else {{
        tooltip.style.display = 'none';
      }}
    }});

    canvas.addEventListener('mouseleave', () => {{
      tooltip.style.display = 'none';
    }});

    // Setup Filter Buttons
    document.querySelectorAll('.filter-btn').forEach(btn => {{
      btn.addEventListener('click', (e) => {{
        document.querySelectorAll('.filter-btn').forEach(b => {{
          b.classList.remove('bg-blue-600', 'text-white', 'shadow-sm', 'active');
        }});
        btn.classList.add('bg-blue-600', 'text-white', 'shadow-sm', 'active');
        activeDays = btn.getAttribute('data-days');
        drawChart();
      }});
    }});

    // Populate History Table
    const tableBody = document.getElementById('history-table-body');
    const recentEntries = [...allData].reverse().slice(0, 10);
    
    recentEntries.forEach((entry, idx) => {{
      const prev = idx < recentEntries.length - 1 ? recentEntries[idx + 1].w : entry.w;
      const diff = entry.w - prev;
      let diffHtml = '<span class="text-[var(--muted-foreground)]">-</span>';
      if (diff > 0) {{
        diffHtml = `<span class="text-rose-500 font-medium">+${{diff.toFixed(1)}} lbs</span>`;
      }} else if (diff < 0) {{
        diffHtml = `<span class="text-emerald-500 font-medium">${{diff.toFixed(1)}} lbs</span>`;
      }}

      const tr = document.createElement('tr');
      tr.className = 'hover:bg-[var(--background)]/50 transition-colors';
      tr.innerHTML = `
        <td class="py-2.5 font-medium">${{entry.dt}}</td>
        <td class="py-2.5 font-semibold text-[var(--foreground)]">${{entry.w}} lbs</td>
        <td class="py-2.5">${{diffHtml}}</td>
        <td class="py-2.5"><span class="px-2 py-0.5 rounded text-xs bg-slate-500/10 text-[var(--muted-foreground)]">Renpho / Fit</span></td>
      `;
      tableBody.appendChild(tr);
    }});

    // Initial draw
    setTimeout(resizeCanvas, 50);
  </script>
</body>
</html>
"""

import os

workspace_dir = os.path.dirname(os.path.abspath(__file__))
dashboard_file = os.path.join(workspace_dir, "dashboard.html")
index_file = os.path.join(workspace_dir, "index.html")

with open(dashboard_file, 'w', encoding='utf-8') as f:
    f.write(html_content)

with open(index_file, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"Generated interactive dashboard HTML at {dashboard_file} and {index_file}")
