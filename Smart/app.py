import streamlit as st
from utils.geo_analysis import TerrainAnalyzer
from utils.network_models import NetworkOptimizer
from utils.cost_simulator import CostSimulator
import folium
import plotly.express as px
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
    st.markdown("""
    # 🌾 Smart Agricultural Connectivity Planner (SACP)

    Welcome to the **Smart Agricultural Connectivity Planner**! This app helps rural farmers and policymakers optimize internet connectivity for agricultural hubs using AI-powered tools.

    ---

    ## 🚀 **How to Use This App**
    ### 2. **Navigation**
    - Use the **sidebar** to switch between different features.
    - Each tab provides a unique functionality to help you plan and optimize connectivity.

    ---

    ## 🛠️ **Features and How to Use Them**

    ### 🗺️ **Geospatial Analysis**
    - **What It Does**: Analyzes terrain and vegetation using uploaded geospatial data.
    - **How to Use**:
      1. Upload a GeoJSON or Shapefile.
      2. Adjust parameters like vegetation density threshold.
      3. View interactive maps and key metrics (elevation, vegetation, water bodies).
    - **How It Helps**: Identifies optimal locations for network nodes based on terrain.

    ### 📡 **Network Design**
    - **What It Does**: Recommends the best network configuration (LoRaWAN, 5G, etc.) for your budget.
    - **How to Use**:
      1. Set your budget and select a technology.
      2. Choose an AI model for recommendations.
      3. View detailed technical plans and cost projections.
    - **How It Helps**: Ensures cost-effective and efficient network deployment.

    ### 💸 **Cost Simulation**
    - **What It Does**: Simulates infrastructure costs based on area size and population.
    - **How to Use**:
      1. Input the area size and target population.
      2. View a breakdown of costs (equipment, installation, maintenance).
      3. Compare different deployment strategies.
    - **How It Helps**: Helps plan budgets and estimate ROI for connectivity projects.

    ### 📊 **Dashboard**
    - **What It Does**: Tracks connectivity scores, yield improvements, and ROI timelines.
    - **How to Use**:
      1. View real-time metrics on network coverage and agricultural impact.
      2. Monitor progress over time.
    - **How It Helps**: Provides actionable insights for improving connectivity and farming outcomes.

    ---

    ## 🎯 **Key Benefits**
    - **For Farmers**:
      - Access real-time market and climate data.
      - Improve crop yields with smart agricultural tools.
    - **For Policymakers**:
      - Plan cost-effective network deployments.
      - Bridge the digital divide in rural areas.

    ---

    ## 📥 **Sample Data**
    Download sample GeoJSON files to test the app:
    [Sample Data Download](https://github.com/hanzlikhan/Smart-Agricultural-Connectivity-Planner/tree/new-feature/Data)

    ---

    ## ❓ **Need Help?**
    - Check the [documentation](https://example.com/docs).
    - Contact support: support@agri-connect.com
    """)
    
# Tab 2: Geospatial Analysis
elif current_tab == "🗺️ Geospatial":
    st.header("Geospatial Analysis Module")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        uploaded_file = st.file_uploader(
            "Upload Geospatial Data",
            type=["geojson", "zip"],
            help="Supported formats: GeoJSON, Zipped Shapefile (.zip)"
        )
        
    with col2:
        st.subheader("Analysis Parameters")
        veg_threshold = st.slider("Vegetation Threshold", 0.0, 1.0, 0.5)
        elevation_range = st.slider("Elevation Range (m)", 0, 2000, (0, 1000))
    
    if uploaded_file:
        try:
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
        except Exception as e:
            st.error(f"An error occurred: {e}")
# Tab 3: Network Design
elif current_tab == "📡 Network":
    st.header("Network Design Studio")
    
    with st.form("network_form"):
        col1, col2 = st.columns(2)
        with col1:
            budget = st.number_input("Budget (USD)", 1000, 1000000, 5000)
            tech_type = st.selectbox("Technology", ["LoRaWAN", "5G", "Satellite", "Mesh"])
            
        with col2:
            model_choice = st.selectbox("AI Model", ["MiniMax-Text-01", "gpt-4.5-preview"])
            terrain_type = st.selectbox("Terrain Complexity", ["Simple", "Moderate", "Complex"])
        
        if st.form_submit_button("Generate Plan"):
            with st.spinner("Creating optimal network configuration..."):
                result = optimizer.recommend_network(budget, tech_type, model_choice)
                
                st.subheader("Technical Plan")
                st.markdown(result["analysis"])
                
                st.subheader("Cost Projection")
                st.plotly_chart(result["cost_chart"])
elif current_tab == "📡 Network":
    st.header("Network Design Studio")
    
    # Use a unique key for the form to avoid conflicts
    with st.form(key="network_form"):
        col1, col2 = st.columns(2)
        with col1:
            budget = st.number_input("Budget (USD)", 1000, 1000000, 5000, key="budget_input")
            tech_type = st.selectbox("Technology", ["LoRaWAN", "5G", "Satellite", "Mesh"], key="tech_select")
            
        with col2:
            model_choice = st.selectbox("AI Model", ["MiniMax-Text-01", "gpt-4.5-preview"], key="model_select")
            terrain_type = st.selectbox("Terrain Complexity", ["Simple", "Moderate", "Complex"], key="terrain_select")
        
        # Form submit button
        if st.form_submit_button("Generate Plan", key="generate_plan_button"):
            with st.spinner("Creating optimal network configuration..."):
                # Call the optimizer
                result = optimizer.recommend_network(budget, tech_type, model_choice)
                
                # Display results
                st.subheader("Technical Plan")
                st.markdown(result["analysis"])
                
                st.subheader("Cost Projection")
                st.plotly_chart(result["cost_chart"])
elif current_tab == "💸 Costs":
    st.header("Cost Simulation Module")
    
    with st.form(key="cost_simulation_form"):
        col1, col2 = st.columns(2)
        with col1:
            area = st.number_input("Area Size (sq km)", min_value=1, value=10, key="area_input")
            population = st.number_input("Target Population", min_value=100, value=1000, key="population_input")
        
        with col2:
            deployment_type = st.selectbox(
                "Deployment Strategy", 
                ["Low-Cost", "Balanced", "High-Coverage"], 
                key="deployment_select"
            )
            tech_type = st.selectbox(
                "Technology", 
                ["LoRaWAN", "5G", "Satellite", "Mesh"], 
                key="cost_tech_select"
            )
        
        # Corrected submit button (no key argument)
        submitted = st.form_submit_button("Simulate Costs")
        if submitted:
            with st.spinner("Calculating infrastructure costs..."):
                simulation_result = simulator.run_simulation(area, population, deployment_type, tech_type)
                
                st.subheader("Cost Breakdown")
                cols = st.columns(3)
                cols[0].metric("Total Cost", f"${simulation_result['total_cost']:,.2f}")
                cols[1].metric("ROI Timeline", f"{simulation_result['roi_years']} years")
                cols[2].metric("Nodes Required", simulation_result['nodes'])
                
                st.subheader("Detailed Cost Components")
                st.table(simulation_result["breakdown"])
                
                st.subheader("Cost vs Coverage")
                st.plotly_chart(px.bar(
                    x=["Low-Cost", "Balanced", "High-Coverage"],
                    y=[simulation_result['low_cost'], simulation_result['balanced'], simulation_result['high_coverage']],
                    labels={'x': 'Strategy', 'y': 'Cost (USD)'},
                    title="Cost Comparison by Deployment Strategy"
                ))

# Tab 5: Dashboard
elif current_tab == "📊 Dashboard":
    st.header("Agricultural Impact Dashboard")
    
    # Sample metrics (replace with real data)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Connectivity Score", "78/100", "+12% potential")
    with col2:
        st.metric("Yield Improvement", "22%", "With full deployment")
    with col3:
        st.metric("ROI Timeline", "3.2 years", "Based on simulation")
    
    # Coverage map
    st.subheader("Network Coverage")
    if st.session_state.map_data:
        folium_static(st.session_state.map_data)
    else:
        st.warning("Upload geospatial data in the 'Geospatial' tab to view coverage.")
    
    # Performance trends
    st.subheader("Performance Over Time")
    trend_data = {
        "Month": ["Jan", "Feb", "Mar", "Apr", "May"],
        "Connectivity": [65, 70, 75, 78, 80],
        "Yield": [15, 17, 19, 21, 22]
    }
    st.line_chart(trend_data, x="Month", y=["Connectivity", "Yield"])
    
    # ROI analysis
    st.subheader("ROI Analysis")
    roi_data = {
        "Year": [1, 2, 3, 4, 5],
        "Cumulative ROI": [0.2, 0.5, 0.8, 1.2, 1.5]
    }
    st.area_chart(roi_data, x="Year", y="Cumulative ROI")
# if __name__ == "__main__":
    # st.session_state.update(st.session_state)
    
# Footer for every tab
st.markdown("---")
st.markdown("### 🛠️ **Developed By**")
st.markdown("- **Muhammad Hanzala**: [khangormani79@gmail.com](mailto:khangormani79@gmail.com)")
st.markdown("- **Amira Sayed**: [amira.sayedza@gmail.com](mailto:amira.sayedza@gmail.com)")