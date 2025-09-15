# Google Earth Engine Setup Instructions

## Step 1: Download Service Account Key

1. Go to Google Cloud Console: https://console.cloud.google.com/
2. Select your project: `uber-462705`
3. Navigate to IAM & Admin > Service Accounts
4. Find your service account: `abhasbali@uber-462705.iam.gserviceaccount.com`
5. Click on the service account
6. Go to the "Keys" tab
7. Click "Add Key" > "Create new key"
8. Select "JSON" format
9. Download the JSON file
10. Save it as `gee-service-account-key.json` in this backend directory

## Step 2: Environment Variables

The `.env` file has been created with your project details:
- GOOGLE_EARTH_ENGINE_PROJECT=uber-462705
- GOOGLE_EARTH_ENGINE_SERVICE_ACCOUNT=abhasbali@uber-462705.iam.gserviceaccount.com
- GOOGLE_EARTH_ENGINE_PRIVATE_KEY_PATH=./gee-service-account-key.json

## Step 3: Verify Setup

Once you've downloaded the key file, restart the backend server:
```
python app.py
```

The system will then use real Google Earth Engine data instead of synthetic data!

## Note
Without the service account key file, the system will continue to work but use synthetic satellite data as a fallback.
