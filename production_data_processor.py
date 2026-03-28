"""
UIDAI Data Hackathon 2026 - Production Data Processor
=====================================================
Processes ALL CSV files from the three datasets and creates clean, aggregated files.

Team: Data Cleaning - Niranjana Vinod | ML - Ashin
"""

import pandas as pd
import os
import glob
from datetime import datetime

# Configuration
DATASET_FOLDERS = {
    'enrolment': 'api_data_aadhar_enrolment',
    'demographic': 'api_data_aadhar_demographic',
    'biometric': 'api_data_aadhar_biometric'
}

print("="*80)
print("🚀 UIDAI PRODUCTION DATA PROCESSOR")
print("="*80)
print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

def process_enrolment_data():
    """Process all enrolment CSV files - detects Ghost Villages"""
    print("\n📊 PROCESSING ENROLMENT DATA...")
    folder_path = DATASET_FOLDERS['enrolment']
    
    if not os.path.exists(folder_path):
        print(f"❌ Folder not found: {folder_path}")
        return None
    
    all_csv_files = glob.glob(os.path.join(folder_path, "*.csv"))
    print(f"   Found {len(all_csv_files)} CSV files to process")
    
    all_data = []
    total_rows = 0
    
    for idx, filename in enumerate(all_csv_files, 1):
        try:
            print(f"   Processing file {idx}/{len(all_csv_files)}: {os.path.basename(filename)}...", end=" ")
            
            # Read the full file
            df = pd.read_csv(filename, low_memory=False)
            all_data.append(df)
            total_rows += len(df)
            print(f"✅ ({len(df):,} rows)")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    if not all_data:
        return None
    
    # Combine all files
    print(f"\n   🔄 Combining {len(all_data)} files...")
    combined_df = pd.concat(all_data, ignore_index=True)
    
    # Clean data
    print("   🧹 Cleaning data...")
    combined_df.columns = combined_df.columns.str.strip().str.lower()
    
    # Fix date format (DD-MM-YYYY)
    combined_df['date'] = pd.to_datetime(combined_df['date'], format='%d-%m-%Y', errors='coerce')
    combined_df = combined_df.dropna(subset=['date'])
    
    # Fill NaN values
    age_cols = ['age_0_5', 'age_5_17', 'age_18_greater']
    for col in age_cols:
        if col in combined_df.columns:
            combined_df[col] = combined_df[col].fillna(0)
    
    # Calculate total enrolment
    combined_df['total_enrolment'] = combined_df[age_cols].sum(axis=1)
    
    # Aggregate by date and pincode
    print("   📈 Aggregating by date and PIN code...")
    daily_data = combined_df.groupby(['date', 'pincode', 'state', 'district']).agg({
        'total_enrolment': 'sum',
        'age_0_5': 'sum',
        'age_5_17': 'sum',
        'age_18_greater': 'sum'
    }).reset_index()
    
    daily_data = daily_data.sort_values(by=['pincode', 'date'])
    
    # Save
    output_file = 'cleaned_enrolment_data.csv'
    daily_data.to_csv(output_file, index=False)
    
    print(f"\n   ✅ SUCCESS!")
    print(f"      Total rows processed: {total_rows:,}")
    print(f"      Cleaned output: {len(daily_data):,} unique date-pincode combinations")
    print(f"      Saved to: {output_file}")
    
    return daily_data


def process_demographic_data():
    """Process all demographic update CSV files - detects Correction Syndicates"""
    print("\n📊 PROCESSING DEMOGRAPHIC UPDATE DATA...")
    folder_path = DATASET_FOLDERS['demographic']
    
    if not os.path.exists(folder_path):
        print(f"❌ Folder not found: {folder_path}")
        return None
    
    all_csv_files = glob.glob(os.path.join(folder_path, "*.csv"))
    print(f"   Found {len(all_csv_files)} CSV files to process")
    
    all_data = []
    total_rows = 0
    
    for idx, filename in enumerate(all_csv_files, 1):
        try:
            print(f"   Processing file {idx}/{len(all_csv_files)}: {os.path.basename(filename)}...", end=" ")
            df = pd.read_csv(filename, low_memory=False)
            all_data.append(df)
            total_rows += len(df)
            print(f"✅ ({len(df):,} rows)")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    if not all_data:
        return None
    
    print(f"\n   🔄 Combining {len(all_data)} files...")
    combined_df = pd.concat(all_data, ignore_index=True)
    
    print("   🧹 Cleaning data...")
    combined_df.columns = combined_df.columns.str.strip().str.lower()
    combined_df['date'] = pd.to_datetime(combined_df['date'], format='%d-%m-%Y', errors='coerce')
    combined_df = combined_df.dropna(subset=['date'])
    
    # Aggregate
    print("   📈 Aggregating updates by type...")
    
    # This will vary based on actual column names - adjust after seeing data
    # Assuming columns: mobile, email, address, name, dob, gender
    agg_dict = {}
    for col in combined_df.columns:
        if col not in ['date', 'pincode', 'state', 'district']:
            if combined_df[col].dtype in ['int64', 'float64']:
                agg_dict[col] = 'sum'
    
    if 'pincode' in combined_df.columns and 'district' in combined_df.columns:
        daily_data = combined_df.groupby(['date', 'pincode', 'state', 'district']).agg(agg_dict).reset_index()
    else:
        daily_data = combined_df  # Return as-is if structure is different
    
    daily_data = daily_data.sort_values(by=['date'])
    
    output_file = 'cleaned_demographic_data.csv'
    daily_data.to_csv(output_file, index=False)
    
    print(f"\n   ✅ SUCCESS!")
    print(f"      Total rows processed: {total_rows:,}")
    print(f"      Saved to: {output_file}")
    
    return daily_data


def process_biometric_data():
    """Process all biometric update CSV files - detects Compliance Gaps"""
    print("\n📊 PROCESSING BIOMETRIC UPDATE DATA...")
    folder_path = DATASET_FOLDERS['biometric']
    
    if not os.path.exists(folder_path):
        print(f"❌ Folder not found: {folder_path}")
        return None
    
    all_csv_files = glob.glob(os.path.join(folder_path, "*.csv"))
    print(f"   Found {len(all_csv_files)} CSV files to process")
    
    all_data = []
    total_rows = 0
    
    for idx, filename in enumerate(all_csv_files, 1):
        try:
            print(f"   Processing file {idx}/{len(all_csv_files)}: {os.path.basename(filename)}...", end=" ")
            df = pd.read_csv(filename, low_memory=False)
            all_data.append(df)
            total_rows += len(df)
            print(f"✅ ({len(df):,} rows)")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    if not all_data:
        return None
    
    print(f"\n   🔄 Combining {len(all_data)} files...")
    combined_df = pd.concat(all_data, ignore_index=True)
    
    print("   🧹 Cleaning data...")
    combined_df.columns = combined_df.columns.str.strip().str.lower()
    combined_df['date'] = pd.to_datetime(combined_df['date'], format='%d-%m-%Y', errors='coerce')
    combined_df = combined_df.dropna(subset=['date'])
    
    output_file = 'cleaned_biometric_data.csv'
    combined_df.to_csv(output_file, index=False)
    
    print(f"\n   ✅ SUCCESS!")
    print(f"      Total rows processed: {total_rows:,}")
    print(f"      Saved to: {output_file}")
    
    return combined_df


# ============= MAIN EXECUTION =============
if __name__ == "__main__":
    print("\n" + "="*80)
    print("STARTING FULL DATA PROCESSING")
    print("="*80)
    print("⚠️  This may take 10-20 minutes for the full dataset.")
    print("⚠️  Do NOT close this window!\n")
    
    start_time = datetime.now()
    
    # Process all three datasets
    enrolment_df = process_enrolment_data()
    demographic_df = process_demographic_data()
    biometric_df = process_biometric_data()
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print("\n" + "="*80)
    print("🎉 ALL PROCESSING COMPLETE!")
    print("="*80)
    print(f"Total time: {duration/60:.1f} minutes")
    print(f"Completed at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n📁 Output files created:")
    print("   • cleaned_enrolment_data.csv")
    print("   • cleaned_demographic_data.csv")
    print("   • cleaned_biometric_data.csv")
    print("\n✅ Ready for ML model processing!")
    print("="*80)
