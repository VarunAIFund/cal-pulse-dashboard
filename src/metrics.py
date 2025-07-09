import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple


class ProductivityMetrics:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.total_days = 30
        self.business_hours_per_day = 8  # Assuming 8-hour workday (9 AM - 5 PM)
        self.working_days_per_month = 22  # Approx 22 working days in 30 days (excluding weekends)
        self.total_business_hours = self.working_days_per_month * self.business_hours_per_day
        self.weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

    def calculate_basic_metrics(self) -> Dict:
        """Calculate basic productivity metrics"""
        if self.df.empty:
            return self._empty_metrics()
        
        # Group by classification
        classification_summary = self.df.groupby('classification')['duration_hours'].sum()
        
        # Calculate totals
        total_meeting_hours = classification_summary.get('meeting', 0)
        total_personal_hours = classification_summary.get('personal', 0)
        
        # Calculate focus time as unscheduled time during weekday business hours (9 AM - 5 PM)
        total_focus_hours = self._calculate_focus_time_weekday_business_hours()
        
        # Calculate free time properly - only count time during business hours (9 AM - 5 PM)
        total_free_hours = self._calculate_free_time_during_business_hours()
        
        # Calculate work-related scheduled hours (excluding personal)
        total_work_hours = total_meeting_hours + total_focus_hours
        total_scheduled_hours = total_meeting_hours + total_focus_hours + total_personal_hours
        
        # Calculate percentages based on business hours only
        meeting_percentage = (total_meeting_hours / self.total_business_hours) * 100
        focus_percentage = (total_focus_hours / self.total_business_hours) * 100
        free_percentage = (total_free_hours / self.total_business_hours) * 100
        
        return {
            'total_meeting_hours': round(total_meeting_hours, 1),
            'total_focus_hours': round(total_focus_hours, 1),
            'total_personal_hours': round(total_personal_hours, 1),
            'total_free_hours': round(total_free_hours, 1),
            'total_scheduled_hours': round(total_scheduled_hours, 1),
            'meeting_percentage': round(meeting_percentage, 1),
            'focus_percentage': round(focus_percentage, 1),
            'free_percentage': round(free_percentage, 1),
            'total_events': len(self.df),
            'meeting_count': len(self.df[self.df['classification'] == 'meeting']),
            'focus_count': len(self.df[self.df['classification'] == 'focus'])
        }

    def calculate_meeting_metrics(self) -> Dict:
        """Calculate meeting-specific metrics"""
        if self.df.empty:
            return {}
        
        meeting_df = self.df[self.df['classification'] == 'meeting']
        
        if meeting_df.empty:
            return {
                'avg_meeting_duration': 0,
                'longest_meeting': 0,
                'shortest_meeting': 0,
                'meetings_per_day': 0,
                'peak_meeting_hour': 'N/A'
            }
        
        # Calculate meeting statistics
        avg_duration = meeting_df['duration_hours'].mean()
        longest_meeting = meeting_df['duration_hours'].max()
        shortest_meeting = meeting_df['duration_hours'].min()
        meetings_per_day = len(meeting_df) / self.total_days
        
        # Find peak meeting hour
        peak_hour = meeting_df['hour_of_day'].mode()
        peak_meeting_hour = f"{peak_hour.iloc[0]:02d}:00" if not peak_hour.empty else 'N/A'
        
        return {
            'avg_meeting_duration': round(avg_duration, 1),
            'longest_meeting': round(longest_meeting, 1),
            'shortest_meeting': round(shortest_meeting, 1),
            'meetings_per_day': round(meetings_per_day, 1),
            'peak_meeting_hour': peak_meeting_hour
        }

    def calculate_focus_metrics(self) -> Dict:
        """Calculate focus time metrics based on available focus time"""
        if self.df.empty:
            return {
                'avg_focus_duration': 0,
                'longest_focus_block': 0,
                'focus_blocks_per_day': 0,
                'fragmentation_score': 0
            }
        
        # Calculate focus time per weekday
        weekday_df = self.df[self.df['day_of_week'].isin(self.weekdays)]
        
        if weekday_df.empty:
            # No weekday events, so all weekday business hours are focus time
            total_focus_hours = self.total_business_hours
            return {
                'avg_focus_duration': round(self.business_hours_per_day, 1),
                'longest_focus_block': round(self.business_hours_per_day, 1),
                'focus_blocks_per_day': round(total_focus_hours / self.working_days_per_month, 1),
                'fragmentation_score': 0
            }
        
        # Calculate focus time available each weekday
        daily_focus_hours = []
        
        for date, day_events in weekday_df.groupby('date'):
            # Filter events that overlap with business hours (9 AM - 5 PM)
            day_business_events = day_events[
                (day_events['hour_of_day'] < 17) & 
                ((day_events['hour_of_day'] + day_events['duration_hours']) > 9)
            ]
            
            if day_business_events.empty:
                # No events during business hours = full day available for focus
                daily_focus_hours.append(self.business_hours_per_day)
                continue
            
            # Calculate scheduled time during business hours for this day
            scheduled_hours_this_day = 0
            
            for _, event in day_business_events.iterrows():
                event_start_hour = event['hour_of_day']
                event_duration = event['duration_hours']
                event_end_hour = event_start_hour + event_duration
                
                # Clip to business hours (9 AM - 5 PM)
                business_start = max(9, event_start_hour)
                business_end = min(17, event_end_hour)
                
                # Add duration that falls within business hours
                if business_end > business_start:
                    scheduled_hours_this_day += business_end - business_start
            
            # Calculate focus time for this day (max 8 hours)
            focus_hours_this_day = max(0, self.business_hours_per_day - scheduled_hours_this_day)
            daily_focus_hours.append(focus_hours_this_day)
        
        # Add days with no events as full focus days
        unique_weekday_dates = len(set(weekday_df['date'].unique()))
        if unique_weekday_dates < self.working_days_per_month:
            empty_days = self.working_days_per_month - unique_weekday_dates
            daily_focus_hours.extend([self.business_hours_per_day] * empty_days)
        
        # Calculate metrics
        if daily_focus_hours:
            avg_duration = sum(daily_focus_hours) / len(daily_focus_hours)
            longest_block = max(daily_focus_hours)
            blocks_per_day = len([h for h in daily_focus_hours if h > 0]) / self.working_days_per_month
            
            # Fragmentation score: measure how consistent daily focus time is
            # Lower score = more consistent focus time availability
            total_focus = sum(daily_focus_hours)
            if total_focus > 0:
                fragmentation_score = len([h for h in daily_focus_hours if h > 0]) / total_focus
            else:
                fragmentation_score = 0
        else:
            avg_duration = 0
            longest_block = 0
            blocks_per_day = 0
            fragmentation_score = 0
        
        return {
            'avg_focus_duration': round(avg_duration, 1),
            'longest_focus_block': round(longest_block, 1),
            'focus_blocks_per_day': round(blocks_per_day, 1),
            'fragmentation_score': round(fragmentation_score, 2)
        }

    def calculate_daily_patterns(self) -> Dict:
        """Calculate daily patterns and trends"""
        if self.df.empty:
            return {}
        
        # Group by date and classification
        daily_summary = self.df.groupby(['date', 'classification'])['duration_hours'].sum().unstack(fill_value=0)
        
        # Calculate daily totals
        daily_totals = daily_summary.sum(axis=1)
        
        # Find busiest and lightest days
        busiest_day = daily_totals.idxmax() if not daily_totals.empty else None
        lightest_day = daily_totals.idxmin() if not daily_totals.empty else None
        
        # Calculate day-of-week patterns
        dow_summary = self.df.groupby(['day_of_week', 'classification'])['duration_hours'].sum().unstack(fill_value=0)
        
        return {
            'busiest_day': str(busiest_day) if busiest_day else 'N/A',
            'lightest_day': str(lightest_day) if lightest_day else 'N/A',
            'avg_daily_scheduled': round(daily_totals.mean(), 1) if not daily_totals.empty else 0,
            'dow_patterns': dow_summary.to_dict() if not dow_summary.empty else {}
        }

    def calculate_productivity_score(self) -> Dict:
        """Calculate overall productivity score and recommendations"""
        basic_metrics = self.calculate_basic_metrics()
        meeting_metrics = self.calculate_meeting_metrics()
        focus_metrics = self.calculate_focus_metrics()
        
        # Calculate productivity score (0-100)
        score = 100
        
        # Deduct points for excessive meetings
        if basic_metrics['meeting_percentage'] > 50:
            score -= 20
        elif basic_metrics['meeting_percentage'] > 30:
            score -= 10
        
        # Deduct points for insufficient focus time
        if basic_metrics['focus_percentage'] < 20:
            score -= 15
        elif basic_metrics['focus_percentage'] < 30:
            score -= 5
        
        # Deduct points for fragmentation
        if focus_metrics.get('fragmentation_score', 0) > 1:
            score -= 10
        
        # Deduct points for too many short meetings
        if meeting_metrics.get('avg_meeting_duration', 0) < 0.5:
            score -= 5
        
        # Bonus for good focus blocks
        if focus_metrics.get('longest_focus_block', 0) > 2:
            score += 5
        
        score = max(0, min(100, score))
        
        return {
            'productivity_score': round(score),
            'score_category': self._get_score_category(score)
        }

    def _get_score_category(self, score: int) -> str:
        """Get category based on productivity score"""
        if score >= 80:
            return 'Excellent'
        elif score >= 60:
            return 'Good'
        elif score >= 40:
            return 'Fair'
        else:
            return 'Needs Improvement'

    def _calculate_free_time_during_business_hours(self) -> float:
        """Calculate free time by looking at unscheduled time during business hours (9 AM - 5 PM)"""
        if self.df.empty:
            return self.total_business_hours
        
        # Create a more accurate calculation by looking at each day individually
        total_free_hours = 0
        business_hours_per_day = 8  # 9 AM to 5 PM
        
        # Group events by date to avoid double counting across days
        for date, day_events in self.df.groupby('date'):
            # Filter events that overlap with business hours (9 AM - 5 PM)
            day_business_events = day_events[
                (day_events['hour_of_day'] < 17) & 
                ((day_events['hour_of_day'] + day_events['duration_hours']) > 9)
            ]
            
            if day_business_events.empty:
                # No events during business hours = full day free
                total_free_hours += business_hours_per_day
                continue
            
            # Calculate scheduled time during business hours for this day
            scheduled_hours_this_day = 0
            
            for _, event in day_business_events.iterrows():
                event_start_hour = event['hour_of_day']
                event_duration = event['duration_hours']
                event_end_hour = event_start_hour + event_duration
                
                # Clip to business hours (9 AM - 5 PM)
                business_start = max(9, event_start_hour)
                business_end = min(17, event_end_hour)
                
                # Add duration that falls within business hours
                if business_end > business_start:
                    scheduled_hours_this_day += business_end - business_start
            
            # Calculate free time for this day (max 8 hours)
            free_hours_this_day = max(0, business_hours_per_day - scheduled_hours_this_day)
            total_free_hours += free_hours_this_day
        
        # For days with no events at all, they should count as full free days
        unique_event_dates = set(self.df['date'].unique())
        
        # Estimate total working days in the 30-day period (excluding weekends)
        # This is a rough estimate - about 22 working days in 30 days
        estimated_working_days = 22
        days_with_events = len(unique_event_dates)
        
        # Add free time for days with no events
        if days_with_events < estimated_working_days:
            days_with_no_events = estimated_working_days - days_with_events
            total_free_hours += days_with_no_events * business_hours_per_day
        
        return total_free_hours

    def _calculate_focus_time_weekday_business_hours(self) -> float:
        """Calculate focus time as unscheduled time during weekday business hours (9 AM - 5 PM)"""
        if self.df.empty:
            return self.total_business_hours
        
        # Filter events to only weekdays
        weekday_df = self.df[self.df['day_of_week'].isin(self.weekdays)]
        
        if weekday_df.empty:
            return self.total_business_hours
        
        # Calculate unscheduled time during weekday business hours
        total_focus_hours = 0
        business_hours_per_day = 8  # 9 AM to 5 PM
        
        # Group weekday events by date
        for date, day_events in weekday_df.groupby('date'):
            # Filter events that overlap with business hours (9 AM - 5 PM)
            day_business_events = day_events[
                (day_events['hour_of_day'] < 17) & 
                ((day_events['hour_of_day'] + day_events['duration_hours']) > 9)
            ]
            
            if day_business_events.empty:
                # No events during business hours = full day available for focus
                total_focus_hours += business_hours_per_day
                continue
            
            # Calculate scheduled time during business hours for this day
            scheduled_hours_this_day = 0
            
            for _, event in day_business_events.iterrows():
                event_start_hour = event['hour_of_day']
                event_duration = event['duration_hours']
                event_end_hour = event_start_hour + event_duration
                
                # Clip to business hours (9 AM - 5 PM)
                business_start = max(9, event_start_hour)
                business_end = min(17, event_end_hour)
                
                # Add duration that falls within business hours
                if business_end > business_start:
                    scheduled_hours_this_day += business_end - business_start
            
            # Calculate focus time for this day (max 8 hours)
            focus_hours_this_day = max(0, business_hours_per_day - scheduled_hours_this_day)
            total_focus_hours += focus_hours_this_day
        
        # For weekdays with no events at all, they should count as full focus days
        unique_weekday_dates = set(weekday_df['date'].unique())
        
        # Calculate total weekdays in the 30-day period
        # This is a rough estimate - about 22 working days in 30 days
        estimated_weekdays = 22
        weekdays_with_events = len(unique_weekday_dates)
        
        # Add focus time for weekdays with no events
        if weekdays_with_events < estimated_weekdays:
            weekdays_with_no_events = estimated_weekdays - weekdays_with_events
            total_focus_hours += weekdays_with_no_events * business_hours_per_day
        
        return total_focus_hours

    def _empty_metrics(self) -> Dict:
        """Return empty metrics when no data is available"""
        return {
            'total_meeting_hours': 0,
            'total_focus_hours': 0,
            'total_personal_hours': 0,
            'total_free_hours': self.total_business_hours,
            'total_scheduled_hours': 0,
            'meeting_percentage': 0,
            'focus_percentage': 0,
            'free_percentage': 100,
            'total_events': 0,
            'meeting_count': 0,
            'focus_count': 0
        }

    def get_all_metrics(self) -> Dict:
        """Get all calculated metrics in one dictionary"""
        all_metrics = {}
        all_metrics.update(self.calculate_basic_metrics())
        all_metrics.update(self.calculate_meeting_metrics())
        all_metrics.update(self.calculate_focus_metrics())
        all_metrics.update(self.calculate_daily_patterns())
        all_metrics.update(self.calculate_productivity_score())
        
        return all_metrics