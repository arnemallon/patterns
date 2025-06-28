#!/usr/bin/env python3
"""
Feature Analysis for Bitcoin Address Classification

This script analyzes the existing feature selection results and provides recommendations
for the best features to use in the Bitcoin address classification model.
"""

import pandas as pd
import numpy as np
import json
import os
from datetime import datetime

def analyze_existing_features():
    """Analyze the existing 8 features used in the current model."""
    
    print("ANALYSIS OF CURRENT FEATURES")
    print("=" * 50)
    
    # Current features used in the model
    current_features = [
        'PAIa13', 'S2-3', 'CI2a32-2', 'CI2a32-4', 
        'S2-2', 'PAIa11-1', 'PAIa11-2', 'S2-1'
    ]
    
    print("Current 8 features used in the ML model:")
    for i, feature in enumerate(current_features, 1):
        print(f"{i:2d}. {feature}")
    
    # Feature descriptions based on the dataset analysis
    feature_descriptions = {
        'PAIa13': 'Ratio of total received to total sent (or total received if sent=0)',
        'S2-3': 'Total number of unique addresses (inputs + outputs)',
        'CI2a32-2': 'Maximum ratio of input amount to total transaction amount',
        'CI2a32-4': 'Maximum ratio of output amount to total transaction amount',
        'S2-2': 'Number of unique output addresses',
        'PAIa11-1': 'Total amount received (in BTC)',
        'PAIa11-2': 'Total amount sent (in BTC)',
        'S2-1': 'Number of unique input addresses'
    }
    
    print("\nFeature descriptions:")
    for feature in current_features:
        print(f"{feature}: {feature_descriptions[feature]}")
    
    return current_features, feature_descriptions

def analyze_feature_categories():
    """Categorize features by their type and importance."""
    
    print("\nFEATURE CATEGORIZATION")
    print("=" * 50)
    
    # Categorize features by type
    transaction_volume_features = ['PAIa11-1', 'PAIa11-2', 'PAIa13']
    network_features = ['S2-1', 'S2-2', 'S2-3']
    behavior_features = ['CI2a32-2', 'CI2a32-4']
    
    print("Transaction Volume Features:")
    for feature in transaction_volume_features:
        print(f"  - {feature}")
    
    print("\nNetwork Topology Features:")
    for feature in network_features:
        print(f"  - {feature}")
    
    print("\nBehavioral Pattern Features:")
    for feature in behavior_features:
        print(f"  - {feature}")
    
    return {
        'transaction_volume': transaction_volume_features,
        'network_topology': network_features,
        'behavioral_patterns': behavior_features
    }

def recommend_feature_improvements():
    """Recommend potential improvements to the feature set."""
    
    print("\nFEATURE IMPROVEMENT RECOMMENDATIONS")
    print("=" * 50)
    
    # Based on the chi-square analysis from previous notebooks
    top_features_from_analysis = [
        'PAIa13', 'S2-3', 'CI2a32-2', 'CI2a32-4', 'S2-2', 
        'PAIa11-1', 'PAIa11-2', 'S2-1', 'CI3a32-2', 'PDIa1-R3',
        'PDIa1-3', 'PDIa13-R'
    ]
    
    current_features = [
        'PAIa13', 'S2-3', 'CI2a32-2', 'CI2a32-4', 
        'S2-2', 'PAIa11-1', 'PAIa11-2', 'S2-1'
    ]
    
    # Find additional features that could be beneficial
    additional_features = [f for f in top_features_from_analysis if f not in current_features]
    
    print("Current feature set is well-optimized based on chi-square analysis.")
    print(f"Current features: {len(current_features)}")
    print(f"Top features from analysis: {len(top_features_from_analysis)}")
    
    if additional_features:
        print(f"\nPotential additional features to consider:")
        for i, feature in enumerate(additional_features, 1):
            print(f"{i}. {feature}")
    
    # Recommendations
    recommendations = [
        "1. The current 8-feature set is well-chosen based on statistical analysis",
        "2. Features cover key aspects: transaction volume, network topology, and behavioral patterns",
        "3. Consider adding CI3a32-2 and PDIa1-R3 if model performance needs improvement",
        "4. Monitor feature importance over time as Bitcoin usage patterns evolve",
        "5. Consider feature engineering to create interaction terms between related features"
    ]
    
    print("\nRecommendations:")
    for rec in recommendations:
        print(f"  {rec}")
    
    return additional_features, recommendations

def analyze_feature_correlations():
    """Analyze potential correlations between features."""
    
    print("\nFEATURE CORRELATION ANALYSIS")
    print("=" * 50)
    
    # Based on feature descriptions, identify potential correlations
    potential_correlations = [
        ("PAIa11-1 (total received) and PAIa11-2 (total sent)", "May be correlated for active addresses"),
        ("S2-1 (input addresses) and S2-2 (output addresses)", "Related to transaction complexity"),
        ("S2-3 (total unique addresses) and S2-1/S2-2", "S2-3 is union of S2-1 and S2-2"),
        ("CI2a32-2 and CI2a32-4", "Both relate to transaction amount ratios"),
        ("PAIa13 (received/sent ratio) and PAIa11-1/PAIa11-2", "Directly related to volume features")
    ]
    
    print("Potential feature correlations to monitor:")
    for i, (features, description) in enumerate(potential_correlations, 1):
        print(f"{i}. {features}: {description}")
    
    return potential_correlations

def create_feature_selection_report():
    """Create a comprehensive feature selection report."""
    
    print("\nCOMPREHENSIVE FEATURE SELECTION REPORT")
    print("=" * 60)
    
    # Get all analyses
    current_features, descriptions = analyze_existing_features()
    categories = analyze_feature_categories()
    additional_features, recommendations = recommend_feature_improvements()
    correlations = analyze_feature_correlations()
    
    # Create report
    report = {
        'timestamp': datetime.now().isoformat(),
        'current_features': current_features,
        'feature_descriptions': descriptions,
        'feature_categories': categories,
        'additional_features': additional_features,
        'recommendations': recommendations,
        'potential_correlations': correlations,
        'summary': {
            'total_current_features': len(current_features),
            'transaction_volume_features': len(categories['transaction_volume']),
            'network_features': len(categories['network_topology']),
            'behavioral_features': len(categories['behavioral_patterns']),
            'additional_features_count': len(additional_features)
        }
    }
    
    # Save report
    if not os.path.exists('results'):
        os.makedirs('results')
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = f"results/feature_selection_report_{timestamp}.json"
    
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nReport saved to: {report_path}")
    
    # Print summary
    print("\nSUMMARY")
    print("=" * 30)
    print(f"Current features: {report['summary']['total_current_features']}")
    print(f"Transaction volume features: {report['summary']['transaction_volume_features']}")
    print(f"Network topology features: {report['summary']['network_features']}")
    print(f"Behavioral pattern features: {report['summary']['behavioral_features']}")
    print(f"Additional features to consider: {report['summary']['additional_features_count']}")
    
    return report

def main():
    """Main function to run the feature analysis."""
    
    print("BITCOIN ADDRESS CLASSIFICATION - FEATURE ANALYSIS")
    print("=" * 60)
    
    # Create comprehensive report
    report = create_feature_selection_report()
    
    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)
    print("The current 8-feature set is well-optimized for Bitcoin address classification.")
    print("Key findings:")
    print("- Features cover transaction volume, network topology, and behavioral patterns")
    print("- Based on chi-square analysis, these are among the most discriminative features")
    print("- Consider adding 4 additional features if model performance needs improvement")
    print("- Monitor feature correlations and importance over time")

if __name__ == "__main__":
    main() 