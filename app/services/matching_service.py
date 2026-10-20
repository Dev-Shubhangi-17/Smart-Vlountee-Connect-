"""Smart matching service for matching volunteers to opportunities."""

from datetime import date
from ..models.event import Event
from ..models.volunteer import Volunteer


def calculate_match_score(volunteer: Volunteer, event: Event) -> int:
    """Calculate match score between a volunteer and an event.

    Weights:
        +3 points for matching interest/cause area
        +2 points for matching city/location
        +1 point for upcoming event (date >= today)
    """
    score = 0
    volunteer_interests = [i.lower() for i in volunteer.interests_list()]
    
    if event.category and event.category.lower() in volunteer_interests:
        score += 3
        
    vol_city = (volunteer.city or "").lower().strip()
    evt_city = (event.city or "").lower().strip()
    if vol_city and evt_city and (vol_city in evt_city or evt_city in vol_city):
        score += 2
        
    if event.event_date >= date.today():
        score += 1
        
    return score


def get_recommendations_for_volunteer(volunteer: Volunteer, limit: int = 10) -> list[dict]:
    """Retrieve top recommended events for a given volunteer."""
    today = date.today()
    enrolled_ids = {enr.event_id for enr in volunteer.enrollments.all()}

    query = Event.query.filter(
        Event.event_date >= today,
        Event.status == "active"
    )
    if enrolled_ids:
        query = query.filter(Event.id.notin_(enrolled_ids))

    events = query.all()
    scored = [(calculate_match_score(volunteer, evt), evt) for evt in events]
    scored.sort(key=lambda x: x[0], reverse=True)

    results = []
    for score, evt in scored[:limit]:
        d = evt.to_dict()
        d["match_score"] = score
        results.append(d)

    return results
