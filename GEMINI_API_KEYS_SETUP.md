# Gemini API Keys Setup Guide

## Overview
This project now supports multiple Gemini API keys to handle rate limits and improve reliability. You can configure up to 5 different API keys that will be used automatically with failover.

## Environment Variables Setup

### For Vercel Deployment:
1. Go to your Vercel project dashboard
2. Navigate to Settings > Environment Variables
3. Add the following environment variables:

```
GEMINI_API_KEY=your_first_api_key_here
GEMINI_API_KEY_2=your_second_api_key_here
GEMINI_API_KEY_3=your_third_api_key_here
GEMINI_API_KEY_4=your_fourth_api_key_here
GEMINI_API_KEY_5=your_fifth_api_key_here
```

### For Local Development:
Create a `.env.local` file in your project root:

```
GEMINI_API_KEY=your_first_api_key_here
GEMINI_API_KEY_2=your_second_api_key_here
GEMINI_API_KEY_3=your_third_api_key_here
GEMINI_API_KEY_4=your_fourth_api_key_here
GEMINI_API_KEY_5=your_fifth_api_key_here
```

## How It Works

### Automatic Failover:
1. **Primary Key**: Uses `GEMINI_API_KEY` first
2. **Fallback Keys**: If primary fails, tries `GEMINI_API_KEY_2`, then `GEMINI_API_KEY_3`, etc.
3. **Smart Retry**: Each key is tried with full retry logic
4. **Final Fallback**: If all keys fail, uses enhanced fallback analysis

### Rate Limit Handling:
- **Multiple Keys**: Distributes requests across different API keys
- **Automatic Switching**: Switches to next key if current one hits rate limit
- **Load Balancing**: Reduces load on individual keys

## Getting Gemini API Keys

1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Sign in with your Google account
3. Click "Get API Key" 
4. Create a new API key
5. Copy the key and add it to your environment variables

## Benefits

### ✅ Rate Limit Resilience:
- **5x Capacity**: 5 API keys = 5x the rate limit capacity
- **Automatic Failover**: No manual intervention needed
- **Seamless Experience**: Users don't notice rate limit issues

### ✅ Improved Reliability:
- **Redundancy**: If one key fails, others continue working
- **Better Performance**: Faster response times with load distribution
- **Higher Success Rate**: More likely to get AI analysis instead of fallback

### ✅ Cost Optimization:
- **Load Distribution**: Spreads usage across multiple keys
- **Efficient Usage**: Each key used optimally
- **Reduced Failures**: Less fallback usage = better user experience

## Monitoring

The system logs which API key is being used:
- `Using Gemini API key 1` - Primary key
- `Using Gemini API key 2` - First fallback
- `Trying alternative Gemini API key 3` - Second fallback
- etc.

## Troubleshooting

### If All Keys Fail:
- Check that all API keys are valid
- Verify environment variables are set correctly
- Check Vercel deployment logs for specific errors
- Ensure API keys have sufficient quota

### Rate Limit Issues:
- Add more API keys to increase capacity
- Monitor usage across keys
- Consider upgrading to paid plans for higher limits

## Example Configuration

```bash
# Primary key (most reliable)
GEMINI_API_KEY=AIzaSyA1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6Q

# Backup keys (for failover)
GEMINI_API_KEY_2=AIzaSyB2C3D4E5F6G7H8I9J0K1L2M3N4O5P6Q7R
GEMINI_API_KEY_3=AIzaSyC3D4E5F6G7H8I9J0K1L2M3N4O5P6Q7R8S
GEMINI_API_KEY_4=AIzaSyD4E5F6G7H8I9J0K1L2M3N4O5P6Q7R8S9T
GEMINI_API_KEY_5=AIzaSyE5F6G7H8I9J0K1L2M3N4O5P6Q7R8S9T0U
```

## Support

If you need help setting up multiple API keys:
1. Check the Vercel logs for specific error messages
2. Verify all environment variables are set
3. Test each API key individually
4. Contact support if issues persist
