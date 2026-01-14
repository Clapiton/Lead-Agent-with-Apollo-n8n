# PH Lead Agent - Manual Configuration Guide

## Overview
This guide explains the manual configuration steps needed in n8n to complete the workflow. Some nodes cannot be fully configured via JSON and require UI interaction.

---

## 1. API Credentials Setup

### Apify API Token
1. In n8n, go to **Credentials** → **New Credential**
2. Select **Header Auth**
3. Configure:
   - **Name**: `Apify API Token`
   - **Header Name**: `Authorization`
   - **Header Value**: `Bearer YOUR_APIFY_API_TOKEN`
4. Save and assign to the "Apify - Google Maps Scraper" node

### Apollo.io API Key
1. In n8n, go to **Credentials** → **New Credential**
2. Select **Header Auth**
3. Configure:
   - **Name**: `Apollo API Key`
   - **Header Name**: `X-Api-Key`
   - **Header Value**: `YOUR_APOLLO_API_KEY`
4. Save

### Google Sheets Service Account
1. In n8n, go to **Credentials** → **New Credential**
2. Select **Google Service Account**
3. Upload your service account JSON file
4. Save

---

## 2. Node-by-Node Configuration

### Node: "Extract Text from HTML" (NEW - Must Add)

**Position**: Between "Merge" and "AI Qualification (OpenAI)"

**Configuration**:
1. Add a **Code** node after the Merge node
2. Name it: `Extract Text from HTML`
3. Paste this JavaScript code:

```javascript
// Extract plain text from HTML responses and combine all scraped pages
const items = $input.all();
const leadData = items[0].json;

// Function to strip HTML tags and extract text
function htmlToText(html) {
  if (!html || typeof html !== 'string') return '';
  
  // Remove script and style tags and their content
  let text = html.replace(/<script[^>]*>.*?<\/script>/gis, '');
  text = text.replace(/<style[^>]*>.*?<\/style>/gis, '');
  
  // Remove HTML tags
  text = text.replace(/<[^>]+>/g, ' ');
  
  // Decode HTML entities
  text = text.replace(/&nbsp;/g, ' ');
  text = text.replace(/&amp;/g, '&');
  text = text.replace(/&lt;/g, '<');
  text = text.replace(/&gt;/g, '>');
  text = text.replace(/&quot;/g, '"');
  
  // Remove extra whitespace
  text = text.replace(/\s+/g, ' ').trim();
  
  return text;
}

// Extract text from all three pages
let homepageText = '';
let aboutText = '';
let companyText = '';

for (const item of items) {
  const html = item.json.body || item.json.data || '';
  const text = htmlToText(html);
  
  // Determine which page this is based on URL or position
  if (item.json.url && item.json.url.includes('uber-uns')) {
    aboutText = text;
  } else if (item.json.url && item.json.url.includes('unternehmen')) {
    companyText = text;
  } else {
    homepageText = text;
  }
}

// Combine all text, limiting to ~3000 chars to save on AI costs
const combinedText = (homepageText + ' ' + aboutText + ' ' + companyText).substring(0, 3000);

return [{
  json: {
    ...leadData,
    website_text: combinedText,
    text_length: combinedText.length
  }
}];
```

4. Connect: `Merge` → `Extract Text from HTML` → `AI Qualification (OpenAI)`

---

### Node: "AI Qualification (OpenAI)" (MUST RECONFIGURE)

**Current Issue**: Using LangChain node without proper configuration

**Fix**:
1. Delete the existing "AI Qualification (OpenAI)" node
2. Add a new **OpenAI** node (NOT the LangChain version - use the standard HTTP Request node)
3. Configure as follows:

**Method**: POST  
**URL**: `https://api.openai.com/v1/chat/completions`  
**Authentication**: Use OpenAI API credential  
**Body** (JSON):

```json
{
  "model": "gpt-4o-mini",
  "messages": [
    {
      "role": "system",
      "content": "You are a B2B lead qualification analyst for PH Management, a German automotive service company. Analyze company website text and return ONLY valid JSON with these fields: workshop_type (Internal/External/None), segment (string), segment_sub (string), fleet_size_estimate (integer or null), vehicle_types (array), trigger_signals (array), company_size_indicator (Small/Large). No markdown, just JSON."
    },
    {
      "role": "user",
      "content": "Company: {{ $json.company_name }}\nWebsite: {{ $json.website }}\nCategory: {{ $json.category }}\n\nWebsite Text:\n{{ $json.website_text }}\n\nAnalyze this German Pflegedienst (nursing service) company. Look for:\n1. Workshop: mentions of 'eigene Werkstatt', 'KFZ-Werkstatt'\n2. Fleet size: mentions of vehicle count or employee count\n3. Vehicle types: typically PKW, Kleinwagen for nursing services\n4. Growth signals: 'Wir suchen', 'Expansion', 'Neuer Standort'\n5. Company size: Small if <50 employees (typical for Pflegedienst)\n\nReturn JSON only."
    }
  ],
  "temperature": 0.3,
  "max_tokens": 500
}
```

---

### Node: "Apollo - Find Owner/CEO" (MUST CONFIGURE)

**Method**: POST  
**URL**: `https://api.apollo.io/v1/mixed_people/search`  
**Authentication**: Apollo API Key credential  
**Body** (JSON):

```json
{
  "organization_domains": ["{{ $json.website.replace('https://', '').replace('http://', '').split('/')[0] }}"],
  "person_titles": ["Geschäftsführer", "Inhaber", "Betriebsleiter", "Owner", "CEO"],
  "page": 1,
  "per_page": 1
}
```

---

### Node: "Apollo - Find Fleet Manager" (MUST CONFIGURE)

**Method**: POST  
**URL**: `https://api.apollo.io/v1/mixed_people/search`  
**Authentication**: Apollo API Key credential  
**Body** (JSON):

```json
{
  "organization_domains": ["{{ $json.website.replace('https://', '').replace('http://', '').split('/')[0] }}"],
  "person_titles": ["Fuhrparkleiter", "Technischer Leiter", "Logistikleiter", "Werkstattleiter", "Fleet Manager"],
  "page": 1,
  "per_page": 1
}
```

---

### Node: "Write to Google Sheets" (MUST CONFIGURE)

1. Select your Google Sheets credential
2. **Operation**: Append
3. **Document ID**: Create a new Google Sheet and paste its ID
4. **Sheet Name**: `Leads`
5. **Columns**: The node should auto-map from the "Format Final Output" node

**Sheet Setup**:
Create a Google Sheet with these column headers:
```
Company Name | Street | City | Zip Code | Sales Region | Website | Phone Number | Segment | Segment Sub-Category | Workshop Type | Fleet Size Estimate | Vehicle Types | Contact Role | Contact First Name | Contact Last Name | Contact Email | Contact LinkedIn | Trigger Signals | Status | Processing Date
```

---

## 3. Connection Updates

After adding the "Extract Text from HTML" node, update these connections:

**OLD**:  
`Merge` → `AI Qualification (OpenAI)`

**NEW**:  
`Merge` → `Extract Text from HTML` → `AI Qualification (OpenAI)`

---

## 4. Testing Checklist

Before running the full workflow:

- [ ] Test Apify API with a single zip code (76133)
- [ ] Verify Apify returns company data (not images/reviews)
- [ ] Test HTML extraction with a sample company website
- [ ] Test AI qualification with sample text
- [ ] Verify Apollo API returns contact data
- [ ] Check Google Sheets write permission
- [ ] Run end-to-end test with 1-2 companies

---

## 5. Cost Optimization Verification

Ensure these settings to stay within budget:

- ✅ Apify: `scrapePhotos: false`
- ✅ Apify: `scrapeReviews: false`
- ✅ Apify: `maxCrawledPlacesPerSearch: 50`
- ✅ OpenAI: Model `gpt-4o-mini` (NOT gpt-4o)
- ✅ OpenAI: `max_tokens: 500`
- ✅ HTML extraction: Limited to 3000 characters

---

## 6. Troubleshooting

### Issue: Apify returns empty results
- Check API token is valid
- Verify zip codes are German format (5 digits)
- Test with known company: "Pflegedienst 76133"

### Issue: AI returns invalid JSON
- Check the response in n8n execution log
- Verify `website_text` field is populated
- May need to adjust the "Parse AI Response" node regex

### Issue: Apollo returns no contacts
- Small German companies often not in Apollo
- Northdata fallback should activate
- Check Northdata scraping logic

### Issue: Google Sheets write fails
- Verify service account has edit access to the sheet
- Check sheet ID is correct
- Ensure column count matches

---

## Next Steps After POC

1. Expand keywords to all 9 industries
2. Add more zip code regions to sales mapping
3. Implement CRM export (beyond Google Sheets)
4. Add error monitoring and alerts
5. Optimize based on actual cost data
