#!/usr/bin/env python3
"""
Feature Selection for Bitcoin Address Classification

This script analyzes the BABD-13 dataset to identify the best features for classifying Bitcoin addresses.
It excludes constant or near-constant features and focuses on discriminative features.
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import SelectKBest, chi2, f_classif
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import warnings
import os
import json
from datetime import datetime

warnings.filterwarnings('ignore')

def load_and_analyze_data(data_path):
    """Load and analyze the dataset."""
    print("Loading dataset...")
    data = pd.read_csv(data_path)
    
    print(f"Dataset shape: {data.shape}")
    print(f"Label distribution:\n{data['label'].value_counts().sort_index()}")
    
    # Remove non-numeric columns (account and SW)
    numeric_columns = data.select_dtypes(include=[np.number]).columns.tolist()
    print(f"Numeric columns: {len(numeric_columns)}")
    
    # Prepare features and target
    X = data[numeric_columns].drop('label', axis=1)
    y = data['label']
    
    print(f"Feature matrix shape: {X.shape}")
    print(f"Target vector shape: {y.shape}")
    
    # Check for missing values
    print(f"Missing values in features: {X.isnull().sum().sum()}")
    print(f"Missing values in target: {y.isnull().sum()}")
    
    # Fill any missing values with 0
    X = X.fillna(0)
    
    return X, y

def remove_constant_features(X, threshold=0.99):
    """Remove features that are constant or nearly constant."""
    print(f"\nRemoving constant/near-constant features (threshold: {threshold})...")
    
    # Calculate coefficient of variation for each feature
    cv_scores = []
    for col in X.columns:
        std = X[col].std()
        mean = X[col].mean()
        if mean != 0:
            cv = std / abs(mean)
        else:
            cv = 0
        cv_scores.append(cv)
    
    # Create DataFrame with CV scores
    cv_df = pd.DataFrame({
        'Feature': X.columns,
        'CV_Score': cv_scores,
        'Std': [X[col].std() for col in X.columns],
        'Mean': [X[col].mean() for col in X.columns],
        'Min': [X[col].min() for col in X.columns],
        'Max': [X[col].max() for col in X.columns]
    })
    
    # Sort by CV score
    cv_df = cv_df.sort_values('CV_Score', ascending=False)
    
    print("Top 20 features by coefficient of variation:")
    print(cv_df.head(20))
    
    print("\nBottom 20 features by coefficient of variation (likely constant):")
    print(cv_df.tail(20))
    
    # Remove features with very low CV (near constant)
    low_variance_features = cv_df[cv_df['CV_Score'] < threshold]['Feature'].tolist()
    print(f"\nRemoving {len(low_variance_features)} low-variance features")
    
    # Keep features with sufficient variance
    good_features = cv_df[cv_df['CV_Score'] >= threshold]['Feature'].tolist()
    X_filtered = X[good_features]
    
    print(f"Features after filtering: {X_filtered.shape[1]}")
    
    return X_filtered, cv_df, low_variance_features

def statistical_feature_selection(X, y):
    """Perform statistical feature selection."""
    print("\nPerforming statistical feature selection...")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"Training set: {X_train.shape}")
    print(f"Test set: {X_test.shape}")
    
    # 1. Chi-square test
    print("\n1. Chi-square Test Results:")
    print("=" * 50)
    
    # Make features non-negative for chi-square test
    X_train_abs = np.abs(X_train)
    
    chi2_selector = SelectKBest(score_func=chi2, k=20)
    chi2_selector.fit(X_train_abs, y_train)
    
    chi2_scores = chi2_selector.scores_
    chi2_pvalues = chi2_selector.pvalues_
    
    chi2_results = pd.DataFrame({
        'Feature': X.columns,
        'Chi2_Score': chi2_scores,
        'P_Value': chi2_pvalues
    })
    chi2_results = chi2_results.sort_values('Chi2_Score', ascending=False)
    
    print("Top 20 features by Chi-square score:")
    print(chi2_results.head(20))
    
    # 2. F-test (ANOVA)
    print("\n2. F-test (ANOVA) Results:")
    print("=" * 50)
    
    f_selector = SelectKBest(score_func=f_classif, k=20)
    f_selector.fit(X_train, y_train)
    
    f_scores = f_selector.scores_
    f_pvalues = f_selector.pvalues_
    
    f_results = pd.DataFrame({
        'Feature': X.columns,
        'F_Score': f_scores,
        'P_Value': f_pvalues
    })
    f_results = f_results.sort_values('F_Score', ascending=False)
    
    print("Top 20 features by F-score:")
    print(f_results.head(20))
    
    return chi2_results, f_results, X_train, X_test, y_train, y_test

def random_forest_selection(X_train, X_test, y_train, y_test, feature_names):
    """Perform Random Forest feature importance selection."""
    print("\n3. Random Forest Feature Importance:")
    print("=" * 50)
    
    try:
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train Random Forest
        rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
        rf.fit(X_train_scaled, y_train)
        
        rf_importance = rf.feature_importances_
        
        rf_results = pd.DataFrame({
            'Feature': feature_names,
            'RF_Importance': rf_importance
        })
        rf_results = rf_results.sort_values('RF_Importance', ascending=False)
        
        print("Top 20 features by Random Forest importance:")
        print(rf_results.head(20))
        
        # Evaluate RF performance
        rf_pred = rf.predict(X_test_scaled)
        rf_accuracy = accuracy_score(y_test, rf_pred)
        print(f"\nRandom Forest Accuracy: {rf_accuracy:.4f}")
        
        return rf_results, rf_accuracy
    except Exception as e:
        print(f"Error in Random Forest selection: {e}")
        return pd.DataFrame(), 0.0

def correlation_analysis(X, y):
    """Perform correlation analysis with target."""
    print("\n4. Feature Correlation with Target:")
    print("=" * 50)
    
    correlations = []
    for feature in X.columns:
        try:
            corr = np.corrcoef(X[feature], y)[0, 1]
            correlations.append(abs(corr) if not np.isnan(corr) else 0.0)
        except:
            correlations.append(0.0)
    
    corr_results = pd.DataFrame({
        'Feature': X.columns,
        'Abs_Correlation': correlations
    })
    corr_results = corr_results.sort_values('Abs_Correlation', ascending=False)
    
    print("Top 20 features by absolute correlation with target:")
    print(corr_results.head(20))
    
    return corr_results

def comprehensive_ranking(chi2_results, f_results, rf_results, corr_results):
    """Combine all methods for comprehensive ranking."""
    print("\n5. Comprehensive Feature Ranking:")
    print("=" * 50)
    
    # Merge all results
    comprehensive_results = chi2_results[['Feature', 'Chi2_Score']].copy()
    comprehensive_results = comprehensive_results.merge(
        f_results[['Feature', 'F_Score']], on='Feature', how='left'
    )
    
    if not rf_results.empty:
        comprehensive_results = comprehensive_results.merge(
            rf_results[['Feature', 'RF_Importance']], on='Feature', how='left'
        )
    else:
        comprehensive_results['RF_Importance'] = 0.0
        
    comprehensive_results = comprehensive_results.merge(
        corr_results[['Feature', 'Abs_Correlation']], on='Feature', how='left'
    )
    
    # Fill NaN values with 0
    comprehensive_results = comprehensive_results.fillna(0)
    
    # Normalize scores to 0-1 range for fair comparison
    for col in ['Chi2_Score', 'F_Score', 'RF_Importance', 'Abs_Correlation']:
        if comprehensive_results[col].max() > comprehensive_results[col].min():
            comprehensive_results[f'{col}_Normalized'] = (
                comprehensive_results[col] - comprehensive_results[col].min()
            ) / (comprehensive_results[col].max() - comprehensive_results[col].min())
        else:
            comprehensive_results[f'{col}_Normalized'] = 0.0
    
    # Calculate average normalized score
    normalized_cols = [
        'Chi2_Score_Normalized', 'F_Score_Normalized', 
        'RF_Importance_Normalized', 'Abs_Correlation_Normalized'
    ]
    comprehensive_results['Average_Score'] = comprehensive_results[normalized_cols].mean(axis=1)
    
    # Sort by average score
    comprehensive_results = comprehensive_results.sort_values('Average_Score', ascending=False)
    
    print("Top 20 features by comprehensive ranking:")
    print(comprehensive_results[['Feature', 'Average_Score'] + normalized_cols].head(20))
    
    return comprehensive_results

def performance_evaluation(X_train, X_test, y_train, y_test, comprehensive_results):
    """Evaluate performance with different numbers of features."""
    print("\n6. Performance Evaluation with Different Feature Sets:")
    print("=" * 50)
    
    feature_counts = [5, 8, 10, 15, 20, 25, 30]
    results = []
    
    for n_features in feature_counts:
        try:
            # Get top n features
            top_features = comprehensive_results['Feature'].head(n_features).tolist()
            
            # Select features
            X_train_selected = X_train[top_features]
            X_test_selected = X_test[top_features]
            
            # Scale features
            scaler_selected = StandardScaler()
            X_train_scaled_selected = scaler_selected.fit_transform(X_train_selected)
            X_test_scaled_selected = scaler_selected.transform(X_test_selected)
            
            # Train Random Forest
            rf_selected = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
            rf_selected.fit(X_train_scaled_selected, y_train)
            
            # Evaluate
            train_score = rf_selected.score(X_train_scaled_selected, y_train)
            test_score = rf_selected.score(X_test_scaled_selected, y_test)
            
            results.append({
                'n_features': n_features,
                'train_accuracy': train_score,
                'test_accuracy': test_score,
                'features': top_features
            })
            
            print(f"{n_features} features - Train: {train_score:.4f}, Test: {test_score:.4f}")
        except Exception as e:
            print(f"Error evaluating {n_features} features: {e}")
    
    return results

def final_recommendation(performance_results, comprehensive_results, current_features):
    """Provide final feature selection recommendation."""
    print("\n7. Final Feature Selection Recommendation:")
    print("=" * 50)
    
    if not performance_results:
        print("No performance results available")
        return {}
    
    results_df = pd.DataFrame(performance_results)
    
    # Find optimal number of features (where test accuracy is highest)
    optimal_idx = results_df['test_accuracy'].idxmax()
    optimal_n_features = results_df.loc[optimal_idx, 'n_features']
    optimal_accuracy = results_df.loc[optimal_idx, 'test_accuracy']
    optimal_features = results_df.loc[optimal_idx, 'features']
    
    print(f"Optimal number of features: {optimal_n_features}")
    print(f"Optimal test accuracy: {optimal_accuracy:.4f}")
    print(f"\nOptimal feature set:")
    for i, feature in enumerate(optimal_features, 1):
        print(f"{i:2d}. {feature}")
    
    # Compare with current features
    print(f"\nCurrent features used in the model:")
    for i, feature in enumerate(current_features, 1):
        print(f"{i:2d}. {feature}")
    
    # Check overlap
    overlap = set(current_features).intersection(set(optimal_features))
    print(f"\nOverlap with optimal features: {len(overlap)}/{len(current_features)} features")
    print(f"Overlapping features: {sorted(overlap)}")
    
    return {
        'optimal_n_features': optimal_n_features,
        'optimal_accuracy': optimal_accuracy,
        'optimal_features': optimal_features,
        'current_features': current_features,
        'overlap_count': len(overlap),
        'overlapping_features': sorted(overlap)
    }

def save_results(comprehensive_results, final_results, cv_df, output_dir="results"):
    """Save all results to files."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save comprehensive results
    csv_path = os.path.join(output_dir, f"feature_selection_results_{timestamp}.csv")
    comprehensive_results.to_csv(csv_path, index=False)
    print(f"\nComprehensive results saved to: {csv_path}")
    
    # Convert numpy types to Python native types for JSON serialization
    final_results_json = {}
    for key, value in final_results.items():
        if isinstance(value, (np.integer, np.int64)):
            final_results_json[key] = int(value)
        elif isinstance(value, (np.floating, np.float64)):
            final_results_json[key] = float(value)
        elif isinstance(value, list):
            final_results_json[key] = [str(item) if isinstance(item, (np.integer, np.int64, np.floating, np.float64)) else item for item in value]
        else:
            final_results_json[key] = value
    
    # Save final recommendation
    json_path = os.path.join(output_dir, f"final_recommendation_{timestamp}.json")
    with open(json_path, 'w') as f:
        json.dump(final_results_json, f, indent=2)
    print(f"Final recommendation saved to: {json_path}")
    
    # Save CV analysis
    cv_path = os.path.join(output_dir, f"cv_analysis_{timestamp}.csv")
    cv_df.to_csv(cv_path, index=False)
    print(f"CV analysis saved to: {cv_path}")

def main():
    """Main function to run the feature selection analysis."""
    # Path to the dataset
    data_path = "/Users/arnemallon/Developer/Datasets/BABD-13.csv"
    
    # Check if dataset exists
    if not os.path.exists(data_path):
        print(f"Error: Dataset not found at {data_path}")
        print("Please update the data_path variable with the correct path to your dataset.")
        return
    
    print("BITCOIN ADDRESS CLASSIFICATION - FEATURE SELECTION")
    print("=" * 60)
    
    # Load and analyze data
    X, y = load_and_analyze_data(data_path)
    
    # Remove constant features (including S features)
    X_filtered, cv_df, low_variance_features = remove_constant_features(X)
    
    # Current features used in the model
    current_features = ['PAIa13', 'S2-3', 'CI2a32-2', 'CI2a32-4', 'S2-2', 'PAIa11-1', 'PAIa11-2', 'S2-1']
    
    # Check which current features were removed
    removed_current_features = [f for f in current_features if f in low_variance_features]
    if removed_current_features:
        print(f"\nWARNING: The following current features were removed as low-variance:")
        for feature in removed_current_features:
            print(f"  - {feature}")
    
    # Perform feature selection
    chi2_results, f_results, X_train, X_test, y_train, y_test = statistical_feature_selection(X_filtered, y)
    rf_results, rf_accuracy = random_forest_selection(X_train, X_test, y_train, y_test, X_filtered.columns)
    corr_results = correlation_analysis(X_filtered, y)
    
    # Create comprehensive ranking
    comprehensive_results = comprehensive_ranking(chi2_results, f_results, rf_results, corr_results)
    
    # Evaluate performance
    performance_results = performance_evaluation(X_train, X_test, y_train, y_test, comprehensive_results)
    
    # Get final recommendation
    final_results = final_recommendation(performance_results, comprehensive_results, current_features)
    
    # Save results
    save_results(comprehensive_results, final_results, cv_df)
    
    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)
    
    # Print summary
    if final_results:
        print("\nSUMMARY:")
        print(f"Optimal number of features: {final_results['optimal_n_features']}")
        print(f"Optimal accuracy: {final_results['optimal_accuracy']:.4f}")
        print(f"Optimal features: {final_results['optimal_features']}")
        print(f"Overlap with current features: {final_results['overlap_count']}/8")
        
        if removed_current_features:
            print(f"\nIMPORTANT: {len(removed_current_features)} current features were low-variance:")
            for feature in removed_current_features:
                print(f"  - {feature}")

if __name__ == "__main__":
    main() 