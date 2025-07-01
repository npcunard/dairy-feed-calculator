import streamlit as st

st.set_page_config(page_title="Dairy Cow Feed Calculator", page_icon="🐄")
st.title("🐄 Dairy Cow Feed Calculator")

st.markdown("""
This tool estimates daily feed requirements for a dairy cow based on milk production, weight, walking distance, and supplements.
""")

# 🐄 Cow details
st.header("1. Cow Information")
liveweight = st.number_input("Liveweight (kg)", value=500)
milk_solids = st.number_input("Milk Solids (kg/day)", value=1.8)
walking = st.number_input("Walking Distance (km/day)", value=3.0)
pregnant = st.checkbox("Pregnant", value=False)
buffer_percent = st.slider("Environmental Buffer (%)", 0, 20, value=5)

# ⚡ Feed energy values
st.header("2. Feed Energy (ME) Values")
me_pasture = st.number_input("Pasture ME (MJ/kg DM)", value=11.0)
me_maize = st.number_input("Maize Silage ME (MJ/kg DM)", value=10.5)
me_pke = st.number_input("PKE ME (MJ/kg DM)", value=10.0)
me_milled = st.number_input("Milled Maize ME (MJ/kg DM)", value=13.0)

# 🧂 Supplement intake
st.header("3. Supplement Feed Offered (kg DM/day)")
kg_maize = st.number_input("Maize Silage (kg DM/day)", value=3.0)
kg_pke = st.number_input("PKE (kg DM/day)", value=1.0)
kg_milled = st.number_input("Milled Maize (kg DM/day)", value=1.0)

# 🔢 Calculations
maintenance = 0.55 * (liveweight ** 0.75)
milk_energy = milk_solids * 82
liveweight_gain_energy = 50  # If gaining weight, e.g. autumn cows
walk_energy = 0.75 * walking
pregnancy_energy = 20 if pregnant else 0
base_energy = maintenance + milk_energy + walk_energy + pregnancy_energy + liveweight_gain_energy
buffer_energy = base_energy * (buffer_percent / 100)
total_me_required = base_energy + buffer_energy

supp_me = (kg_maize * me_maize) + (kg_pke * me_pke) + (kg_milled * me_milled)
pasture_me_required = total_me_required - supp_me
pasture_dm_required = pasture_me_required / me_pasture if pasture_me_required > 0 else 0

# 📊 Output
st.header("4. Results")
st.write(f"**Total ME Required:** {total_me_required:.1f} MJ/day")
st.write(f"**Supplement ME Provided:** {supp_me:.1f} MJ/day")
st.write(f"**Pasture ME Needed:** {pasture_me_required:.1f} MJ/day")
st.write(f"**Pasture DM Required:** {pasture_dm_required:.2f} kg/day")

# Footer
st.markdown("---")
st.caption("Built by npcunard with 🐮 and 🔥. Streamlit version.")
