---
name: content_writer
description: Research and write SEO-optimized blog posts, articles, newsletters, and marketing copy. Repurpose content across platforms. Publish to Google Docs or send via Gmail.
author:
  name: MyClawBots
  url: https://myclawbots.ai
license: MIT
category: content
tags: [writing, seo, blog, newsletter]
suggested_template: content_creator
---

# Content Writer

## Overview
Research and write SEO-optimized blog posts, articles, newsletters, and marketing copy. Repurpose content across platforms. Publish to Google Docs or send via Gmail.

**You are the writer.** This skill guides your best practices for research, structure, and publishing.

## Dependencies

| Dependency | Required? | Why |
|---|---|---|
| `google-workspace` skill | Optional | For publishing to Google Docs and sending via Gmail |
| AI provider | No | The agent IS the writer (uses its own model) |

**Pre-flight checks:**
- If publishing/sending via Google Workspace, verify `$GWS_GOOGLE_ACCOUNT` environment variable is set
- If not set, content can still be written and saved locally as markdown/HTML

## Capabilities
- Write original, well-researched content on any topic
- Optimize for SEO: keyword research, heading hierarchy, meta descriptions
- Google EEAT compliance (Experience, Expertise, Authority, Trust)
- Adapt content across formats: blog → LinkedIn post → Twitter thread → email newsletter → Instagram captions
- Publish: save to Google Docs, email via Gmail, or save as markdown/HTML

## Step-by-Step Workflow

### 1. Research Phase
- Search the web for current information on the topic (use your web search capability)
- Identify top-ranking competitors for the target keyword
- Extract key statistics, case studies, and expert opinions
- Note the most common misconceptions (helps establish EEAT)

### 2. Content Structure (SEO-First)
- **Title/H1:** Include primary keyword, under 60 characters, compelling
- **Meta Description:** 150–160 characters, summarizes content and keyword
- **Introduction:** Hook reader, state the problem, hint at solution
- **H2 Sections:** Logical flow, each answers a user question
- **Body Paragraphs:** 2-4 sentences, active voice, clear value
- **Keyword Density:** 1-2% for primary keyword, naturally distributed
- **Internal Links:** Link to related content (if using within an organization)
- **Conclusion:** Summarize key takeaways, call-to-action

### 3. Google EEAT Standards
- **Experience:** Demonstrate hands-on knowledge; use case studies and real examples
- **Expertise:** Cite sources, reference industry standards, show credentials
- **Authority:** Link to authority sources (government, academic, industry leaders)
- **Trust:** Be transparent about limitations, avoid exaggeration, cite your sources

### 4. Writing Best Practices
- Use short sentences (12-15 words avg) and short paragraphs (2-3 sentences)
- Break text with subheadings every 150-200 words
- Use bullet points and numbered lists for scannability
- Include data visualization descriptions (if charts/tables apply)
- Write in second person ("you") for newsletters and blog posts
- Avoid jargon unless it's industry-standard; define new terms

### 5. Output Formats

#### Blog Post / Long-Form Article (2000-3000 words)
Write the full article in well-structured markdown:
```markdown
# [Title - H1]

[Meta description context]

## Introduction
[Hook + problem statement]

## H2 Subheading
Content...

## H2 Subheading
Content...

## Conclusion
[Summary + CTA]
```

#### Newsletter / Email (400-600 words)
- Shorter paragraphs (1-2 sentences)
- Clear subject line (under 50 chars)
- 1-2 main ideas, not overwhelming detail
- Strong CTA at end (link, button text)

#### Social Media Adaptations
- **LinkedIn:** Professional tone, 1-2 paragraphs, trending hashtags
- **Twitter/X:** Hook + 1 insight, under 280 chars or thread of 3-5 tweets
- **Instagram Caption:** 100-150 chars, 3-5 relevant hashtags, emoji sparingly
- **TikTok Script:** Hook in first 3 seconds, conversational, story-driven

### 6. Publishing

#### To Google Docs (requires google-workspace skill)
```bash
# Create a new Google Doc with markdown content
gws docs +create --title "Blog Post Title" --content "[markdown content]"
```
Output: shareable Google Doc link

#### Via Email (requires google-workspace skill)
```bash
# Send as email via Gmail
gws gmail +send \
  --to recipient@example.com \
  --subject "Article: [Title]" \
  --body "[formatted content]"
```

#### Save Locally
Write to markdown or HTML file:
```bash
cat > article.md << 'EOF'
# [Your content here]
EOF
```

## Repurposing Workflow
1. Write the full blog post first (authoritative, detailed)
2. From the blog post:
   - Extract 3-5 key insights for LinkedIn
   - Create a Twitter thread from the main points
   - Write email newsletter highlighting the top takeaway
   - Create Instagram carousel captions from sections
   - Adapt tone for each platform (formal → casual)
3. Publish each version on its native platform

## Cost
**Free.** Uses the model already running. No additional API costs.

## Pro Tips
- Research phase typically adds 20% to writing time but significantly improves EEAT
- Use your knowledge cutoff strategically; web search is good for recent events, data, trends
- Always fact-check statistics before publishing
- Re-reading aloud catches flow issues and clunky phrasing
- Schedule content publishing during peak audience times (vary by platform)
