import json

with open("dashboard_data.json", "r") as f:
    data = json.load(f)

weights_json = json.dumps(data['weights'])

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
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
      background: rgba(15, 23, 42, 0.94);
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
    input[type=range] {{
      accent-color: #3b82f6;
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
        <p class="text-sm text-[var(--muted-foreground)] mt-1">Live synchronized data from your smart scale & Google Fit</p>
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
          <span class="text-3xl font-extrabold text-rose-400">336.9</span>
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
          <p class="text-xs text-[var(--muted-foreground)]">Interactive trendline with live smoothing</p>
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

    <!-- 🔮 Interactive Future ETA Projection & Sliding Scale -->
    <div class="bg-[var(--card)] p-5 rounded-xl border border-[var(--border)] shadow-sm space-y-6">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between border-b border-[var(--border)] pb-4 gap-3">
        <div>
          <div class="flex items-center gap-2">
            <span class="text-xl">🎯</span>
            <h2 class="text-lg font-semibold">Future Weight Loss Projection & Milestone ETAs</h2>
          </div>
          <p class="text-xs text-[var(--muted-foreground)] mt-0.5">
            Adjust the sliding rate scale below to recalculate your estimated arrival dates for every milestone in real-time.
          </p>
        </div>
        <div class="flex items-center gap-2">
          <span class="text-xs text-[var(--muted-foreground)]">Baseline:</span>
          <span class="px-2.5 py-1 bg-blue-500/10 text-blue-500 font-bold text-xs rounded-md border border-blue-500/20">
            217.2 lbs (Current)
          </span>
        </div>
      </div>

      <!-- Controls & Sliding Scale -->
      <div class="grid grid-cols-1 md:grid-cols-12 gap-6 items-center bg-[var(--background)] p-4 rounded-xl border border-[var(--border)]">
        
        <!-- Slider Area -->
        <div class="md:col-span-8 space-y-2">
          <div class="flex justify-between items-center">
            <label for="rateSlider" class="text-sm font-semibold text-[var(--foreground)] flex items-center gap-1.5">
              <span>Target Rate of Loss:</span>
              <span id="rateDisplay" class="text-base font-extrabold text-blue-500">1.5 lbs / week</span>
            </label>
            <span class="text-xs font-medium text-[var(--muted-foreground)]" id="calDeficitDisplay">≈ -750 kcal/day deficit</span>
          </div>

          <input 
            type="range" 
            id="rateSlider" 
            min="0.25" 
            max="3.0" 
            step="0.25" 
            value="1.5" 
            class="w-full h-2.5 bg-slate-200 dark:bg-slate-700 rounded-lg appearance-none cursor-pointer"
          >

          <div class="flex justify-between text-[11px] text-[var(--muted-foreground)] px-0.5 font-medium">
            <span>0.25 lbs/wk (Gentle)</span>
            <span>1.0 lbs/wk</span>
            <span>1.5 lbs/wk (Standard)</span>
            <span>2.0 lbs/wk</span>
            <span>3.0 lbs/wk (Aggressive)</span>
          </div>
        </div>

        <!-- Custom Target Input -->
        <div class="md:col-span-4 border-t md:border-t-0 md:border-l border-[var(--border)] pt-4 md:pt-0 md:pl-6 space-y-2">
          <label for="customTargetInput" class="block text-xs font-semibold uppercase text-[var(--muted-foreground)]">
            Custom Goal Target:
          </label>
          <div class="flex items-center gap-2">
            <input 
              type="number" 
              id="customTargetInput" 
              value="185" 
              min="100" 
              max="216" 
              step="1" 
              class="w-24 px-3 py-1.5 bg-[var(--card)] border border-[var(--border)] rounded-lg font-bold text-sm text-[var(--foreground)] focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
            <span class="text-sm font-medium text-[var(--muted-foreground)]">lbs</span>
          </div>
          <p class="text-xs text-emerald-500 font-semibold" id="customTargetEta">ETA: Calculating...</p>
        </div>

      </div>

      <!-- Projection Milestones Table -->
      <div class="overflow-x-auto">
        <table class="w-full text-left text-sm">
          <thead>
            <tr class="border-b border-[var(--border)] text-xs uppercase text-[var(--muted-foreground)]">
              <th class="pb-2 font-semibold">Milestone Weight</th>
              <th class="pb-2 font-semibold">Lbs to Lose</th>
              <th class="pb-2 font-semibold">Weeks Away</th>
              <th class="pb-2 font-semibold">Projected ETA Date</th>
              <th class="pb-2 font-semibold">Days Remaining</th>
              <th class="pb-2 font-semibold text-right">Progress Toward Goal</th>
            </tr>
          </thead>
          <tbody id="etaTableBody" class="divide-y divide-[var(--border)]">
            <!-- Dynamic projection rows injected via JS -->
          </tbody>
        </table>
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

    // Time Filter Buttons
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

    // 🔮 Sliding Scale & Future ETA Calculations
    const currentWeight = 217.2;
    const baseDate = new Date("2026-09-08T00:00:00"); // Current baseline
    const rateSlider = document.getElementById('rateSlider');
    const rateDisplay = document.getElementById('rateDisplay');
    const calDeficitDisplay = document.getElementById('calDeficitDisplay');
    const customTargetInput = document.getElementById('customTargetInput');
    const customTargetEta = document.getElementById('customTargetEta');
    const etaTableBody = document.getElementById('etaTableBody');

    // Milestones definition
    const standardMilestones = [215, 210, 205, 200, 195, 190, 185, 180, 175, 170];

    function calculateETAs() {{
      const ratePerWeek = parseFloat(rateSlider.value);
      rateDisplay.textContent = `${{ratePerWeek.toFixed(2)}} lbs / week`;
      
      const dailyCalDeficit = Math.round((ratePerWeek * 3500) / 7);
      calDeficitDisplay.textContent = `≈ -${{dailyCalDeficit}} kcal/day deficit`;

      const customGoal = parseFloat(customTargetInput.value) || 185;

      // Update custom target ETA
      if (customGoal < currentWeight) {{
        const customLbs = currentWeight - customGoal;
        const customWeeks = customLbs / ratePerWeek;
        const customDays = Math.round(customWeeks * 7);
        const targetDate = new Date(baseDate.getTime() + customDays * 24 * 60 * 60 * 1000);
        const dateStr = targetDate.toLocaleDateString('en-US', {{ month: 'short', day: 'numeric', year: 'numeric' }});
        customTargetEta.innerHTML = `🎯 Target ETA: <span class="font-bold text-[var(--foreground)]">${{dateStr}}</span> (${{customDays}} days / ${{customWeeks.toFixed(1)}} wks)`;
      }} else {{
        customTargetEta.textContent = "Goal reached!";
      }}

      // Build Milestone Rows
      let rowsHtml = '';
      standardMilestones.forEach(m => {{
        if (m < currentWeight) {{
          const lbsToLose = currentWeight - m;
          const weeksAway = lbsToLose / ratePerWeek;
          const daysAway = Math.round(weeksAway * 7);
          const milestoneDate = new Date(baseDate.getTime() + daysAway * 24 * 60 * 60 * 1000);
          const formattedDate = milestoneDate.toLocaleDateString('en-US', {{ weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' }});

          const isCustomMatch = (m === customGoal);
          const rowBg = isCustomMatch ? 'bg-blue-500/10 font-bold border-l-4 border-blue-500' : 'hover:bg-[var(--background)]/60';
          const badgeClass = m <= 200 ? 'bg-indigo-500/15 text-indigo-400 border border-indigo-500/20' : 'bg-blue-500/10 text-blue-500 border border-blue-500/20';

          // Progress percentage towards overall goal of 175 lbs
          const totalGoalSpan = currentWeight - 175;
          const currentProgressSpan = currentWeight - m;
          const pct = Math.min(100, Math.round((currentProgressSpan / totalGoalSpan) * 100));

          rowsHtml += `
            <tr class="${{rowBg}} transition-colors">
              <td class="py-3 font-bold text-[var(--foreground)] flex items-center gap-2">
                <span class="px-2.5 py-0.5 rounded-md text-xs font-extrabold ${{badgeClass}}">${{m}} lbs</span>
                ${{m === 200 ? '<span class="text-xs text-amber-500 font-bold">⭐ Onederland</span>' : ''}}
                ${{isCustomMatch ? '<span class="text-xs text-blue-500 font-bold">🎯 Your Goal</span>' : ''}}
              </td>
              <td class="py-3 font-semibold text-rose-500">-${{lbsToLose.toFixed(1)}} lbs</td>
              <td class="py-3 font-medium text-[var(--muted-foreground)]">${{weeksAway.toFixed(1)}} wks</td>
              <td class="py-3 font-semibold text-emerald-500">${{formattedDate}}</td>
              <td class="py-3 font-medium text-[var(--foreground)]">in ${{daysAway}} days</td>
              <td class="py-3 text-right">
                <div class="w-24 ml-auto bg-slate-200 dark:bg-slate-700 rounded-full h-2 overflow-hidden">
                  <div class="bg-blue-500 h-2 rounded-full" style="width: ${{pct}}%"></div>
                </div>
              </td>
            </tr>
          `;
        }}
      }});

      etaTableBody.innerHTML = rowsHtml;
    }}

    rateSlider.addEventListener('input', calculateETAs);
    customTargetInput.addEventListener('input', calculateETAs);

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

    // Initialize
    calculateETAs();
    setTimeout(resizeCanvas, 50);
  </script>
</body>
</html>
"""

# Write to artifact dir and workspace
artifact_file = r"C:\Users\DigitalArthas\.gemini\antigravity\brain\1ec6b764-ab9d-477a-bc51-69a33c482e05\health_dashboard.html"
workspace_file = r"C:\Users\DigitalArthas\.gemini\antigravity\scratch\google_fit_dashboard\health_dashboard.html"

with open(artifact_file, 'w', encoding='utf-8') as f:
    f.write(html_content)

with open(workspace_file, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"Successfully restored sliding scale & ETA table in both:\n1. {artifact_file}\n2. {workspace_file}")
