import folium
import geopandas as gpd
import tempfile
import os
import streamlit as st
import zipfile

class TerrainAnalyzer:
    def __init__(self, uploaded_file):
        # Check if the uploaded file is a Shapefile (zipped)
        if uploaded_file.name.endswith('.zip'):
            # Extract the Shapefile from the zip
            with tempfile.TemporaryDirectory() as tmp_dir:
                zip_path = os.path.join(tmp_dir, uploaded_file.name)
                with open(zip_path, 'wb') as f:
                    f.write(uploaded_file.getbuffer())
                
                # Extract the zip file
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(tmp_dir)
                
                # Find the .shp file in the extracted files
                shp_file = None
                for file in os.listdir(tmp_dir):
                    if file.endswith('.shp'):
                        shp_file = os.path.join(tmp_dir, file)
                        break
                
                if shp_file:
                    try:
                        self.gdf = gpd.read_file(shp_file)
                    except Exception as e:
                        st.error(f"Error reading Shapefile: {e}")
                        raise
                else:
                    st.error("No .shp file found in the uploaded zip.")
                    raise ValueError("No .shp file found in the uploaded zip.")
        else:
            # Handle GeoJSON or other formats
            with tempfile.NamedTemporaryFile(delete=False, suffix='.geojson') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name

            try:
                self.gdf = gpd.read_file(tmp_file_path)
            except Exception as e:
                st.error(f"Error reading file: {e}")
                raise
            finally:
                os.unlink(tmp_file_path)

        # Ensure the GeoDataFrame has a valid geometry column
        if not isinstance(self.gdf, gpd.GeoDataFrame):
            st.error("Uploaded file does not contain valid geospatial data.")
            raise ValueError("Uploaded file does not contain valid geospatial data.")

        self.center = self._calculate_center()
        
    def _calculate_center(self):
        centroid = self.gdf.geometry.centroid
        return [centroid.y.mean(), centroid.x.mean()]
        
    def generate_map(self, vegetation_threshold=0.5):
        m = folium.Map(location=self.center, zoom_start=12)
        
        # Add Stamen Terrain tiles with attribution
        folium.TileLayer(
            tiles='Stamen Terrain',
            attr='Map tiles by <a href="https://stamen.com">Stamen Design</a>, under <a href="https://creativecommons.org/licenses/by/3.0">CC BY 3.0</a>. Data by <a href="https://openstreetmap.org">OpenStreetMap</a>, under <a href="https://www.openstreetmap.org/copyright">ODbL</a>.',
            name='Stamen Terrain'
        ).add_to(m)
        
        # Add GeoJSON layer
        folium.GeoJson(
            self.gdf,
            style_function=lambda feature: {
                'fillColor': self._color_by_vegetation(feature),
                'color': 'black',
                'weight': 1,
                'fillOpacity': 0.7
            }
        ).add_to(m)
        
        return m
    
    def _color_by_vegetation(self, feature):
        # Mock vegetation analysis
        if 'ndvi' in feature['properties']:
            return '#238823' if feature['properties']['ndvi'] > vegetation_threshold else '#ffd700'
        else:
            # Default color if 'ndvi' property is missing
            return '#ffd700'
    
    def get_statistics(self):
        return {
            'area': round(self.gdf.geometry.area.sum(), 2),
            'elevation': round(self.gdf['elevation'].mean(), 1) if 'elevation' in self.gdf.columns else 0,
            'vegetation': round(len(self.gdf[self.gdf['ndvi'] > 0.5])/len(self.gdf)*100, 1) if 'ndvi' in self.gdf.columns else 0
        }