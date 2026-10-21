---
name: meta_ads
description: Create and manage Facebook ad campaigns, ad sets, creatives, and ads via the Meta Marketing API. Requires a Facebook account connected with ads permissions.
author:
  name: MyClawBots
  url: https://myclawbots.ai
license: MIT
category: social
tags: [facebook-ads, meta, campaigns, advertising]
suggested_template: meta_ads_manager
---

# Meta Ads Manager

> **IMPORTANT:** This skill manages paid Facebook advertising that costs real money.
> **ALWAYS show a full summary and ask for explicit confirmation before creating anything.**
> **NEVER activate a campaign without user approval — all campaigns start PAUSED.**

## Requirements
- A Facebook account must be connected in Settings → Social
- The account must have **ads permissions** (check with tool #1 below)
- If no accounts have ads permission, direct the user to Settings → Social → click "Upgrade permissions" next to their Facebook Page

## How it works
- All ad operations go through the proxy — no secrets on this machine
- Campaigns are always created in **PAUSED** status for safety
- Only activate (`ACTIVE`) a campaign after the user explicitly approves

---

## Available Tools

### 1. List ad accounts (ALWAYS do this first)
```bash
curl -s -X GET "${PROXY_URL}/social/ads/accounts" \
  -H "x-api-key: $PROXY_API_KEY"
```
Returns: `{ "accounts": [{ "id": "...", "page_name": "...", "ad_account_id": "act_XXXX", "has_ads_permission": true }] }`

If the list is empty, the user has not granted ads permissions. Tell them to go to Settings → Social and click "Upgrade permissions" next to their Facebook Page.

---

### 2. Create a campaign (starts PAUSED)
```bash
curl -s -X POST "${PROXY_URL}/social/ads/campaign" \
  -H "x-api-key: $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "<id from step 1>",
    "name": "My Campaign Name",
    "objective": "OUTCOME_TRAFFIC",
    "status": "PAUSED",
    "special_ad_categories": [],
    "daily_budget": 5000,
    "bid_strategy": "LOWEST_COST_WITHOUT_CAP"
  }'
```

#### Budget Strategy: CBO vs ABO
You must choose ONE budget strategy per campaign:

- **CBO (Campaign Budget Optimization)** — set `daily_budget` or `lifetime_budget` **on the campaign**.
  Meta automatically distributes spend across ad sets. Do **NOT** set budget on ad sets.
- **ABO (Ad Set Budget Optimization)** — do **NOT** set budget on the campaign.
  Set `daily_budget` or `lifetime_budget` on **each ad set** instead.

> ⚠️ **CBO + ad set budget = error.** Never set budget at both levels.
> ⚠️ `daily_budget` and `lifetime_budget` are **mutually exclusive** — pick one.

#### Campaign Fields
| Field | Required | Description |
|---|---|---|
| `account_id` | ✅ | From step 1 |
| `name` | ✅ | Campaign name |
| `objective` | ✅ | ODAX objective (see below) |
| `special_ad_categories` | ✅ | `[]` for normal ads, or `["HOUSING"]`, `["CREDIT"]`, `["EMPLOYMENT"]`, `["ISSUES_ELECTIONS_POLITICS"]` |
| `status` | | Default: `PAUSED` |
| `daily_budget` | CBO only | In **cents** (5000 = $50.00). Omit for ABO. |
| `lifetime_budget` | CBO only | In **cents**. Mutually exclusive with `daily_budget`. |
| `bid_strategy` | | `LOWEST_COST_WITHOUT_CAP` (default), `LOWEST_COST_WITH_BID_CAP`, `COST_CAP` |
| `is_adset_budget_sharing_enabled` | ABO only | Set to `false` when creating ABO campaigns (no campaign budget). Meta requires this field when budget is NOT set at campaign level. |

- **⚠️ Objectives (ODAX — required for API v21+).** Use ONLY these values:
  - `OUTCOME_AWARENESS` — brand visibility, reach
  - `OUTCOME_TRAFFIC` — website/app clicks
  - `OUTCOME_ENGAGEMENT` — likes, comments, video views, messages
  - `OUTCOME_LEADS` — lead forms, calls, messaging
  - `OUTCOME_APP_PROMOTION` — app installs
  - `OUTCOME_SALES` — purchases, conversions
- ❌ Do NOT use legacy objectives like `LINK_CLICKS`, `CONVERSIONS`, `BRAND_AWARENESS` — they are deprecated.
- Returns: `{ "campaign_id": "...", "status": "PAUSED" }`

---

### 3. Create an ad set (targeting + budget)

#### Example A: CBO campaign (budget already on campaign — omit budget here)
```bash
curl -s -X POST "${PROXY_URL}/social/ads/adset" \
  -H "x-api-key: $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "<id from step 1>",
    "campaign_id": "<campaign_id from step 2>",
    "name": "My Ad Set",
    "billing_event": "IMPRESSIONS",
    "optimization_goal": "LINK_CLICKS",
    "targeting": {
      "geo_locations": { "countries": ["US"] },
      "age_min": 18,
      "age_max": 65
    },
    "status": "PAUSED"
  }'
```

#### Example B: ABO campaign (budget on ad set)
```bash
curl -s -X POST "${PROXY_URL}/social/ads/adset" \
  -H "x-api-key: $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "<id from step 1>",
    "campaign_id": "<campaign_id from step 2>",
    "name": "My Ad Set",
    "daily_budget": 1000,
    "bid_strategy": "LOWEST_COST_WITHOUT_CAP",
    "billing_event": "IMPRESSIONS",
    "optimization_goal": "LINK_CLICKS",
    "targeting": {
      "geo_locations": { "countries": ["US"] },
      "age_min": 18,
      "age_max": 65
    },
    "status": "PAUSED"
  }'
```

#### Ad Set Fields
| Field | Required | Description |
|---|---|---|
| `account_id` | ✅ | From step 1 |
| `campaign_id` | ✅ | From step 2 |
| `name` | ✅ | Ad set name |
| `billing_event` | ✅ | `IMPRESSIONS` (safest default), `LINK_CLICKS`, `THRUPLAY`, `PAGE_LIKES` |
| `optimization_goal` | ✅ | Must match campaign objective (see table below) |
| `targeting` | ✅ | Meta targeting spec (geo, age, interests, etc.) |
| `daily_budget` | ABO only | In **cents** (1000 = $10.00). Omit for CBO campaigns. |
| `lifetime_budget` | ABO only | In **cents**. Mutually exclusive with `daily_budget`. |
| `bid_strategy` | | `LOWEST_COST_WITHOUT_CAP`, `LOWEST_COST_WITH_BID_CAP`, `COST_CAP` |
| `bid_amount` | | Required when `bid_strategy` is `LOWEST_COST_WITH_BID_CAP`, in **cents** |
| `promoted_object` | Conversion campaigns | Required for `OUTCOME_SALES`, `OUTCOME_LEADS`, `OUTCOME_APP_PROMOTION`. See below. |
| `start_time` | | ISO 8601 (e.g. `2026-04-15T00:00:00-0400`) |
| `end_time` | | ISO 8601 |
| `status` | | Default: `PAUSED` |

> ⚠️ **CBO campaigns:** Do NOT send `daily_budget` or `lifetime_budget` on the ad set — Meta will reject it.
> ⚠️ **ABO campaigns:** You MUST send `daily_budget` or `lifetime_budget` on the ad set.

#### Promoted Object (conversion tracking)
Required when the campaign objective needs a conversion target:
- **`OUTCOME_SALES`** (Pixel tracking):
  ```json
  { "promoted_object": { "pixel_id": "<pixel_id>", "custom_event_type": "PURCHASE" } }
  ```
- **`OUTCOME_LEADS`** (Lead forms):
  ```json
  { "promoted_object": { "pixel_id": "<pixel_id>", "custom_event_type": "LEAD" } }
  ```
- **`OUTCOME_APP_PROMOTION`** (App installs):
  ```json
  { "promoted_object": { "application_id": "<app_id>", "object_store_url": "<store_url>" } }
  ```
- `custom_event_type` values: `PURCHASE`, `LEAD`, `COMPLETE_REGISTRATION`, `ADD_TO_CART`, `INITIATED_CHECKOUT`, `SEARCH`, `CONTENT_VIEW`, `ADD_PAYMENT_INFO`, `ADD_TO_WISHLIST`, `OTHER`
- If you don't know the Pixel ID, ask the user to find it in Meta Events Manager.

- **optimization_goal** — must match the campaign objective:
  - `OUTCOME_AWARENESS` → `REACH` or `AD_RECALL_LIFT`
  - `OUTCOME_TRAFFIC` → `LINK_CLICKS` or `LANDING_PAGE_VIEWS`
  - `OUTCOME_ENGAGEMENT` → `POST_ENGAGEMENT`, `THRUPLAY`, or `EVENT_RESPONSES`
  - `OUTCOME_LEADS` → `LEAD_GENERATION` or `QUALITY_LEAD`
  - `OUTCOME_APP_PROMOTION` → `APP_INSTALLS` or `APP_EVENTS`
  - `OUTCOME_SALES` → `OFFSITE_CONVERSIONS` or `VALUE`
- ⚠️ If you get a "billing_event incompatible" error, switch to `IMPRESSIONS`.
- Returns: `{ "adset_id": "...", "status": "PAUSED" }`

---

### 4. Create an ad creative (the visual + copy)
```bash
curl -s -X POST "${PROXY_URL}/social/ads/creative" \
  -H "x-api-key: $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "<id from step 1>",
    "name": "My Creative",
    "page_id": "<facebook_page_id>",
    "message": "Ad copy text here",
    "link": "https://yourwebsite.com",
    "link_title": "Check this out",
    "link_description": "Optional description",
    "image_url": "https://example.com/image.jpg",
    "call_to_action": "LEARN_MORE"
  }'
```
- **call_to_action options:** `LEARN_MORE`, `SHOP_NOW`, `SIGN_UP`, `CONTACT_US`, `BOOK_NOW`, `GET_OFFER`
- Returns: `{ "creative_id": "..." }`

---

### 5. Create the ad (links ad set + creative)
```bash
curl -s -X POST "${PROXY_URL}/social/ads/ad" \
  -H "x-api-key: $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "<id from step 1>",
    "adset_id": "<adset_id from step 3>",
    "creative_id": "<creative_id from step 4>",
    "name": "My Ad",
    "status": "PAUSED"
  }'
```
Returns: `{ "ad_id": "...", "status": "PAUSED" }`

---

### 6. List existing campaigns
```bash
curl -s -X GET "${PROXY_URL}/social/ads/campaigns?account_id=<id>&status=PAUSED" \
  -H "x-api-key: $PROXY_API_KEY"
```
- Optional `status` filter: `ACTIVE`, `PAUSED`, `ARCHIVED`
- Returns campaigns with spend, budget, reach, impressions

---

### 7. Get performance insights
```bash
curl -s -X GET "${PROXY_URL}/social/ads/insights?account_id=<id>&level=campaign&date_preset=last_7d" \
  -H "x-api-key: $PROXY_API_KEY"
```
- `level`: `campaign`, `adset`, `ad`
- `date_preset`: `today`, `yesterday`, `last_7d`, `last_14d`, `last_30d`, `last_month`, `this_month`
- `object_id`: (optional) specific campaign/adset/ad ID
- Returns: impressions, clicks, spend, CTR, CPM, reach, actions

---

### 8. Pause or activate a campaign
```bash
curl -s -X POST "${PROXY_URL}/social/ads/campaign/<campaign_id>/status" \
  -H "x-api-key: $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "<id from step 1>",
    "status": "ACTIVE"
  }'
```
- `status`: `ACTIVE` or `PAUSED`
- ⚠️ **ALWAYS** confirm with the user before activating. Activated campaigns spend real money.

---

### 9. Search for targeting interests
Use this to find valid **interest IDs** for ad set targeting. Never guess interest IDs — always look them up.
```bash
curl -s -X GET "${PROXY_URL}/social/ads/targeting/search?account_id=<id>&q=fitness&type=adinterest&limit=10" \
  -H "x-api-key: $PROXY_API_KEY"
```
- `q`: Search term (e.g. "fitness", "small business", "marketing")
- `type`: (optional) `adinterest` (default), `adinterestsuggestion`, `adTargetingCategory`, `adinterestvalid`
- `limit`: (optional) Max results, default 20
- Returns: `{ "results": [{ "id": "6003139266461", "name": "Fitness and wellness", "audience_size_lower_bound": 474000000, ... }] }`

Use the returned `id` and `name` in your targeting spec:
```json
{
  "targeting": {
    "geo_locations": { "countries": ["US"] },
    "age_min": 25,
    "age_max": 55,
    "interests": [
      { "id": "6003139266461", "name": "Fitness and wellness" },
      { "id": "6003277229371", "name": "Physical fitness" }
    ]
  }
}
```

---

## Workflow: Creating a Complete Ad Campaign

Follow these steps in order — each step depends on the previous:

1. **List ad accounts** → get `account_id` and confirm the right ad account
2. **Create campaign** → define objective + budget strategy (always PAUSED)
3. **Search targeting interests** → look up interest IDs for audience targeting
4. **Create ad set** → define audience, budget (ABO only), schedule (always PAUSED)
5. **Create creative** → define the visual and copy
6. **Create ad** → link the above (always PAUSED)
7. **Show full summary** → present campaign_id, adset_id, creative_id, ad_id, budget, audience
8. **Ask for activation** → "Shall I activate this campaign? It will begin spending $X/day."
9. **Activate** → only if user explicitly confirms

---

## Important Rules
1. **ALWAYS** list ad accounts first — never assume account_id
2. **ALWAYS** create everything in PAUSED status first
3. **ALWAYS** show a complete summary before activating:
   - Campaign name + objective
   - Daily budget (in dollars, not cents)
   - Target audience
   - Ad copy preview
4. **ALWAYS** say "This will spend real money" when asking for activation approval
5. **NEVER** activate without explicit user confirmation ("yes", "go ahead", "activate it")
6. After activation, offer to check insights in 24 hours
7. If the user says "stop the campaign" → immediately PAUSE it
8. Budgets are in **cents** (e.g., `1000` = $10.00 USD) — always convert to dollars when showing the user
9. **CBO campaigns** = budget on campaign, no budget on ad sets. **ABO campaigns** = no budget on campaign, budget on each ad set.
10. When in doubt, use **CBO with `LOWEST_COST_WITHOUT_CAP`** — it's the simplest setup and Meta optimizes spend automatically.

## Handling Missing Ads Permissions
If `GET /social/ads/accounts` returns an empty list:
- Tell the user: "Your Facebook account doesn't have ads permissions yet."
- Instruct them: "Go to Settings → Social, find your Facebook Page, and click 'Upgrade permissions'."
- After they reconnect, run `GET /social/ads/accounts` again to confirm.
