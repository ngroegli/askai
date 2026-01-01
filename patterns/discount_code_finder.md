# Pattern: Discount Code Finder

**Tags:** `content`, `automation`, `shopping`, `discount`

## Purpose

The `discount_code_finder` pattern helps users discover current discount codes and promotional offers for a given online store. You are tasked with scouring the internet and leaving no stone unturned in your pursuit of discount codes. Search coupon sites like RetailMeNot and Slickdeals, check the store's official website, social media, and any other sources. Predict likely code patterns based on current promotions, seasons, and common code structures. Return all potentially valid codes you find or can reasonably predict.

## Functionality

* Accept a store or service domain (e.g., `amazon.com`, `nike.com`, `disney.com`) as input
* Scour the internet for discount codes from coupon sites (RetailMeNot, Slickdeals, Honey, etc.), the store's website, social media (YouTube, Instagram, TikTok), and influencer partnerships
* Specifically search for influencer discount codes - these often follow patterns like influencer names, channel names, or branded codes (e.g., "MKBHD20", "SARAH15", "TECHGUY", "BEAUTYBAY10")
* Check for affiliate and partner codes that influencers share in video descriptions, Instagram bios, and stories
* Predict likely discount code patterns based on current promotions, seasons, popular influencers in the niche, and common naming conventions
* Include influencer codes, percentage-off codes, dollar-amount codes, free shipping codes, seasonal codes, welcome codes, and clearance codes
* For each code, provide the discount amount/type, source (especially if from a specific influencer), and any known restrictions
* List codes from most likely to work to least likely, prioritizing recent influencer codes
* Include reasoning about why each code might be valid
* Return all potentially valid options even if uncertain - the user will test them at checkout
* Check both current codes and predict patterns that might still work, especially non-time-restricted influencer codes

## Pattern Inputs

```yaml
inputs:
  - name: store_domain
    description: The domain of the online store or service (e.g., amazon.com)
    type: text
    required: true
    example: "nike.com"
```

## Pattern Outputs

```yaml
results:
  - name: discount_codes
    description: List of discovered and predicted discount codes with details
    type: json
    required: true
    example: |
      {
        "codes": [
          {
            "code": "MKBHD15",
            "discount": "15% off",
            "confidence": "high",
            "source": "YouTube influencer Marques Brownlee partnership",
            "restrictions": "May exclude sale items",
            "reasoning": "Popular tech reviewer with ongoing brand partnerships, code pattern matches influencer name"
          },
          {
            "code": "HONEYDEW",
            "discount": "20% off",
            "confidence": "medium",
            "source": "Beauty influencer shared on Instagram",
            "restrictions": "Unknown, test at checkout",
            "reasoning": "Common beauty influencer code style, often non-expiring"
          },
          {
            "code": "TECHLINKED10",
            "discount": "10% off",
            "confidence": "medium",
            "source": "Linus Tech Tips affiliate code",
            "restrictions": "First purchase may be required",
            "reasoning": "Tech channel commonly partners with brands for viewer discounts"
          },
          {
            "code": "CLEARANCE",
            "discount": "Varies by item",
            "confidence": "medium",
            "source": "Generic clearance pattern",
            "restrictions": "Clearance items only",
            "reasoning": "Common code structure for clearance sales"
          },
          {
            "code": "WELCOME10",
            "discount": "10% off",
            "confidence": "low",
            "source": "Standard new customer pattern",
            "restrictions": "First-time customers only",
            "reasoning": "Generic welcome discount, may be deactivated"
          }
        ],
        "search_notes": "Searched YouTube influencer partnerships, Instagram bios, RetailMeNot, and predicted common influencer code patterns for this brand's niche."
      }
```

## Model Configuration

```yaml
model:
  provider: openrouter
  model_name: openai/gpt-4o
  temperature: 0.1
  max_tokens: 2000
  custom_parameters: {}
```
