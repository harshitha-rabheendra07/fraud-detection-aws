import pandas as pd
import numpy as np
import os
import json
from datetime import date

def generate_reference_data():
    """Create reference data matching training distribution"""
    np.random.seed(42)
    n = 1000
    data = {
        'amount':         np.random.lognormal(6.5, 0.8, n).round(2),
        'hour':           np.random.choice(range(8, 22), n),
        'day_of_week':    np.random.randint(0, 7, n),
        'customer_age':   np.random.randint(25, 60, n),
        'num_prev_txns':  np.random.randint(20, 200, n),
        'avg_txn_amount': np.random.lognormal(6.2, 0.6, n).round(2),
    }
    return pd.DataFrame(data)

def generate_normal_data():
    """Current data similar to training — no drift expected"""
    np.random.seed(10)
    n = 500
    data = {
        'amount':         np.random.lognormal(6.6, 0.9, n).round(2),
        'hour':           np.random.choice(range(8, 22), n),
        'day_of_week':    np.random.randint(0, 7, n),
        'customer_age':   np.random.randint(24, 62, n),
        'num_prev_txns':  np.random.randint(18, 210, n),
        'avg_txn_amount': np.random.lognormal(6.3, 0.6, n).round(2),
    }
    return pd.DataFrame(data)

def generate_drifted_data():
    """Current data very different from training — drift expected"""
    np.random.seed(99)
    n = 500
    data = {
        'amount':         np.random.lognormal(10.5, 1.2, n).round(2),
        'hour':           np.random.choice([0,1,2,3,22,23], n),
        'day_of_week':    np.random.randint(0, 7, n),
        'customer_age':   np.random.randint(18, 30, n),
        'num_prev_txns':  np.random.randint(0, 5, n),
        'avg_txn_amount': np.random.lognormal(9.0, 1.0, n).round(2),
    }
    return pd.DataFrame(data)

def run_drift_check(reference_data, current_data, report_name='drift_report'):
    """
    Run drift detection using scipy KS Test and PSI.
    Returns dict with results for each feature.
    """
    from scipy import stats

    features = ['amount', 'hour', 'customer_age',
                'num_prev_txns', 'avg_txn_amount']

    results = {}
    drifted_features = []

    print("\n" + "="*55)
    print("  DRIFT DETECTION REPORT")
    print("="*55)
    print(f"  Reference data: {len(reference_data)} rows")
    print(f"  Current data  : {len(current_data)} rows")
    print("="*55)

    for feature in features:
        ref_vals  = reference_data[feature].dropna().values
        curr_vals = current_data[feature].dropna().values

        # KS Test
        ks_stat, p_value = stats.ks_2samp(ref_vals, curr_vals)

        # Mean comparison
        ref_mean  = round(float(np.mean(ref_vals)), 2)
        curr_mean = round(float(np.mean(curr_vals)), 2)
        mean_diff = round(abs(curr_mean - ref_mean) / (ref_mean + 1e-9) * 100, 1)

        drift_detected = p_value < 0.05

        results[feature] = {
            'ks_statistic' : round(ks_stat, 4),
            'p_value'      : round(p_value, 6),
            'drift'        : drift_detected,
            'ref_mean'     : ref_mean,
            'curr_mean'    : curr_mean,
            'mean_change_pct': mean_diff
        }

        status = "DRIFT DETECTED" if drift_detected else "OK"
        icon   = "X" if drift_detected else "+"
        print(f"\n  [{icon}] {feature}")
        print(f"      Training mean : {ref_mean}")
        print(f"      Current mean  : {curr_mean}  ({mean_diff}% change)")
        print(f"      KS Statistic  : {ks_stat:.4f}")
        print(f"      P-value       : {p_value:.6f}")
        print(f"      Status        : {status}")

        if drift_detected:
            drifted_features.append(feature)

    dataset_drift = len(drifted_features) / len(features) > 0.2

    print("\n" + "="*55)
    print(f"  Drifted features : {len(drifted_features)}/{len(features)}")
    print(f"  Drifted list     : {drifted_features}")
    print(f"  Dataset drift    : {'YES - RETRAIN NEEDED' if dataset_drift else 'NO - Model still good'}")
    print("="*55)

    return {
        'dataset_drift'    : dataset_drift,
        'drifted_features' : drifted_features,
        'feature_results'  : results
    }

def save_report(results, report_path='reports'):
    """Save drift results as JSON"""
    os.makedirs(report_path, exist_ok=True)
    report_file = os.path.join(report_path, f'{date.today()}_drift_report.json')
    with open(report_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nReport saved: {report_file}")

if __name__ == "__main__":
    print("Generating datasets...")
    reference = generate_reference_data()
    normal    = generate_normal_data()
    drifted   = generate_drifted_data()

    # Save datasets
    os.makedirs('../data/reference',  exist_ok=True)
    os.makedirs('../data/demo_drift', exist_ok=True)
    reference.to_csv('../data/reference/training_reference.csv',  index=False)
    normal.to_csv('../data/demo_drift/normal_current.csv',         index=False)
    drifted.to_csv('../data/demo_drift/drifted_current.csv',       index=False)

    print("\n\n======== SCENARIO 1: Normal Data (No Drift Expected) ========")
    result1 = run_drift_check(reference, normal, 'normal_report')

    print("\n\n======== SCENARIO 2: Drifted Data (Drift Expected) ========")
    result2 = run_drift_check(reference, drifted, 'drift_report')

    print("\n\n======== SUMMARY ========")
    print(f"Scenario 1 (Normal)  → Dataset Drift: {result1['dataset_drift']}")
    print(f"Scenario 2 (Drifted) → Dataset Drift: {result2['dataset_drift']}")
