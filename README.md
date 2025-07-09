# Cal Pulse Dashboard

A web application that analyzes Apple Calendar ICS files to provide productivity insights and recommendations.

## Features

- **Calendar Analysis**: Parse ICS files from Apple Calendar
- **Smart Classification**: Automatically categorize events as meetings, focus time, or personal
- **Productivity Metrics**: Calculate meeting load, focus time, and productivity scores
- **Visual Insights**: Interactive charts and visualizations
- **Actionable Recommendations**: Get specific tips to optimize your schedule
- **Privacy-First**: All processing happens locally - no data is stored or transmitted

## How to Use

1. **Export Your Calendar**:
   - Open Calendar app on Mac
   - Select File → Export → Export...
   - Choose date range (last 30 days recommended)
   - Save as .ics file

2. **Run the Application**:
   ```bash
   pip install -r requirements.txt
   streamlit run app.py
   ```

3. **Upload & Analyze**:
   - Upload your ICS file using the sidebar
   - View your productivity insights and recommendations

## Installation

```bash
# Clone or download the project
cd cal-pulse-dashboard

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

## Project Structure

```
cal-pulse-dashboard/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── src/
│   ├── ics_parser.py     # ICS file parsing and event extraction
│   ├── metrics.py        # Productivity metrics calculation
│   ├── insights.py       # Insights generation and recommendations
│   └── charts.py         # Chart generation with Plotly
├── data/                 # Sample data (optional)
├── tests/                # Test files
└── README.md            # This file
```

## Key Metrics

- **Meeting Load**: Percentage of time spent in meetings
- **Focus Time**: Dedicated time for deep work
- **Productivity Score**: Overall calendar health (0-100)
- **Fragmentation Score**: How scattered your focus time is
- **Peak Hours**: When you're most busy

## Classification Logic

The application uses rule-based logic to classify events:

### Meeting Indicators:
- Multiple attendees
- Keywords: "meeting", "call", "standup", "sync", "review"
- Typical durations (30min, 1hr)
- Conference room locations

### Focus Time Indicators:
- Single attendee or no attendees
- Keywords: "focus", "deep work", "coding", "development"
- Longer durations (2+ hours)
- Blocked time

### Exclusions:
- Personal events: "lunch", "doctor", "gym"
- Out of office: "vacation", "holiday", "sick"

## Technical Details

- **Frontend**: Streamlit for web interface
- **Backend**: Python with pandas for data processing
- **Charts**: Plotly for interactive visualizations
- **Calendar Parsing**: icalendar library for ICS file processing
- **Timezone Handling**: pytz for timezone conversion

## Privacy & Security

- No data is stored or transmitted
- All processing happens locally on your machine
- Calendar data never leaves your device
- No external API calls required

## Requirements

- Python 3.7+
- See `requirements.txt` for package dependencies

## Troubleshooting

### Common Issues:

1. **"No events found"**: Check your calendar export includes the desired date range
2. **"Error parsing ICS file"**: Ensure the file is exported from Apple Calendar in ICS format
3. **Empty dashboard**: The file may not contain events in the last 30 days

### Getting Help:

1. Check that your ICS file is valid
2. Ensure all dependencies are installed
3. Try with a different date range in your calendar export

## Future Enhancements

- Support for other calendar formats (Google Calendar, Outlook)
- Machine learning-based event classification
- Integration with productivity tools
- Historical trend analysis
- Team calendar analysis

## License

This project is provided as-is for educational and personal use.# project-3
