# TravelMaster AI - Amadeus API Setup Instructions

## Getting Your Amadeus API Keys

1. **Sign up for Amadeus Self-Service**:
   - Go to: https://developers.amadeus.com/register
   - Create a free developer account

2. **Create a new application**:
   - Log into: https://developers.amadeus.com/my-apps
   - Click "Create New App" 
   - Choose "Self-Service" plan (free tier includes 1000+ API calls/month)

3. **Get your API credentials**:
   - After creating the app, you'll see:
     - **API Key** (Client ID)
     - **API Secret** (Client Secret)

4. **Set up your environment**:
   - Copy `.env.example` to `.env`
   - Replace the placeholder values with your real credentials:

```bash
# Copy the example file
cp .env.example .env

# Edit the .env file with your credentials
AMADEUS_API_KEY=your_actual_api_key_here
AMADEUS_API_SECRET=your_actual_api_secret_here
```

## Amadeus API Endpoints Used

- **Hotel Search by City**: `reference-data/locations/hotels/by-city`
- **Hotel Offers Search**: `shopping/hotel-offers-search`  
- **Location Search**: `reference-data/locations`

## API Limits (Free Tier)

- **1000 API calls/month** (resets monthly)
- **10 calls/second** rate limit
- **Hotel Search**: ~2-3 calls per hotel search (city lookup + offers)

## Testing

Once configured, the TravelMaster AI will:
- ✅ Use real Amadeus hotel data when API keys are set
- 🔄 Fall back to mock data if API keys are missing or invalid
- 📊 Display search status in console logs

## Troubleshooting

If you see "Using mock hotel data":
1. Check that `.env` file exists in project root
2. Verify API key/secret are correctly set (no quotes needed)
3. Ensure your Amadeus app is active and has API quota remaining
4. Check console logs for specific error messages