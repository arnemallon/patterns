# Bitcoin Address Classification - Feature Selection Analysis

## Executive Summary

The feature selection analysis was conducted on a large Bitcoin address dataset (544,462 samples, 151 features) to identify the optimal feature set for address classification. The analysis revealed that the current 8-feature model is well-designed, but there's potential for improvement with additional features.

## Key Findings

### 1. Data Quality Issues
- **26 low-variance features removed** (including S2-2, S2-3 from current model)
- **S-features are problematic**: Many S-features show very low variance and were correctly identified as unsuitable
- **Final dataset**: 122 features after filtering (from original 151)

### 2. Current Model Assessment
**Current 8 features used:**
- PAIa13, S2-3, CI2a32-2, CI2a32-4, S2-2, PAIa11-1, PAIa11-2, S2-1

**Issues identified:**
- S2-2 and S2-3 were removed as low-variance features
- 6 out of 8 current features overlap with optimal selection

### 3. Optimal Feature Selection

**Best performing feature set (30 features):**
1. S2-1 (top performer across all methods)
2. PTIa41-2 (highest correlation with target)
3. PTIa41-3
4. S4
5. CI2a32-2 (current feature)
6. PTIa21
7. CI3a12-3
8. S8
9. S9
10. PTIa41-1
11. CI3a22-2
12. CI3a21-1
13. PAIa13 (current feature)
14. CI3a22-1
15. CI3a22-5
16. CI3a23-1
17. CI3a12-4
18. PTIa2
19. CI2a32-4 (current feature)
20. CI3a31-2
21. CI3a22-3
22. PTIa31-2
23. PTIa42
24. CI3a21-3
25. CI3a11-1
26. PTIa1
27. PAIa11-1 (current feature)
28. PAIa11-2 (current feature)
29. PAIa16-1
30. PAIa16-R1

### 4. Performance Comparison

| Feature Count | Train Accuracy | Test Accuracy | Improvement |
|---------------|----------------|---------------|-------------|
| 5 features    | 0.9951         | 0.8818        | Baseline    |
| 8 features    | 0.9971         | 0.8934        | +1.16%      |
| 10 features   | 0.9971         | 0.9090        | +2.72%      |
| 15 features   | 0.9971         | 0.9069        | +2.51%      |
| 20 features   | 0.9971         | 0.9114        | +2.96%      |
| 25 features   | 0.9971         | 0.9104        | +2.86%      |
| **30 features** | **0.9969**     | **0.9194**    | **+3.76%**  |

### 5. Top Performing Features by Method

**Chi-square Test (Statistical):**
- CI2a32-2, PAIa13, CI2a32-4, PAIa11-1, PAIa11-2

**F-test (ANOVA):**
- S2-1, PTIa41-2, CI3a12-3, PTIa41-3, CI3a22-2

**Random Forest Importance:**
- S2-1, S4, S9, PTIa41-2, S8

**Correlation with Target:**
- PTIa41-2, S2-1, PTIa41-3, PTIa21, CI3a22-2

## Recommendations

### Immediate Actions
1. **Remove S2-2 and S2-3** from current model (confirmed as low-variance)
2. **Keep the 6 overlapping features** that are in the optimal set
3. **Consider adding 4 high-performing features** for immediate improvement:
   - PTIa41-2 (highest correlation: 0.187)
   - PTIa41-3 (correlation: 0.171)
   - PTIa21 (correlation: 0.117)
   - S4 (high RF importance: 0.091)

### Long-term Strategy
1. **Implement the 30-feature optimal set** for maximum performance (3.76% improvement)
2. **Focus on PTIa features** - they show strong predictive power
3. **Monitor S-features carefully** - only S2-1 and S4 appear useful
4. **Consider feature engineering** for CI3 features which show good performance

### Model Performance
- **Current model**: 89.34% test accuracy
- **Optimal model**: 91.94% test accuracy
- **Improvement potential**: +2.6 percentage points

## Technical Notes

- **Dataset size**: 544,462 samples, 13 classes
- **Class imbalance**: Present (class 3: 300,000 samples, class 7: 27 samples)
- **Feature types**: All numeric, no missing values
- **Variance threshold**: 0.99 (removes features with >99% constant values)

## Files Generated
- `feature_selection_results_[timestamp].csv` - Comprehensive analysis
- `final_recommendation_[timestamp].json` - Final recommendations
- `cv_analysis_[timestamp].csv` - Coefficient of variation analysis

---

*Analysis completed on: 2025-01-28*
*Script version: 1.0* 