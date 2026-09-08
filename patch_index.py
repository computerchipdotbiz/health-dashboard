import re

with open("index.html", "r", encoding="utf-8") as f:
    content = f.read()

# Check if anomaliesList is declared
if "const anomaliesList =" not in content:
    # Insert anomaliesList and reportsList declaration right after baselineAvgSteps
    insertion = """
    const anomaliesList = [
      {
        metric: "Weight Trajectory",
        title: "All-Time Low Milestone Reached",
        type: "success",
        desc: "Recorded new all-time low of 217.2 lbs on Sep 02, 2026. Total weight loss now stands at -119.7 lbs."
      },
      {
        metric: "Daily Activity",
        title: "Consistent 45-Day Walking Baseline",
        type: "info",
        desc: "Daily steps averaging 4,227 steps/day across the last 45 days. Adding walking intervals accelerates milestone arrival."
      },
      {
        metric: "Resting Heart Rate",
        title: "Strong Recovery Baseline",
        type: "success",
        desc: "Overnight resting heart rate dipping to 52 BPM indicates excellent cardiovascular recovery during sleep."
      },
      {
        metric: "Oxygen Saturation",
        title: "Optimal Overnight Oxygenation",
        type: "success",
        desc: "SpO2 levels maintained consistently in the 97–99% range throughout overnight monitoring."
      }
    ];

    const reportsList = [
      {
        date: "2026-09-04",
        weight: 217.2,
        weekly_change: -1.4,
        steps_avg: 4227,
        rhr_min: 52,
        spo2_avg: 98,
        url: "#"
      }
    ];
"""
    content = content.replace("const baselineAvgSteps = 4227;", "const baselineAvgSteps = 4227;\n" + insertion)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(content)
    print("Inserted anomaliesList and reportsList successfully!")
else:
    print("anomaliesList was already present.")
