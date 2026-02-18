"""
This example demonstrates how to export time-series stream data from given facility to a
CSV file using pandas. It queries sensor/parameter data over a date range and formats it
with human-readable timestamps.

Prerequisites:
- Your APS application must be added to the facility as a service
- The facility must have streams configured with the target parameter
- Install dependencies: pip install -r requirements.txt

Output:
- CSV file with timestamps and values for each stream's parameter
- Each column represents: "<Stream Name> - <Parameter Name>"

"""
from datetime import datetime, timezone
import pandas as pd

from common.auth import create_token
from common.constants import (
    QC_KEY,
    QC_NAME,
    QC_ONAME
)
from common.encoding import to_short_key
from common.tandemClient import TandemClient
from common.utils import get_default_model

# Configuration - Replace these placeholders with your actual values
APS_CLIENT_ID = 'YOUR_CLIENT_ID' # Your APS application client ID
APS_CLIENT_SECRET = 'YOUR_CLIENT_SECRET' # Your APS application client secret
FACILITY_URN = 'YOUR_FACILITY_URN' # Facility URN

# Query parameters
PARAMETER_NAME = 'Temperature' # Name of the parameter to export
START_DATE = '2026-01-01' # Start date (YYYY-MM-DD format)
END_DATE = '2026-01-31' # End date (YYYY-MM-DD format)

# Output configuration
OUTPUT_CSV = 'exported-stream-data.csv' # Output file name


def expand_values(values: list) -> list:
    """
    Utility function to expand values when they are stored as deltas.
    The first value is treated as absolute value, the rest of values are treated as deltas
    from the previous value.
    """

    if not values:
        return []
    result = [values[0]]
    for delta in values[1:]:
        result.append(result[-1] + delta)
    return result

def main():
    # Start
    # STEP 1 - obtain token. The sample uses 2-legged token but it would also work
    # with 3-legged token assuming that user has access to the facility
    token = create_token(APS_CLIENT_ID, APS_CLIENT_SECRET, ['data:read'])
    with TandemClient(lambda: token) as client:
        # STEP 2 - get facility and default model. The default model has same id as facility
        facility = client.get_facility(FACILITY_URN)
        default_model = get_default_model(FACILITY_URN, facility)
        if default_model is None:
            raise Exception('Default model not found')
        default_model_id = default_model.get('modelId')
        # STEP 3 - get model schema, streams, and stream configurations
        schema = client.get_model_schema(default_model_id)
        streams = client.get_streams(default_model_id)
        stream_configs = client.get_stream_configs(default_model_id)
        # STEP 4 -Find streams that have the target parameter configured
        # Iterate through stream configurations and collect:
        # - stream IDs (elements with sensors/data)
        # - property definitions for the parameter we want to export
        stream_ids: list[str] = []
        prop_defs: dict[str, dict] = {}

        for stream_config in stream_configs:
            settings = stream_config.get('streamSettings', None)
            if not settings:
                continue
            mapping = settings.get('sourceMapping', None)
            if not mapping:
                continue
            for prop_id in mapping:
                prop_def = next((a for a in schema.get('attributes', []) if a.get('id') == prop_id), None)
                if not prop_def:
                    continue
                if prop_def.get('name') == PARAMETER_NAME:
                    prop_defs[prop_id] = prop_def
                    stream_ids.append(stream_config.get('elementId'))
        if len(stream_ids) == 0:
            raise Exception(f'Warning: No streams found with parameter "{PARAMETER_NAME}"')
        # STEP 5 - calculate from and to dates in milliseconds.
        start_date = int(
            datetime.strptime(START_DATE, '%Y-%m-%d')
            .replace(tzinfo=timezone.utc)
            .timestamp() * 1000
        )
        end_date = int(
            datetime.strptime(END_DATE, '%Y-%m-%d')
            .replace(hour=23, minute=59, second=59, tzinfo=timezone.utc)
            .timestamp() * 1000
        )
        # STEP 6 - query stream data for selected stream IDs, collect values in a dictionary (key = timestamp, value = dict of column name to value)
        rows_by_timestamp: dict[int, dict[str, float]] = {}

        for stream_id in stream_ids:
            prop_ids = prop_defs.keys()
            stream_data = client.query_stream_data(default_model_id,
                                                   [stream_id],
                                                   attrs=list(prop_ids),
                                                   from_date=start_date,
                                                   to_date=end_date)
            if len(stream_data) == 0:
                continue
            # STEP 7 - find stream to get stream name for the current stream ID
            stream_key = to_short_key(stream_id)
            stream = next((s for s in streams if s.get(QC_KEY) == stream_key), None)
            if not stream:
                continue
            stream_name = stream.get(QC_ONAME) or stream.get(QC_NAME)
            print(f'Processing: {stream_name}')
            count = 0

            for item in stream_data:
                prop_id = item.get('s', None)
                if prop_id not in prop_defs:
                    continue
                param_name = prop_defs[prop_id].get('name') or prop_id
                column_name = f'{stream_name} - {param_name}'
                timestamps = expand_values(item.get('t', []))
                values = expand_values(item.get('v', []))
                count += len(values)
                for timestamp, value in zip(timestamps, values):
                    row = rows_by_timestamp.setdefault(timestamp, {})
                    row[column_name] = value
            print(f'  Total values: {count}')
        # STEP 8 - export to CSV file using pandas. Timestamps are converted to human-readable format in the 'timestamp' column.
        if rows_by_timestamp:
            df = pd.DataFrame.from_dict(rows_by_timestamp, orient='index')
            df.index.name = 'timestamp_s'
            df = df.sort_index()
            # Convert timestamps to human-readable format and insert as a new column
            df.insert(
                0,
                'timestamp',
                pd.to_datetime(df.index, unit='s', utc=True).strftime('%Y-%m-%d %H:%M:%S')
            )
            df = df.reset_index(drop=True)
            df.to_csv(OUTPUT_CSV, index=False)
            print(f'Exported stream data to {OUTPUT_CSV}')
        else:
            print('No stream data found for the selected date range.')

if __name__ == '__main__':
    main()