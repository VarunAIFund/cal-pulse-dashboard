import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, List
import numpy as np


class ChartGenerator:
    def __init__(self, df: pd.DataFrame, metrics: Dict):
        self.df = df
        self.metrics = metrics
        self.colors = {
            'meeting': '#FF6B6B',
            'focus': '#4ECDC4',
            'personal': '#45B7D1',
            'free': '#96CEB4'
        }

    def create_time_allocation_pie_chart(self):
        """Create pie chart showing time allocation"""
        values = [
            self.metrics.get('total_meeting_hours', 0),
            self.metrics.get('total_focus_hours', 0),
            self.metrics.get('total_free_hours', 0)
        ]
        
        labels = ['Meetings', 'Available Focus Time', 'Free Time']
        colors = [self.colors['meeting'], self.colors['focus'], self.colors['free']]
        
        # Only include non-zero values
        filtered_data = [(v, l, c) for v, l, c in zip(values, labels, colors) if v > 0]
        
        if not filtered_data:
            # Return empty figure if no data
            fig = go.Figure()
            fig.add_annotation(
                text="No calendar data available",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=20)
            )
            return fig
        
        values, labels, colors = zip(*filtered_data)
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.3,
            marker=dict(colors=colors),
            textinfo='label+percent',
            textposition='outside',
            hovertemplate='<b>%{label}</b><br>' +
                         'Hours: %{value:.1f}<br>' +
                         'Percentage: %{percent}<br>' +
                         '<extra></extra>'
        )])
        
        fig.update_layout(
            title={
                'text': 'Time Allocation (Last 30 Days)',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20}
            },
            showlegend=True,
            height=400,
            font=dict(size=12)
        )
        
        return fig

    def create_daily_trend_chart(self):
        """Create bar chart showing daily meeting hours trend"""
        if self.df.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="No calendar data available",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=20)
            )
            return fig
        
        # Group by date and classification
        daily_data = self.df.groupby(['date', 'classification'])['duration_hours'].sum().unstack(fill_value=0)
        
        # Sort by date
        daily_data = daily_data.sort_index()
        
        fig = go.Figure()
        
        # Add bars for each classification
        for classification in ['meeting', 'focus', 'personal']:
            if classification in daily_data.columns:
                fig.add_trace(go.Bar(
                    name=classification.title(),
                    x=daily_data.index,
                    y=daily_data[classification],
                    marker_color=self.colors.get(classification, '#888888')
                ))
        
        fig.update_layout(
            title={
                'text': 'Daily Calendar Activity',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20}
            },
            xaxis_title='Date',
            yaxis_title='Hours',
            barmode='stack',
            height=400,
            showlegend=True
        )
        
        return fig

    def create_hourly_heatmap(self):
        """Create heatmap showing meeting density by hour and day"""
        if self.df.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="No calendar data available",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=20)
            )
            return fig
        
        # Filter only meetings and focus time
        activity_df = self.df[self.df['classification'].isin(['meeting', 'focus'])]
        
        if activity_df.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="No meeting or focus time data available",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=20)
            )
            return fig
        
        # Create hour bins
        activity_df = activity_df.copy()
        activity_df['hour_bin'] = activity_df['hour_of_day']
        
        # Group by day of week and hour
        heatmap_data = activity_df.groupby(['day_of_week', 'hour_bin'])['duration_hours'].sum().unstack(fill_value=0)
        
        # Reorder days
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        heatmap_data = heatmap_data.reindex(day_order, fill_value=0)
        
        # Create hour labels
        hour_labels = [f"{h:02d}:00" for h in range(24)]
        
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data.values,
            x=hour_labels,
            y=heatmap_data.index,
            colorscale='Viridis',
            hovertemplate='<b>%{y}</b><br>' +
                         'Hour: %{x}<br>' +
                         'Activity: %{z:.1f} hours<br>' +
                         '<extra></extra>'
        ))
        
        fig.update_layout(
            title={
                'text': 'Weekly Activity Heatmap',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20}
            },
            xaxis_title='Hour of Day',
            yaxis_title='Day of Week',
            height=400
        )
        
        return fig

    def create_meeting_duration_distribution(self):
        """Create histogram of meeting durations"""
        if self.df.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="No calendar data available",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=20)
            )
            return fig
        
        meeting_df = self.df[self.df['classification'] == 'meeting']
        
        if meeting_df.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="No meeting data available",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=20)
            )
            return fig
        
        fig = px.histogram(
            meeting_df,
            x='duration_hours',
            nbins=20,
            title='Meeting Duration Distribution',
            labels={'duration_hours': 'Duration (hours)', 'count': 'Number of Meetings'},
            color_discrete_sequence=[self.colors['meeting']]
        )
        
        fig.update_layout(
            title={
                'text': 'Meeting Duration Distribution',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20}
            },
            height=400,
            showlegend=False
        )
        
        return fig

    def create_productivity_gauge(self):
        """Create gauge chart for productivity score"""
        score = self.metrics.get('productivity_score', 0)
        
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Productivity Score"},
            delta = {'reference': 75},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 40], 'color': "lightgray"},
                    {'range': [40, 60], 'color': "yellow"},
                    {'range': [60, 80], 'color': "lightgreen"},
                    {'range': [80, 100], 'color': "green"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        fig.update_layout(
            height=300,
            title={
                'text': 'Productivity Score',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20}
            }
        )
        
        return fig

    def create_classification_summary_chart(self):
        """Create summary chart of event classifications"""
        if self.df.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="No calendar data available",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=20)
            )
            return fig
        
        # Count events by classification
        classification_counts = self.df['classification'].value_counts()
        
        fig = go.Figure(data=[go.Bar(
            x=classification_counts.index,
            y=classification_counts.values,
            marker_color=[self.colors.get(cls, '#888888') for cls in classification_counts.index]
        )])
        
        fig.update_layout(
            title={
                'text': 'Event Count by Type',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20}
            },
            xaxis_title='Event Type',
            yaxis_title='Number of Events',
            height=400,
            showlegend=False
        )
        
        return fig

    def create_focus_vs_meeting_comparison(self):
        """Create comparison chart of focus vs meeting time"""
        meeting_hours = self.metrics.get('total_meeting_hours', 0)
        focus_hours = self.metrics.get('total_focus_hours', 0)
        
        fig = go.Figure(data=[
            go.Bar(
                name='Hours',
                x=['Meeting Time', 'Available Focus Time'],
                y=[meeting_hours, focus_hours],
                marker_color=[self.colors['meeting'], self.colors['focus']],
                text=[f'{meeting_hours:.1f}h', f'{focus_hours:.1f}h'],
                textposition='auto'
            )
        ])
        
        fig.update_layout(
            title={
                'text': 'Meeting vs Available Focus Time Comparison',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20}
            },
            yaxis_title='Hours',
            height=400,
            showlegend=False
        )
        
        return fig