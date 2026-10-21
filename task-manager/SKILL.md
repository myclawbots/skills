---
name: task_manager
description: Create and manage tasks, projects, and sprints. Track assignments, priorities, statuses, and deadlines across your connected project management tool.
author:
  name: MyClawBots
  url: https://myclawbots.ai
license: MIT
category: productivity
tags: [tasks, projects, sprints, deadlines]
suggested_template: project_manager
---

# Task Manager Skill

Create and manage tasks, projects, and sprints across your connected project management platform. Track work progress, assign tasks, manage priorities, and coordinate team efforts through a unified API.

> **Dashboard Connection Required**
> This skill works with any connected project management tool (Linear, Jira, Trello, Asana, etc.) via the MyClawBots proxy. The underlying platform is abstracted — the API remains consistent. Configure your tool connection and API key in the dashboard.

## Prerequisites

- Project management tool connected via dashboard (Linear, Jira, Asana, Trello, etc.)
- `${PROXY_URL}` and `$PROXY_API_KEY` environment variables configured
- Access to at least one project
- Appropriate task creation and management permissions

## Dependencies

| Dependency | Required? | Why |
|---|---|---|
| `${PROXY_URL}` and `$PROXY_API_KEY` | Yes | Required for proxy authentication |
| `slack` skill | No | Optional: for task notifications and updates |
| `google-workspace` skill | No | Optional: for calendar sync and scheduling |

**Pre-flight checks:**
- Confirm `${PROXY_URL}` and `$PROXY_API_KEY` environment variables are set
- If integrating with Slack: ensure `slack` skill is connected
- If syncing with Google Calendar: ensure `google-workspace` skill is available
- Verify that the connected project management tool is active in the dashboard

## How It Works

This skill provides a unified interface to project management operations regardless of the underlying tool. The proxy handles provider-specific API translation, so your agent code remains portable and tool-agnostic.

The skill supports:
- **Task Lifecycle**: Create, read, update, search, and delete tasks
- **Project Management**: Organize tasks across multiple projects
- **Sprint Planning**: Create and manage sprint cycles
- **Assignment & Tracking**: Assign tasks, set priorities, track status
- **Collaboration**: Add comments, track activity, view dashboards
- **Filtering & Search**: Find tasks by status, assignee, priority, and keywords

## Available Tools

### 1. List Tasks with Filters
Retrieve tasks with optional filtering by project, status, assignee, and other criteria.

```bash
curl -X GET "${PROXY_URL}/tasks?project_id=proj_123&status=open&assignee=user_456&limit=50" \
  -H "Authorization: Bearer $PROXY_API_KEY"
```

**Query Parameters:**
- `project_id`: Filter by project (optional)
- `status`: Filter by status like "open", "in_progress", "completed", "blocked" (optional)
- `assignee`: Filter by assignee user ID (optional)
- `priority`: Filter by priority "high", "medium", "low" (optional)
- `limit`: Max results, default 50 (optional)

**Returns:** Array of task objects with IDs, titles, status, priority, assignee, and due dates.

---

### 2. Create Task
Create a new task in a project with title, description, priority, and optional assignment.

```bash
curl -X POST "${PROXY_URL}/tasks" \
  -H "Authorization: Bearer $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Implement user authentication",
    "description": "Add OAuth2 integration for Google and GitHub login",
    "project_id": "proj_123",
    "assignee_id": "user_456",
    "priority": "high",
    "labels": ["backend", "security"],
    "due_date": "2026-04-15"
  }'
```

**Request Body:**
- `title`: Task title (required)
- `description`: Task description (required for clarity)
- `project_id`: Project ID (required)
- `assignee_id`: User ID to assign to (optional)
- `priority`: "high", "medium", or "low" (required)
- `labels`: Array of label strings (optional)
- `due_date`: ISO date string YYYY-MM-DD (optional)

**Returns:** Created task ID and full task object.

---

### 3. Get Task Details
Retrieve detailed information about a specific task including comments and activity history.

```bash
curl -X GET "${PROXY_URL}/tasks/task_123" \
  -H "Authorization: Bearer $PROXY_API_KEY"
```

**Parameters:**
- `task_id`: Task ID (required)

**Returns:** Task object with title, description, status, priority, assignee, labels, comments, activity timeline, and metadata.

---

### 4. Update Task
Modify task properties like status, priority, assignee, due date, and labels.

```bash
curl -X PUT "${PROXY_URL}/tasks/task_123" \
  -H "Authorization: Bearer $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "in_progress",
    "priority": "high",
    "assignee_id": "user_789",
    "due_date": "2026-04-20",
    "labels": ["backend", "security", "urgent"]
  }'
```

**Request Body:**
- Any of: `status`, `priority`, `assignee_id`, `due_date`, `labels`, `description`

**Returns:** Updated task object.

---

### 5. Delete Task
Remove a task from the project.

```bash
curl -X DELETE "${PROXY_URL}/tasks/task_123" \
  -H "Authorization: Bearer $PROXY_API_KEY"
```

**Parameters:**
- `task_id`: Task ID (required)

**Returns:** Confirmation of deletion.

---

### 6. Add Comment to Task
Post a comment on a task for discussion and collaboration.

```bash
curl -X POST "${PROXY_URL}/tasks/task_123/comments" \
  -H "Authorization: Bearer $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Started implementation. OAuth2 setup is complete, now integrating with frontend."
  }'
```

**Request Body:**
- `content`: Comment text (required)

**Returns:** Created comment with ID, author, timestamp, and content.

---

### 7. List Projects
Get all projects you have access to.

```bash
curl -X GET "${PROXY_URL}/projects" \
  -H "Authorization: Bearer $PROXY_API_KEY"
```

**Returns:** Array of project objects with IDs, names, descriptions, and member counts.

---

### 8. Create Project
Create a new project to organize related tasks.

```bash
curl -X POST "${PROXY_URL}/projects" \
  -H "Authorization: Bearer $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Mobile App Redesign",
    "description": "Modernize mobile app UI and improve performance"
  }'
```

**Request Body:**
- `name`: Project name (required)
- `description`: Project description (optional but recommended)

**Returns:** Created project ID and metadata.

---

### 9. List Project Members
Get all members and their roles in a project.

```bash
curl -X GET "${PROXY_URL}/projects/proj_123/members" \
  -H "Authorization: Bearer $PROXY_API_KEY"
```

**Parameters:**
- `project_id`: Project ID (required)

**Returns:** Array of team members with user IDs, names, emails, and roles.

---

### 10. List Sprints
Get all sprints in a project, including active, future, and completed sprints.

```bash
curl -X GET "${PROXY_URL}/sprints?project_id=proj_123" \
  -H "Authorization: Bearer $PROXY_API_KEY"
```

**Query Parameters:**
- `project_id`: Filter by project (optional)

**Returns:** Array of sprint objects with IDs, names, dates, and status.

---

### 11. Get Sprint Tasks
Retrieve all tasks in a specific sprint.

```bash
curl -X GET "${PROXY_URL}/sprints/sprint_456/tasks" \
  -H "Authorization: Bearer $PROXY_API_KEY"
```

**Parameters:**
- `sprint_id`: Sprint ID (required)

**Returns:** Array of tasks assigned to the sprint with status and priority.

---

### 12. Create Sprint
Create a new sprint for planning and organizing work cycles.

```bash
curl -X POST "${PROXY_URL}/sprints" \
  -H "Authorization: Bearer $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "proj_123",
    "name": "Q2 Sprint 1",
    "start_date": "2026-04-01",
    "end_date": "2026-04-14"
  }'
```

**Request Body:**
- `project_id`: Project ID (required)
- `name`: Sprint name (required)
- `start_date`: ISO date YYYY-MM-DD (required)
- `end_date`: ISO date YYYY-MM-DD (required)

**Returns:** Created sprint ID and metadata.

---

### 13. Search Tasks
Search for tasks across projects by keyword.

```bash
curl -X GET "${PROXY_URL}/tasks/search?q=authentication%20oauth&limit=25" \
  -H "Authorization: Bearer $PROXY_API_KEY"
```

**Query Parameters:**
- `q`: Search query (required)
- `limit`: Max results, default 50 (optional)

**Returns:** Array of matching tasks with relevance ordering.

---

### 14. Get Dashboard Summary
View a high-level summary of work status: overdue tasks, in-progress items, blockers, and completed work.

```bash
curl -X GET "${PROXY_URL}/tasks/dashboard" \
  -H "Authorization: Bearer $PROXY_API_KEY"
```

**Returns:** Object with counts and lists:
- `overdue`: Tasks past their due date
- `in_progress`: Currently active tasks
- `blocked`: Tasks with blockers set
- `completed_this_week`: Tasks finished in last 7 days
- `unassigned`: Tasks without assignees
- `high_priority`: High priority items

---

## Task Status Values

Standard status values supported across all providers:

| Status | Meaning |
|--------|---------|
| `open` | Not started |
| `in_progress` | Currently being worked on |
| `blocked` | Cannot proceed (waiting for something) |
| `in_review` | Under review before completion |
| `completed` | Finished and closed |
| `cancelled` | Abandoned without completion |

---

## Priority Levels

| Priority | Meaning |
|----------|---------|
| `low` | Can wait, nice to have |
| `medium` | Standard priority, schedule in sprint |
| `high` | Important, prioritize in sprint |
| `urgent` | Critical blocker, address immediately |

---

## Important Rules

1. **Check Existing Tasks First**: Always search for existing tasks before creating new ones. Use the search tool to avoid duplicates.

2. **Always Include Descriptions**: Provide clear, detailed descriptions when creating tasks. This helps team members understand scope and requirements.

3. **Use Appropriate Priorities**: Set realistic priorities. Over-using "high" reduces impact. Reserve "urgent" for real blockers.

4. **Assign Early**: Assign tasks to team members as soon as created when possible. Unassigned tasks often get lost.

5. **Track Blockers**: When a task is blocked, use the `blocked` status and add a comment explaining the blocker. Update when unblocked.

6. **Update Status Regularly**: Keep task status current. Move tasks to "in_progress" when work begins and "completed" when finished.

7. **Use Labels**: Add relevant labels (feature, bug, documentation, infrastructure, etc.) for better organization and filtering.

8. **Set Realistic Due Dates**: Only set due dates for time-sensitive work. Arbitrary dates create alert fatigue.

9. **Comment for Context**: Use comments to provide progress updates, ask questions, and document decisions.

10. **Review Before Sprinting**: Before sprint planning, review overdue and blocked tasks to identify impediments.
