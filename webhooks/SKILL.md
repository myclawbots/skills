---
name: webhooks
description: Create automated workflows with webhooks and triggers. Connect events across services to automate repetitive tasks like notifications, data sync, and status updates.
author:
  name: MyClawBots
  url: https://myclawbots.ai
license: MIT
category: integrations
tags: [webhooks, automation, triggers, integrations]
suggested_template: devops_bot
---

# Webhooks & Automation

> **Dashboard Connection Required**
> This skill enables you to create automated workflows across your connected services. Configure at least two services in your MyClawBots dashboard (e.g., GitHub + Slack, CRM + Email) before creating automations. Auth is handled by the proxy—provide `${PROXY_URL}` and `$PROXY_API_KEY` in curl requests.

## Prerequisites

- At least two connected services to trigger workflows (see available services below)
- Slack, email, or other notification channels configured for action destinations
- `${PROXY_URL}` environment variable set to your proxy endpoint
- `$PROXY_API_KEY` environment variable set to your API key
- Automation limits depend on your plan (typically 10-100 active webhooks)

## Dependencies

| Dependency | Required? | Why |
|---|---|---|
| `${PROXY_URL}` and `$PROXY_API_KEY` | Yes | Required for proxy authentication |
| Other skills (trigger/action sources) | Yes | At least two connected skills to create meaningful automations |
| Event source skills | No | GitHub, GitLab, Slack, CRM, help desk, project management for triggers |
| Action skills | No | Slack, email, CRM, Sheets, HTTP webhooks for actions |

**Supported trigger services:**
- GitHub, GitLab (PR, issue, push events)
- Slack (message, reaction events)
- CRM (new lead, deal stage change)
- Help desk (ticket created, updated)
- Project management (task created, overdue)
- Form services (new submission)
- HTTP webhooks (custom events)

**Supported action services:**
- Slack (send message)
- Email (send email)
- SMS (send text)
- CRM (create/update record)
- Help desk (create ticket)
- Project management (create task)
- Google Sheets (append row)
- HTTP (POST to custom endpoint)

**Pre-flight checks:**
- Confirm `${PROXY_URL}` and `$PROXY_API_KEY` environment variables are set
- Verify at least two services are connected in the dashboard
- Identify trigger service and action service before creating automation
- Test webhook with sample data before enabling in production

## How it works

The Webhooks & Automation skill lets you create "if this, then that" workflows. When an event happens in one service (PR merged, new lead in CRM, task overdue), trigger actions in other services (send Slack notification, create task, send email). This eliminates manual tasks and keeps your team synchronized.

Use this to:

- Notify teams instantly when important events occur
- Sync data across platforms without manual export/import
- Escalate issues (overdue tasks → manager email)
- Welcome new customers (new CRM deal → email sequence)
- Track deployments (GitHub push → Slack announcement)
- Keep status consistent (update CRM when task completes)

Supported trigger services: GitHub, GitLab, Slack, email, CRM systems, help desk platforms, project management tools, form services, HTTP webhooks.

Supported action services: Slack, Email, SMS, CRM (create/update records), Help Desk (create tickets), Project Management (create tasks), Google Sheets (append rows), HTTP (POST to custom endpoint).

## Available Tools

### 1. List Active Webhooks
View all configured automations.

```bash
curl -X GET "${PROXY_URL}/webhooks" \
  -H "Authorization: Bearer $PROXY_API_KEY"
```

Returns: webhook ID, name, trigger service, trigger event, actions, status (enabled/disabled), created date, last triggered date, success rate. Use to audit existing automations.

### 2. Create a Webhook/Automation
Set up a new trigger-action workflow.

```bash
curl -X POST "${PROXY_URL}/webhooks" \
  -H "Authorization: Bearer $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "GitHub PR merged → Slack notification",
    "trigger": {
      "service": "github",
      "event": "pull_request",
      "filters": {
        "action": "closed",
        "merged": true,
        "repository": "my-org/my-repo"
      }
    },
    "actions": [
      {
        "service": "slack",
        "action": "send_message",
        "config": {
          "channel": "#deployments",
          "message": "PR #{pr_number} ({pr_title}) merged to {base_branch} by {author}",
          "include_link": true,
          "thread": false
        }
      }
    ]
  }'
```

Parameters:
- `name`: Friendly name for the automation
- `trigger`: The event that starts the workflow
  - `service`: github, gitlab, slack, crm, help_desk, forms, email (depends on connections)
  - `event`: Service-specific event name (pull_request, new_lead, task_overdue, etc.)
  - `filters`: Optional conditions (only trigger if action=closed, only for certain repos, etc.)
- `actions`: Array of actions to execute when triggered
  - `service`: slack, email, sms, crm, help_desk, project_management, sheets, http
  - `action`: Specific action (send_message, create_ticket, update_record, append_row, etc.)
  - `config`: Action-specific configuration (channel, recipients, template, etc.)

Returns: webhook ID, status, confirmation that triggers are listening.

### 3. Get Webhook Details
View full configuration of a specific automation.

```bash
curl -X GET "${PROXY_URL}/webhooks/{id}" \
  -H "Authorization: Bearer $PROXY_API_KEY"
```

Replace `{id}` with webhook ID. Returns: complete trigger and action configuration, status, creation date, execution history summary, average execution time.

### 4. Update a Webhook
Modify trigger conditions or actions without recreating.

```bash
curl -X PUT "${PROXY_URL}/webhooks/{id}" \
  -H "Authorization: Bearer $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "GitHub PR merged → Slack + Log to Sheets",
    "actions": [
      {
        "service": "slack",
        "action": "send_message",
        "config": {
          "channel": "#deployments",
          "message": "PR #{pr_number} merged!"
        }
      },
      {
        "service": "sheets",
        "action": "append_row",
        "config": {
          "spreadsheet_id": "abc123",
          "sheet_name": "Deployments",
          "values": ["{timestamp}", "{author}", "{pr_title}"]
        }
      }
    ]
  }'
```

Replace `{id}` with webhook ID. Only include fields you want to change. Returns: updated webhook configuration.

### 5. Delete a Webhook
Remove an automation (stops all future triggers).

```bash
curl -X DELETE "${PROXY_URL}/webhooks/{id}" \
  -H "Authorization: Bearer $PROXY_API_KEY"
```

Replace `{id}` with webhook ID. Deletion is permanent. Historical logs remain. Returns: confirmation.

### 6. View Webhook Execution Logs
See what happened when the webhook triggered.

```bash
curl -X GET "${PROXY_URL}/webhooks/{id}/logs?limit=50&status=all" \
  -H "Authorization: Bearer $PROXY_API_KEY"
```

Replace `{id}` with webhook ID. Parameters:
- `limit`: Number of recent executions to return (default 20, max 100)
- `status`: all, success, failed

Returns: timestamp, trigger data, action results, error messages (if any), execution duration. Essential for debugging.

### 7. Test a Webhook
Manually trigger the webhook with sample data to verify it works.

```bash
curl -X POST "${PROXY_URL}/webhooks/{id}/test" \
  -H "Authorization: Bearer $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "sample_data": {
      "pr_number": 42,
      "pr_title": "Add dark mode",
      "author": "jane@company.com",
      "base_branch": "main"
    }
  }'
```

Replace `{id}` with webhook ID. Returns: execution result as if the trigger fired with provided sample data. Logs the test in execution history (optional). Use before enabling to verify everything works.

### 8. Enable a Webhook
Reactivate a disabled webhook.

```bash
curl -X PUT "${PROXY_URL}/webhooks/{id}/enable" \
  -H "Authorization: Bearer $PROXY_API_KEY"
```

Replace `{id}` with webhook ID. Returns: updated status. Webhook begins listening for triggers immediately.

### 9. Disable a Webhook
Pause a webhook without deleting it.

```bash
curl -X PUT "${PROXY_URL}/webhooks/{id}/disable" \
  -H "Authorization: Bearer $PROXY_API_KEY"
```

Replace `{id}` with webhook ID. Returns: updated status. Webhook stops listening but configuration is preserved. Useful for temporarily stopping automations during maintenance.

## Common Automation Examples

### GitHub PR Merged → Slack Announcement
Notify the team when code lands.

```bash
{
  "trigger": {
    "service": "github",
    "event": "pull_request",
    "filters": {"action": "closed", "merged": true}
  },
  "actions": [
    {
      "service": "slack",
      "action": "send_message",
      "config": {
        "channel": "#deployments",
        "message": "🚀 PR merged: {pr_title}"
      }
    }
  ]
}
```

### New CRM Deal → Email Welcome Sequence
Automate customer onboarding.

```bash
{
  "trigger": {
    "service": "crm",
    "event": "deal_created",
    "filters": {"stage": "won"}
  },
  "actions": [
    {
      "service": "email",
      "action": "send_email",
      "config": {
        "template": "welcome_sequence",
        "recipient": "{customer_email}",
        "variables": {
          "name": "{customer_name}",
          "deal_value": "{deal_amount}"
        }
      }
    }
  ]
}
```

### Social Post Published → Slack Announcement
Keep the team informed about company announcements.

```bash
{
  "trigger": {
    "service": "social",
    "event": "post_published",
    "filters": {"account": "company_main"}
  },
  "actions": [
    {
      "service": "slack",
      "action": "send_message",
      "config": {
        "channel": "#marketing",
        "message": "📱 New post: {post_text}\n{post_url}"
      }
    }
  ]
}
```

### Task Overdue → Email Reminder
Escalate overdue items to owners.

```bash
{
  "trigger": {
    "service": "project_management",
    "event": "task_overdue",
    "filters": {"priority": "high"}
  },
  "actions": [
    {
      "service": "email",
      "action": "send_email",
      "config": {
        "recipient": "{assignee_email}",
        "subject": "Task Due: {task_name}",
        "template": "overdue_reminder"
      }
    },
    {
      "service": "slack",
      "action": "send_message",
      "config": {
        "channel": "{assignee_slack_dm}",
        "message": "⚠️ Task overdue: {task_name}"
      }
    }
  ]
}
```

## Important Rules

1. **Always Confirm Before Creating** — Describe the automation in plain language first. Get approval that the trigger conditions and actions are correct before actually creating the webhook.

2. **Test Before Enabling** — Use the test endpoint to trigger the webhook with sample data. Review the logs and Slack/email output to ensure it works as expected.

3. **Review Logs After Setup** — After the automation runs for the first time in production, check execution logs for errors. Fix any issues immediately.

4. **Warn About Notification Fatigue** — If a trigger fires frequently (e.g., every commit to a busy repo), it can spam Slack. Add filters (only on PRs, only on main branch) or use threads to reduce noise.

5. **Filter Intelligently** — Use trigger filters to be specific. "Send alert when task is overdue AND priority is high" is better than "when task is overdue." Reduces false positives.

6. **Rate Limits** — Some services rate-limit actions. Slack has a few per-second limit. Email providers have daily limits. Monitor logs for rate limit errors; add delays if needed.

7. **Error Handling** — If an action fails (email bounces, Slack channel doesn't exist), the webhook logs the error but continues. Check logs regularly. Fix invalid targets (bad email, deleted Slack channel).

8. **Data Mapping** — Variables like {pr_number}, {author}, {customer_email} must exist in the trigger data. Test with the test endpoint to verify all variables are available.

## Smart Strategy

1. **Start Simple** — Your first automation should have one trigger and one action. Verify it works before adding complexity.

2. **Automate High-Frequency Tasks** — Prioritize automations for events that happen often (every commit, every form submission, every new lead). These save the most time.

3. **Add Filters for Precision** — Don't automate everything. Add filters so only important events trigger. "PR merged to main" not just "PR merged." "New lead in enterprise segment" not just "new lead."

4. **Chain Multiple Actions** — One trigger can fire multiple actions. When a GitHub PR merges: Slack notification + update CRM + append to sheets log. More powerful.

5. **Use Threads for Related Alerts** — If a trigger fires multiple times (multiple commits), use Slack threads to group notifications. Cleaner conversation.

6. **Monitor Success Rate** — Periodically check execution logs. High failure rate? Investigate. Bad email? Fix it. Missing data field? Adjust the automation.

7. **Disable During Maintenance** — If you're making changes to source systems, disable automations temporarily. Prevents spamming your team with alerts about changes you're making.

8. **Document Your Automations** — Name them clearly: "GitHub PR merged → Slack deployments" is better than "webhook_1". Document in a wiki or doc what each automation does and why.
