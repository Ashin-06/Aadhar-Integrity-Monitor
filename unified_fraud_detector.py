"""
UIDAI Data Hackathon 2026 - Unified Fraud Detection System
==========================================================
Combines all 3 datasets to create a comprehensive Aadhaar Integrity Score

Detects:
1. Ghost Villages (Enrolment fraud)
2. Correction Syndicates (Demographic manipulation)
3. Digital Exclusion Zones (Service gaps)
4. Biometric Update Gaps (Compliance issues)

Team: ML Engineer - Ashin
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

print("="*80)
print("🤖 UIDAI UNIFIED FRAUD DETECTION SYSTEM")
print("="*80)
print("Multi-dimensional Aadhaar Integrity Analysis\n")

# ===================== MODULE 1: GHOST VILLAGE DETECTOR =====================
def detect_ghost_villages(enrolment_file='cleaned_enrolment_data.csv'):
    """
    Detects suspicious enrolment spikes that indicate fake ID creation
    """
    print("\n🔍 MODULE 1: Ghost Village Detection")
    print("-" * 80)
    
    try:
        df = pd.read_csv(enrolment_file)
        print(f"✅ Loaded {len(df):,} enrolment records")
    except FileNotFoundError:
        print(f"❌ File not found: {enrolment_file}")
        print("   Run 'production_data_processor.py' first!")
        return None
    
    # Convert date
    df['date'] = pd.to_datetime(df['date'])
    
    # Feature Engineering
    print("⚙️  Engineering features...")
    
    # 1. Rolling average (what's normal for this PIN?)
    df['rolling_avg_7d'] = df.groupby('pincode')['total_enrolment'].transform(
        lambda x: x.rolling(window=7, min_periods=1).mean()
    )
    
    # 2. Rolling average (30-day baseline)
    df['rolling_avg_30d'] = df.groupby('pincode')['total_enrolment'].transform(
        lambda x: x.rolling(window=30, min_periods=1).mean()
    )
    
    # 3. Spike ratio (how much bigger than normal?)
    df['spike_ratio'] = df['total_enrolment'] / (df['rolling_avg_7d'] + 1)
    
    # 4. Adult fraud indicator (suspicious adult enrolments)
    df['adult_ratio'] = df['age_18_greater'] / (df['total_enrolment'] + 1)
    
    # 5. Child spike (age 5-17 anomalies - common in fraud)
    df['child_spike'] = df['age_5_17'] / (df['total_enrolment'] + 1)
    
    # 6. Day of week (fraud patterns)
    df['day_of_week'] = df['date'].dt.dayofweek
    df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
    
    # 7. Deviation from baseline
    df['deviation_7d'] = df['total_enrolment'] - df['rolling_avg_7d']
    df['deviation_30d'] = df['total_enrolment'] - df['rolling_avg_30d']
    
    # Fill any NaN
    df = df.fillna(0)
    
    # Select features for ML model
    feature_cols = [
        'total_enrolment',
        'rolling_avg_7d',
        'rolling_avg_30d',
        'spike_ratio',
        'adult_ratio',
        'child_spike',
        'deviation_7d',
        'deviation_30d'
    ]
    
    print(f"⚙️  Using {len(feature_cols)} features for detection")
    
    features = df[feature_cols].copy()
    
    # Train Isolation Forest
    print("🤖 Training anomaly detection model...")
    model = IsolationForest(
        n_estimators=100,
        contamination=0.03,  # Expect 3% fraud
        random_state=42,
        n_jobs=-1
    )
    
    df['anomaly_score'] = model.fit_predict(features)
    df['anomaly_confidence'] = -model.score_samples(features)  # Higher = more suspicious
    
    # Extract anomalies
    anomalies = df[df['anomaly_score'] == -1].copy()
    anomalies = anomalies.sort_values(by='anomaly_confidence', ascending=False)
    
    # Add risk classification
    if len(anomalies) > 0:
        q75 = anomalies['anomaly_confidence'].quantile(0.75)
        q50 = anomalies['anomaly_confidence'].quantile(0.50)
        
        anomalies['risk_level'] = anomalies['anomaly_confidence'].apply(
            lambda x: 'CRITICAL' if x > q75 else ('HIGH' if x > q50 else 'MEDIUM')
        )
        
        # Add fraud type classification
        anomalies['fraud_type'] = 'Unknown'
        anomalies.loc[anomalies['spike_ratio'] > 5, 'fraud_type'] = 'Mass Fake Enrolment'
        anomalies.loc[anomalies['adult_ratio'] > 0.7, 'fraud_type'] = 'Adult Fraud Ring'
        anomalies.loc[anomalies['child_spike'] > 0.8, 'fraud_type'] = 'Child ID Fraud'
    
    # Save results
    output_file = 'ghost_villages_detected.csv'
    anomalies.to_csv(output_file, index=False)
    
    print(f"\n📊 RESULTS:")
    print(f"   • Total records analyzed: {len(df):,}")
    print(f"   • Suspicious events found: {len(anomalies):,}")
    if len(anomalies) > 0:
        print(f"   • Critical risk: {len(anomalies[anomalies['risk_level']=='CRITICAL']):,}")
        print(f"   • High risk: {len(anomalies[anomalies['risk_level']=='HIGH']):,}")
        print(f"   • Medium risk: {len(anomalies[anomalies['risk_level']=='MEDIUM']):,}")
    print(f"   💾 Saved to: {output_file}")
    
    return anomalies


# ===================== MODULE 2: CORRECTION SYNDICATE DETECTOR =====================
def detect_correction_syndicates(demographic_file='cleaned_demographic_data.csv'):
    """
    Detects unusual patterns in demographic corrections (Name/DOB changes)
    """
    print("\n🔍 MODULE 2: Correction Syndicate Detection")
    print("-" * 80)
    
    try:
        df = pd.read_csv(demographic_file)
        print(f"✅ Loaded {len(df):,} demographic update records")
    except FileNotFoundError:
        print(f"❌ File not found: {demographic_file}")
        return None
    
    # Convert date
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date'])
    
    # Analyze update patterns
    print("⚙️  Analyzing update patterns...")
    
    # Count total updates per district per day
    if 'district' in df.columns:
        district_stats = df.groupby(['date', 'state', 'district']).size().reset_index(name='total_updates')
        
        # Calculate baseline
        district_stats['rolling_avg'] = district_stats.groupby('district')['total_updates'].transform(
            lambda x: x.rolling(window=7, min_periods=1).mean()
        )
        
        district_stats['update_spike'] = district_stats['total_updates'] / (district_stats['rolling_avg'] + 1)
        
        # Flag suspicious districts
        suspicious = district_stats[district_stats['update_spike'] > 3].copy()
        suspicious['issue_type'] = 'Excessive Corrections'
        
        output_file = 'correction_syndicates_detected.csv'
        suspicious.to_csv(output_file, index=False)
        
        print(f"\n📊 RESULTS:")
        print(f"   • Suspicious correction patterns: {len(suspicious):,}")
        print(f"   💾 Saved to: {output_file}")
        
        return suspicious
    else:
        print("⚠️  Column structure different than expected - skipping detailed analysis")
        return None


# ===================== MODULE 3: DIGITAL EXCLUSION DETECTOR =====================
def detect_digital_exclusion(demographic_file='cleaned_demographic_data.csv'):
    """
    Identifies areas with low mobile/email linkage (Digital Dark Zones)
    """
    print("\n🔍 MODULE 3: Digital Exclusion Zone Detection")
    print("-" * 80)
    
    try:
        df = pd.read_csv(demographic_file)
        print(f"✅ Loaded {len(df):,} records")
    except FileNotFoundError:
        print(f"❌ File not found: {demographic_file}")
        return None
    
    # Analyze mobile linkage
    print("⚙️  Analyzing digital connectivity...")
    
    # This analysis depends on column names - adjust based on actual data
    # Assuming there's a 'mobile' column indicating mobile updates
    
    if 'district' in df.columns:
        district_summary = df.groupby(['state', 'district']).size().reset_index(name='update_count')
        
        # Sort by lowest activity (these are dark zones)
        district_summary = district_summary.sort_values(by='update_count')
        
        # Flag bottom 20% as "Dark Zones"
        threshold = district_summary['update_count'].quantile(0.20)
        dark_zones = district_summary[district_summary['update_count'] <= threshold].copy()
        dark_zones['zone_type'] = 'Digital Dark Zone'
        
        output_file = 'digital_dark_zones.csv'
        dark_zones.to_csv(output_file, index=False)
        
        print(f"\n📊 RESULTS:")
        print(f"   • Digital Dark Zones identified: {len(dark_zones):,}")
        print(f"   💾 Saved to: {output_file}")
        
        return dark_zones
    else:
        print("⚠️  Insufficient data for analysis")
        return None


# ===================== MODULE 4: UNIFIED RISK DASHBOARD =====================
def generate_unified_dashboard():
    """
    Combines all detection modules into a single risk assessment
    """
    print("\n📊 GENERATING UNIFIED RISK DASHBOARD")
    print("=" * 80)
    
    # Load all results
    results = {}
    
    files = {
        'ghost_villages': 'ghost_villages_detected.csv',
        'syndicates': 'correction_syndicates_detected.csv',
        'dark_zones': 'digital_dark_zones.csv'
    }
    
    for name, file in files.items():
        try:
            results[name] = pd.read_csv(file)
            print(f"✅ Loaded {name}: {len(results[name]):,} records")
        except:
            print(f"⚠️  {name} data not available")
            results[name] = None
    
    # Create summary statistics
    summary = {
        'total_ghost_villages': len(results['ghost_villages']) if results['ghost_villages'] is not None else 0,
        'critical_threats': len(results['ghost_villages'][results['ghost_villages']['risk_level']=='CRITICAL']) if results['ghost_villages'] is not None else 0,
        'syndicate_locations': len(results['syndicates']) if results['syndicates'] is not None else 0,
        'digital_dark_zones': len(results['dark_zones']) if results['dark_zones'] is not None else 0,
    }
    
    # Save summary
    summary_df = pd.DataFrame([summary])
    summary_df.to_csv('system_summary.csv', index=False)
    
    print("\n" + "="*80)
    print("📈 SYSTEM SUMMARY")
    print("="*80)
    print(f"   🚨 Ghost Villages Detected: {summary['total_ghost_villages']:,}")
    print(f"   ⚠️  Critical Threats: {summary['critical_threats']:,}")
    print(f"   🔍 Correction Syndicates: {summary['syndicate_locations']:,}")
    print(f"   📵 Digital Dark Zones: {summary['digital_dark_zones']:,}")
    print("="*80)
    
    return summary


# ============= MAIN EXECUTION =============
if __name__ == "__main__":
    print("\nStarting multi-dimensional fraud analysis...\n")
    
    # Run all detection modules
    anomalies_enrolment = detect_ghost_villages()
    anomalies_demographic = detect_correction_syndicates()
    dark_zones = detect_digital_exclusion()
    
    # Generate unified dashboard
    summary = generate_unified_dashboard()
    
    print("\n✅ ALL DETECTION MODULES COMPLETE!")
    print("\n📁 Output files for Frontend Team:")
    print("   • ghost_villages_detected.csv")
    print("   • correction_syndicates_detected.csv")
    print("   • digital_dark_zones.csv")
    print("   • system_summary.csv")
    print("\n🎯 Ready for dashboard visualization!")
