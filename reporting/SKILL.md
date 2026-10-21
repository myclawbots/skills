---
name: reporting
description: Generate, schedule, and manage cross-platform reports combining data from connected services. Create PDF/CSV exports and automated report delivery.
author:
  name: MyClawBots
  url: https://myclawbots.ai
license: MIT
category: analytics
tags: [reports, pdf, csv, scheduling]
suggested_template: data_analyst
---

# Reporting

> **Dashboard Connection Required**
> This skill enables report generation across all your connected services (Analytics, CRM, Email, Social, etc.). Configure at least one data source in your MyClawBots dashboard before generating reports. Auth is handled by the proxy—provide `${PROXY_URL}` and `$PROXY_API_KEY` in curl requests.

## Prerequisites

- At least one connected data source (analytics, CRM, email platform, social media, etc.)
- Recipients for scheduled reports must have valid email addresses
- `${PROXY_URL}` environment variable set to your proxy endpoint
- `$PROXY_API_KEY` environment variable set to your API key
- PDF generation requires LaTeX or equivalent on proxy (for PDF format)

## Dependencies

| Dependency | Required? | Why |
|---|---|---|
| `${PROXY_URL}` and `$PROXY_API_KEY` | Yes | Required for proxy authentication |
| Data skills (recommended) | No | Recommended: `web-analytics`, `social-manager`, `crm`, `email-outreach` for rich reports |
| `google-workspace` skill | No | Optional: for saving reports to Google Drive and emailing |

**Pre-flight checks:**
- Confirm `${PROXY_URL}` and `$PROXY_API_KEY` environment variables are set
- Verify at least one data source is connected in the dashboard (analytics, CRM, email, social, etc.)
- If including analytics data: ensure `web-analytics` skill is connected
- If including CRM data: ensure `crm` skill is connected
- If including email data: ensure `email-outreach` skill is connected
- If saving/emailing reports: ensure `google-workspace` skill is connected

## How it works

The Reporting skill lets you generate on-demand and scheduled reports from all your connected platforms. Build custom report configurations, pull data from multiple sources in one report, export to PDF or CSV, and automate delivery. Use this to:

- Generate executive summaries combining analytics, CRM, and email data
- Create weekly/monthly performance reports for stakeholders
- Export data for archival or further analysis
- Automate report delivery on a schedule (daily, weekly, monthly)
- Track report history and audit who accessed what
- Build reusable report templates for consistency

All reports can mix data sources—combine website analytics with CRM sales data, email campaign performance, and social metrics in a single report.

## Available Tools

### 1. List Saved Reports
View all reports you've created and saved.

```bash
curl -X GET "${PROXY_URL}/reports" \
  -H "Authorization: Bearer $PROXY_API_KEY"
```

Returns: report ID, name, created date, last generated date, status (active/archived). Use to find existing reports before generating or scheduling.

### 2. Generate a Report
Create a new report with custom sections and data sources.

```bash
curl -X POST "${PROXY_URL}/reports/generate" \
  -H "Authorization: Bearer $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Monthly Performance Summary",
    "sections": [
      {
        "source": "analytics",
        "metrics": ["visitors", "pageviews", "bounce_rate", "conversions"],
        "filters": {"period": "30d"}
      },
      {
        "source": "crm",
        "metrics": ["new_deals", "deal_value", "close_rate"],
        "filters": {"stage": "won"}
      },
      {
        "source": "email",
        "metrics": ["sent", "opened", "clicked", "unsubscribed"],
        "filters": {"campaign_type": "newsletter"}
      }
    ],
    "format": "pdf",
    "date_range": "30d"
  }'
```

Parameters:
- `title`: Report name (string)
- `sections`: Array of data sections. Each section includes:
  - `source`: analytics, crm, email, social, help_desk (depends on connections)
  - `metrics`: Array of metric names to include
  - `filters`: Object with filtering options (period, campaign, stage, etc.)
- `format`: pdf, csv, json (default: pdf)
- `date_range`: 7d, 30d, 90d, custom (also supports start_date/end_date strings)

Returns: report ID, status, estimated generation time. If report is large, processing may be async.

### 3. Get Report Details
Retrieve a generated report's metadata and download URL.

```bash
curl -X GET "${PROXY_URL}/reports/{id}" \
  -H "Authorization: Bearer $PROXY_API_KEY"
```

Replace `{id}` with your report ID. Returns: report title, sections, format, date range, generated timestamp, file size, download URL, expiry date.

### 4. Download Report File
Get the actual report file (PDF or CSV).

```bash
curl -X GET "${PROXY_URL}/reports/{id}/download" \
  -H "Authorization: Bearer $PROXY_API_KEY" \
  -o my_report.pdf
```

Replace `{id}` with report ID. Downloads the file directly. Files typically expire after 7 days.

### 5. Schedule a Recurring Report
Automate report generation and delivery on a schedule.

```bash
curl -X POST "${PROXY_URL}/reports/schedule" \
  -H "Authorization: Bearer $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "report_config": {
      "title": "Weekly Executive Summary",
      "sections": [
        {
          "source": "analytics",
          "metrics": ["visitors", "pageviews", "conversions"],
          "filters": {"period": "7d"}
        },
        {
          "source": "crm",
          "metrics": ["new_deals", "deal_value"],
          "filters": {}
        }
      ],
      "format": "pdf",
      "date_range": "7d"
    },
    "frequency": "weekly",
    "recipients": ["exec@company.com", "manager@company.com"],
    "day_of_week": "monday",
    "time": "09:00"
  }'
```

Parameters:
- `report_config`: The report definition (same structure as /reports/generate)
- `frequency`: daily, weekly, monthly
- `recipients`: Email addresses to send to (array)
- `day_of_week`: For weekly (monday-sunday)
- `day_of_month`: For monthly (1-31)
- `time`: Send time in HH:MM format (24-hour, UTC or local per settings)

Returns: schedule ID, next run date, confirmation that recipients were added.

### 6. List Scheduled Reports
View all active scheduled reports.

```bash
curl -X GET "${PROXY_URL}/reports/schedules" \
  -H "Authorization: Bearer $PROXY_API_KEY"
```

Returns: schedule ID, report name, frequency, recipients, next run date, last run date, status (active/paused/failed). Use to audit which reports are running.

### 7. Update a Schedule
Modify frequency, recipients, or report configuration.

```bash
curl -X PUT "${PROXY_URL}/reports/schedules/{id}" \
  -H "Authorization: Bearer $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "recipients": ["newexec@company.com"],
    "frequency": "daily",
    "time": "08:00"
  }'
```

Replace `{id}` with schedule ID. Only include fields you want to change. Returns: updated schedule details.

### 8. Delete a Schedule
Stop a scheduled report from running.

```bash
curl -X DELETE "${PROXY_URL}/reports/schedules/{id}" \
  -H "Authorization: Bearer $PROXY_API_KEY"
```

Replace `{id}` with schedule ID. Deletion is permanent; historical reports remain available. Returns: confirmation.

### 9. Quick Snapshot
Generate a quick overview of key metrics across all connected services in one call.

```bash
curl -X POST "${PROXY_URL}/reports/snapshot" \
  -H "Authorization: Bearer $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "services": ["analytics", "crm", "email"],
    "period": "30d"
  }'
```

Parameters:
- `services`: Array of service names to include (uses connected services only)
- `period`: 7d, 30d, 90d

Returns: top-level metrics from each service (no deep drill-down, just highlights). Fast to generate. Good for quick dashboards.

### 10. List Report Templates
View saved report templates for reuse.

```bash
curl -X GET "${PROXY_URL}/reports/templates" \
  -H "Authorization: Bearer $PROXY_API_KEY"
```

Returns: template ID, name, description, source services included, last used date. Templates are reusable blueprints.

### 11. Save Report as Template
Create a template from an existing report for future use.

```bash
curl -X POST "${PROXY_URL}/reports/templates" \
  -H "Authorization: Bearer $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Monthly Business Review",
    "description": "Combines analytics, sales, and marketing metrics",
    "config": {
      "sections": [
        {
          "source": "analytics",
          "metrics": ["visitors", "pageviews", "conversions"]
        },
        {
          "source": "crm",
          "metrics": ["new_deals", "deal_value", "close_rate"]
        },
        {
          "source": "email",
          "metrics": ["sent", "opened", "clicked"]
        }
      ],
      "format": "pdf"
    }
  }'
```

Parameters:
- `name`: Template name
- `description`: What this template is for
- `config`: Report structure to save

Returns: template ID. Use this template ID to quickly generate reports with the same structure later.

## Important Rules

1. **Always Confirm Parameters** — Before generating a report, verify the date range, services included, and metrics requested. Ask clarifying questions if unclear what the requester wants.

2. **Check Date Ranges** — Ensure date ranges make sense. Don't generate 90-day reports on services with only 7 days of data. Warn if a service has sparse data.

3. **Warn About Large Exports** — Reports with multiple services and long date ranges can be large. CSV exports of years of data may be unwieldy. Offer to split into smaller chunks or suggest a filter.

4. **Offer Scheduling for Repetitive Requests** — If someone asks for the same report structure multiple times, suggest saving as a template and/or scheduling recurring delivery. Saves time and ensures consistency.

5. **Recipient Validation** — Always verify email addresses before scheduling. Invalid recipients will cause failed sends.

6. **Service Availability** — Confirm that requested data sources are connected before building sections. If analytics data is requested but analytics isn't connected, fail gracefully and suggest connecting first.

7. **Format Appropriateness** — PDF is best for human readability and sharing. CSV is better for further analysis in Excel/tools. JSON is best for API consumption or archival.

8. **Historical Access** — Generated reports are typically accessible for 7-30 days depending on system settings. Suggest downloading or scheduling recurring generation if a report needs permanent retention.

## Smart Strategy

1. **Start with Snapshot** — If unsure what to build, generate a quick snapshot first. This shows available metrics across services and helps clarify what the requester actually wants.

2. **Identify Your Audience** — Is this for an executive, a marketer, or an analyst? Executives want high-level trends and ROI. Marketers want detailed campaign breakdowns. Analysts want raw data and filters.

3. **Mix Services Strategically** — The power of cross-platform reporting is correlation. Link traffic to sales. Link email campaigns to CRM pipeline. Link social posts to conversions.

4. **Use Templates for Scale** — Build 3-4 core templates (Executive Summary, Marketing Performance, Sales Pipeline, Financial). Reuse them for all future scheduling. Consistency saves time.

5. **Schedule Recurring Reports** — Don't generate reports manually every week. Schedule them once and they run automatically. Frees up time for analysis instead of creation.

6. **Build Filters Into Sections** — Use filters (campaign type, deal stage, page segment) to narrow focus. A "newsletter-only" email section is more meaningful than all email campaigns mixed together.

7. **Choose the Right Format** — PDF for sharing and archival. CSV for analysis and drill-down. JSON only if the report will be consumed by a system.

8. **Review and Iterate** — After the first scheduled run, review the output. Did it include the right metrics? Was the layout clear? Adjust the template before it runs again.
