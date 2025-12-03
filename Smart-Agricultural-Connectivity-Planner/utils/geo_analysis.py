import geopandas as gpd
import folium
import streamlit as st
from shapely.geometry import shape

class TerrainAnalyzer:
    def __init__(self, geospatial_file):
        self.gdf = gpd.read_file(geospatial_file)
        self.center = self._calculate_center()
        
    def _calculate_center(self):
        centroid = self.gdf.geometry.centroid
        return [centroid.y.mean(), centroid.x.mean()]
        
    def generate_map(self, vegetation_threshold=0.5):
        m = folium.Map(location=self.center, zoom_start=12)
        
        # Add terrain layers
        folium.TileLayer('Stamen Terrain').add_to(m)
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
        return '#238823' if feature.properties.get('ndvi', 0) > 0.5 else '#ffd700'
    
    def get_statistics(self):
        return {
            'area': round(self.gdf.geometry.area.sum(), 2),
            'elevation': round(self.gdf['elevation'].mean(), 1),
            'vegetation': round(len(self.gdf[self.gdf['ndvi'] > 0.5])/len(self.gdf)*100, 1)
        }