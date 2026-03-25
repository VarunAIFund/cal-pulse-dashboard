import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from icalendar import Calendar, Event
from dateutil.rrule import rrule, DAILY, WEEKLY, MONTHLY, YEARLY
import pandas as pd


class ICSParser:
    def __init__(self):
        self.meeting_keywords = [
            'meeting', 'call', 'standup', 'sync', 'review', 'discussion',
            'interview', 'presentation', 'demo', 'retrospective', 'planning',
            'workshop', 'session', 'conference', 'consultation', 'catchup',
            'check-in', 'huddle', 'briefing', 'training', 'seminar',
            'webinar', 'scrum', 'sprint', 'one-on-one', '1:1', 'all-hands'
        ]
        
        self.focus_keywords = [
            'focus', 'deep work', 'coding', 'development', 'programming',
            'writing', 'research', 'analysis', 'study', 'learning',
            'blocked', 'do not disturb', 'dnd', 'concentration', 'work block',
            'thinking time', 'planning', 'design', 'architecture', 'documentation',
            'admin', 'email', 'task', 'project'
        ]
        
        self.exclude_keywords = [
            'lunch', 'dinner', 'breakfast', 'break', 'holiday', 'vacation',
            'personal', 'dentist', 'doctor', 'appointment', 'gym', 'workout',
            'commute', 'travel', 'flight', 'out of office', 'ooo', 'sick'
        ]

    def parse_ics_file(self, file_content: bytes) -> List[Dict]:
        """Parse ICS file and extract events"""
        try:
            calendar = Calendar.from_ical(file_content)
            events = []
            
            for component in calendar.walk():
                if component.name == "VEVENT":
                    event_data = self._extract_event_data(component)
                    if event_data:
                        events.append(event_data)
            
            return events
        except Exception as e:
            raise ValueError(f"Error parsing ICS file: {str(e)}")

    def _extract_event_data(self, event: Event) -> Optional[Dict]:
        """Extract relevant data from a calendar event"""
        try:
            # Get basic event info
            title = str(event.get('SUMMARY', ''))
            description = str(event.get('DESCRIPTION', ''))
            location = str(event.get('LOCATION', ''))
            
            # Get start and end times
            start_dt = event.get('DTSTART')
            end_dt = event.get('DTEND')
            
            if not start_dt or not end_dt:
                return None
            
            start_time = start_dt.dt
            end_time = end_dt.dt
            
            # Handle timezone conversion
            if hasattr(start_time, 'tzinfo') and start_time.tzinfo:
                # Convert to the system's local timezone
                local_tz = datetime.now().astimezone().tzinfo
                start_time = start_time.astimezone(local_tz)
                end_time = end_time.astimezone(local_tz)
            
            # Get attendees
            attendees = []
            if 'ATTENDEE' in event:
                attendee_data = event.get('ATTENDEE')
                if isinstance(attendee_data, list):
                    attendees = [str(att) for att in attendee_data]
                else:
                    attendees = [str(attendee_data)]
            
            # Get organizer
            organizer = str(event.get('ORGANIZER', ''))
            
            # Calculate duration
            duration = end_time - start_time
            duration_minutes = duration.total_seconds() / 60
            
            # Handle recurring events
            rrule_data = event.get('RRULE')
            
            event_data = {
                'title': title,
                'description': description,
                'location': location,
                'start_time': start_time,
                'end_time': end_time,
                'duration_minutes': duration_minutes,
                'attendees': attendees,
                'attendee_count': len(attendees),
                'organizer': organizer,
                'rrule': rrule_data,
                'is_recurring': rrule_data is not None
            }
            
            return event_data
            
        except Exception as e:
            print(f"Error extracting event data: {str(e)}")
            return None

    def expand_recurring_events(self, events: List[Dict], start_date: datetime, end_date: datetime) -> List[Dict]:
        """Expand recurring events within the specified date range"""
        expanded_events = []
        
        for event in events:
            if not event['is_recurring']:
                # Check if single event is within date range
                if start_date <= event['start_time'] <= end_date:
                    expanded_events.append(event)
            else:
                # Handle recurring events
                expanded_events.extend(self._expand_recurring_event(event, start_date, end_date))
        
        return expanded_events

    def _expand_recurring_event(self, event: Dict, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Expand a single recurring event"""
        expanded = []
        
        try:
            rrule_data = event['rrule']
            if not rrule_data:
                return [event] if start_date <= event['start_time'] <= end_date else []
            
            # Simple recurring event expansion
            original_start = event['start_time']
            duration = event['end_time'] - event['start_time']
            
            # Get frequency from rrule
            freq_mapping = {
                'DAILY': DAILY,
                'WEEKLY': WEEKLY,
                'MONTHLY': MONTHLY,
                'YEARLY': YEARLY
            }
            
            freq = freq_mapping.get(rrule_data.get('FREQ', ['WEEKLY'])[0], WEEKLY)
            interval = int(rrule_data.get('INTERVAL', [1])[0])
            count = rrule_data.get('COUNT', [None])[0]
            until = rrule_data.get('UNTIL', [None])[0]
            
            # Generate occurrences
            rule = rrule(
                freq=freq,
                interval=interval,
                dtstart=original_start,
                until=until if until else end_date,
                count=int(count) if count else None
            )
            
            for occurrence in rule:
                if start_date <= occurrence <= end_date:
                    occurrence_event = event.copy()
                    occurrence_event['start_time'] = occurrence
                    occurrence_event['end_time'] = occurrence + duration
                    occurrence_event['is_recurring'] = False  # Mark as expanded
                    expanded.append(occurrence_event)
                    
        except Exception as e:
            print(f"Error expanding recurring event: {str(e)}")
            # Return original event if expansion fails
            if start_date <= event['start_time'] <= end_date:
                expanded.append(event)
        
        return expanded

    def filter_last_30_days(self, events: List[Dict]) -> List[Dict]:
        """Filter events to only include those from the last 30 days"""
        end_date = datetime.now().astimezone()
        start_date = end_date - timedelta(days=30)
        
        # Expand recurring events within the 30-day window
        expanded_events = self.expand_recurring_events(events, start_date, end_date)
        
        # Filter events within the date range
        filtered_events = []
        for event in expanded_events:
            event_start = event['start_time']
            if event_start.tzinfo is None:
                event_start = event_start.astimezone()

            if start_date <= event_start <= end_date:
                filtered_events.append(event)
        
        return filtered_events

    def classify_events(self, events: List[Dict]) -> List[Dict]:
        """Classify events as meetings, focus time, or personal"""
        classified_events = []
        
        for event in events:
            classification = self._classify_single_event(event)
            event_copy = event.copy()
            event_copy['classification'] = classification
            classified_events.append(event_copy)
        
        return classified_events

    def _classify_single_event(self, event: Dict) -> str:
        """Classify a single event based on rules"""
        title = event['title'].lower()
        description = event['description'].lower()
        location = event['location'].lower()
        attendee_count = event['attendee_count']
        duration_minutes = event['duration_minutes']
        
        # Check for exclusions first
        for keyword in self.exclude_keywords:
            if keyword in title or keyword in description:
                return 'personal'
        
        # Meeting indicators
        meeting_score = 0
        focus_score = 0
        
        # Check attendee count
        if attendee_count > 1:
            meeting_score += 3
        elif attendee_count == 1:
            meeting_score += 1
        else:
            focus_score += 1
        
        # Check keywords in title and description
        text_to_check = f"{title} {description} {location}"
        
        for keyword in self.meeting_keywords:
            if keyword in text_to_check:
                meeting_score += 2
        
        for keyword in self.focus_keywords:
            if keyword in text_to_check:
                focus_score += 2
        
        # Check duration patterns
        if duration_minutes <= 30:
            meeting_score += 1
        elif 30 < duration_minutes <= 90:
            meeting_score += 2
        elif duration_minutes > 120:
            focus_score += 2
        
        # Check location
        if any(room_type in location for room_type in ['room', 'conference', 'meeting']):
            meeting_score += 1
        
        # Check time of day (business hours more likely to be meetings)
        start_hour = event['start_time'].hour
        if 9 <= start_hour <= 17:
            meeting_score += 1
        
        # Make final classification
        if meeting_score > focus_score:
            return 'meeting'
        elif focus_score > meeting_score:
            return 'focus'
        else:
            # Default classification based on duration
            if duration_minutes <= 60:
                return 'meeting'
            else:
                return 'focus'

    def create_dataframe(self, events: List[Dict]) -> pd.DataFrame:
        """Convert events to pandas DataFrame for analysis"""
        if not events:
            return pd.DataFrame()
        
        df_data = []
        for event in events:
            df_data.append({
                'title': event['title'],
                'start_time': event['start_time'],
                'end_time': event['end_time'],
                'duration_minutes': event['duration_minutes'],
                'duration_hours': event['duration_minutes'] / 60,
                'attendee_count': event['attendee_count'],
                'classification': event.get('classification', 'unknown'),
                'day_of_week': event['start_time'].strftime('%A'),
                'hour_of_day': event['start_time'].hour,
                'date': event['start_time'].date()
            })
        
        return pd.DataFrame(df_data)