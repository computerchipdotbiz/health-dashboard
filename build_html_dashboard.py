import json
import os

workspace_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(workspace_dir, 'dashboard_data.json')

with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

weights_json = json.dumps(data['weights'])

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Renpho & Google Fit Health Analytics</title>
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
      background: rgba(15, 23, 42, 0.94);
      color: #fff;
      padding: 8px 12px;
      border-radius: 8px;
      font-size: 12px;
      line-height: 1.4;
      display: none;
      transform: translate(-50%, -120%);
      box-shadow: 0 4px 14px rgba(0,0,0,0.35);
      z-index: 50;
      white-space: nowrap;
      border: 1px solid rgba(255,255,255,0.1);
    }}
  </style>
</head>
<body class="bg-[var(--background)] text-[var(--foreground)] antialiased p-4 md:p-6 min-h-screen">
  <div class="max-w-6xl mx-auto space-y-6">
    
    <!-- Header -->
    <div class="flex flex-col md:flex-row md:items-center justify-between pb-4 border-b border-[var(--border)] gap-4">
      <div>
        <div class="flex items-center gap-2.5">
          <span class="inline-block w-3 h-3 rounded-full bg-emerald-500 animate-pulse"></span>
          <h1 class="text-2xl md:text-3xl font-extrabold tracking-tight">Renpho & Google Fit Health Analytics</h1>
        </div>
        <p class="text-sm text-[var(--muted-foreground)] mt-1">Live synchronized scale metrics, weight trends & interactive goal forecasting</p>
      </div>
      <div class="flex items-center gap-2">
        <span class="px-3.5 py-1 bg-emerald-500/10 text-emerald-500 font-semibold text-xs rounded-full border border-emerald-500/20">
          613 Scale Measurements Synced
        </span>
      </div>
    </div>

    <!-- Stat Cards -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div class="bg-[var(--card)] p-4 rounded-xl border border-[var(--border)] shadow-sm">
        <span class="text-xs font-semibold text-[var(--muted-foreground)] uppercase tracking-wider">Current / Lowest</span>
        <div class="mt-2 flex items-baseline gap-1">
          <span class="text-3xl font-black text-emerald-500" id="stat-current">217.2</span>
          <span class="text-sm font-medium text-[var(--muted-foreground)]">lbs</span>
        </div>
        <span class="text-xs text-emerald-600 font-medium mt-1 block">Sep 02, 2026 (All-Time Low)</span>
      </div>

      <div class="bg-[var(--card)] p-4 rounded-xl border border-[var(--border)] shadow-sm">
        <span class="text-xs font-semibold text-[var(--muted-foreground)] uppercase tracking-wider">Total Weight Lost</span>
        <div class="mt-2 flex items-baseline gap-1">
          <span class="text-3xl font-black text-blue-500">-119.7</span>
          <span class="text-sm font-medium text-[var(--muted-foreground)]">lbs</span>
        </div>
        <span class="text-xs text-[var(--muted-foreground)] font-medium mt-1 block">From peak of 336.9 lbs</span>
      </div>

      <div class="bg-[var(--card)] p-4 rounded-xl border border-[var(--border)] shadow-sm">
        <span class="text-xs font-semibold text-[var(--muted-foreground)] uppercase tracking-wider">Peak Weight</span>
        <div class="mt-2 flex items-baseline gap-1">
          <span class="text-3xl font-black text-rose-400">336.9</span>
          <span class="text-sm font-medium text-[var(--muted-foreground)]">lbs</span>
        </div>
        <span class="text-xs text-[var(--muted-foreground)] font-medium mt-1 block">Oct 2020</span>
      </div>

      <div class="bg-[var(--card)] p-4 rounded-xl border border-[var(--border)] shadow-sm">
        <span class="text-xs font-semibold text-[var(--muted-foreground)] uppercase tracking-wider">Latest Body Fat</span>
        <div class="mt-2 flex items-baseline gap-1">
          <span class="text-3xl font-black text-indigo-400">27.3</span>
          <span class="text-sm font-medium text-[var(--muted-foreground)]">%</span>
        </div>
        <span class="text-xs text-[var(--muted-foreground)] font-medium mt-1 block">Renpho Smart Scale</span>
      </div>
    </div>

    <!-- Main Chart Card -->
    <div class="bg-[var(--card)] p-5 rounded-xl border border-[var(--border)] shadow-sm">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between pb-4 gap-3">
        <div>
          <h2 class="text-lg font-bold">Weight Progression Over Time</h2>
          <p class="text-xs text-[var(--muted-foreground)]">Interactive trendline with historical logs</p>
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

    <!-- Goal Forecast & Interactive Step Accelerator Section -->
    <div class="bg-[var(--card)] p-5 md:p-6 rounded-xl border border-[var(--border)] shadow-sm space-y-6">
      
      <!-- Section Header -->
      <div class="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-[var(--border)] gap-4">
        <div class="flex items-center gap-3">
          <div class="p-2.5 rounded-xl bg-emerald-500/10 text-emerald-500 border border-emerald-500/20">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path></svg>
          </div>
          <div>
            <h2 class="text-lg font-bold">Goal Target Projection & Step Accelerator</h2>
            <p class="text-xs text-[var(--muted-foreground)]">Real-time weight goal estimation based on your recent 6-month trajectory and daily step booster</p>
          </div>
        </div>

        <div class="flex items-center gap-3 bg-[var(--background)] px-3.5 py-2 rounded-xl border border-[var(--border)]">
          <span class="text-xs font-semibold text-[var(--muted-foreground)]">Goal Weight:</span>
          <div class="flex items-center gap-1">
            <input type="number" id="targetWeightInput" value="190" step="0.5" min="100" max="300" class="w-16 bg-transparent text-base font-extrabold text-center focus:outline-none text-[var(--foreground)] border-b border-blue-500 focus:border-blue-400" />
            <span class="text-xs font-bold text-[var(--muted-foreground)]">lbs</span>
          </div>
        </div>
      </div>

      <!-- Projection Stat Cards Grid -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        
        <!-- 6-Month Baseline Pace -->
        <div class="bg-[var(--background)] p-4 rounded-xl border border-[var(--border)] flex flex-col justify-between">
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold text-[var(--muted-foreground)] uppercase tracking-wider">6-Mo Historical Pace</span>
            <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-500/10 text-blue-500">Actual Data</span>
          </div>
          <div class="my-2">
            <div class="flex items-baseline gap-1">
              <span class="text-3xl font-black text-blue-500" id="histRateText">-0.49</span>
              <span class="text-xs font-semibold text-[var(--muted-foreground)]">lbs / week</span>
            </div>
            <p class="text-[11px] text-[var(--muted-foreground)] mt-1" id="histLossDetail">-11.5 lbs lost over the last 180 days</p>
          </div>
          <div class="text-[11px] text-[var(--muted-foreground)] border-t border-[var(--border)] pt-2">
            Baseline rate without extra workout
          </div>
        </div>

        <!-- Projected Goal Date (Dynamic) -->
        <div class="bg-[var(--background)] p-4 rounded-xl border border-[var(--border)] flex flex-col justify-between">
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold text-[var(--muted-foreground)] uppercase tracking-wider">Projected Goal Date</span>
            <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/10 text-emerald-500" id="acceleratorBadge">Baseline Pace</span>
          </div>
          <div class="my-2">
            <div class="flex items-baseline gap-2">
              <span class="text-2xl md:text-3xl font-black text-emerald-500" id="projectedDateText">Sep 27, 2027</span>
            </div>
            <p class="text-[11px] text-[var(--muted-foreground)] mt-1" id="projectedWeeksText">~55.8 weeks remaining (27.2 lbs to go)</p>
          </div>
          <div class="text-[11px] text-[var(--muted-foreground)] border-t border-[var(--border)] pt-2 flex items-center justify-between">
            <span>Target: <strong id="goalTargetDisplay" class="text-[var(--foreground)]">190.0 lbs</strong></span>
            <span id="daysRemainingBadge" class="font-medium text-emerald-600">391 days</span>
          </div>
        </div>

        <!-- Effective Rate & Acceleration -->
        <div class="bg-[var(--background)] p-4 rounded-xl border border-[var(--border)] flex flex-col justify-between">
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold text-[var(--muted-foreground)] uppercase tracking-wider">Combined Loss Rate</span>
            <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/10 text-amber-500" id="speedupPill">Base</span>
          </div>
          <div class="my-2">
            <div class="flex items-baseline gap-1">
              <span class="text-3xl font-black text-amber-500" id="effectiveRateText">-0.49</span>
              <span class="text-xs font-semibold text-[var(--muted-foreground)]">lbs / week</span>
            </div>
            <p class="text-[11px] text-[var(--muted-foreground)] mt-1" id="savingsDetail">Adjust step slider below to accelerate</p>
          </div>
          <div class="text-[11px] text-[var(--muted-foreground)] border-t border-[var(--border)] pt-2" id="timeSavedSubtitle">
            Time saved: <strong class="text-[var(--foreground)]">0 weeks</strong>
          </div>
        </div>

      </div>

      <!-- Interactive Daily Step Slider Box -->
      <div class="bg-[var(--background)] p-5 rounded-xl border border-[var(--border)] space-y-4">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <span class="text-sm font-bold flex items-center gap-2 text-[var(--foreground)]">
              <span class="text-xl">👟</span> Daily Step Booster Slider
            </span>
            <p class="text-xs text-[var(--muted-foreground)] mt-0.5">Simulate adding extra daily walking steps (burns ~50 kcal per 1,000 steps at ~215 lbs)</p>
          </div>
          <div class="flex items-center gap-2">
            <span class="text-xs text-[var(--muted-foreground)] font-medium">Daily Boost:</span>
            <span class="px-3 py-1 bg-blue-600 text-white font-extrabold text-sm rounded-lg shadow-sm tracking-wide" id="stepValueBadge">+0 steps/day</span>
          </div>
        </div>

        <!-- Range Slider -->
        <div class="space-y-2 py-1">
          <input type="range" id="stepSlider" min="0" max="15000" step="500" value="0" class="w-full h-3 bg-slate-200 dark:bg-slate-700 rounded-lg appearance-none cursor-pointer accent-blue-600" />
          <div class="flex justify-between text-[11px] text-[var(--muted-foreground)] font-semibold">
            <span>+0 (Baseline)</span>
            <span>+5,000 (+0.5 lb/wk)</span>
            <span>+10,000 (+1.0 lb/wk)</span>
            <span>+15,000 (+1.5 lb/wk)</span>
          </div>
        </div>

        <!-- Live Impact Banner -->
        <div id="impactBanner" class="p-4 rounded-xl bg-blue-500/10 border border-blue-500/20 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
          <div class="flex items-center gap-2.5">
            <span class="text-xl" id="bannerEmoji">🎯</span>
            <span id="bannerSummary" class="text-[var(--foreground)] font-medium leading-relaxed">
              Currently on track to hit <strong>190.0 lbs</strong> at your baseline 6-month pace of <strong>0.49 lbs/week</strong>.
            </span>
          </div>
          <div id="bannerMetric" class="font-bold text-blue-500 text-right whitespace-nowrap">
            +0 extra kcal/day
          </div>
        </div>

      </div>

    </div>

    <!-- Recent Weigh-ins Table -->
    <div class="bg-[var(--card)] p-5 rounded-xl border border-[var(--border)] shadow-sm">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-base font-bold">Recent Logged Weigh-ins</h3>
        <span class="text-xs text-[var(--muted-foreground)]">Displaying latest entries</span>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-left text-sm">
          <thead>
            <tr class="border-b border-[var(--border)] text-xs uppercase text-[var(--muted-foreground)] font-semibold">
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

    // === GOAL PROJECTION & STEP ACCELERATOR LOGIC ===
    const latestEntry = allData[allData.length - 1];
    const latestWeight = latestEntry.w;
    const latestDate = new Date(latestEntry.dt);

    // Compute 6-month historical loss rate
    const sixMonthsAgo = new Date(latestDate.getTime() - 180 * 24 * 60 * 60 * 1000);
    const sixMonthData = allData.filter(d => new Date(d.dt) >= sixMonthsAgo);
    
    let histStartWeight = sixMonthData.length > 0 ? sixMonthData[0].w : latestWeight;
    let histStartDate = sixMonthData.length > 0 ? new Date(sixMonthData[0].dt) : latestDate;
    let daysDiff = Math.max(1, (latestDate - histStartDate) / (1000 * 60 * 60 * 24));
    let weeksDiff = daysDiff / 7.0;
    let histLossLbs = histStartWeight - latestWeight;
    let baseRatePerWeek = weeksDiff > 0 ? Math.max(0.1, histLossLbs / weeksDiff) : 0.5;

    document.getElementById('histRateText').textContent = `-${{baseRatePerWeek.toFixed(2)}}`;
    document.getElementById('histLossDetail').textContent = `-${{histLossLbs.toFixed(1)}} lbs lost over the last ${{Math.round(daysDiff)}} days`;

    const targetInput = document.getElementById('targetWeightInput');
    const stepSlider = document.getElementById('stepSlider');
    const stepValueBadge = document.getElementById('stepValueBadge');
    const projectedDateText = document.getElementById('projectedDateText');
    const projectedWeeksText = document.getElementById('projectedWeeksText');
    const effectiveRateText = document.getElementById('effectiveRateText');
    const savingsDetail = document.getElementById('savingsDetail');
    const timeSavedSubtitle = document.getElementById('timeSavedSubtitle');
    const acceleratorBadge = document.getElementById('acceleratorBadge');
    const speedupPill = document.getElementById('speedupPill');
    const goalTargetDisplay = document.getElementById('goalTargetDisplay');
    const daysRemainingBadge = document.getElementById('daysRemainingBadge');
    const bannerEmoji = document.getElementById('bannerEmoji');
    const bannerSummary = document.getElementById('bannerSummary');
    const bannerMetric = document.getElementById('bannerMetric');

    function updateProjection() {{
      const targetWeight = parseFloat(targetInput.value) || 190.0;
      const extraSteps = parseInt(stepSlider.value) || 0;
      
      goalTargetDisplay.textContent = `${{targetWeight.toFixed(1)}} lbs`;
      stepValueBadge.textContent = `+${{extraSteps.toLocaleString()}} steps/day`;

      const remainingWeight = Math.max(0, latestWeight - targetWeight);
      
      // Step calorie calculation: ~50 kcal per 1000 steps (~215 lbs person)
      // 1 lb of fat = 3,500 kcal
      const extraDailyKcal = (extraSteps / 1000.0) * 50.0;
      const extraWeeklyLbs = (extraDailyKcal * 7.0) / 3500.0;
      
      const totalWeeklyRate = baseRatePerWeek + extraWeeklyLbs;
      effectiveRateText.textContent = `-${{totalWeeklyRate.toFixed(2)}}`;

      // Baseline weeks needed
      const baseWeeksNeeded = remainingWeight / baseRatePerWeek;
      const baseProjectedTime = new Date(latestDate.getTime() + baseWeeksNeeded * 7 * 24 * 60 * 60 * 1000);

      // Accelerated weeks needed
      const accelWeeksNeeded = remainingWeight / totalWeeklyRate;
      const accelProjectedTime = new Date(latestDate.getTime() + accelWeeksNeeded * 7 * 24 * 60 * 60 * 1000);

      const weeksSaved = Math.max(0, baseWeeksNeeded - accelWeeksNeeded);
      const daysRemaining = Math.max(0, Math.round(accelWeeksNeeded * 7));

      const dateOptions = {{ year: 'numeric', month: 'short', day: 'numeric' }};
      projectedDateText.textContent = accelProjectedTime.toLocaleDateString('en-US', dateOptions);
      projectedWeeksText.textContent = `~${{accelWeeksNeeded.toFixed(1)}} weeks remaining (${{remainingWeight.toFixed(1)}} lbs to go)`;
      daysRemainingBadge.textContent = `${{daysRemaining}} days`;

      if (extraSteps === 0) {{
        acceleratorBadge.textContent = 'Baseline Pace';
        acceleratorBadge.className = 'px-2 py-0.5 rounded text-[10px] font-bold bg-blue-500/10 text-blue-500';
        speedupPill.textContent = 'Base';
        speedupPill.className = 'px-2 py-0.5 rounded text-[10px] font-bold bg-slate-500/10 text-[var(--muted-foreground)]';
        savingsDetail.textContent = 'Slide below to simulate step booster!';
        timeSavedSubtitle.innerHTML = 'Time saved: <strong class="text-[var(--foreground)]">0 weeks</strong>';
        bannerEmoji.textContent = '🎯';
        bannerSummary.innerHTML = `Currently on track to hit <strong>${{targetWeight.toFixed(1)}} lbs</strong> on <strong>${{baseProjectedTime.toLocaleDateString('en-US', dateOptions)}}</strong> at your baseline pace.`;
        bannerMetric.textContent = '+0 extra kcal/day';
        bannerMetric.className = 'font-bold text-blue-500 text-right whitespace-nowrap';
      }} else {{
        const monthsSaved = (weeksSaved / 4.345).toFixed(1);
        acceleratorBadge.textContent = `⚡ ${{weeksSaved.toFixed(0)}} Wks Faster`;
        acceleratorBadge.className = 'px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/10 text-emerald-500 animate-pulse';
        speedupPill.textContent = `+${{extraWeeklyLbs.toFixed(2)}} lb/wk`;
        speedupPill.className = 'px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/10 text-amber-500';
        savingsDetail.textContent = `🔥 Shaves off ${{weeksSaved.toFixed(1)}} weeks (~${{monthsSaved}} months sooner!)`;
        timeSavedSubtitle.innerHTML = `Time saved: <strong class="text-emerald-500 font-bold">${{weeksSaved.toFixed(1)}} weeks sooner!</strong>`;
        bannerEmoji.textContent = '🚀';
        bannerSummary.innerHTML = `Boosted by <strong>+${{extraSteps.toLocaleString()}} steps/day</strong> (+${{extraWeeklyLbs.toFixed(2)}} lbs/wk), you will hit <strong>${{targetWeight.toFixed(1)}} lbs</strong> on <strong class="text-emerald-500">${{accelProjectedTime.toLocaleDateString('en-US', dateOptions)}}</strong>!`;
        bannerMetric.textContent = `+${{Math.round(extraDailyKcal)}} kcal/day burned`;
        bannerMetric.className = 'font-bold text-emerald-500 text-right whitespace-nowrap';
      }}
    }}

    targetInput.addEventListener('input', updateProjection);
    stepSlider.addEventListener('input', updateProjection);

    // Initial calculations
    updateProjection();

    // Initial draw
    setTimeout(resizeCanvas, 50);
  </script>
</body>
</html>
"""

workspace_dir = os.path.dirname(os.path.abspath(__file__))
dashboard_file = os.path.join(workspace_dir, "dashboard.html")
index_file = os.path.join(workspace_dir, "index.html")

with open(dashboard_file, 'w', encoding='utf-8') as f:
    f.write(html_content)

with open(index_file, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"Generated interactive dashboard HTML at {dashboard_file} and {index_file}")
