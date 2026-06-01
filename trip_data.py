from dataclasses import dataclass, field
from typing import Optional
import json


@dataclass
class Place:
    name: str
    description: str
    latitude: float
    longitude: float
    nights: int = 0
    to_visit: list[str] = field(default_factory=list)
    to_eat: list[str] = field(default_factory=list)
    notes: str = ""


TRIP = {
    "title": "Georgia",
    "when": "End of August / beginning of September",
    "travelers": 2,
    "route_note": "Tbilisi - Gori - Kutaisi - Batumi",
}

PLACES: list[Place] = [
    Place(
        name="Tbilisi",
        description="Capital city. Old town, sulfur baths, wine bars, markets.",
        latitude=41.6941,
        longitude=44.8015,
        nights=3,
        to_visit=[
            "Narikala Fortress"
        ],
        to_eat=[
            "Khinkali",
            "Khachapuri"
        ],
        notes="Rent a car",
    ),
    Place(
        name="Gori",
        description="Stalin's birthplace.",
        latitude=41.9816,
        longitude=44.1135,
        nights=0,
        to_visit=[
            "Stalin Museum",
            "Stalin's birth house",
            "Stalin's personal railway car",
        ],
        to_eat=[
            "blahblah",
        ],
        notes="not that far from tbilisi",
    ),
    Place(
        name="Kutaisi",
        description="Second largest city.",
        latitude=42.2679,
        longitude=42.6946,
        nights=1,
        to_visit=[
            "Bagrati Cathedral",
            "Gelati Monastery",
        ],
        to_eat=[
            "blahblah",
        ],
        notes="stay for a night",
    ),
    Place(
        name="Batumi",
        description="",
        latitude=41.6168,
        longitude=41.6367,
        nights=3,
        to_visit=[
            "Old Town",
        ],
        to_eat=[
            "blahblah",
        ],
        notes="Fly out from Batumi airport. Return rental car here.",
    ),
]

DRIVE_ROUTE = [
    (41.6941, 44.8015),  # Tbilisi
    (41.9816, 44.1135),  # Gori
    (42.2679, 42.6946),  # Kutaisi
    (41.6168, 41.6367),  # Batumi
]

PLACE_COLORS = {
    "Tbilisi": "#E07A5F",
    "Gori": "#81B29A",
    "Kutaisi": "#B5838D",
    "Batumi": "#3D405B",
}


def data_to_dict():
    return {
        "trip": TRIP,
        "places": [
            {
                "name": p.name,
                "description": p.description,
                "latitude": p.latitude,
                "longitude": p.longitude,
                "nights": p.nights,
                "to_visit": p.to_visit,
                "to_eat": p.to_eat,
                "notes": p.notes,
            }
            for p in PLACES
        ],
    }


def export_text():
    lines = [TRIP["title"], TRIP["when"], ""]
    lines.append(f"{TRIP['travelers']} travelers")
    lines.append(TRIP["route_note"])
    lines.append("")
    for p in PLACES:
        stay = f"{p.nights} night{'s' if p.nights != 1 else ''}" if p.nights else "day stop"
        lines.append(f"{p.name.upper()}  ({stay})")
        lines.append(p.description)
        if p.to_visit:
            lines.append("  To visit:")
            for v in p.to_visit:
                lines.append(f"    - {v}")
        if p.to_eat:
            lines.append("  To eat:")
            for e in p.to_eat:
                lines.append(f"    - {e}")
        if p.notes:
            lines.append(f"  Note: {p.notes}")
        lines.append("")
    return "\n".join(lines)