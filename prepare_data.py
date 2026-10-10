import pandas as pd
import glob
import os

print("Loading all 546 station files...")
use_cols = ['pm2.5','pm10','no2','so2','co','ozone','nh3','timestamp']
all_files = glob.glob("**/*.csv", recursive=True)
all_files = [f for f in all_files if "stations.csv" not in f]
stations = pd.read_csv("stations.csv")
print(f"Found {len(all_files)} station files")

dfs = []; skipped = 0
for i, filepath in enumerate(all_files):
    try:
        available = pd.read_csv(filepath, nrows=0).columns.tolist()
        cols = [c for c in use_cols if c in available]
        temp = pd.read_csv(filepath, usecols=cols,
                           dtype={c:'float32' for c in cols if c!='timestamp'})
        temp['timestamp'] = pd.to_datetime(temp['timestamp'], errors='coerce')
        temp = temp.dropna(subset=['timestamp'])
        temp = temp.set_index('timestamp').resample('D').mean().reset_index()
        temp['station_code'] = os.path.splitext(os.path.basename(filepath))[0]
        temp['state'] = os.path.basename(os.path.dirname(filepath)).replace("_"," ")
        dfs.append(temp)
        if (i+1) % 50 == 0:
            print(f"  Processed {i+1}/{len(all_files)} files...")
    except Exception as e:
        skipped += 1

print("Combining all files...")
df_raw = pd.concat(dfs, ignore_index=True)
df = df_raw.merge(stations, on='station_code', how='left')

# Clean invalid / unknown station metadata before creating charts
# This removes the "Unknown Unassigned" category appearing in the dashboard.
df['state'] = df['state'].astype(str).str.strip()
df['city'] = df['city'].astype(str).str.strip()
unknown_mask = df['state'].str.lower().str.contains('unknown|unassigned', na=False) | \
               df['city'].str.lower().str.contains('unknown|unassigned', na=False)
if unknown_mask.any():
    print(f"Removing {unknown_mask.sum():,} rows with unknown/unassigned state/city labels")
    df = df[~unknown_mask].copy()

df = df[df['state'].ne('nan') & df['state'].ne('')].copy()

df.rename(columns={'timestamp':'date'}, inplace=True)
df['date'] = pd.to_datetime(df['date'])
df['year'] = df['date'].dt.year
df['month'] = df['date'].dt.month
df['season'] = df['month'].map({12:'Winter',1:'Winter',2:'Winter',3:'Spring',4:'Spring',5:'Spring',6:'Summer',7:'Summer',8:'Summer',9:'Autumn',10:'Autumn',11:'Autumn'})

pollutants = [p for p in ['pm2.5','pm10','no2','so2','co','ozone','nh3'] if p in df.columns]
for col in pollutants:
    df[col] = df[col].fillna(df[col].median())

def calc_aqi(pm25):
    if pd.isna(pm25): return None
    if pm25<=12: return round((50/12)*pm25)
    elif pm25<=35.4: return round(((100-51)/(35.4-12.1))*(pm25-12.1)+51)
    elif pm25<=55.4: return round(((150-101)/(55.4-35.5))*(pm25-35.5)+101)
    elif pm25<=150.4: return round(((200-151)/(150.4-55.5))*(pm25-55.5)+151)
    elif pm25<=250.4: return round(((300-201)/(250.4-150.5))*(pm25-150.5)+201)
    else: return round(((500-301)/(500.4-250.5))*(pm25-250.5)+301)

def aqi_bucket(val):
    if pd.isna(val): return None
    if val<=50: return 'Good'
    elif val<=100: return 'Satisfactory'
    elif val<=200: return 'Moderate'
    elif val<=300: return 'Poor'
    elif val<=400: return 'Very Poor'
    else: return 'Severe'

print("Calculating AQI...")
df['AQI'] = df['pm2.5'].apply(calc_aqi)
df['AQI_Bucket'] = df['AQI'].apply(aqi_bucket)
df = df.dropna(subset=['AQI'])

print("Saving processed data...")
df.to_parquet("processed_aqi.parquet", index=False)
print(f"\n✅ Done! saved processed_aqi.parquet")
print(f"   Rows: {len(df):,} | Skipped files: {skipped}")
print(f"\n🚀 Now run: python -m streamlit run Home.py")
