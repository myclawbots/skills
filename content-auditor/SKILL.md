---
name: content_auditor
description: Scan websites for broken links, outdated statistics, SEO issues, and content quality problems. Generate audit reports with actionable recommendations.
author:
  name: MyClawBots
  url: https://myclawbots.ai
license: MIT
category: content
tags: [seo, audit, broken-links, website]
suggested_template: marketing_strategist
---

# Content Auditor

## Overview
Scan websites for broken links, outdated statistics, SEO issues, and content quality problems. Generate audit reports with actionable recommendations.

**You crawl and analyze the website yourself** using requests + BeautifulSoup for HTML parsing, curl for link checking, and web analysis techniques.

## Dependencies

| Dependency | Required? | Why |
|---|---|---|
| `google-workspace` skill | Optional | For saving audit reports to Drive and emailing via Gmail |
| `requests` library | Required | Web crawling and HTTP requests (`pip install requests`) |
| `beautifulsoup4` library | Required | HTML parsing and content extraction (`pip install beautifulsoup4`) |

**Pre-flight checks:**
- Verify `requests` and `beautifulsoup4` are installed; if not, run `pip install requests beautifulsoup4`
- Check Google Workspace connection for report delivery (optional)
- Verify target website is accessible before running audit

## Capabilities
- Crawl websites page-by-page
- Check for broken links (HTTP status codes)
- Find outdated statistics and dates
- Audit SEO basics (meta tags, heading hierarchy, keyword usage)
- Check accessibility (alt text, ARIA labels, color contrast)
- Identify thin content, duplicate titles
- Generate prioritized audit reports
- Track improvements over time

## Step-by-Step Workflow

### 1. Gather Target Website Info
- Domain to audit (http://example.com or https://example.com)
- Crawl depth: 1 (homepage only) / 2-3 (key pages) / 4-5 (comprehensive)
- Checks to run: broken links, outdated data, SEO, accessibility, images
- Page limit (default: 50 pages max per audit)

### 2. Install Dependencies

```bash
pip install requests beautifulsoup4 lxml
```

### 3. Create Web Crawler & Analyzer

Python script to crawl and audit:

```python
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
from datetime import datetime, timedelta
import re

class WebAuditor:
    def __init__(self, url, max_pages=50):
        self.domain = urlparse(url).netloc
        self.base_url = url.rstrip('/')
        self.visited = set()
        self.to_visit = [url]
        self.pages_scanned = 0
        self.max_pages = max_pages
        self.issues = []

    def crawl(self, depth=2):
        """Crawl website up to specified depth"""
        current_depth_urls = [self.to_visit[0]]

        for d in range(depth):
            next_depth_urls = []
            for url in current_depth_urls:
                if self.pages_scanned >= self.max_pages:
                    break
                if url in self.visited:
                    continue

                self.visited.add(url)
                self.audit_page(url)
                self.pages_scanned += 1

                # Find new links to visit
                try:
                    response = requests.get(url, timeout=5)
                    soup = BeautifulSoup(response.content, 'html.parser')
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        if not href.startswith('http'):
                            href = urljoin(url, href)
                        if self.domain in href and href not in self.visited:
                            next_depth_urls.append(href)
                except Exception as e:
                    self.issues.append({
                        'type': 'crawl_error',
                        'url': url,
                        'message': str(e),
                        'severity': 'medium'
                    })

            current_depth_urls = next_depth_urls[:10]  # Limit next batch

        return self.get_report()

    def audit_page(self, url):
        """Audit a single page"""
        try:
            response = requests.get(url, timeout=5)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Check HTTP status
            if response.status_code != 200:
                self.issues.append({
                    'type': 'http_error',
                    'url': url,
                    'status_code': response.status_code,
                    'severity': 'critical' if response.status_code >= 500 else 'high'
                })

            # Check broken links
            self.check_broken_links(soup, url)

            # Check SEO
            self.check_seo(soup, url)

            # Check accessibility
            self.check_accessibility(soup, url)

            # Check for outdated stats
            self.check_outdated_content(soup, url)

        except requests.Timeout:
            self.issues.append({
                'type': 'timeout',
                'url': url,
                'severity': 'medium'
            })
        except Exception as e:
            self.issues.append({
                'type': 'audit_error',
                'url': url,
                'message': str(e),
                'severity': 'low'
            })

    def check_broken_links(self, soup, page_url):
        """Check for broken links on the page"""
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.startswith('http'):
                # Check external links with HEAD request
                try:
                    response = requests.head(href, timeout=3, allow_redirects=True)
                    if response.status_code >= 400:
                        self.issues.append({
                            'type': 'broken_link',
                            'source_page': page_url,
                            'broken_url': href,
                            'status_code': response.status_code,
                            'severity': 'high'
                        })
                except:
                    pass  # Skip if check fails

    def check_seo(self, soup, url):
        """Check SEO best practices"""
        # Check title
        title = soup.find('title')
        if not title or len(title.text) < 10:
            self.issues.append({
                'type': 'seo_missing_title',
                'url': url,
                'message': 'Title tag missing or too short',
                'severity': 'high'
            })

        # Check meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if not meta_desc or not meta_desc.get('content') or len(meta_desc.get('content')) < 50:
            self.issues.append({
                'type': 'seo_missing_description',
                'url': url,
                'message': 'Meta description missing or too short',
                'severity': 'high'
            })

        # Check h1 tags
        h1_count = len(soup.find_all('h1'))
        if h1_count == 0:
            self.issues.append({
                'type': 'seo_missing_h1',
                'url': url,
                'message': 'No H1 tag found',
                'severity': 'high'
            })
        elif h1_count > 1:
            self.issues.append({
                'type': 'seo_multiple_h1',
                'url': url,
                'message': f'{h1_count} H1 tags found (should be 1)',
                'severity': 'medium'
            })

        # Check heading hierarchy
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        if len(headings) < 2:
            self.issues.append({
                'type': 'seo_thin_content',
                'url': url,
                'message': 'Few headings; content may be thin',
                'severity': 'medium'
            })

    def check_accessibility(self, soup, url):
        """Check accessibility issues"""
        # Check for images without alt text
        for img in soup.find_all('img'):
            if not img.get('alt') or img.get('alt').strip() == '':
                self.issues.append({
                    'type': 'accessibility_missing_alt',
                    'url': url,
                    'image': img.get('src', 'unknown'),
                    'severity': 'medium'
                })

        # Check for links without anchor text
        for link in soup.find_all('a'):
            if not link.text.strip():
                self.issues.append({
                    'type': 'accessibility_empty_link',
                    'url': url,
                    'href': link.get('href', 'unknown'),
                    'severity': 'low'
                })

    def check_outdated_content(self, soup, url):
        """Check for outdated statistics and dates"""
        text_content = soup.get_text()

        # Look for old years (2020, 2021, etc.)
        current_year = datetime.now().year
        old_years = ['2019', '2020', '2021', '2022']
        for year in old_years:
            if f'as of {year}' in text_content.lower() or f'{year} report' in text_content.lower():
                self.issues.append({
                    'type': 'outdated_content',
                    'url': url,
                    'message': f'Reference to {year} found; may be outdated',
                    'severity': 'medium'
                })

        # Look for "last updated" dates older than 6 months
        date_pattern = r'(last updated|updated on|modified|posted)\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})'
        matches = re.findall(date_pattern, text_content, re.IGNORECASE)
        for match in matches:
            # Simple check: if it says "2024" or older in 2026
            if '2024' in match[1] or '2023' in match[1]:
                self.issues.append({
                    'type': 'potentially_outdated',
                    'url': url,
                    'date_found': match[1],
                    'severity': 'low'
                })

    def get_report(self):
        """Generate audit report"""
        # Prioritize by severity
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        sorted_issues = sorted(
            self.issues,
            key=lambda x: severity_order.get(x.get('severity', 'low'), 4)
        )

        # Count by type
        critical_count = len([i for i in sorted_issues if i.get('severity') == 'critical'])
        high_count = len([i for i in sorted_issues if i.get('severity') == 'high'])
        medium_count = len([i for i in sorted_issues if i.get('severity') == 'medium'])
        low_count = len([i for i in sorted_issues if i.get('severity') == 'low'])

        report = {
            'url': self.base_url,
            'scanned_at': datetime.now().isoformat(),
            'pages_scanned': self.pages_scanned,
            'total_issues': len(sorted_issues),
            'summary': {
                'critical': critical_count,
                'high': high_count,
                'medium': medium_count,
                'low': low_count
            },
            'issues': sorted_issues
        }

        return report

# Run audit
if __name__ == '__main__':
    import json

    auditor = WebAuditor('https://example.com')
    report = auditor.crawl(depth=2)

    # Save report
    with open('audit_report.json', 'w') as f:
        json.dump(report, f, indent=2)

    print(f'✓ Audit complete')
    print(f'Pages scanned: {report["pages_scanned"]}')
    print(f'Total issues: {report["total_issues"]}')
    print(f'  Critical: {report["summary"]["critical"]}')
    print(f'  High: {report["summary"]["high"]}')
    print(f'  Medium: {report["summary"]["medium"]}')
    print(f'  Low: {report["summary"]["low"]}')
    print(f'Report saved to: audit_report.json')
```

Run it:
```bash
python web_auditor.py
```

### 4. Generate Markdown Report

Convert JSON to readable markdown:

```python
import json

with open('audit_report.json', 'r') as f:
    report = json.load(f)

# Create markdown
md = f"""# Website Audit Report

**URL:** {report['url']}
**Scanned:** {report['scanned_at']}
**Pages Scanned:** {report['pages_scanned']}

## Summary

- **Critical Issues:** {report['summary']['critical']}
- **High Priority:** {report['summary']['high']}
- **Medium Priority:** {report['summary']['medium']}
- **Low Priority:** {report['summary']['low']}

## Issues by Priority

"""

# Group by severity
for severity in ['critical', 'high', 'medium', 'low']:
    issues = [i for i in report['issues'] if i.get('severity') == severity]
    if issues:
        md += f"\n### {severity.upper()} Issues\n\n"
        for issue in issues[:10]:  # Show top 10
            md += f"- **{issue.get('type', 'unknown')}** on {issue.get('url', 'unknown')}\n"
            md += f"  {issue.get('message', '')}\n\n"

# Save
with open('audit_report.md', 'w') as f:
    f.write(md)

print('✓ Markdown report saved: audit_report.md')
```

### 5. Save Report to Google Drive

```bash
gws drive +upload --file audit_report.md --folder "[folder_id]"
gws drive +upload --file audit_report.json --folder "[folder_id]"
```

### 6. Email Report (Optional)

```bash
gws gmail +send \
  --to team@company.com \
  --subject "Website Audit Report: example.com" \
  --body "See attached audit report. Critical issues: [count]. See Google Drive for full details."
```

## Issue Types & Fixes

| Issue Type | Severity | Fix |
|---|---|---|
| HTTP 404/500 | Critical | Fix links or remove dead pages |
| Missing title | High | Add unique title tag (50-60 chars) |
| Missing meta description | High | Add 150-160 char description |
| No H1 | High | Add single H1 with main keyword |
| Broken external links | High | Update or remove broken URLs |
| Missing alt text | Medium | Add descriptive alt text to images |
| Thin content | Medium | Expand page to 500+ words minimum |
| Outdated stats | Medium | Update with current data + date |
| Multiple H1s | Medium | Keep only one H1 per page |
| Empty links | Low | Add descriptive anchor text |

## Cost

- **requests + BeautifulSoup:** Free (open source)
- **Google Drive storage:** Free (15GB)

**Total cost per audit:** $0

## Pro Tips

- **Start small:** Audit homepage first (depth=1), then expand
- **Prioritize fixes:** Focus on critical + high first (broken links, 404s, missing SEO)
- **Set realistic goals:** 500 pages takes 30+ min; aim for 50 pages per audit
- **Schedule recurring audits:** Run monthly to catch new issues
- **Track improvements:** Compare reports to show progress
- **Fix one issue type at a time:** All broken links → then SEO → then accessibility
- **Validate fixes:** After fixing, re-audit to confirm improvements
