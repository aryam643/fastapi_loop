# Data Directory

Place your CSV files in this directory:

1. `store_status.csv` - Store polling data with columns: store_id, timestamp_utc, status
2. `business_hours.csv` - Business hours data with columns: store_id, dayOfWeek, start_time_local, end_time_local  
3. `store_timezones.csv` - Timezone data with columns: store_id, timezone_str

## Running Data Import

After placing the CSV files in this directory, run:

\`\`\`bash
python data_import_script.py
\`\`\`

This will populate the database with your CSV data.
