import json
import os
import datetime

workspace_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(workspace_dir, 'dashboard_data.json')

with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

weights_json = json.dumps(data['weights'])
avg_steps = data.get('avg_45d_steps', 4227)
weekly = data.get('weekly_stats', {})
anomalies = data.get('anomalies', [])
past_reports = data.get('past_reports', [])

reports_json = json.dumps(past_reports)
anomalies_json = json.dumps(anomalies)
refreshed_on = data.get('last_updated', datetime.datetime.now().strftime('%b %d, %Y'))

# Server-side milestone generation (Progressive enhancement fallback)
all_weights = sorted(data['weights'], key=lambda x: x['dt'])
latest_entry = all_weights[-1] if all_weights else {'w': 217.2, 'dt': '2026-09-02'}
latest_w = latest_entry['w']

def parse_dt(dt_str):
    try:
        return datetime.datetime.strptime(dt_str[:10], '%Y-%m-%d')
    except Exception:
        return datetime.datetime.now()

latest_dt = parse_dt(latest_entry['dt'])

# 6-month historical loss rate calculation
six_mo_ago = latest_dt - datetime.timedelta(days=180)
six_mo_data = [d for d in all_weights if parse_dt(d['dt']) >= six_mo_ago]
if six_mo_data:
    start_w = six_mo_data[0]['w']
    start_dt = parse_dt(six_mo_data[0]['dt'])
    days_diff = max(1, (latest_dt - start_dt).days)
    base_rate = max(0.2, (start_w - latest_w) / (days_diff / 7.0))
else:
    base_rate = 0.49

milestone_targets = [215, 210, 205, 200, 195, 190, 185, 180, 175]
milestones_html_list = []
for target in milestone_targets:
    rem = max(0.0, latest_w - target)
    weeks = rem / base_rate
    proj_date = latest_dt + datetime.timedelta(days=weeks * 7)
    proj_str = proj_date.strftime('%b %d, %Y')
    
    special_tag = ''
    if target == 200:
        special_tag = '<span class="ml-2 px-2 py-0.5 text-[10px] font-extrabold bg-purple-500/10 text-purple-400 border border-purple-500/20 rounded-md uppercase">Onederland 🎉</span>'
    elif target == 190:
        special_tag = '<span class="ml-2 px-2 py-0.5 text-[10px] font-extrabold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded-md uppercase">Target Goal 🎯</span>'
    
    milestones_html_list.append(f"""
      <tr class="hover:bg-[var(--background)]/50 transition-colors">
        <td class="py-3 px-4 font-bold text-base flex items-center">
          {target} lbs {special_tag}
        </td>
        <td class="py-3 px-4 text-[var(--foreground)] font-semibold">
          -{rem:.1f} lbs
        </td>
        <td class="py-3 px-4 text-[var(--muted-foreground)] font-medium">
          {proj_str}
          <span class="text-xs block text-[var(--muted-foreground)]/70">~{weeks:.1f} wks</span>
        </td>
        <td class="py-3 px-4 font-bold text-[var(--foreground)]">
          {proj_str}
          <span class="text-xs block font-medium opacity-80">~{weeks:.1f} wks</span>
        </td>
        <td class="py-3 px-4 text-right">
          <span class="text-[var(--muted-foreground)] font-medium">0 days</span>
        </td>
      </tr>
    """)
initial_milestones_html = "\n".join(milestones_html_list)

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate" />
  <meta http-equiv="Pragma" content="no-cache" />
  <meta http-equiv="Expires" content="0" />
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
    input[type=range]::-webkit-slider-thumb {{
      cursor: grab;
    }}
    input[type=range]:active::-webkit-slider-thumb {{
      cursor: grabbing;
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
        <p class="text-sm text-[var(--muted-foreground)] mt-1">Live synchronized scale metrics, weight trends & interactive 5-lb milestone forecasts • <span class="font-semibold text-emerald-500">Data refreshed on {refreshed_on}</span></p>
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
          <span class="text-3xl font-black text-emerald-500" id="stat-current">{latest_w}</span>
          <span class="text-sm font-medium text-[var(--muted-foreground)]">lbs</span>
        </div>
        <span class="text-xs text-emerald-600 font-medium mt-1 block">{weekly.get('period_end', 'Sep 02, 2026')} (All-Time Low)</span>
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
        <span class="text-xs font-semibold text-[var(--muted-foreground)] uppercase tracking-wider">45-Day Step Avg</span>
        <div class="mt-2 flex items-baseline gap-1">
          <span class="text-3xl font-black text-amber-500">{avg_steps:,}</span>
          <span class="text-sm font-medium text-[var(--muted-foreground)]">steps/day</span>
        </div>
        <span class="text-xs text-[var(--muted-foreground)] font-medium mt-1 block">Synced from Pixel Watch & Fit</span>
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

    <!-- Goal Forecast & Step Accelerator Section -->
    <div class="bg-[var(--card)] p-5 md:p-6 rounded-xl border border-[var(--border)] shadow-sm space-y-6">
      
      <!-- Section Header -->
      <div class="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-[var(--border)] gap-4">
        <div class="flex items-center gap-3">
          <div class="p-2.5 rounded-xl bg-blue-500/10 text-blue-500 border border-blue-500/20">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
          </div>
          <div>
            <h2 class="text-lg font-bold">Step Booster & Goal Acceleration Simulator</h2>
            <p class="text-xs text-[var(--muted-foreground)]">Calculate exact speed-up from adding extra daily steps to your current 45-day baseline</p>
          </div>
        </div>

        <div class="flex items-center gap-3 bg-[var(--background)] px-3.5 py-2 rounded-xl border border-[var(--border)]">
          <span class="text-xs font-semibold text-[var(--muted-foreground)]">45-Day Baseline:</span>
          <span class="text-sm font-extrabold text-amber-500">{avg_steps:,} steps/day</span>
        </div>
      </div>

      <!-- Interactive Step Slider Card -->
      <div class="bg-[var(--background)] p-5 rounded-xl border border-[var(--border)] space-y-4">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <span class="text-sm font-bold flex items-center gap-2 text-[var(--foreground)]">
              <span class="text-xl">👟</span> Extra Steps Added Per Day (X)
            </span>
            <p class="text-xs text-[var(--muted-foreground)] mt-0.5">
              Current 45-day average: <strong class="text-[var(--foreground)]">{avg_steps:,} steps/day</strong>. Slide to simulate adding extra daily walking.
            </p>
          </div>
          <div class="flex items-center gap-2">
            <span class="px-3.5 py-1.5 bg-blue-600 text-white font-black text-sm rounded-xl shadow-sm tracking-wide" id="stepValueBadge">+0 extra steps/day</span>
          </div>
        </div>

        <!-- Range Slider -->
        <div class="space-y-2 py-1">
          <input type="range" id="stepSlider" min="0" max="15000" step="500" value="0" oninput="renderMilestones()" onchange="renderMilestones()" class="w-full h-3.5 bg-slate-200 dark:bg-slate-700 rounded-lg appearance-none cursor-pointer accent-blue-600" />
          <div class="flex justify-between text-[11px] text-[var(--muted-foreground)] font-semibold">
            <span>+0 (Baseline: {avg_steps:,})</span>
            <span>+5,000 (Total: {avg_steps + 5000:,})</span>
            <span>+10,000 (Total: {avg_steps + 10000:,})</span>
            <span>+15,000 (Total: {avg_steps + 15000:,})</span>
          </div>
        </div>

        <!-- Dynamic Impact Equation Banner -->
        <div id="impactEquationBox" class="p-4 rounded-xl bg-blue-500/10 border border-blue-500/20 space-y-2">
          <div class="flex flex-col md:flex-row md:items-center justify-between gap-2">
            <div class="text-sm font-bold text-[var(--foreground)] flex items-center gap-2">
              <span class="text-lg">🔥</span>
              <span id="equationText">If you stay at your 45-day baseline of <strong>{avg_steps:,} steps/day</strong>, your loss rate is <strong>-{base_rate:.2f} lbs/week</strong>.</span>
            </div>
            <div class="text-xs font-bold text-blue-500 bg-blue-500/10 px-3 py-1 rounded-lg border border-blue-500/20 whitespace-nowrap" id="totalRateBadge">
              Total Rate: -{base_rate:.2f} lbs / week
            </div>
          </div>
          <p class="text-xs text-[var(--muted-foreground)]" id="equationSubtext">
            Baseline 6-month loss rate is <strong>-{base_rate:.2f} lbs/week</strong> at {avg_steps:,} steps/day. Each +1,000 extra daily steps burns ~50 kcal/day (~0.10 lb fat/week).
          </p>
        </div>

      </div>

      <!-- 5-lb Weight Loss Milestones Table -->
      <div class="space-y-3">
        <div class="flex items-center justify-between">
          <div>
            <h3 class="text-base font-bold text-[var(--foreground)] flex items-center gap-2">
              <span>🎯</span> 5-lb Milestone Target Dates
            </h3>
            <p class="text-xs text-[var(--muted-foreground)]">Projected completion dates for each 5-lb interval from current weight ({latest_w} lbs)</p>
          </div>
          <span class="text-xs font-bold px-2.5 py-1 rounded-lg bg-blue-500/10 text-blue-500" id="milestoneSpeedBadge">
            Baseline Pace (-{base_rate:.2f} lb/wk)
          </span>
        </div>

        <div class="overflow-x-auto rounded-xl border border-[var(--border)]">
          <table class="w-full text-left text-sm">
            <thead class="bg-[var(--background)]">
              <tr class="border-b border-[var(--border)] text-xs uppercase text-[var(--muted-foreground)] font-bold">
                <th class="py-3 px-4">Milestone Goal</th>
                <th class="py-3 px-4">Remaining</th>
                <th class="py-3 px-4">Baseline Date (No Extra Steps)</th>
                <th class="py-3 px-4">Accelerated Date (With Extra Steps)</th>
                <th class="py-3 px-4 text-right">Time Saved</th>
              </tr>
            </thead>
            <tbody id="milestones-table-body" class="divide-y divide-[var(--border)] bg-[var(--card)]">
{initial_milestones_html}
            </tbody>
          </table>
        </div>
      </div>

    </div>

    <!-- ========================================================= -->
    <!-- SECTION 2: 💓 HEART RATE & CARDIOVASCULAR HEALTH          -->
    <!-- ========================================================= -->
    <div class="space-y-4">
      <div class="flex items-center justify-between">
        <h2 class="text-xl font-bold tracking-tight flex items-center gap-2">
          <span>💓</span> Heart Rate & Cardiovascular Health
        </h2>
        <span class="text-xs text-[var(--muted-foreground)]">Renpho Smart Ring Continuous Tracking</span>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div class="bg-[var(--card)] p-5 rounded-xl border border-[var(--border)] shadow-sm">
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold text-[var(--muted-foreground)] uppercase tracking-wider">Weekly Average HR</span>
            <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-500/10 text-rose-500">24/7 Continuous</span>
          </div>
          <div class="mt-2 flex items-baseline gap-1">
            <span class="text-3xl font-black text-rose-500">{weekly.get('hr_avg', 82.5)}</span>
            <span class="text-sm font-medium text-[var(--muted-foreground)]">BPM</span>
          </div>
          <p class="text-xs text-[var(--muted-foreground)] mt-1">Normal daily operational rhythm</p>
        </div>

        <div class="bg-[var(--card)] p-5 rounded-xl border border-[var(--border)] shadow-sm">
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold text-[var(--muted-foreground)] uppercase tracking-wider">Overnight Resting Low (RHR)</span>
            <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/10 text-emerald-500">Recovery Baseline</span>
          </div>
          <div class="mt-2 flex items-baseline gap-1">
            <span class="text-3xl font-black text-emerald-500">{weekly.get('rhr_min', 52)}</span>
            <span class="text-sm font-medium text-[var(--muted-foreground)]">BPM</span>
          </div>
          <p class="text-xs text-[var(--muted-foreground)] mt-1">Deep sleep recovery baseline</p>
        </div>

        <div class="bg-[var(--card)] p-5 rounded-xl border border-[var(--border)] shadow-sm">
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold text-[var(--muted-foreground)] uppercase tracking-wider">Peak Active HR</span>
            <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/10 text-amber-500">High Intensity</span>
          </div>
          <div class="mt-2 flex items-baseline gap-1">
            <span class="text-3xl font-black text-amber-500">{weekly.get('hr_peak_max', 129)}</span>
            <span class="text-sm font-medium text-[var(--muted-foreground)]">BPM</span>
          </div>
          <p class="text-xs text-[var(--muted-foreground)] mt-1">Recorded during peak walking cadence</p>
        </div>
      </div>
    </div>

    <!-- ========================================================= -->
    <!-- SECTION 3: 🫁 BLOOD OXYGEN SATURATION (SpO2)              -->
    <!-- ========================================================= -->
    <div class="space-y-4">
      <div class="flex items-center justify-between">
        <h2 class="text-xl font-bold tracking-tight flex items-center gap-2">
          <span>🫁</span> Blood Oxygen Saturation (SpO2)
        </h2>
        <span class="text-xs text-[var(--muted-foreground)]">Continuous Ring Pulse Oximetry</span>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div class="bg-[var(--card)] p-5 rounded-xl border border-[var(--border)] shadow-sm">
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold text-[var(--muted-foreground)] uppercase tracking-wider">Weekly SpO2 Average</span>
            <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-cyan-500/10 text-cyan-500">Optimal</span>
          </div>
          <div class="mt-2 flex items-baseline gap-1">
            <span class="text-3xl font-black text-cyan-500">{weekly.get('spo2_avg', 97.9)}</span>
            <span class="text-sm font-medium text-[var(--muted-foreground)]">%</span>
          </div>
          <p class="text-xs text-[var(--muted-foreground)] mt-1">Excellent oxygenation efficiency</p>
        </div>

        <div class="bg-[var(--card)] p-5 rounded-xl border border-[var(--border)] shadow-sm">
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold text-[var(--muted-foreground)] uppercase tracking-wider">Recorded SpO2 Range</span>
            <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/10 text-emerald-500">Stable</span>
          </div>
          <div class="mt-2 flex items-baseline gap-1">
            <span class="text-3xl font-black text-emerald-500">{weekly.get('spo2_min', 96.0)}% – 100%</span>
          </div>
          <p class="text-xs text-[var(--muted-foreground)] mt-1">Zero hypoxic dips below 95%</p>
        </div>

        <div class="bg-[var(--card)] p-5 rounded-xl border border-[var(--border)] shadow-sm flex flex-col justify-between">
          <span class="text-xs font-bold text-[var(--muted-foreground)] uppercase tracking-wider">Oxygen Stability Status</span>
          <div class="flex items-center gap-2 mt-2">
            <span class="w-3 h-3 rounded-full bg-emerald-500 animate-pulse"></span>
            <span class="text-lg font-extrabold text-emerald-500">Optimal & Consistent</span>
          </div>
          <p class="text-xs text-[var(--muted-foreground)] mt-1">Respiratory stability throughout day & sleep</p>
        </div>
      </div>
    </div>

    <!-- ========================================================= -->
    <!-- SECTION 4: 🔥 ACTIVE CALORIE BURN VS. STEPS               -->
    <!-- ========================================================= -->
    <div class="space-y-4">
      <div class="flex items-center justify-between">
        <h2 class="text-xl font-bold tracking-tight flex items-center gap-2">
          <span>🔥</span> Energy Expenditure & Activity Cadence
        </h2>
        <span class="text-xs text-[var(--muted-foreground)]">Daily Ring & Phone Telemetry</span>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="bg-[var(--card)] p-5 rounded-xl border border-[var(--border)] shadow-sm">
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold text-[var(--muted-foreground)] uppercase tracking-wider">Daily Active Burn (Ring)</span>
            <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-orange-500/10 text-orange-500">Active Output</span>
          </div>
          <div class="mt-2 flex items-baseline gap-1">
            <span class="text-3xl font-black text-orange-500">~280 – 365</span>
            <span class="text-sm font-medium text-[var(--muted-foreground)]">kcal / day</span>
          </div>
          <p class="text-xs text-[var(--muted-foreground)] mt-1">Directly drives weekly fat loss deficit</p>
        </div>

        <div class="bg-[var(--card)] p-5 rounded-xl border border-[var(--border)] shadow-sm">
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold text-[var(--muted-foreground)] uppercase tracking-wider">Weekly Calorie Deficit Value</span>
            <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/10 text-emerald-500">Fat Loss Impact</span>
          </div>
          <div class="mt-2 flex items-baseline gap-1">
            <span class="text-3xl font-black text-emerald-500">~1,750+</span>
            <span class="text-sm font-medium text-[var(--muted-foreground)]">kcal / week</span>
          </div>
          <p class="text-xs text-[var(--muted-foreground)] mt-1">Equivalent to ~0.50 lb fat loss pace</p>
        </div>
      </div>
    </div>

    <!-- ========================================================= -->
    <!-- SECTION 5: 🌙 SLEEP & RECOVERY                            -->
    <!-- ========================================================= -->
    <div class="space-y-4">
      <div class="flex items-center justify-between">
        <h2 class="text-xl font-bold tracking-tight flex items-center gap-2">
          <span>🌙</span> Sleep & Overnight Restoration
        </h2>
        <span class="text-xs text-[var(--muted-foreground)]">Overnight Ring Telemetry</span>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div class="bg-[var(--card)] p-5 rounded-xl border border-[var(--border)] shadow-sm">
          <span class="text-xs font-bold text-[var(--muted-foreground)] uppercase tracking-wider">Sleep Duration Target</span>
          <div class="mt-2 flex items-baseline gap-1">
            <span class="text-3xl font-black text-indigo-400">7.5</span>
            <span class="text-sm font-medium text-[var(--muted-foreground)]">hrs / night</span>
          </div>
          <p class="text-xs text-[var(--muted-foreground)] mt-1">Optimal hormonal and metabolic recovery</p>
        </div>

        <div class="bg-[var(--card)] p-5 rounded-xl border border-[var(--border)] shadow-sm">
          <span class="text-xs font-bold text-[var(--muted-foreground)] uppercase tracking-wider">Deep Recovery Window</span>
          <div class="mt-2 flex items-baseline gap-1">
            <span class="text-3xl font-black text-blue-400">12:30 AM – 4:00 AM</span>
          </div>
          <p class="text-xs text-[var(--muted-foreground)] mt-1">Lowest resting HR (52 BPM) recorded</p>
        </div>

        <div class="bg-[var(--card)] p-5 rounded-xl border border-[var(--border)] shadow-sm">
          <span class="text-xs font-bold text-[var(--muted-foreground)] uppercase tracking-wider">Overnight SpO2 Stability</span>
          <div class="mt-2 flex items-baseline gap-1">
            <span class="text-3xl font-black text-emerald-400">97 – 99%</span>
          </div>
          <p class="text-xs text-[var(--muted-foreground)] mt-1">Consistent airflow and oxygenation</p>
        </div>
      </div>
    </div>

    <!-- ========================================================= -->
    <!-- SECTION 6: ⚡ WEEKLY HIGHLIGHTS & ANOMALY DETECTION        -->
    <!-- ========================================================= -->
    <div class="bg-[var(--card)] p-5 md:p-6 rounded-xl border border-[var(--border)] shadow-sm space-y-4">
      <div class="flex items-center justify-between pb-3 border-b border-[var(--border)]">
        <div>
          <h2 class="text-lg font-bold flex items-center gap-2">
            <span>⚡</span> Weekly Highlights & Anomaly Analysis
          </h2>
          <p class="text-xs text-[var(--muted-foreground)]">Automated health intelligence report generated for Week of {weekly.get('period_end', '2026-09-02')}</p>
        </div>
        <span class="px-3 py-1 bg-purple-500/10 text-purple-400 font-bold text-xs rounded-full border border-purple-500/20">
          Weekly Audit
        </span>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4" id="anomaly-container">
        <!-- Anomaly Callout Cards injected via JS -->
      </div>
    </div>

    <!-- ========================================================= -->
    <!-- SECTION 7: 📁 52-WEEK HISTORICAL ARCHIVE                  -->
    <!-- ========================================================= -->
    <div class="bg-[var(--card)] p-5 md:p-6 rounded-xl border border-[var(--border)] shadow-sm space-y-4">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between pb-3 border-b border-[var(--border)] gap-2">
        <div>
          <h2 class="text-lg font-bold flex items-center gap-2">
            <span>📁</span> Weekly Reports Historical Archive
          </h2>
          <p class="text-xs text-[var(--muted-foreground)]">Permanent archive of all past Friday weekly reports. Each week is permanently preserved.</p>
        </div>
        <span class="text-xs font-semibold text-[var(--muted-foreground)]" id="archiveCountBadge">
          1 Report Archived
        </span>
      </div>

      <div class="overflow-x-auto rounded-xl border border-[var(--border)]">
        <table class="w-full text-left text-sm">
          <thead class="bg-[var(--background)]">
            <tr class="border-b border-[var(--border)] text-xs uppercase text-[var(--muted-foreground)] font-bold">
              <th class="py-3 px-4">Report Date</th>
              <th class="py-3 px-4">Weight</th>
              <th class="py-3 px-4">Weekly Change</th>
              <th class="py-3 px-4">Avg Daily Steps</th>
              <th class="py-3 px-4">Resting HR</th>
              <th class="py-3 px-4">Avg SpO2</th>
              <th class="py-3 px-4 text-right">Action</th>
            </tr>
          </thead>
          <tbody id="archive-table-body" class="divide-y divide-[var(--border)] bg-[var(--card)]">
            <!-- Archived reports list injected via JS -->
          </tbody>
        </table>
      </div>
    </div>

  </div>

  <script>
    const allData = {weights_json};
    const baselineAvgSteps = {avg_steps};
    const anomaliesList = {anomalies_json};
    const reportsList = {reports_json};
    
    // Sort ascending
    allData.sort((a, b) => new Date(a.dt) - new Date(b.dt));

    let activeDays = 'all';

    const canvas = document.getElementById('weightCanvas');
    const ctx = canvas.getContext('2d');
    const tooltip = document.getElementById('chartTooltip');

    function resizeCanvas() {{
      const parent = canvas.parentElement;
      if (!parent) return;
      const rect = parent.getBoundingClientRect();
      const width = rect.width;
      const height = rect.height || 340;
      if (!width || !height) return;

      const dpr = window.devicePixelRatio || 1;
      canvas.width = Math.round(width * dpr);
      canvas.height = Math.round(height * dpr);
      canvas.style.width = width + 'px';
      canvas.style.height = height + 'px';

      ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.scale(dpr, dpr);
      drawChart();
    }}

    const chartBoxEl = document.getElementById('chart-box');
    if (chartBoxEl && window.ResizeObserver) {{
      new ResizeObserver(() => resizeCanvas()).observe(chartBoxEl);
    }}
    window.addEventListener('resize', resizeCanvas);
    window.addEventListener('load', resizeCanvas);
    document.addEventListener('DOMContentLoaded', resizeCanvas);

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

    // Populate History Table (if exists)
    const tableBody = document.getElementById('history-table-body');
    if (tableBody) {{
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
    }}

    // === 5-LB MILESTONE & STEP BOOSTER ENGINE ===
    const latestEntry = allData && allData.length > 0 ? allData[allData.length - 1] : {{ w: 217.2, dt: '2026-09-02' }};
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
    let baseRatePerWeek = weeksDiff > 0 && histLossLbs > 0 ? Math.max(0.2, histLossLbs / weeksDiff) : 0.49;

    const stepSlider = document.getElementById('stepSlider');
    const stepValueBadge = document.getElementById('stepValueBadge');
    const equationText = document.getElementById('equationText');
    const equationSubtext = document.getElementById('equationSubtext');
    const totalRateBadge = document.getElementById('totalRateBadge');
    const milestoneSpeedBadge = document.getElementById('milestoneSpeedBadge');
    const milestonesTableBody = document.getElementById('milestones-table-body');

    // Generate dynamic 5-lb milestone targets down to 175 lbs
    const milestoneTargets = [215, 210, 205, 200, 195, 190, 185, 180, 175];

    function renderMilestones() {{
      if (!stepSlider || !milestonesTableBody) return;
      const extraSteps = parseInt(stepSlider.value) || 0;
      const totalSteps = baselineAvgSteps + extraSteps;
      
      if (stepValueBadge) {{
        stepValueBadge.textContent = `+${{extraSteps.toLocaleString()}} extra steps/day (Total: ${{totalSteps.toLocaleString()}})`;
      }}

      // Extra burn: 50 kcal / 1k steps
      const extraDailyKcal = (extraSteps / 1000.0) * 50.0;
      const extraWeeklyLoss = (extraDailyKcal * 7.0) / 3500.0;
      const totalRate = baseRatePerWeek + extraWeeklyLoss;

      if (totalRateBadge) {{
        totalRateBadge.textContent = `Total Rate: -${{totalRate.toFixed(2)}} lbs / week`;
      }}

      if (equationText && equationSubtext) {{
        if (extraSteps === 0) {{
          equationText.innerHTML = `If you stay at your 45-day baseline of <strong>${{baselineAvgSteps.toLocaleString()}} steps/day</strong>, your loss rate is <strong>-${{baseRatePerWeek.toFixed(2)}} lbs/week</strong>.`;
          equationSubtext.innerHTML = `Slide above to simulate adding extra walking steps and see milestones accelerate in real time!`;
          if (milestoneSpeedBadge) {{
            milestoneSpeedBadge.textContent = `Baseline Pace (-${{baseRatePerWeek.toFixed(2)}} lb/wk)`;
            milestoneSpeedBadge.className = 'text-xs font-bold px-2.5 py-1 rounded-lg bg-blue-500/10 text-blue-500';
          }}
        }} else {{
          equationText.innerHTML = `If you increase your steps by <strong class="text-blue-500">+${{extraSteps.toLocaleString()}} extra/day</strong> (Total: <strong>${{totalSteps.toLocaleString()}}</strong>), you accelerate weight loss by <strong class="text-emerald-500">+${{extraWeeklyLoss.toFixed(2)}} lbs/week</strong>!`;
          equationSubtext.innerHTML = `Burns an extra <strong>${{Math.round(extraDailyKcal)}} kcal/day</strong> (<strong>${{Math.round(extraDailyKcal * 7).toLocaleString()}} kcal/week</strong>). Total loss pace: <strong>-${{totalRate.toFixed(2)}} lbs/week</strong>.`;
          if (milestoneSpeedBadge) {{
            milestoneSpeedBadge.textContent = `⚡ Boosted by +${{extraWeeklyLoss.toFixed(2)}} lb/wk`;
            milestoneSpeedBadge.className = 'text-xs font-bold px-2.5 py-1 rounded-lg bg-emerald-500/10 text-emerald-500 animate-pulse';
          }}
        }}
      }}

      // Clear and populate table
      milestonesTableBody.innerHTML = '';
      const dateOptions = {{ year: 'numeric', month: 'short', day: 'numeric' }};

      milestoneTargets.forEach(target => {{
        const remainingLbs = Math.max(0, latestWeight - target);
        
        // Baseline time
        const baseWeeks = remainingLbs / baseRatePerWeek;
        const baseDate = new Date(latestDate.getTime() + baseWeeks * 7 * 24 * 60 * 60 * 1000);

        // Accelerated time
        const accelWeeks = remainingLbs / totalRate;
        const accelDate = new Date(latestDate.getTime() + accelWeeks * 7 * 24 * 60 * 60 * 1000);

        const weeksSaved = Math.max(0, baseWeeks - accelWeeks);
        const monthsSaved = (weeksSaved / 4.345).toFixed(1);

        let specialTag = '';
        if (target === 200) {{
          specialTag = '<span class="ml-2 px-2 py-0.5 text-[10px] font-extrabold bg-purple-500/10 text-purple-400 border border-purple-500/20 rounded-md uppercase">Onederland 🎉</span>';
        }} else if (target === 190) {{
          specialTag = '<span class="ml-2 px-2 py-0.5 text-[10px] font-extrabold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded-md uppercase">Target Goal 🎯</span>';
        }}

        let timeSavedHtml = '<span class="text-[var(--muted-foreground)] font-medium">0 days</span>';
        if (extraSteps > 0) {{
          if (weeksSaved < 1.0) {{
            timeSavedHtml = `<span class="px-2.5 py-1 rounded-lg bg-emerald-500/10 text-emerald-500 font-extrabold text-xs">⚡ ${{Math.round(weeksSaved * 7)}} days sooner</span>`;
          }} else {{
            timeSavedHtml = `<span class="px-2.5 py-1 rounded-lg bg-emerald-500/10 text-emerald-500 font-extrabold text-xs">⚡ ${{weeksSaved.toFixed(1)}} wks (${{monthsSaved}} mo) sooner</span>`;
          }}
        }}

        const tr = document.createElement('tr');
        tr.className = 'hover:bg-[var(--background)]/50 transition-colors';
        tr.innerHTML = `
          <td class="py-3 px-4 font-bold text-base flex items-center">
            ${{target.toFixed(0)}} lbs ${{specialTag}}
          </td>
          <td class="py-3 px-4 text-[var(--foreground)] font-semibold">
            -${{remainingLbs.toFixed(1)}} lbs
          </td>
          <td class="py-3 px-4 text-[var(--muted-foreground)] font-medium">
            ${{baseDate.toLocaleDateString('en-US', dateOptions)}}
            <span class="text-xs block text-[var(--muted-foreground)]/70">~${{baseWeeks.toFixed(1)}} wks</span>
          </td>
          <td class="py-3 px-4 font-bold ${{extraSteps > 0 ? 'text-emerald-500' : 'text-[var(--foreground)]'}}">
            ${{accelDate.toLocaleDateString('en-US', dateOptions)}}
            <span class="text-xs block font-medium opacity-80">~${{accelWeeks.toFixed(1)}} wks</span>
          </td>
          <td class="py-3 px-4 text-right">
            ${{timeSavedHtml}}
          </td>
        `;
        milestonesTableBody.appendChild(tr);
      }});
    }}

    if (stepSlider) {{
      stepSlider.addEventListener('input', renderMilestones);
      stepSlider.addEventListener('change', renderMilestones);
    }}

    // Initial render of milestones
    renderMilestones();

    // Render Anomalies Section
    const anomalyContainer = document.getElementById('anomaly-container');
    if (anomalyContainer && typeof anomaliesList !== 'undefined') {{
      anomalyContainer.innerHTML = '';
      anomaliesList.forEach(a => {{
        let borderClass = 'border-emerald-500/20 bg-emerald-500/5';
        let titleClass = 'text-emerald-500';
        let icon = '✅';
        if (a.type === 'warning') {{
          borderClass = 'border-rose-500/20 bg-rose-500/5';
          titleClass = 'text-rose-500';
          icon = '⚠️';
        }} else if (a.type === 'info') {{
          borderClass = 'border-blue-500/20 bg-blue-500/5';
          titleClass = 'text-blue-500';
          icon = 'ℹ️';
        }}

        const div = document.createElement('div');
        div.className = `p-4 rounded-xl border ${{borderClass}} space-y-1.5`;
        div.innerHTML = `
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold uppercase tracking-wider text-[var(--muted-foreground)]">${{a.metric}}</span>
            <span class="text-sm">${{icon}}</span>
          </div>
          <h4 class="text-sm font-bold ${{titleClass}}">${{a.title}}</h4>
          <p class="text-xs text-[var(--muted-foreground)] leading-relaxed">${{a.desc}}</p>
        `;
        anomalyContainer.appendChild(div);
      }});
    }}

    // Render Archive Table
    const archiveTableBody = document.getElementById('archive-table-body');
    if (archiveTableBody && typeof reportsList !== 'undefined') {{
      archiveTableBody.innerHTML = '';
      const countBadge = document.getElementById('archiveCountBadge');
      if (countBadge) countBadge.textContent = `${{reportsList.length}} Report(s) Archived`;

      reportsList.forEach(r => {{
        const tr = document.createElement('tr');
        tr.className = 'hover:bg-[var(--background)]/50 transition-colors';
        const changeColor = r.weekly_change < 0 ? 'text-emerald-500' : (r.weekly_change > 0 ? 'text-rose-500' : 'text-[var(--muted-foreground)]');
        const changeSign = r.weekly_change > 0 ? '+' : '';
        
        tr.innerHTML = `
          <td class="py-3 px-4 font-bold">${{r.date}}</td>
          <td class="py-3 px-4 font-semibold">${{r.weight}} lbs</td>
          <td class="py-3 px-4 font-bold ${{changeColor}}">${{changeSign}}${{r.weekly_change}} lbs</td>
          <td class="py-3 px-4">${{(r.steps_avg || 0).toLocaleString()}} / day</td>
          <td class="py-3 px-4">${{r.rhr_min || '--'}} BPM</td>
          <td class="py-3 px-4">${{r.spo2_avg || '--'}}%</td>
          <td class="py-3 px-4 text-right">
            <a href="${{r.url}}" target="_blank" class="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs rounded-lg shadow-sm transition-all inline-block">
              View Report →
            </a>
          </td>
        `;
        archiveTableBody.appendChild(tr);
      }});
    }}

    // Immediate and layout settled draws
    resizeCanvas();
    requestAnimationFrame(resizeCanvas);
    setTimeout(resizeCanvas, 100);
    setTimeout(resizeCanvas, 400);
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

# Save snapshot to reports/
reports_dir = os.path.join(workspace_dir, "reports")
os.makedirs(reports_dir, exist_ok=True)
current_date_str = weekly.get('period_end', '2026-09-04')
snapshot_path = os.path.join(reports_dir, f"report_{current_date_str}.html")
with open(snapshot_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"Generated interactive dashboard at {index_file} and archived snapshot at {snapshot_path}")
