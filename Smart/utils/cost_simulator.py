import streamlit as st

class CostSimulator:
    def run_simulation(self, area, population, deployment_type, tech_type):
        # Base costs based on area and population
        base_costs = {
            'equipment': 1500 * (area / 10),
            'installation': 500 * population,
            'maintenance': 200 * area,
            'licensing': 1000
        }

        # Adjust costs based on deployment type
        if deployment_type == "Low-Cost":
            base_costs['equipment'] *= 0.8  # 20% discount on equipment
            base_costs['installation'] *= 0.9  # 10% discount on installation
        elif deployment_type == "High-Coverage":
            base_costs['equipment'] *= 1.2  # 20% increase for better equipment
            base_costs['installation'] *= 1.1  # 10% increase for better installation

        # Adjust costs based on technology type
        if tech_type == "LoRaWAN":
            base_costs['equipment'] *= 0.9  # 10% discount for LoRaWAN
        elif tech_type == "5G":
            base_costs['equipment'] *= 1.5  # 50% increase for 5G
        elif tech_type == "Satellite":
            base_costs['equipment'] *= 2.0  # 100% increase for satellite

        # Calculate total cost
        total = sum(base_costs.values())

        # Calculate ROI (Return on Investment) in years
        roi_years = round(total / (population * 120), 1)

        # Calculate number of nodes required
        nodes = int(area / 5)  # 1 node per 5 sq km

        return {
            'total_cost': total,
            'breakdown': base_costs,
            'roi_years': roi_years,
            'nodes': nodes,
            'low_cost': total * 0.8,  # Low-cost strategy
            'balanced': total,  # Balanced strategy
            'high_coverage': total * 1.2  # High-coverage strategy
        }