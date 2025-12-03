import plotly.express as px
from utils.aiml_integration import AIMLClient

class NetworkOptimizer:
    def __init__(self):
        self.client = AIMLClient()
        
    def recommend_network(self, budget, tech_type, model_choice):
        system_prompt = f"""You are a network infrastructure expert specializing in {tech_type} 
        deployments for agricultural areas. Provide detailed technical recommendations including:
        - Optimal node placement strategy
        - Equipment specifications
        - Coverage expectations
        - Maintenance considerations"""
        
        user_prompt = f"""
        Budget: ${budget}
        Technology: {tech_type}
        Terrain Type: Agricultural land with mixed vegetation
        
        Required Output Format:
        ### Technical Analysis
        [detailed analysis]
        
        ### Recommended Equipment
        - [equipment list]
        
        ### Expected Coverage
        - Radius: [value] km
        """
        
        analysis = self.client.generate(
            model=model_choice,
            system_prompt=system_prompt,
            user_prompt=user_prompt
        )
        
        return {
            "analysis": analysis,
            "cost_chart": self._generate_cost_chart(budget)
        }
    
    def _generate_cost_chart(self, budget):
        nodes = [5, 10, 15, 20]
        costs = [budget * 0.2, budget * 0.5, budget * 0.8, budget]
        return px.bar(
            x=nodes, y=costs,
            labels={'x': 'Number of Nodes', 'y': 'Cost (USD)'},
            title="Cost vs Network Density"
        )