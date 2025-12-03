import streamlit as st
from utils.geo_analysis import TerrainAnalyzer
from utils.network_models import NetworkOptimizer
from utils.cost_simulator import CostSimulator
import folium
from streamlit_folium import folium_static

# Initialize core components
optimizer = NetworkOptimizer()
simulator = CostSimulator()

# App Configuration
st.set_page_config(
    page_title="SACP",
    layout="wide",
    page_icon="🌱",
    initial_sidebar_state="expanded"
)

# Session State
if 'map_data' not in st.session_state:
    st.session_state.map_data = None

# Tabs
tabs = ["📚 Instructions", "🗺️ Geospatial", "📡 Network", "💸 Costs", "📊 Dashboard"]
current_tab = st.sidebar.radio("Navigation", tabs)

# Tab 1: Instructions
if current_tab == "📚 Instructions":
    st.markdown("# 🌾 Smart Agricultural Connectivity Planner")
    try:
        with open("assets/instructions.md", "r", encoding="utf-8") as f:
            st.markdown(f.read())
    except Exception as e:
        st.error(f"Error reading instructions file: {e}")
    
# Tab 2: Geospatial Analysis
elif current_tab == "🗺️ Geospatial":
    st.header("Geospatial Analysis Module")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        uploaded_file = st.file_uploader(
            "Upload Geospatial Data",
            type=["geojson", "shp"],
            help="Supported formats: GeoJSON, ESRI Shapefile"
        )
        
    with col2:
        st.subheader("Analysis Parameters")
        veg_threshold = st.slider("Vegetation Threshold", 0.0, 1.0, 0.5)
        elevation_range = st.slider("Elevation Range (m)", 0, 2000, (0, 1000))
    
    if uploaded_file:
        analyzer = TerrainAnalyzer(uploaded_file)
        with st.spinner("Processing geospatial data..."):
            st.session_state.map_data = analyzer.generate_map(veg_threshold)
            stats = analyzer.get_statistics()
            
            st.subheader("Terrain Visualization")
            folium_static(st.session_state.map_data)
            
            cols = st.columns(3)
            cols[0].metric("Total Area", f"{stats['area']} km²")
            cols[1].metric("Avg Elevation", f"{stats['elevation']} m")
            cols[2].metric("Vegetation Cover", f"{stats['vegetation']}%")

# Tab 3: Network Design
elif current_tab == "📡 Network":
    st.header("Network Design Studio")
    
    # Use a unique key for the form to avoid conflicts
    with st.form(key="network_form"):
        col1, col2 = st.columns(2)
        with col1:
            budget = st.number_input("Budget (USD)", 1000, 1000000, 5000, key="budget")
            tech_type = st.selectbox("Technology", ["LoRaWAN", "5G", "Satellite", "Mesh"], key="tech_type")
            
        with col2:
            model_choice = st.selectbox("AI Model", ["MiniMax-Text-01", "gpt-4.5-preview"], key="model_choice")
            terrain_type = st.selectbox("Terrain Complexity", ["Simple", "Moderate", "Complex"], key="terrain_type")
        
        submitted = st.form_submit_button("Generate Plan")
        
        if submitted:
            with st.spinner("Creating optimal network configuration..."):
                result = optimizer.recommend_network(budget, tech_type, model_choice)
                
                st.subheader("Technical Plan")
                st.markdown(result["analysis"])
                
                st.subheader("Cost Projection")
                st.plotly_chart(result["cost_chart"])

# Other tabs follow similar patterns...

if __name__ == "__main__":
    # No need to update st.session_state here
    pass