#!/usr/bin/env python3
"""
Test script to verify the free time calculation is working correctly
"""

import sys
import os
sys.path.append('cal-pulse-dashboard/src')

from ics_parser import ICSParser
from metrics import ProductivityMetrics

def test_free_time_calculation():
    """Test the free time calculation with sample data"""
    print("🧪 Testing Free Time Calculation")
    print("=" * 50)
    
    # Parse sample calendar
    parser = ICSParser()
    with open('cal-pulse-dashboard/data/sample_calendar.ics', 'rb') as f:
        content = f.read()
    
    events = parser.parse_ics_file(content)
    print(f"📅 Parsed {len(events)} events from calendar")
    
    # Filter to last 30 days
    filtered = parser.filter_last_30_days(events)
    print(f"📋 Filtered to {len(filtered)} events in last 30 days")
    
    # Classify events
    classified = parser.classify_events(filtered)
    print(f"🏷️  Classified {len(classified)} events")
    
    # Create DataFrame
    df = parser.create_dataframe(classified)
    print(f"📊 Created DataFrame with {len(df)} rows")
    
    if len(df) == 0:
        print("❌ No events found in DataFrame")
        return
    
    print("\n📋 Event Details:")
    print("-" * 70)
    for _, event in df.iterrows():
        print(f"{event['date']} {event['hour_of_day']:02d}:00 | {event['title']:<30} | {event['duration_hours']:>4.1f}h | {event['classification']}")
    
    # Calculate metrics
    print("\n📊 Productivity Metrics:")
    print("-" * 50)
    
    metrics_calc = ProductivityMetrics(df)
    metrics = metrics_calc.get_all_metrics()
    
    print(f"🏢 Total business hours (22 working days × 8h): {metrics_calc.total_business_hours}h")
    print(f"🤝 Meeting hours: {metrics['total_meeting_hours']}h ({metrics['meeting_percentage']:.1f}%)")
    print(f"🎯 Focus hours: {metrics['total_focus_hours']}h ({metrics['focus_percentage']:.1f}%)")
    print(f"👤 Personal hours: {metrics['total_personal_hours']}h")
    print(f"🆓 Free hours: {metrics['total_free_hours']}h ({metrics['free_percentage']:.1f}%)")
    print(f"📅 Total scheduled: {metrics['total_scheduled_hours']}h")
    
    # Verify calculation makes sense
    print("\n✅ Verification:")
    print("-" * 30)
    total_accounted = metrics['total_meeting_hours'] + metrics['total_focus_hours'] + metrics['total_personal_hours'] + metrics['total_free_hours']
    print(f"Total accounted time: {total_accounted}h")
    print(f"Total business hours: {metrics_calc.total_business_hours}h")
    print(f"Difference: {abs(total_accounted - metrics_calc.total_business_hours):.1f}h")
    
    if abs(total_accounted - metrics_calc.total_business_hours) < 1:
        print("✅ FREE TIME CALCULATION IS CORRECT!")
    else:
        print("❌ FREE TIME CALCULATION NEEDS ADJUSTMENT")
    
    print("\n🎯 Key Insight:")
    if metrics['free_percentage'] > 80:
        print("You have plenty of free time during business hours!")
    elif metrics['free_percentage'] > 50:
        print("You have a good balance of scheduled and free time.")
    elif metrics['free_percentage'] > 20:
        print("Your calendar is fairly busy but still manageable.")
    else:
        print("Your calendar is very busy - consider blocking more free time!")

if __name__ == "__main__":
    test_free_time_calculation()