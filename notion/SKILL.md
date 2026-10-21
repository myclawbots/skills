---
name: notion
description: Create and manage Notion pages, databases, and wikis. Search content, update properties, and organize knowledge bases.
author:
  name: MyClawBots
  url: https://myclawbots.ai
license: MIT
category: productivity
tags: [notion, wiki, databases, knowledge-base]
suggested_template: project_manager
---

# Notion Skill

Create and manage Notion workspaces, pages, databases, and content blocks. Search your knowledge base, organize wikis, and maintain structured databases with properties and filters.

> **Dashboard Connection Required**
> This skill requires Notion to be connected via the MyClawBots dashboard. You'll need a Notion integration token configured in the proxy. All requests use `${PROXY_URL}` and `$PROXY_API_KEY` from your environment.

## Prerequisites

- Notion workspace access (free or paid plan)
- Notion integration created and connected via dashboard
- `${PROXY_URL}` and `$PROXY_API_KEY` environment variables configured
- Appropriate page/database permissions in Notion

## Dependencies

| Dependency | Required? | Why |
|---|---|---|
| Notion workspace connected via dashboard | Yes | Enables access to Notion pages and databases |
| `${PROXY_URL}` and `$PROXY_API_KEY` | Yes | Required for proxy authentication |

**Pre-flight checks:**
- Verify Notion workspace is configured in the MyClawBots dashboard with an integration token
- Confirm `${PROXY_URL}` and `$PROXY_API_KEY` environment variables are set
- Ensure appropriate permissions are granted to the Notion integration for target pages/databases

## How It Works

This skill provides agent-friendly access to Notion's core operations through a REST API proxy. Authentication is handled automatically — you simply use `curl` with the proxy endpoint and API key.

The skill supports:
- **Search**: Find pages and databases by keyword
- **Page Management**: Create, read, update, and archive pages
- **Content Blocks**: Work with text, headings, lists, code, tables, and more
- **Database Operations**: Query databases, add/update rows, manage properties
- **Organization**: Use icons and covers to structure your workspace

## Available Tools

### 1. Search Pages and Databases
Search across your Notion workspace for pages and databases by keyword.

```bash
curl -X GET "${PROXY_URL}/notion/search?query=meeting%20notes&limit=10" \
  -H "Authorization: Bearer $PROXY_API_KEY"
```

**Parameters:**
- `query`: Search term (required)
- `limit`: Maximum results, default 10 (optional)

**Returns:** List of matching pages and databases with IDs, titles, and types.

---

### 2. Get Page Content
Retrieve the content blocks from a specific page.

```bash
curl -X GET "${PROXY_URL}/notion/pages/page_id" \
  -H "Authorization: Bearer $PROXY_API_KEY"
```

**Parameters:**
- `page_id`: Notion page ID (required)

**Returns:** Page metadata (title, icon, cover) and all content blocks with types and properties.

---

### 3. Create Page
Create a new page in Notion with optional content blocks, icon, and cover image.

```bash
curl -X POST "${PROXY_URL}/notion/pages" \
  -H "Authorization: Bearer $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "parent_id": "workspace_id_or_page_id",
    "title": "Project Kickoff Meeting",
    "icon": "🚀",
    "cover": "https://example.com/cover.jpg",
    "content_blocks": [
      {
        "type": "heading_1",
        "text": "Project Overview"
      },
      {
        "type": "paragraph",
        "text": "This project aims to..."
      },
      {
        "type": "bulleted_list_item",
        "text": "Goal 1"
      },
      {
        "type": "bulleted_list_item",
        "text": "Goal 2"
      }
    ]
  }'
```

**Request Body:**
- `parent_id`: Notion page or workspace ID (required)
- `title`: Page title (required)
- `content_blocks`: Array of block objects (optional)
- `icon`: Emoji or URL (optional)
- `cover`: Cover image URL (optional)

**Returns:** Created page ID and metadata.

---

### 4. Update Page
Modify page properties, title, icon, cover, and content blocks.

```bash
curl -X PUT "${PROXY_URL}/notion/pages/page_id" \
  -H "Authorization: Bearer $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Title",
    "icon": "📝",
    "properties": {
      "Status": "In Progress",
      "Owner": "John Doe"
    },
    "content_blocks": [
      {
        "type": "paragraph",
        "text": "Updated content"
      }
    ]
  }'
```

**Request Body:**
- Any combination of: `title`, `icon`, `properties`, `content_blocks`

**Returns:** Updated page metadata.

---

### 5. Archive Page
Archive (soft-delete) a page. Use before destructive operations.

```bash
curl -X DELETE "${PROXY_URL}/notion/pages/page_id" \
  -H "Authorization: Bearer $PROXY_API_KEY"
```

**Parameters:**
- `page_id`: Notion page ID (required)

**Returns:** Confirmation of archival.

---

### 6. Query Database
Retrieve rows from a database with optional filtering, sorting, and limits.

```bash
curl -X GET "${PROXY_URL}/notion/databases/database_id/query" \
  -H "Authorization: Bearer $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "filter": {
      "property": "Status",
      "select": {
        "equals": "Open"
      }
    },
    "sorts": [
      {
        "property": "Due Date",
        "direction": "ascending"
      }
    ],
    "limit": 25
  }'
```

**Request Body:**
- `filter`: Property filter object (optional)
- `sorts`: Array of sort specs with property and direction (optional)
- `limit`: Max rows to return, default 100 (optional)

**Returns:** Array of database rows with all properties.

---

### 7. Add Database Row
Insert a new row into a Notion database with property values.

```bash
curl -X POST "${PROXY_URL}/notion/databases/database_id/rows" \
  -H "Authorization: Bearer $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "properties": {
      "Name": "Q2 Planning",
      "Status": "In Progress",
      "Owner": "Sarah Chen",
      "Due Date": "2026-06-30",
      "Priority": "High"
    }
  }'
```

**Request Body:**
- `properties`: Object with property names as keys and values (required)

**Returns:** Created row with ID and properties.

---

### 8. Update Database Row
Modify an existing database row's properties.

```bash
curl -X PUT "${PROXY_URL}/notion/databases/database_id/rows/row_id" \
  -H "Authorization: Bearer $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "properties": {
      "Status": "Completed",
      "Owner": "Alex Park"
    }
  }'
```

**Request Body:**
- `properties`: Object with properties to update (required)

**Returns:** Updated row metadata.

---

### 9. List Databases
Get all databases in the connected Notion workspace.

```bash
curl -X GET "${PROXY_URL}/notion/databases" \
  -H "Authorization: Bearer $PROXY_API_KEY"
```

**Returns:** Array of database IDs, titles, and property schemas.

---

### 10. Append Blocks to Page
Add content blocks to the end of an existing page.

```bash
curl -X POST "${PROXY_URL}/notion/blocks/page_id/children" \
  -H "Authorization: Bearer $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "blocks": [
      {
        "type": "heading_2",
        "text": "New Section"
      },
      {
        "type": "paragraph",
        "text": "Content here"
      },
      {
        "type": "code",
        "text": "const x = 42;",
        "language": "javascript"
      },
      {
        "type": "quote",
        "text": "Great things ahead"
      }
    ]
  }'
```

**Request Body:**
- `blocks`: Array of block objects (required)

**Returns:** Created block IDs and positions.

---

## Content Block Types

Use these `type` values when creating or updating blocks:

| Type | Description | Extra Fields |
|------|-------------|--------------|
| `paragraph` | Regular text paragraph | `text` |
| `heading_1` | Top-level heading (H1) | `text` |
| `heading_2` | Second-level heading (H2) | `text` |
| `heading_3` | Third-level heading (H3) | `text` |
| `bulleted_list_item` | Bullet point | `text` |
| `numbered_list_item` | Numbered item | `text` |
| `to_do` | Checkbox task | `text`, `checked` (boolean) |
| `toggle` | Expandable toggle | `text`, `children` (block array) |
| `code` | Code block | `text`, `language` |
| `quote` | Block quote | `text` |
| `callout` | Highlighted callout | `text`, `icon`, `color` |
| `divider` | Horizontal line | (none) |
| `table` | Data table | `cells` (array of arrays) |

---

## Important Rules

1. **Search Before Creating**: Always search for existing pages/databases before creating duplicates. Use the search tool first.

2. **Use Appropriate Block Types**: Choose the right block type for your content (headings for structure, lists for enumerations, code for code samples).

3. **Confirm Before Archiving**: Always confirm archival of pages. Archived pages can be restored but it's disruptive.

4. **Structure with Headings**: Use `heading_1`, `heading_2`, and `heading_3` to organize page content logically.

5. **Property Consistency**: When updating database rows, use property names that exactly match the database schema.

6. **Icon and Cover Use**: Use icons and covers to make pages visually distinct and easier to scan in workspace.

7. **Batch Updates**: Group related block updates in a single append operation when possible.

8. **Archive Over Delete**: Use archival rather than permanent deletion to maintain workspace history.
