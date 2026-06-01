import streamlit as st
import folium
from streamlit_folium import st_folium
import json

from trip_data import TRIP, PLACES, DRIVE_ROUTE, PLACE_COLORS, data_to_dict, export_text

st.set_page_config(
    page_title="Georgia Trip",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .block-container { padding-top: 2rem; max-width: 1100px; }
    h1, h2, h3, h4 { font-family: 'Helvetica Neue', sans-serif; font-weight: 400; }
    .place-header { font-size: 1.1em; font-weight: 600; margin-bottom: 0.2rem; }
    .place-desc { color: #555; font-size: 0.95em; margin-bottom: 0.6rem; }
    .place-note { color: #888; font-size: 0.88em; font-style: italic; }
    .section-label {
        font-size: 0.75em; text-transform: uppercase;
        letter-spacing: 0.08em; color: #999; margin-bottom: 0.3rem;
    }
    .tag {
        display: inline-block;
        background: #f0f0f0;
        border-radius: 4px;
        padding: 2px 10px;
        font-size: 0.88em;
        margin: 2px 3px 2px 0;
        color: #333;
    }
    .night-badge {
        font-size: 0.8em;
        color: #888;
        margin-left: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)


# ── sidebar ──
st.sidebar.title("Georgia Trip")
st.sidebar.caption(TRIP["when"])
st.sidebar.caption(TRIP["route_note"])
st.sidebar.markdown("---")

page = st.sidebar.radio("", ["Overview", "Map", "Export"])


if page == "Overview":
    st.title(TRIP["title"])
    st.caption(f"{TRIP['when']}  /  {TRIP['travelers']} travelers  /  {TRIP['route_note']}")
    st.markdown("---")

    for place in PLACES:
        color = PLACE_COLORS.get(place.name, "#999")
        stay_label = (
            f"{place.nights} night{'s' if place.nights != 1 else ''}"
            if place.nights else "day stop"
        )

        # place header with color bar
        st.markdown(
            f"""<div style="border-left: 4px solid {color}; padding: 0.4rem 1rem; margin-bottom: 0.3rem;">
                <span class="place-header">{place.name}</span>
                <span class="night-badge">{stay_label}</span>
                <div class="place-desc">{place.description}</div>
            </div>""",
            unsafe_allow_html=True,
        )

        col1, col2 = st.columns(2)

        with col1:
            st.markdown('<div class="section-label">To visit</div>', unsafe_allow_html=True)
            tags = "".join(f'<span class="tag">{v}</span>' for v in place.to_visit)
            st.markdown(tags, unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="section-label">To eat</div>', unsafe_allow_html=True)
            tags = "".join(f'<span class="tag">{e}</span>' for e in place.to_eat)
            st.markdown(tags, unsafe_allow_html=True)

        if place.notes:
            st.markdown(
                f'<div class="place-note" style="margin-top:0.4rem">{place.notes}</div>',
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)


elif page == "Map":
    st.title("Map")

    selected_name = st.selectbox(
        "Highlight a place",
        ["All"] + [p.name for p in PLACES],
    )

    m = folium.Map(
        location=[42.0, 43.2],
        zoom_start=7,
        tiles="CartoDB positron",
    )

    # drive route
    folium.PolyLine(
        DRIVE_ROUTE,
        color="#aaa",
        weight=3,
        opacity=0.7,
        dash_array="8",
        tooltip="Driving route",
    ).add_to(m)

    for place in PLACES:
        color = PLACE_COLORS.get(place.name, "#999")
        is_selected = selected_name == "All" or selected_name == place.name

        stay_label = (
            f"{place.nights} night{'s' if place.nights != 1 else ''}"
            if place.nights else "day stop"
        )

        visit_list = "".join(f"<li>{v}</li>" for v in place.to_visit)
        eat_list = "".join(f"<li>{e}</li>" for e in place.to_eat)

        popup_html = f"""
        <div style="width:240px; font-family:sans-serif">
            <div style="
                border-left: 4px solid {color};
                padding-left: 8px;
                margin-bottom: 8px;
            ">
                <b style="font-size:1.05em">{place.name}</b>
                <div style="color:#888; font-size:0.85em">{stay_label}</div>
            </div>
            <div style="font-size:0.85em; color:#555; margin-bottom:8px">
                {place.description}
            </div>
            <div style="font-size:0.8em">
                <b>To visit</b>
                <ul style="margin:4px 0 8px 0; padding-left:16px; color:#333">
                    {visit_list}
                </ul>
                <b>To eat</b>
                <ul style="margin:4px 0; padding-left:16px; color:#333">
                    {eat_list}
                </ul>
            </div>
            {"<div style='font-size:0.78em;color:#999;margin-top:6px'>" + place.notes + "</div>" if place.notes else ""}
        </div>
        """

        folium.CircleMarker(
            location=[place.latitude, place.longitude],
            radius=10 if is_selected else 6,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.9 if is_selected else 0.4,
            tooltip=place.name,
            popup=folium.Popup(popup_html, max_width=260),
        ).add_to(m)

        # label
        if is_selected:
            folium.Marker(
                location=[place.latitude + 0.06, place.longitude],
                icon=folium.DivIcon(
                    html=f"""<div style="
                        font-family: sans-serif;
                        font-size: 12px;
                        font-weight: 600;
                        color: {color};
                        white-space: nowrap;
                    ">{place.name}</div>""",
                    icon_size=(100, 20),
                    icon_anchor=(0, 0),
                ),
            ).add_to(m)

    st_folium(m, height=640, use_container_width=True)

    # legend
    st.markdown("---")
    cols = st.columns(len(PLACES))
    for col, place in zip(cols, PLACES):
        color = PLACE_COLORS.get(place.name, "#999")
        stay = (
            f"{place.nights}n"
            if place.nights else "stop"
        )
        col.markdown(
            f'<div style="text-align:center">'
            f'<div style="width:12px;height:12px;border-radius:50%;'
            f'background:{color};margin:0 auto 4px"></div>'
            f'<small>{place.name}</small><br>'
            f'<small style="color:#aaa">{stay}</small>'
            f'</div>',
            unsafe_allow_html=True,
        )


elif page == "Export":
    st.title("Export")

    st.download_button(
        "Download JSON",
        data=json.dumps(data_to_dict(), indent=2),
        file_name="georgia_trip.json",
        mime="application/json",
    )

    txt = export_text()
    st.download_button(
        "Download text",
        data=txt,
        file_name="georgia_trip.txt",
        mime="text/plain",
    )

    st.text_area("Plain text", txt, height=500)