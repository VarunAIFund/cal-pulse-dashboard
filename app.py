import streamlit as st
import pandas as pd
import sys
import os
from datetime import datetime
import traceback

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from ics_parser import ICSParser
from metrics import ProductivityMetrics
from insights import InsightsGenerator
from charts import ChartGenerator


def main():
    st.set_page_config(
        page_title="Cal Pulse Dashboard",
        page_icon="📅",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("📅 Cal Pulse Dashboard")
    st.markdown("### Analyze your Apple Calendar for productivity insights")
    
    # Sidebar
    with st.sidebar:
        st.header("Upload Calendar")
        st.markdown("Export your Apple Calendar as an ICS file and upload it here.")
        
        uploaded_file = st.file_uploader(
            "Choose an ICS file",
            type=['ics'],
            help="Export your calendar from Apple Calendar as an ICS file"
        )
        
        if uploaded_file is not None:
            st.success("File uploaded successfully!")
            st.info(f"File size: {len(uploaded_file.getvalue())} bytes")
    
    # Main content
    if uploaded_file is None:
        show_landing_page()
    else:
        try:
            process_calendar_file(uploaded_file)
        except Exception as e:
            st.error(f"Error processing calendar file: {str(e)}")
            st.error("Please check that your file is a valid ICS calendar export.")
            if st.checkbox("Show technical details"):
                st.code(traceback.format_exc())


def show_landing_page():
    """Show the landing page with instructions"""
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ## How to use Cal Pulse Dashboard
        
        1. **Export your Apple Calendar:**
           - Open Calendar app on Mac
           - Select File → Export → Export...
           - Choose date range (last 30 days recommended)
           - Save as .ics file
        
        2. **Upload the file** using the sidebar
        
        3. **Get insights** about your productivity patterns
        
        ### What you'll discover:
        - **Meeting vs Focus Time**: How much time you spend in meetings vs focused work
        - **Productivity Score**: Overall calendar health assessment
        - **Time Patterns**: When you're most busy and available
        - **Optimization Tips**: Actionable recommendations to improve your schedule
        """)
    
    with col2:
        st.info("""
        **Supported Features:**
        ✅ Meeting detection  
        ✅ Focus time analysis  
        ✅ Recurring events  
        ✅ Timezone handling  
        ✅ Productivity scoring  
        ✅ Visual insights  
        """)
        
        st.warning("""
        **Privacy Note:**
        Your calendar data is processed locally and never stored or transmitted.
        """)


def process_calendar_file(uploaded_file):
    """Process the uploaded ICS file and display dashboard"""
    
    with st.spinner("Processing your calendar..."):
        try:
            # Parse ICS file
            parser = ICSParser()
            file_content = uploaded_file.getvalue()
            
            # Extract events
            events = parser.parse_ics_file(file_content)
            
            if not events:
                st.error("No events found in the calendar file. Please check your export settings.")
                return
            
            # Filter to last 30 days
            filtered_events = parser.filter_last_30_days(events)
            
            if not filtered_events:
                st.warning("No events found in the last 30 days. Try uploading a calendar with more recent events.")
                return
            
            # Classify events
            classified_events = parser.classify_events(filtered_events)
            
            # Create DataFrame
            df = parser.create_dataframe(classified_events)
            
            # Calculate metrics
            metrics_calc = ProductivityMetrics(df)
            metrics = metrics_calc.get_all_metrics()
            
            # Generate insights
            insights_gen = InsightsGenerator(metrics)
            insights = insights_gen.generate_insights()
            recommendations = insights_gen.get_recommendations()
            summary = insights_gen.get_summary()
            
            # Create charts
            chart_gen = ChartGenerator(df, metrics)
            
            # Display dashboard
            display_dashboard(df, metrics, insights, recommendations, summary, chart_gen)
            
        except Exception as e:
            st.error(f"Error processing calendar: {str(e)}")
            if st.checkbox("Show technical details"):
                st.code(traceback.format_exc())


def display_dashboard(df, metrics, insights, recommendations, summary, chart_gen):
    """Display the main dashboard"""
    
    # Summary metrics
    st.header("📊 Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Events",
            f"{metrics['total_events']:,}",
            help="Total number of calendar events in the last 30 days"
        )
    
    with col2:
        st.metric(
            "Meeting Hours",
            f"{metrics['total_meeting_hours']:.1f}h",
            f"{metrics['meeting_percentage']:.1f}%",
            help="Total time spent in meetings"
        )
    
    with col3:
        st.metric(
            "Available Focus Time", 
            f"{metrics['total_focus_hours']:.1f}h",
            f"{metrics['focus_percentage']:.1f}%",
            help="Unscheduled time during weekday business hours (9-5) available for deep work"
        )
    
    with col4:
        st.metric(
            "Productivity Score",
            f"{metrics['productivity_score']}/100",
            f"{metrics['score_category']}",
            help="Overall calendar health score"
        )
    
    # Main charts
    st.header("📈 Time Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(
            chart_gen.create_time_allocation_pie_chart(),
            use_container_width=True
        )
    
    with col2:
        st.plotly_chart(
            chart_gen.create_productivity_gauge(),
            use_container_width=True
        )
    
    # Additional charts
    st.plotly_chart(
        chart_gen.create_daily_trend_chart(),
        use_container_width=True
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(
            chart_gen.create_hourly_heatmap(),
            use_container_width=True
        )
    
    with col2:
        st.plotly_chart(
            chart_gen.create_focus_vs_meeting_comparison(),
            use_container_width=True
        )
    
    # Insights section
    st.header("💡 Insights")
    
    # Display insights by priority
    high_priority = [i for i in insights if i['priority'] == 'high']
    medium_priority = [i for i in insights if i['priority'] == 'medium']
    low_priority = [i for i in insights if i['priority'] == 'low']
    
    if high_priority:
        st.subheader("🔴 High Priority")
        for insight in high_priority:
            if insight['type'] == 'warning':
                st.error(f"**{insight['title']}**: {insight['message']}")
            else:
                st.info(f"**{insight['title']}**: {insight['message']}")
    
    if medium_priority:
        st.subheader("🟡 Medium Priority")
        for insight in medium_priority:
            if insight['type'] == 'warning':
                st.warning(f"**{insight['title']}**: {insight['message']}")
            else:
                st.info(f"**{insight['title']}**: {insight['message']}")
    
    if low_priority:
        st.subheader("🟢 Low Priority")
        for insight in low_priority:
            if insight['type'] == 'success':
                st.success(f"**{insight['title']}**: {insight['message']}")
            else:
                st.info(f"**{insight['title']}**: {insight['message']}")
    
    # Recommendations
    st.header("🎯 Recommendations")
    
    if recommendations:
        for rec in recommendations:
            st.markdown(f"• {rec}")
    else:
        st.info("Your calendar is well-optimized! Keep up the good work.")
    
    # Detailed metrics (expandable)
    with st.expander("📋 Detailed Metrics"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Meeting Metrics")
            st.metric("Average Meeting Duration", f"{metrics.get('avg_meeting_duration', 0):.1f}h")
            st.metric("Longest Meeting", f"{metrics.get('longest_meeting', 0):.1f}h")
            st.metric("Meetings per Day", f"{metrics.get('meetings_per_day', 0):.1f}")
            st.metric("Peak Meeting Hour", metrics.get('peak_meeting_hour', 'N/A'))
        
        with col2:
            st.subheader("Focus Availability Metrics")
            st.metric("Average Daily Available Focus Time", f"{metrics.get('avg_focus_duration', 0):.1f}h")
            st.metric("Best Day Available Focus Time", f"{metrics.get('longest_focus_block', 0):.1f}h")
            st.metric("Days with Available Focus Time", f"{metrics.get('focus_blocks_per_day', 0):.1f}")
            st.metric("Schedule Consistency Score", f"{metrics.get('fragmentation_score', 0):.2f}")
    
    # Raw data (expandable)
    with st.expander("📊 Raw Event Data"):
        st.dataframe(
            df[['title', 'start_time', 'duration_hours', 'classification', 'attendee_count']],
            use_container_width=True
        )
    
    # Footer
    st.markdown("---")
    st.markdown(
        "**Cal Pulse Dashboard** - Built with Streamlit • "
        "Your data is processed locally and never stored"
    )


if __name__ == "__main__":
    main()