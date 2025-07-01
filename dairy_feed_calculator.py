import streamlit as st

# --- Pasture Nutrient Defaults by Season ---
season_defaults = {
    "Spring":   {"CP": 25, "NDF": 38, "Starch": 1.5, "Sugar": 12, "Fat": 4.5},
    "Summer":   {"CP": 18, "NDF": 50, "Starch": 1.0, "Sugar": 8,  "Fat": 3.5},
    "Autumn":   {"CP": 22, "NDF": 45, "Starch": 1.2, "Sugar": 10, "Fat": 4.0},
    "Winter":   {"CP": 20, "NDF": 48, "Starch": 1.0, "Sugar": 9,  "Fat": 3.8},
}

feed_cost_defaults = {
    "Maize Silage": 150,
    "PKE": 300,
    "Milled Maize": 450,
    "Grass Silage": 180,
    "Custom 1": 350,
    "Custom 2": 350
}

# --- Streamlit UI Setup ---
st.set_page_config(page_title="Herd Feed & Nutrient Calculator", page_icon="🐄")
st.title("🐄 Dairy Cow Feed Calculator with Herd View & Nutrients")

# --- Sidebar: Herd Settings ---
st.sidebar.header("Herd Settings")
num_cows = st.sidebar.number_input("Number of cows", min_value=1, value=600)
milk_price = st.sidebar.number_input("Milk payout ($/kg MS)", min_value=0.0, value=7.50)

# --- Cow Inputs ---
st.header("1. Cow Requirements (per cow)")
liveweight = st.number_input("Liveweight (kg)", value=500)
milk_solids = st.number_input("Milk Solids (kg/day)", value=2.0)
walking = st.number_input("Walking Distance (km/day)", value=3.0)
pregnant = st.checkbox("Pregnant (last trimester)", value=False)
liveweight_gain_energy = st.number_input("Liveweight Gain Energy (MJ/day)", value=50)
buffer_percent = st.slider("Environmental Buffer (%)", 0, 20, value=5)

# --- Pasture Inputs ---
st.header("2. Pasture Settings")
season = st.selectbox("Pasture Season", options=list(season_defaults.keys()), index=0)
pasture_me = st.number_input("Pasture ME (MJ/kg DM)", value=11.0)
pasture_dm = st.number_input("Pasture DM Intake (kg/cow/day)", value=12.0)

# Nutrient inputs for pasture
st.subheader(f"{season} Pasture Nutrient Profile (% of DM)")
cp_pasture = st.number_input("Pasture CP (%)", value=season_defaults[season]["CP"])
ndf_pasture = st.number_input("Pasture NDF (%)", value=season_defaults[season]["NDF"])
starch_pasture = st.number_input("Pasture Starch (%)", value=season_defaults[season]["Starch"])
sugar_pasture = st.number_input("Pasture Sugar (%)", value=season_defaults[season]["Sugar"])
fat_pasture = st.number_input("Pasture Fat (%)", value=season_defaults[season]["Fat"])

# --- Supplement Inputs ---
st.header("3. Supplement Feeds")

def feed_input(name, default_me, default_cp, default_ndf, default_starch, default_sugar, default_fat, default_cost):
    st.subheader(f"{name}")
    dm = st.number_input(f"{name} DM (kg/cow/day)", value=0.0)
    me = st.number_input(f"{name} ME (MJ/kg DM)", value=default_me)
    cp = st.number_input(f"{name} CP (%)", value=default_cp)
    ndf = st.number_input(f"{name} NDF (%)", value=default_ndf)
    starch = st.number_input(f"{name} Starch (%)", value=default_starch)
    sugar = st.number_input(f"{name} Sugar (%)", value=default_sugar)
    fat = st.number_input(f"{name} Fat (%)", value=default_fat)
    cost = st.number_input(f"{name} Cost ($/tonne DM)", value=default_cost)
    return {"DM": dm, "ME": me, "CP": cp, "NDF": ndf, "Starch": starch, "Sugar": sugar, "Fat": fat, "Cost": cost}

feeds = {
    "Maize Silage": feed_input("Maize Silage", 10.5, 8.5, 38, 25, 4, 3, feed_cost_defaults["Maize Silage"]),
    "PKE": feed_input("PKE", 10.0, 16.0, 60, 1.5, 8, 8, feed_cost_defaults["PKE"]),
    "Milled Maize": feed_input("Milled Maize", 13.0, 9.0, 12, 65, 2, 3.5, feed_cost_defaults["Milled Maize"]),
    "Grass Silage": feed_input("Grass Silage", 10.0, 16.0, 50, 2.0, 8, 3.0, feed_cost_defaults["Grass Silage"]),
    "Custom 1": feed_input("Custom 1", 10.0, 10.0, 30, 10, 10, 3.0, feed_cost_defaults["Custom 1"]),
    "Custom 2": feed_input("Custom 2", 10.0, 10.0, 30, 10, 10, 3.0, feed_cost_defaults["Custom 2"]),
}

# --- Core Calculations (per cow then scaled) ---
maintenance = 0.55 * (liveweight ** 0.75)
milk_energy = milk_solids * 82
walk_energy = 0.75 * walking
pregnancy_energy = 20 if pregnant else 0
base_energy = maintenance + milk_energy + walk_energy + pregnancy_energy + liveweight_gain_energy
buffer_energy = base_energy * (buffer_percent / 100)
me_required_per_cow = base_energy + buffer_energy

me_supplied_supps = sum(feed["DM"] * feed["ME"] for feed in feeds.values())
dm_supps_total = sum(feed["DM"] for feed in feeds.values())

me_pasture = pasture_dm * pasture_me
total_me_supplied = me_pasture + me_supplied_supps
total_dm = pasture_dm + dm_supps_total

# --- Nutrient Calculations (total herd)
def kg_nutrient(dm, pct): return dm * pct / 100

nutrients = {
    "CP": kg_nutrient(pasture_dm, cp_pasture),
    "NDF": kg_nutrient(pasture_dm, ndf_pasture),
    "Starch": kg_nutrient(pasture_dm, starch_pasture),
    "Sugar": kg_nutrient(pasture_dm, sugar_pasture),
    "Fat": kg_nutrient(pasture_dm, fat_pasture),
}
for feed in feeds.values():
    for k in nutrients:
        nutrients[k] += kg_nutrient(feed["DM"], feed[k])

nutrients = {k: v * num_cows for k, v in nutrients.items()}
nutrient_percent_dm = {k: v / (total_dm * num_cows) * 100 if total_dm > 0 else 0 for k, v in nutrients.items()}

# --- Feed Cost Calculation ---
daily_cost = sum(feed["DM"] * feed["Cost"] / 1000 for feed in feeds.values())  # per cow/day
total_daily_cost = daily_cost * num_cows
cost_per_kg_ms = total_daily_cost / (milk_solids * num_cows) if milk_solids > 0 else 0

# --- Output ---
st.header("4. Results")

st.subheader("Energy & DM")
st.write(f"**ME Required (per cow):** {me_required_per_cow:.1f} MJ")
st.write(f"**ME Supplied (per cow):** {total_me_supplied:.1f} MJ")
st.write(f"**Pasture ME Gap (per cow):** {me_required_per_cow - total_me_supplied:.1f} MJ")
st.write(f"**Total Herd ME Required:** {me_required_per_cow * num_cows:.0f} MJ")
st.write(f"**Total Herd DM Intake:** {total_dm * num_cows:.0f} kg")

st.subheader("Nutrient Totals (Herd Daily)")
for n in nutrients:
    st.write(f"**{n}:** {nutrients[n]:.1f} kg ({nutrient_percent_dm[n]:.1f}% of DM)")

st.subheader("Feed Costs")
st.write(f"**Cost per cow per day:** ${daily_cost:.2f}")
st.write(f"**Total feed cost per day:** ${total_daily_cost:,.2f}")
st.write(f"**Feed cost per kg MS:** ${cost_per_kg_ms:.2f}")
st.write(f"**Feed cost per kg MS vs payout (${milk_price:.2f}):** Profit margin = ${(milk_price - cost_per_kg_ms):.2f}/kg MS")

st.markdown("---")
st.caption("Built by npcunard. Herd-scale, cost-aware, nutrient-balanced.")
