import streamlit as st
import json

# Load seasonal pasture nutrient defaults
season_defaults = {
    "Spring":   {"CP": 25, "NDF": 38, "Starch": 1.5, "Sugar": 12, "Fat": 4.5},
    "Summer":   {"CP": 18, "NDF": 50, "Starch": 1.0, "Sugar": 8,  "Fat": 3.5},
    "Autumn":   {"CP": 22, "NDF": 45, "Starch": 1.2, "Sugar": 10, "Fat": 4.0},
    "Winter":   {"CP": 20, "NDF": 48, "Starch": 1.0, "Sugar": 9,  "Fat": 3.8},
}

st.set_page_config(page_title="Dairy Cow Feed Calculator", page_icon="🐄")
st.title("🐄 Dairy Cow Feed Calculator with Nutrient Tracking")

# Cow Inputs
st.header("1. Cow Information")
liveweight = st.number_input("Liveweight (kg)", value=500)
milk_solids = st.number_input("Milk Solids (kg/day)", value=2.0)
walking = st.number_input("Walking Distance (km/day)", value=3.0)
pregnant = st.checkbox("Pregnant (last trimester)", value=False)
liveweight_gain_energy = st.number_input("Liveweight Gain Energy (MJ/day)", value=50)
buffer_percent = st.slider("Environmental Buffer (%)", 0, 20, value=5)

# Pasture Season
st.header("2. Pasture Settings")
season = st.selectbox("Pasture Season", options=["Spring", "Summer", "Autumn", "Winter"], index=0)
pasture_me = st.number_input("Pasture ME (MJ/kg DM)", value=11.0)
pasture_dm = st.number_input("Pasture DM Intake (kg)", value=12.0)

# Load default nutrients
pasture_nutrients = season_defaults[season]
st.subheader(f"{season} Pasture Nutrient Values (% of DM)")
cp_pasture = st.number_input("CP (%)", value=pasture_nutrients["CP"])
ndf_pasture = st.number_input("NDF (%)", value=pasture_nutrients["NDF"])
starch_pasture = st.number_input("Starch (%)", value=pasture_nutrients["Starch"])
sugar_pasture = st.number_input("Sugar (%)", value=pasture_nutrients["Sugar"])
fat_pasture = st.number_input("Fat (%)", value=pasture_nutrients["Fat"])

# Supplement Feeds
st.header("3. Supplement Feeds (kg DM/day + nutrient %)")

def feed_input(name, default_me, default_cp, default_ndf, default_starch, default_sugar, default_fat):
    dm = st.number_input(f"{name} (kg DM/day)", value=0.0)
    me = st.number_input(f"{name} ME (MJ/kg DM)", value=default_me)
    cp = st.number_input(f"{name} CP (%)", value=default_cp)
    ndf = st.number_input(f"{name} NDF (%)", value=default_ndf)
    starch = st.number_input(f"{name} Starch (%)", value=default_starch)
    sugar = st.number_input(f"{name} Sugar (%)", value=default_sugar)
    fat = st.number_input(f"{name} Fat (%)", value=default_fat)
    return {"DM": dm, "ME": me, "CP": cp, "NDF": ndf, "Starch": starch, "Sugar": sugar, "Fat": fat}

feeds = {}
feeds["Maize Silage"] = feed_input("Maize Silage", 10.5, 8.5, 38, 25, 4, 3.0)
feeds["PKE"] = feed_input("PKE", 10.0, 16.0, 60, 1.5, 8, 8.0)
feeds["Milled Maize"] = feed_input("Milled Maize", 13.0, 9.0, 12, 65, 2, 3.5)
feeds["Grass Silage"] = feed_input("Grass Silage", 10.0, 16.0, 50, 2.0, 8, 3.0)
feeds["Custom 1"] = feed_input("Custom 1", 10.0, 10.0, 30, 10, 10, 3.0)
feeds["Custom 2"] = feed_input("Custom 2", 10.0, 10.0, 30, 10, 10, 3.0)

# Core ME requirements
maintenance = 0.55 * (liveweight ** 0.75)
milk_energy = milk_solids * 82
walk_energy = 0.75 * walking
pregnancy_energy = 20 if pregnant else 0

base_energy = maintenance + milk_energy + walk_energy + pregnancy_energy + liveweight_gain_energy
buffer_energy = base_energy * (buffer_percent / 100)
total_me_required = base_energy + buffer_energy

# Supplement and pasture ME
supp_me = sum(feed["DM"] * feed["ME"] for feed in feeds.values())
pasture_me = pasture_dm * pasture_me
total_me_supplied = supp_me + pasture_me
pasture_me_gap = total_me_required - total_me_supplied

# Total DM and nutrients
total_dm = pasture_dm + sum(feed["DM"] for feed in feeds.values())

def nutrient_kg(feed, pct_key):
    return feed["DM"] * feed[pct_key] / 100

nutrients = {
    "CP": pasture_dm * cp_pasture / 100,
    "NDF": pasture_dm * ndf_pasture / 100,
    "Starch": pasture_dm * starch_pasture / 100,
    "Sugar": pasture_dm * sugar_pasture / 100,
    "Fat": pasture_dm * fat_pasture / 100,
}

for name, feed in feeds.items():
    for n in nutrients:
        nutrients[n] += nutrient_kg(feed, n)

nutrient_percent = {k: (v / total_dm * 100 if total_dm > 0 else 0) for k, v in nutrients.items()}

# Output
st.header("4. Results")

st.subheader("Energy Requirements")
st.write(f"**Total ME Required:** {total_me_required:.1f} MJ/day")
st.write(f"**ME Supplied (Supps + Pasture):** {total_me_supplied:.1f} MJ/day")
st.write(f"**Pasture ME Gap:** {pasture_me_gap:.1f} MJ/day")

st.subheader("Total Dry Matter")
st.write(f"**Total DM Intake:** {total_dm:.1f} kg/day")

st.subheader("Nutrient Supply")
for n in ["CP", "NDF", "Starch", "Sugar", "Fat"]:
    st.write(f"**{n}:** {nutrients[n]:.2f} kg/day ({nutrient_percent[n]:.1f}% of DM)")

st.markdown("---")
st.caption("Built by npcunard — Nutrient-aware dairy feeding calculator.")
