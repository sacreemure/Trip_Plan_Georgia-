from dataclasses import dataclass, field
from datetime import date
from typing import Optional
import json


@dataclass
class Activity:
    name: str
    location: str
    category: str
    notes: str = ""
    latitude: Optional[float] = None
    longitude: Optional[float] = None


@dataclass
class DayPlan:
    date: date
    title: str
    city: str
    activities: list[Activity] = field(default_factory=list)


CATEGORY_COLORS = {
    "to visit": "#E07A5F",
    "to eat": "#81B29A",
    "stay": "#7E8D9B",
}

DRIVE_ROUTE = [
    (41.6941, 44.8015),   # Tbilisi
    (41.9816, 44.1135),   # Gori
    (41.9975, 43.5977),   # Khashuri
    (41.8427, 43.5290),   # Borjomi
    (42.2679, 42.6946),   # Kutaisi area
    (41.8214, 41.7768),   # Kobuleti
    (41.6168, 41.6367),   # Batumi
]


def get_default_trip():
    trip_info = {
        "name": "Georgia - Tbilisi and Batumi",
        "travelers": 2,
        "start_date": "2026-09-01",
        "end_date": "2026-09-09",
    }

    days = [
        DayPlan(
            date=date(2025, 3, 15),
            title="Arrival",
            city="Tbilisi",
            activities=[
                Activity(
                    name="blahblah",
                    location="blahblah",
                    category="to eat",
                    latitude=41.6692, longitude=44.9547,
                ),
           ],
        ),      
    ]

    return trip_info, days


def trip_to_dict(trip_info, days):
    return {
        "trip_info": trip_info,
        "days": [
            {
                "date": d.date.isoformat(),
                "title": d.title,
                "city": d.city,
                "activities": [
                    {
                        "name": a.name,
                        "location": a.location,
                        "category": a.category,
                        "notes": a.notes,
                        "latitude": a.latitude,
                        "longitude": a.longitude,
                    }
                    for a in d.activities
                ],
            }
            for d in days
        ],
    }


def save_trip(trip_info, days, path="trip_plan.json"):
    with open(path, "w") as f:
        json.dump(trip_to_dict(trip_info, days), f, indent=2)


def load_trip(path="trip_plan.json"):
    with open(path) as f:
        data = json.load(f)
    trip_info = data["trip_info"]
    days = [
        DayPlan(
            date=date.fromisoformat(d["date"]),
            title=d["title"],
            city=d["city"],
            activities=[Activity(**a) for a in d["activities"]],
        )
        for d in data["days"]
    ]
    return trip_info, days
