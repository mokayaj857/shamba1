import streamlit as st

class CostSimulator:
    def run_simulation(self, area, population):
        base_costs = {
            'equipment': 1500 * (area / 10),
            'installation': 500 * population,
            'maintenance': 200 * area,
            'licensing': 1000
        }
        total = sum(base_costs.values())
        
        return {
            'total_cost': total,
            'breakdown': base_costs,
            'roi_years': round(total / (population * 120), 1)
        }