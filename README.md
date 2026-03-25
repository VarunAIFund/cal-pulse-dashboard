# Cal Pulse Dashboard

![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=flat-square&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.29-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-5.18-3F4F75?style=flat-square&logo=plotly&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Privacy](https://img.shields.io/badge/Privacy-100%25%20Local-brightgreen?style=flat-square)

**Upload your Apple Calendar export and get an instant, private breakdown of where your time actually goes.**

---

## Overview

Cal Pulse Dashboard turns a raw `.ics` calendar export into a visual productivity report in seconds. It classifies every event on your calendar, calculates how much of your workday is consumed by meetings versus left open for deep work, and surfaces specific recommendations to reclaim your schedule — all without sending a single byte of your data anywhere.

---

## How It Works

```
Export .ics from Apple Calendar
        │
        ▼
   ICS Parser          — extracts & expands recurring events, normalises timezones
        │
        ▼
  Event Classifier     — scores each event against meeting / focus / personal keyword sets
        │
        ▼
 Metrics Engine        — calculates hours, percentages, and a 0–100 productivity score
        │
        ▼
Insights Generator     — produces prioritised insights and actionable recommendations
        │
        ▼
  Chart Generator      — renders interactive Plotly visualisations
        │
        ▼
  Streamlit Dashboard  — displays everything in a clean, single-page UI
```

---

## Features

### Metrics Calculated
| Metric | Description |
|--------|-------------|
| **Meeting Hours** | Total hours in meetings over the last 30 days |
| **Available Focus Time** | Unscheduled weekday business hours (9 AM – 5 PM) |
| **Productivity Score** | Composite 0–100 calendar health score |
| **Meeting Load %** | Share of business hours consumed by meetings |
| **Avg Meeting Duration** | Mean length of detected meetings |
| **Peak Meeting Hour** | Hour of day with the highest meeting concentration |
| **Schedule Consistency** | Day-to-day variance in available focus time |
| **Meetings per Day** | Average daily meeting count |

### Visualisations
- **Time Allocation Donut** — meetings vs focus time vs free time
- **Daily Activity Bar Chart** — stacked daily hours over 30 days
- **Weekly Heatmap** — activity intensity by hour and day of week
- **Productivity Gauge** — real-time score with colour-coded bands
- **Meeting vs Focus Comparison** — side-by-side hour totals

### Smart Event Classification

Events are scored against three weighted rule sets:

- **Meeting** — multiple attendees, keywords (`standup`, `sync`, `review`, `1:1`, `all-hands`, …), conference room locations, 30–90 min durations
- **Focus** — solo/no attendees, keywords (`deep work`, `blocked`, `dnd`, `architecture`, …), 2+ hour blocks
- **Personal** — excluded from work analysis (`lunch`, `gym`, `doctor`, `vacation`, `ooo`, …)

---

## Privacy

> **Your calendar data never leaves your machine.**

- No external API calls
- No database writes
- No telemetry or analytics
- File is held in memory only for the duration of the session

This is a deliberate design choice. Calendar data is sensitive — it reveals your work patterns, relationships, and routines. Cal Pulse processes everything locally using Python and renders results entirely in your browser via Streamlit.

---

## Setup

### Prerequisites
- Python 3.8 or higher
- pip

### Installation

```bash
# 1. Clone the repo
git clone https://github.com/your-username/cal-pulse-dashboard.git
cd cal-pulse-dashboard

# 2. Create and activate a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

---

## Usage

### 1. Export Your Apple Calendar

1. Open **Calendar** on macOS
2. Go to **File → Export → Export…**
3. Select a date range (last 30–60 days recommended)
4. Save the `.ics` file somewhere accessible

### 2. Start the Dashboard

```bash
streamlit run app.py
# or
python run.py
```

The app opens at `http://localhost:8501`.

### 3. Upload and Explore

Upload the `.ics` file via the sidebar. The dashboard populates immediately with metrics, charts, insights, and recommendations.

---

## Project Structure

```
cal-pulse-dashboard/
├── app.py                  # Streamlit entry point and UI layout
├── run.py                  # Optional convenience launcher
├── requirements.txt        # Pinned dependencies
├── src/
│   ├── ics_parser.py       # ICS parsing, recurring event expansion, classification
│   ├── metrics.py          # Productivity metrics and scoring engine
│   ├── insights.py         # Rule-based insight and recommendation generation
│   └── charts.py           # Plotly chart builders
├── data/
│   └── sample_calendar.ics # Anonymised sample data for testing
└── test_free_time.py       # Manual verification script for focus-time logic
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| UI | [Streamlit](https://streamlit.io) |
| Data processing | [pandas](https://pandas.pydata.org) |
| Visualisation | [Plotly](https://plotly.com/python/) |
| Calendar parsing | [icalendar](https://icalendar.readthedocs.io) |
| Date/recurrence | [python-dateutil](https://dateutil.readthedocs.io) |

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "No events found" | Confirm the export includes the desired date range |
| "Error parsing ICS file" | Use the **File → Export** path in Apple Calendar; third-party exports may differ |
| Empty dashboard after upload | Your export may not contain events in the last 30 days — try a wider export window |
| Timezone looks wrong | Events are converted to your system's local timezone automatically |

---

## Roadmap

- [ ] Google Calendar and Outlook `.ics` export support
- [ ] Configurable analysis window (7 / 14 / 30 / 90 days)
- [ ] Meeting-free day detection and suggestions
- [ ] Week-over-week trend comparison
- [ ] Export insights as PDF report

---

## License

MIT — free to use, modify, and distribute.
