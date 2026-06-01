import streamlit as st
import folium
from streamlit_folium import st_folium
from datetime import date
import json
import os

from trip_data import (
    get_default_trip, save_trip, load_trip, trip_to_dict,
    Activity, DayPlan,
    CATEGORY_COLORS, DRIVE_ROUTE,
)

st.set_page_config(
    page_title="Georgia Trip",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .block-container { padding-top: 2rem; }
    h1, h2, h3 { font-family: 'Helvetica Neue', sans-serif; }
</style>
""", unsafe_allow_html=True)

# ── state ──
if "trip_info" not in st.session_state:
    if os.path.exists("trip_plan.json"):
        i, d = load_trip()
    else:
        i, d = get_default_trip()
    st.session_state.trip_info = i
    st.session_state.days = d

trip_info = st.session_state.trip_info
days = st.session_state.days

# ── sidebar ──
st.sidebar.title("Georgia Trip")
st.sidebar.caption(
    f"{trip_info['start_date']}  to  {trip_info['end_date']}"
)
st.sidebar.caption(f"{len(days)} days / {trip_info['travelers']} travelers")
st.sidebar.markdown("---")

page = st.sidebar.radio("", ["Map", "Itinerary", "Edit"])


# MAP
if page == "Map":
    st.title("Map")

    filter_opts = ["Everything"] + [
        f"Day {i+1} — {d.title}" for i, d in enumerate(days)
    ]
    selected = st.selectbox("Filter", filter_opts)

    m = folium.Map(
        location=[42.0, 43.3],
        zoom_start=7,
        tiles="CartoDB positron",
    )

    # drive route
    folium.PolyLine(
        DRIVE_ROUTE,
        color="#3D405B",
        weight=3,
        opacity=0.6,
        dash_array="8",
        tooltip="Tbilisi to Batumi",
    ).add_to(m)

    if selected == "Everything":
        show_days = days
    else:
        idx = filter_opts.index(selected) - 1
        show_days = [days[idx]]

    day_line_colors = [
        "#E07A5F", "#81B29A", "#F2CC8F",
        "#3D405B", "#7E8D9B", "#B5838D", "#6D6875",
    ]

    for day in show_days:
        di = days.index(day)
        coords = []
        for act in day.activities:
            if act.latitude and act.longitude:
                color = CATEGORY_COLORS.get(act.category, "#666")
                popup_text = (
                    f"<b>{act.name}</b><br>"
                    f"Day {di+1} / {act.time_start}-{act.time_end}<br>"
                    f"{act.location}"
                )
                if act.notes:
                    popup_text += f"<br><em>{act.notes}</em>"

                folium.CircleMarker(
                    [act.latitude, act.longitude],
                    radius=7,
                    color=color,
                    fill=True,
                    fill_color=color,
                    fill_opacity=0.85,
                    tooltip=act.name,
                    popup=folium.Popup(popup_text, max_width=220),
                ).add_to(m)
                coords.append([act.latitude, act.longitude])

        if len(coords) > 1:
            folium.PolyLine(
                coords,
                color=day_line_colors[di % len(day_line_colors)],
                weight=2,
                opacity=0.5,
                dash_array="4",
            ).add_to(m)

    legend_items = " / ".join(
        f'<span style="color:{c}">{cat}</span>'
        for cat, c in CATEGORY_COLORS.items()
    )
    st.markdown(
        f'<small style="color:#888">{legend_items}</small>',
        unsafe_allow_html=True,
    )

    st_folium(m, height=620, use_container_width=True)


# ITINERARY
elif page == "Itinerary":
    st.title("Itinerary")
    st.caption(
        f"{trip_info['name']}  /  "
        f"{trip_info['start_date']} to {trip_info['end_date']}"
    )

    for i, day in enumerate(days):
        with st.expander(
            f"Day {i+1}  —  {day.date.strftime('%a %b %d')}  —  "
            f"{day.title}  ({day.city})",
            expanded=(i == 0),
        ):
            for act in day.activities:
                color = CATEGORY_COLORS.get(act.category, "#ccc")
                notes_line = (
                    f"<br><span style='color:#999'>{act.notes}</span>"
                    if act.notes else ""
                )
                st.markdown(
                    f"""<div style="
                        border-left: 3px solid {color};
                        padding: 0.5rem 0.8rem;
                        margin: 0.3rem 0;
                        font-size: 0.95em;
                    ">
                        <strong>{act.time_start} – {act.time_end}</strong>
                        &nbsp;&nbsp;{act.name}<br>
                        <span style="color:#777">{act.location}</span>
                        {notes_line}
                    </div>""",
                    unsafe_allow_html=True,
                )


# EDIT
elif page == "Edit":
    st.title("Edit trip")

    with st.expander("Trip details"):
        trip_info["name"] = st.text_input("Name", trip_info["name"])
        trip_info["travelers"] = st.number_input(
            "Travelers", value=trip_info["travelers"], min_value=1,
        )
        c1, c2 = st.columns(2)
        trip_info["start_date"] = str(
            c1.date_input("Start", value=date.fromisoformat(trip_info["start_date"]))
        )
        trip_info["end_date"] = str(
            c2.date_input("End", value=date.fromisoformat(trip_info["end_date"]))
        )

    st.markdown("---")
    st.subheader("Add a day")
    with st.form("add_day"):
        c1, c2, c3 = st.columns(3)
        nd = c1.date_input("Date")
        nt = c2.text_input("Title")
        nc = c3.text_input("City")
        if st.form_submit_button("Add"):
            days.append(DayPlan(date=nd, title=nt, city=nc))
            days.sort(key=lambda x: x.date)
            st.rerun()

    st.markdown("---")
    st.subheader("Add activity")
    if days:
        labels = [f"Day {i+1}: {d.title}" for i, d in enumerate(days)]
        chosen = st.selectbox("Day", labels, key="act_day")
        di = labels.index(chosen)

        with st.form("add_act"):
            a_name = st.text_input("Name")
            c1, c2 = st.columns(2)
            a_start = c1.text_input("Start time", "10:00")
            a_end = c2.text_input("End time", "12:00")
            a_loc = st.text_input("Location")
            a_cat = st.selectbox(
                "Category",
                ["sightseeing", "food", "adventure", "transport", "hotel"],
            )
            c1, c2 = st.columns(2)
            a_lat = c1.number_input("Lat", value=0.0, format="%.4f")
            a_lng = c2.number_input("Lng", value=0.0, format="%.4f")
            a_notes = st.text_input("Notes", "")
            if st.form_submit_button("Add"):
                days[di].activities.append(
                    Activity(
                        name=a_name,
                        time_start=a_start,
                        time_end=a_end,
                        location=a_loc,
                        category=a_cat,
                        notes=a_notes,
                        latitude=a_lat or None,
                        longitude=a_lng or None,
                    )
                )
                st.rerun()

    st.markdown("---")
    st.subheader("Remove a day")
    if days:
        labels = [f"Day {i+1}: {d.title}" for i, d in enumerate(days)]
        to_del = st.selectbox("Day", labels, key="del_day")
        if st.button("Remove"):
            days.pop(labels.index(to_del))
            st.rerun()


# EXPORT / SHARE
elif page == "Export":
    st.title("Export")

    st.download_button(
        "Download JSON",
        data=json.dumps(trip_to_dict(trip_info, days), indent=2),
        file_name="georgia_trip.json",
        mime="application/json",
    )

    # plain text
    lines = [trip_info["name"], ""]
    lines.append(f"{trip_info['start_date']} to {trip_info['end_date']}")
    lines.append(f"{trip_info['travelers']} travelers")
    lines.append("")
    for i, day in enumerate(days):
        lines.append(
            f"Day {i+1}  {day.date.strftime('%a %b %d')}  "
            f"{day.title}  ({day.city})"
        )
        for a in day.activities:
            lines.append(f"  {a.time_start}-{a.time_end}  {a.name}")
            lines.append(f"    {a.location}")
            if a.notes:
                lines.append(f"    {a.notes}")
        lines.append("")
    summary = "\n".join(lines)

    st.text_area("Plain text summary", summary, height=400)
    st.download_button(
        "Download text",
        data=summary,
        file_name="georgia_trip.txt",
        mime="text/plain",
    )

    st.markdown("---")
    st.subheader("Import")
    up = st.file_uploader("Upload a JSON plan", type="json")
    if up:
        data = json.loads(up.read())
        st.session_state.trip_info = data["trip_info"]
        st.session_state.days = [
            DayPlan(
                date=date.fromisoformat(d["date"]),
                title=d["title"],
                city=d["city"],
                activities=[Activity(**a) for a in d["activities"]],
            )
            for d in data["days"]
        ]
        st.success("Loaded.")
        st.rerun()
