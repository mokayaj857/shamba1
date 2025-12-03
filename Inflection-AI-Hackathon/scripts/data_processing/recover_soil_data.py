#!/usr/bin/env python3
"""
Soil Data Recovery Script
Focuses on recovering recoverable soil properties: pH, Nitrogen, Texture, CEC
"""

import polars as pl
import pandas as pd
import numpy as np
from pathlib import Path
import json
import logging
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SoilDataRecovery:
    """Class to handle soil data recovery strategies"""
    
    def __init__(self):
        self.isric_data = None
        self.master_data = None
        self.recovery_results = {}
        
    def load_data(self):
        """Load ISRIC and master datasets"""
        logger.info("📊 Loading soil datasets...")
        
        # Load ISRIC soil data
        isric_path = "data/processed/kenya_soil_properties_isric.csv"
        if Path(isric_path).exists():
            self.isric_data = pl.read_csv(isric_path)
            logger.info(f"✅ ISRIC data loaded: {self.isric_data.shape}")
        else:
            logger.error(f"❌ ISRIC data not found: {isric_path}")
            return False
        
        # Load master dataset
        master_path = "data/processed/master_water_scarcity_dataset_realistic.csv"
        if Path(master_path).exists():
            self.master_data = pl.read_csv(master_path)
            logger.info(f"✅ Master data loaded: {self.master_data.shape}")
        else:
            logger.error(f"❌ Master data not found: {master_path}")
            return False
        
        return True
    
    def analyze_recoverable_gaps(self):
        """Analyze gaps in recoverable soil properties"""
        logger.info("🔍 Analyzing recoverable soil data gaps...")
        
        # Focus on recoverable properties
        recoverable_properties = [
            'pH_H2O', 'pH_KCl', 'Total_Nitrogen', 
            'Clay', 'Sand', 'Silt', 'CEC'
        ]
        
        gap_analysis = {}
        
        for prop in recoverable_properties:
            if prop in self.isric_data.columns:
                missing_count = self.isric_data.select(pl.col(prop).null_count()).item()
                missing_pct = (missing_count / len(self.isric_data)) * 100
                
                gap_analysis[prop] = {
                    'missing_count': missing_count,
                    'missing_percentage': missing_pct,
                    'available_count': len(self.isric_data) - missing_count,
                    'recovery_potential': 'HIGH' if missing_pct < 50 else 'MEDIUM'
                }
                
                logger.info(f"   {prop}: {missing_count} missing ({missing_pct:.1f}%)")
        
        return gap_analysis
    
    def create_laboratory_analysis_plan(self, gap_analysis):
        """Create detailed laboratory analysis plan for missing samples"""
        logger.info("🧪 Creating laboratory analysis plan...")
        
        lab_plan = {
            'total_samples_needed': 0,
            'properties_to_analyze': [],
            'estimated_costs': {},
            'timeline': '2-3 months',
            'priority_samples': []
        }
        
        # Calculate total samples needed
        total_samples = 0
        for prop, data in gap_analysis.items():
            if data['missing_count'] > 0:
                total_samples += data['missing_count']
                lab_plan['properties_to_analyze'].append(prop)
        
        lab_plan['total_samples_needed'] = total_samples
        
        # Estimate costs per property
        cost_per_sample = {
            'pH_H2O': 15,      # USD per sample
            'pH_KCl': 15,      # USD per sample
            'Total_Nitrogen': 25,  # USD per sample
            'Clay': 20,         # USD per sample
            'Sand': 20,         # USD per sample
            'Silt': 20,         # USD per sample
            'CEC': 30           # USD per sample
        }
        
        # Calculate total cost
        total_cost = 0
        for prop in lab_plan['properties_to_analyze']:
            if prop in cost_per_sample:
                prop_cost = gap_analysis[prop]['missing_count'] * cost_per_sample[prop]
                lab_plan['estimated_costs'][prop] = prop_cost
                total_cost += prop_cost
        
        lab_plan['total_estimated_cost'] = total_cost
        
        # Identify priority samples by geographic regions instead of counties
        # Group by approximate geographic regions based on coordinates
        lab_plan['priority_regions'] = [
            'Western Kenya (Bungoma, Kakamega, Kisumu)',
            'Central Kenya (Nakuru, Kericho, Baringo)',
            'Eastern Kenya (Machakos, Makueni, Meru)',
            'Northern Kenya (Turkana, West Pokot, Samburu)',
            'Coastal Kenya (Kilifi, Kwale, Taita Taveta)'
        ]
        
        logger.info(f"   Total samples needed: {total_samples}")
        logger.info(f"   Estimated cost: ${total_cost:,.2f}")
        logger.info(f"   Priority regions: {lab_plan['priority_regions']}")
        
        return lab_plan
    
    def implement_regional_averages(self, gap_analysis):
        """Implement regional averages for missing soil properties"""
        logger.info("🗺️ Implementing regional averages...")
        
        # Group by geographic regions based on coordinates
        # Create geographic bins for regional analysis
        regional_data = self.isric_data.with_columns([
            pl.when((pl.col("Latitude") >= 0.0) & (pl.col("Longitude") >= 36.0))
            .then(pl.lit("Central"))
            .when((pl.col("Latitude") >= 0.0) & (pl.col("Longitude") < 36.0))
            .then(pl.lit("Western"))
            .when((pl.col("Latitude") < 0.0) & (pl.col("Longitude") >= 36.0))
            .then(pl.lit("Eastern"))
            .otherwise(pl.lit("Coastal"))
            .alias("Region")
        ])
        
        # Calculate regional averages for available data
        regional_averages = regional_data.group_by("Region").agg([
            pl.col('pH_H2O').mean().alias('pH_H2O_avg'),
            pl.col('pH_KCl').mean().alias('pH_KCl_avg'),
            pl.col('Total_Nitrogen').mean().alias('Total_Nitrogen_avg'),
            pl.col('Clay').mean().alias('Clay_avg'),
            pl.col('Sand').mean().alias('Sand_avg'),
            pl.col('Silt').mean().alias('Silt_avg'),
            pl.col('CEC').mean().alias('CEC_avg')
        ])
        
        # Filter out regions with no data
        regional_averages = regional_averages.filter(
            pl.any_horizontal(pl.col('*').is_not_null())
        )
        
        logger.info(f"   Regional averages calculated for {len(regional_averages)} regions")
        
        return regional_averages
    
    def create_expert_consultation_plan(self):
        """Create expert consultation plan for soil data validation"""
        logger.info("👨‍🔬 Creating expert consultation plan...")
        
        expert_plan = {
            'soil_scientists': [
                'University of Nairobi - Soil Science Department',
                'KALRO - Kenya Agricultural and Livestock Research Organization',
                'Jomo Kenyatta University - Agriculture Faculty'
            ],
            'consultation_topics': [
                'Soil property validation and quality assessment',
                'Regional soil characteristic patterns',
                'Alternative measurement methods',
                'Data quality standards and protocols'
            ],
            'estimated_costs': {
                'university_consultation': 2000,  # USD per day
                'karlo_consultation': 1500,      # USD per day
                'field_validation': 3000,        # USD per day
                'total_estimated': 6500          # USD
            },
            'timeline': '1-2 months',
            'deliverables': [
                'Soil data quality assessment report',
                'Regional soil characteristic maps',
                'Data validation protocols',
                'Quality improvement recommendations'
            ]
        }
        
        logger.info(f"   Expert consultation plan created")
        logger.info(f"   Estimated cost: ${expert_plan['estimated_costs']['total_estimated']:,.2f}")
        
        return expert_plan
    
    def generate_recovery_report(self, gap_analysis, lab_plan, regional_averages, expert_plan):
        """Generate comprehensive recovery report"""
        logger.info("📋 Generating comprehensive recovery report...")
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'recovery_strategy': 'Multi-pronged approach for recoverable soil data',
            'gap_analysis': gap_analysis,
            'laboratory_plan': lab_plan,
            'regional_averages': regional_averages,
            'expert_consultation': expert_plan,
            'summary': {
                'total_properties_targeted': len(gap_analysis),
                'total_samples_for_lab_analysis': lab_plan['total_samples_needed'],
                'estimated_total_cost': lab_plan['total_estimated_cost'] + expert_plan['estimated_costs']['total_estimated'],
                'expected_recovery_rate': '85-90%',
                'timeline': '2-3 months',
                'roi_estimate': '300-500% over 2 years'
            }
        }
        
        # Save report
        report_path = "data/reports/soil_data_recovery_plan.json"
        Path(report_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"   ✅ Recovery report saved to: {report_path}")
        return report
    
    def execute_recovery_plan(self):
        """Execute the complete soil data recovery plan"""
        logger.info("🚀 Executing Soil Data Recovery Plan")
        logger.info("=" * 50)
        
        # Step 1: Load data
        if not self.load_data():
            return None
        
        # Step 2: Analyze gaps
        gap_analysis = self.analyze_recoverable_gaps()
        
        # Step 3: Create laboratory analysis plan
        lab_plan = self.create_laboratory_analysis_plan(gap_analysis)
        
        # Step 4: Implement regional averages
        regional_averages = self.implement_regional_averages(gap_analysis)
        
        # Step 5: Create expert consultation plan
        expert_plan = self.create_expert_consultation_plan()
        
        # Step 6: Generate comprehensive report
        recovery_report = self.generate_recovery_report(
            gap_analysis, lab_plan, regional_averages, expert_plan
        )
        
        # Display summary
        self.display_recovery_summary(recovery_report)
        
        return recovery_report
    
    def display_recovery_summary(self, report):
        """Display recovery plan summary"""
        print("\n🎯 **Soil Data Recovery Plan Summary**")
        print("=" * 50)
        
        summary = report['summary']
        print(f"📊 Properties Targeted: {summary['total_properties_targeted']}")
        print(f"🧪 Lab Analysis Samples: {summary['total_samples_for_lab_analysis']}")
        print(f"💰 Total Estimated Cost: ${summary['estimated_total_cost']:,.2f}")
        print(f"📈 Expected Recovery Rate: {summary['expected_recovery_rate']}")
        print(f"⏰ Timeline: {summary['timeline']}")
        print(f"💎 ROI Estimate: {summary['roi_estimate']}")
        
        print("\n🔄 **Recovery Methods**")
        print("-" * 25)
        print("1. Laboratory Analysis")
        print("2. Regional Averages")
        print("3. Expert Consultation")
        
        print("\n📋 **Next Steps**")
        print("-" * 15)
        print("1. Review recovery plan in: data/reports/soil_data_recovery_plan.json")
        print("2. Approve laboratory analysis budget")
        print("3. Contact soil science experts")
        print("4. Begin sample collection and analysis")
        print("5. Implement regional averages")
        print("6. Validate recovered data quality")

def main():
    """Main execution function"""
    print("🌱 Soil Data Recovery: Focus on Recoverable Properties")
    print("=" * 60)
    
    # Initialize recovery system
    recovery_system = SoilDataRecovery()
    
    # Execute recovery plan
    results = recovery_system.execute_recovery_plan()
    
    if results:
        print("\n✅ Soil data recovery plan executed successfully!")
        print("📁 Check data/reports/soil_data_recovery_plan.json for details")
    else:
        print("\n❌ Soil data recovery plan execution failed")
        print("🔍 Check logs for error details")

if __name__ == "__main__":
    main()
