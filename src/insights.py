from typing import Dict, List


class InsightsGenerator:
    def __init__(self, metrics: Dict):
        self.metrics = metrics

    def generate_insights(self) -> List[Dict]:
        """Generate insights based on calculated metrics"""
        insights = []
        
        # Meeting load insights
        insights.extend(self._meeting_load_insights())
        
        # Focus time insights
        insights.extend(self._focus_time_insights())
        
        # Productivity insights
        insights.extend(self._productivity_insights())
        
        # Schedule optimization insights
        insights.extend(self._schedule_optimization_insights())
        
        return insights

    def _meeting_load_insights(self) -> List[Dict]:
        """Generate insights about meeting load"""
        insights = []
        meeting_pct = self.metrics.get('meeting_percentage', 0)
        
        if meeting_pct > 50:
            insights.append({
                'type': 'warning',
                'title': 'High Meeting Load',
                'message': f'You spend {meeting_pct}% of your time in meetings. Consider declining non-essential meetings or suggesting async alternatives.',
                'priority': 'high'
            })
        elif meeting_pct > 30:
            insights.append({
                'type': 'info',
                'title': 'Moderate Meeting Load',
                'message': f'You spend {meeting_pct}% of your time in meetings. This is within a reasonable range but monitor for increases.',
                'priority': 'medium'
            })
        else:
            insights.append({
                'type': 'success',
                'title': 'Balanced Meeting Load',
                'message': f'You spend {meeting_pct}% of your time in meetings. This leaves good time for focused work.',
                'priority': 'low'
            })
        
        # Average meeting duration insights
        avg_meeting = self.metrics.get('avg_meeting_duration', 0)
        if avg_meeting < 0.5:
            insights.append({
                'type': 'warning',
                'title': 'Many Short Meetings',
                'message': f'Your average meeting is {avg_meeting} hours. Consider combining related meetings or switching to async communication.',
                'priority': 'medium'
            })
        elif avg_meeting > 2:
            insights.append({
                'type': 'info',
                'title': 'Long Meetings',
                'message': f'Your average meeting is {avg_meeting} hours. Ensure these meetings have clear agendas and outcomes.',
                'priority': 'medium'
            })
        
        return insights

    def _focus_time_insights(self) -> List[Dict]:
        """Generate insights about focus time"""
        insights = []
        focus_pct = self.metrics.get('focus_percentage', 0)
        
        if focus_pct < 20:
            insights.append({
                'type': 'warning',
                'title': 'Insufficient Available Focus Time',
                'message': f'Only {focus_pct}% of your weekday business hours are unscheduled for focus work. Consider reducing meeting load.',
                'priority': 'high'
            })
        elif focus_pct < 30:
            insights.append({
                'type': 'info',
                'title': 'Limited Available Focus Time',
                'message': f'You have {focus_pct}% of weekday business hours available for focus work. Consider protecting more unscheduled time.',
                'priority': 'medium'
            })
        else:
            insights.append({
                'type': 'success',
                'title': 'Good Available Focus Time',
                'message': f'You have {focus_pct}% of weekday business hours available for focus work. This provides good capacity for deep work.',
                'priority': 'low'
            })
        
        # Focus availability analysis
        avg_daily_focus = self.metrics.get('avg_focus_duration', 0)
        if avg_daily_focus < 2:
            insights.append({
                'type': 'warning',
                'title': 'Limited Daily Focus Capacity',
                'message': f'You average {avg_daily_focus} hours of unscheduled time per weekday. Consider reducing meeting frequency.',
                'priority': 'medium'
            })
        elif avg_daily_focus >= 6:
            insights.append({
                'type': 'success',
                'title': 'Excellent Daily Focus Capacity',
                'message': f'You average {avg_daily_focus} hours of unscheduled time per weekday. Great capacity for deep work!',
                'priority': 'low'
            })
        
        # Consistency analysis
        fragmentation = self.metrics.get('fragmentation_score', 0)
        if fragmentation > 0.2:
            insights.append({
                'type': 'warning',
                'title': 'Inconsistent Focus Time Availability',
                'message': 'Your available focus time varies significantly day-to-day. Try to maintain more consistent schedule patterns.',
                'priority': 'medium'
            })
        elif fragmentation < 0.1:
            insights.append({
                'type': 'success',
                'title': 'Consistent Focus Time Availability',
                'message': 'You have consistent unscheduled time available each weekday. This supports regular deep work habits.',
                'priority': 'low'
            })
        
        return insights

    def _productivity_insights(self) -> List[Dict]:
        """Generate overall productivity insights"""
        insights = []
        score = self.metrics.get('productivity_score', 0)
        category = self.metrics.get('score_category', 'Unknown')
        
        if score >= 80:
            insights.append({
                'type': 'success',
                'title': 'Excellent Productivity',
                'message': f'Your productivity score is {score}/100 ({category}). You have a well-balanced calendar!',
                'priority': 'low'
            })
        elif score >= 60:
            insights.append({
                'type': 'info',
                'title': 'Good Productivity',
                'message': f'Your productivity score is {score}/100 ({category}). Some optimizations could help.',
                'priority': 'medium'
            })
        else:
            insights.append({
                'type': 'warning',
                'title': 'Productivity Needs Improvement',
                'message': f'Your productivity score is {score}/100 ({category}). Consider major calendar restructuring.',
                'priority': 'high'
            })
        
        return insights

    def _schedule_optimization_insights(self) -> List[Dict]:
        """Generate schedule optimization insights"""
        insights = []
        
        # Free time analysis
        free_pct = self.metrics.get('free_percentage', 0)
        if free_pct < 20:
            insights.append({
                'type': 'warning',
                'title': 'Overscheduled Calendar',
                'message': f'Only {free_pct}% of your time is unscheduled. Consider leaving more buffer time.',
                'priority': 'high'
            })
        elif free_pct > 50:
            insights.append({
                'type': 'info',
                'title': 'Underutilized Calendar',
                'message': f'{free_pct}% of your time is unscheduled. You might have capacity for more focused work blocks.',
                'priority': 'low'
            })
        
        # Meeting frequency insights
        meetings_per_day = self.metrics.get('meetings_per_day', 0)
        if meetings_per_day > 4:
            insights.append({
                'type': 'warning',
                'title': 'Too Many Daily Meetings',
                'message': f'You average {meetings_per_day} meetings per day. Consider meeting-free time blocks.',
                'priority': 'medium'
            })
        
        # Peak meeting hour insight
        peak_hour = self.metrics.get('peak_meeting_hour', 'N/A')
        if peak_hour != 'N/A':
            insights.append({
                'type': 'info',
                'title': 'Peak Meeting Time',
                'message': f'Most meetings occur at {peak_hour}. Consider scheduling focus work during quieter hours.',
                'priority': 'low'
            })
        
        return insights

    def get_recommendations(self) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        meeting_pct = self.metrics.get('meeting_percentage', 0)
        focus_pct = self.metrics.get('focus_percentage', 0)
        fragmentation = self.metrics.get('fragmentation_score', 0)
        
        # Meeting recommendations
        if meeting_pct > 40:
            recommendations.append("📅 Audit your recurring meetings - decline or delegate non-essential ones")
            recommendations.append("⏰ Set default meeting lengths to 25/50 minutes instead of 30/60")
        
        if meeting_pct > 30:
            recommendations.append("🚫 Implement 'No Meeting' time blocks (e.g., mornings or specific days)")
        
        # Focus time recommendations
        if focus_pct < 25:
            recommendations.append("🎯 Reduce meeting load to create more unscheduled time for deep work")
            recommendations.append("📅 Block recurring focus time on your calendar to protect unscheduled hours")
        
        avg_daily_focus = self.metrics.get('avg_focus_duration', 0)
        if avg_daily_focus < 3:
            recommendations.append("⏰ Aim for at least 3 hours of unscheduled time per weekday")
        
        if fragmentation > 0.15:
            recommendations.append("🔄 Try to maintain consistent daily schedules to ensure predictable focus time")
        
        # General recommendations
        if self.metrics.get('free_percentage', 0) < 20:
            recommendations.append("🛡️ Leave 20% of your calendar unscheduled for unexpected priorities")
        
        if self.metrics.get('meetings_per_day', 0) > 4:
            recommendations.append("📋 Batch similar meetings on specific days")
        
        if self.metrics.get('avg_meeting_duration', 0) < 0.5:
            recommendations.append("💬 Convert short meetings to async communication when possible")
        
        return recommendations

    def get_summary(self) -> Dict:
        """Generate executive summary"""
        total_events = self.metrics.get('total_events', 0)
        meeting_hours = self.metrics.get('total_meeting_hours', 0)
        focus_hours = self.metrics.get('total_focus_hours', 0)
        score = self.metrics.get('productivity_score', 0)
        
        return {
            'total_events': total_events,
            'meeting_hours': meeting_hours,
            'focus_hours': focus_hours,
            'productivity_score': score,
            'key_insight': self._get_key_insight()
        }

    def _get_key_insight(self) -> str:
        """Generate the most important insight"""
        meeting_pct = self.metrics.get('meeting_percentage', 0)
        focus_pct = self.metrics.get('focus_percentage', 0)
        
        if meeting_pct > 50:
            return "Your calendar is meeting-heavy. Focus on reducing meeting load."
        elif focus_pct < 20:
            return "You need more unscheduled time available for deep work."
        elif self.metrics.get('fragmentation_score', 0) > 0.2:
            return "Your available focus time varies too much day-to-day. Try to maintain consistent schedules."
        elif self.metrics.get('productivity_score', 0) >= 80:
            return "Your calendar is well-balanced. Keep up the good work!"
        else:
            return "Your calendar has room for optimization. Focus on the key recommendations."