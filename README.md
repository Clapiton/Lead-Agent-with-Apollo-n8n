# Lead Agent - Complete Workflow JSON

This file contains the complete, corrected n8n workflow JSON. Import this into n8n to replace the existing workflow.

## Key Improvements

1. ✅ Fixed Map Sales Region with proper zip code routing
2. ✅ Fixed Apify API call structure  
3. ✅ Added HTML-to-text extraction node
4. ✅ Configured AI qualification with comprehensive system prompt
5. ✅ Configured Apollo API calls for contact enrichment
6. ✅ All nodes properly connected

## Import Instructions

1. Open n8n
2. Click **Workflows** → **Import from File**
3. Select: `Lead_Agent_Complete.json`
4. Follow the CONFIGURATION_GUIDE.md to add API credentials
5. Test with a single zip code first

## What Still Needs Manual Configuration

- Apify API token (Header Auth credential)
- Apollo.io API key (Header Auth credential)
- Google Sheets service account
- Google Sheet ID in the final node

See CONFIGURATION_GUIDE.md for detailed steps.
