"""
Generate complete n8n workflow JSON for PH Lead Agent
This script creates a properly structured workflow with all nodes configured
"""

import json

# Create the complete workflow structure
workflow = {
    "nodes": [
        # Node 1: Manual Trigger
        {
            "parameters": {},
            "type": "n8n-nodes-base.manualTrigger",
            "typeVersion": 1,
            "position": [-528, 560],
            "id": "trigger-001",
            "name": "When clicking 'Execute workflow'"
        },
        
        # Node 2: Manual Input - Zip Codes
        {
            "parameters": {
                "values": {
                    "string": [
                        {"name": "zip_codes", "value": "76133,76185,76227"},
                        {"name": "search_keyword", "value": "Pflegedienst"}
                    ]
                },
                "options": {}
            },
            "id": "input-001",
            "name": "Manual Input - Zip Codes",
            "type": "n8n-nodes-base.set",
            "typeVersion": 1,
            "position": [-256, 560]
        },
        
        # Node 3: Map Sales Region
        {
            "parameters": {
                "rules": {
                    "values": [
                        {
                            "conditions": {
                                "options": {
                                    "caseSensitive": True,
                                    "leftValue": "",
                                    "typeValidation": "strict",
                                    "version": 3
                                },
                                "conditions": [
                                    {
                                        "leftValue": "={{ $json.zip_codes.substring(0, 2) }}",
                                        "rightValue": "76",
                                        "operator": {
                                            "type": "string",
                                            "operation": "equals"
                                        },
                                        "id": "zip-check-001"
                                    }
                                ],
                                "combinator": "and"
                            },
                            "renameOutput": True,
                            "outputKey": "Team Karlsruhe"
                        }
                    ]
                },
                "options": {
                    "fallbackOutput": "extra"
                }
            },
            "type": "n8n-nodes-base.switch",
            "typeVersion": 3.4,
            "position": [16, 528],
            "id": "switch-001",
            "name": "Map Sales Region",
            "notes": "Routes zip codes to sales teams. POC: 76xxx = Team Karlsruhe"
        },
        
        # Node 4: Apify - Google Maps Scraper
        {
            "parameters": {
                "method": "POST",
                "url": "https://api.apify.com/v2/acts/compass~google-maps-scraper/run-sync-get-dataset-items",
                "authentication": "headerAuth",
                "sendBody": True,
                "specifyBody": "json",
                "jsonBody": '={\\n  "searchStringsArray": [\\n    "{{ $json.search_keyword }} {{ $json.zip_codes.split(\',\')[0] }}",\\n    "{{ $json.search_keyword }} {{ $json.zip_codes.split(\',\')[1] }}",\\n    "{{ $json.search_keyword }} {{ $json.zip_codes.split(\',\')[2] }}"\\n  ],\\n  "maxCrawledPlacesPerSearch": 50,\\n  "language": "de",\\n  "scrapePhotos": false,\\n  "scrapeReviews": false,\\n  "exportPlaceUrls": true,\\n  "maxImages": 0,\\n  "maxReviews": 0\\n}',
                "options": {
                    "timeout": 300000,
                    "response": {
                        "response": {
                            "fullResponse": False,
                            "neverError": False
                        }
                    }
                }
            },
            "id": "apify-001",
            "name": "Apify - Google Maps Scraper",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 3,
            "position": [224, 528],
            "notes": "Cost-optimized: Text only, no images/reviews. Searches 3 zip codes for Pflegedienst"
        }
    ],
    
    "connections": {
        "When clicking 'Execute workflow'": {
            "main": [[{"node": "Manual Input - Zip Codes", "type": "main", "index": 0}]]
        },
        "Manual Input - Zip Codes": {
            "main": [[{"node": "Map Sales Region", "type": "main", "index": 0}]]
        },
        "Map Sales Region": {
            "main": [[{"node": "Apify - Google Maps Scraper", "type": "main", "index": 0}], [], [], []]
        }
    },
    
    "pinData": {
        "Manual Input - Zip Codes": [
            {
                "zip_codes": "76133,76185,76227",
                "search_keyword": "Pflegedienst"
            }
        ]
    },
    
    "meta": {
        "templateCredsSetupCompleted": True,
        "instanceId": "ph-lead-agent-poc-v1"
    }
}

# Write to file
with open('PH_Lead_Agent_Complete.json', 'w', encoding='utf-8') as f:
    json.dump(workflow, f, indent=2, ensure_ascii=False)

print("✅ Complete workflow JSON generated: PH_Lead_Agent_Complete.json")
print("📝 Next steps:")
print("   1. Import this file into n8n")
print("   2. Follow CONFIGURATION_GUIDE.md to add remaining nodes")
print("   3. Configure API credentials")
print("   4. Test with single zip code")
