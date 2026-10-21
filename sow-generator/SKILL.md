---
name: sow_generator
description: Generate detailed Scope of Work documents, proposals, invoices, and contracts. Export as DOCX/PDF and save to Google Drive.
author:
  name: MyClawBots
  url: https://myclawbots.ai
license: MIT
category: productivity
tags: [proposals, contracts, invoices, docx]
suggested_template: legal_assistant
---

# SOW Generator

## Overview
Generate detailed Scope of Work documents, proposals, invoices, and contracts. Export as DOCX/PDF and save to Google Drive.

**You write the documents yourself** using python-docx library or by crafting markdown that converts to DOCX.

## Dependencies

| Dependency | Required? | Why |
|---|---|---|
| `google-workspace` skill | Optional | For saving to Google Drive and creating Google Docs |
| `python-docx` library | Required | DOCX output generation (`pip install python-docx`) |
| `pandoc` | Optional | Markdown → PDF conversion |

**Pre-flight checks:**
- Verify `python-docx` is installed; if not, run `pip install python-docx`
- Check Google Workspace connection for Drive saving (optional)
- If PDF conversion needed, verify `pandoc` is available on system

## Capabilities
- Generate SOWs with all standard sections
- Create proposals, invoices, and contracts from SOWs
- Output DOCX and PDF formats
- Save to Google Drive
- Support for any industry or project type
- Professional formatting and business language

## Step-by-Step Workflow

### 1. Gather Project Requirements
- Client name and contact
- Project name and description
- Deliverables (specific, measurable)
- Timeline (start date, end date, phases)
- Budget or budget range
- Key dates/milestones
- Assumptions and risks
- Payment terms

### 2. Create SOW Structure

Standard SOW sections:
1. **Executive Summary** (1 paragraph: what, why, when, cost)
2. **Objectives** (2-3 sentences: business goals)
3. **Scope of Work** (what IS included, 2-3 paragraphs)
4. **Out of Scope** (what is NOT included, explicit disclaimers)
5. **Deliverables** (numbered list with descriptions)
6. **Timeline & Milestones** (phases, key dates)
7. **Budget** (cost breakdown by phase or deliverable)
8. **Acceptance Criteria** (how we'll know it's done)
9. **Assumptions** (client dependencies, resource availability)
10. **Risks & Mitigation** (potential issues and solutions)
11. **Change Management** (how to handle scope changes)
12. **Payment Terms** (invoice schedule, Net 30, etc.)
13. **Signatures** (client and service provider)

### 3. Generate DOCX with Python

Install python-docx:
```bash
pip install python-docx
```

Write a Python script:
```python
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT

# Create document
doc = Document()

# Add title
title = doc.add_heading('SCOPE OF WORK', 0)
title.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

subtitle = doc.add_paragraph()
subtitle_format = subtitle.add_run('E-Commerce Platform Redesign')
subtitle_format.bold = True
subtitle_format.font.size = Pt(14)
subtitle.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

doc.add_paragraph()

# Add date
date_para = doc.add_paragraph()
date_para.add_run('Prepared for: ').bold = True
date_para.add_run('TechRetail Inc.')
date_para = doc.add_paragraph()
date_para.add_run('Date: ').bold = True
date_para.add_run('March 29, 2026')

doc.add_paragraph()

# Executive Summary
doc.add_heading('1. Executive Summary', level=1)
doc.add_paragraph(
    'TechRetail Inc. seeks to modernize their e-commerce platform with a complete '
    'redesign focusing on mobile responsiveness, improved payment processing, and '
    'enhanced performance. This 16-week engagement will deliver a state-of-the-art '
    'platform improving conversion rates by an estimated 25%. Budget range: $50,000-$75,000.'
)

# Objectives
doc.add_heading('2. Objectives', level=1)
objectives = [
    'Redesign user interface for modern, intuitive shopping experience',
    'Improve mobile responsiveness and page load times',
    'Integrate advanced payment processing and security measures',
    'Increase conversion rate and reduce cart abandonment'
]
for obj in objectives:
    doc.add_paragraph(obj, style='List Bullet')

# Scope of Work
doc.add_heading('3. Scope of Work', level=1)
doc.add_paragraph(
    'This engagement includes a complete redesign of the e-commerce platform, '
    'including frontend development, backend optimization, payment integration, '
    'and comprehensive testing. Work will be delivered in 4 phases over 16 weeks.'
)

# Out of Scope
doc.add_heading('4. Out of Scope', level=1)
doc.add_paragraph(
    'The following items are explicitly NOT included in this scope and may be '
    'addressed in a separate engagement:'
)
out_of_scope = [
    'Data migration from legacy systems (will be scoped separately)',
    'Third-party marketplace integrations (e.g., Amazon, eBay)',
    'Mobile app development (web-only)',
    'Ongoing support beyond 2-week post-launch period'
]
for item in out_of_scope:
    doc.add_paragraph(item, style='List Bullet')

# Deliverables
doc.add_heading('5. Deliverables', level=1)
deliverables = [
    ('Responsive UI/UX Design',
     'Pixel-perfect designs for desktop, tablet, and mobile. Includes wireframes, '
     'design system, and component library.'),
    ('Frontend Development',
     'React-based frontend with state management, responsive CSS, and accessibility compliance.'),
    ('Backend API Optimization',
     'Refactored REST API with performance improvements, caching, and load testing.'),
    ('Payment Gateway Integration',
     'Stripe integration with PCI compliance, secure checkout flow, and error handling.'),
    ('Admin Dashboard',
     'Product management, order tracking, analytics, and reporting tools.'),
    ('Testing & QA Report',
     'Comprehensive test results including functional, performance, and security testing.'),
    ('Deployment & Training',
     'Production deployment, staff training, and 2-week post-launch support.')
]
for title, description in deliverables:
    p = doc.add_paragraph(style='List Bullet')
    p.add_run(title + ': ').bold = True
    p.add_run(description)

# Timeline
doc.add_heading('6. Timeline & Milestones', level=1)
doc.add_paragraph('Project Duration: 16 weeks (April 1 - July 15, 2026)')
doc.add_paragraph()
timeline = [
    ('Phase 1: Discovery & Design (Weeks 1-4)', 'Requirements, design mockups, client approval'),
    ('Phase 2: Frontend Development (Weeks 5-10)', 'React development, testing, integration'),
    ('Phase 3: Backend & Integration (Weeks 11-14)', 'API optimization, payment integration, testing'),
    ('Phase 4: Launch & Support (Weeks 15-16)', 'Final testing, deployment, staff training, support')
]
for phase, activities in timeline:
    p = doc.add_paragraph(style='List Bullet')
    p.add_run(phase + ': ').bold = True
    p.add_run(activities)

# Budget
doc.add_heading('7. Budget', level=1)
budget_table = doc.add_table(rows=6, cols=2)
budget_table.style = 'Light Grid Accent 1'
header_cells = budget_table.rows[0].cells
header_cells[0].text = 'Phase'
header_cells[1].text = 'Cost'
data = [
    ('Phase 1: Design & Planning', '$10,000'),
    ('Phase 2: Frontend Development', '$20,000'),
    ('Phase 3: Backend & Integration', '$25,000'),
    ('Phase 4: Launch & Support', '$15,000-$20,000'),
    ('Total', '$50,000-$75,000')
]
for i, (phase, cost) in enumerate(data, 1):
    row_cells = budget_table.rows[i].cells
    row_cells[0].text = phase
    row_cells[1].text = cost

# Acceptance Criteria
doc.add_heading('8. Acceptance Criteria', level=1)
doc.add_paragraph('Project will be considered complete when:')
criteria = [
    'All deliverables have been reviewed and approved by client stakeholder',
    'Site loads in under 2 seconds on standard broadband connection',
    'Mobile responsiveness verified on iOS and Android devices',
    'Payment gateway processes transactions securely with 100% uptime during testing',
    'All critical bugs identified during UAT have been resolved'
]
for criterion in criteria:
    doc.add_paragraph(criterion, style='List Bullet')

# Assumptions
doc.add_heading('9. Assumptions', level=1)
assumptions = [
    'Client will designate a primary stakeholder for decision-making and approvals',
    'Client will provide necessary assets (logo, existing content, product images)',
    'Client will have test environment ready by Week 2 for integration testing',
    'Key client decisions will not be delayed beyond the documented timeline'
]
for assumption in assumptions:
    doc.add_paragraph(assumption, style='List Bullet')

# Risks
doc.add_heading('10. Risks & Mitigation', level=1)
risks = [
    ('Scope Creep', 'Detailed change management process; changes logged and evaluated separately'),
    ('Resource Availability', 'Confirm team availability upfront; escalate conflicts immediately'),
    ('Technical Challenges', 'Allocate 10% contingency time; identify risks early in design phase'),
    ('Third-Party Delays', 'Secure API credentials and documentation before development begins')
]
for risk_title, mitigation in risks:
    p = doc.add_paragraph(style='List Bullet')
    p.add_run(risk_title + ': ').bold = True
    p.add_run(mitigation)

# Change Management
doc.add_heading('11. Change Management', level=1)
doc.add_paragraph(
    'Scope changes requested after Phase 1 completion require formal change '
    'request documentation including:\n'
)
changes = [
    'Description of requested change',
    'Business justification and impact',
    'Estimated effort and cost impact',
    'Timeline impact (if any)',
    'Client approval signature'
]
for change in changes:
    doc.add_paragraph(change, style='List Bullet')

doc.add_paragraph(
    'Changes will be evaluated and either incorporated into the current phase '
    '(if minimal impact) or scheduled for a separate engagement.'
)

# Payment Terms
doc.add_heading('12. Payment Terms', level=1)
doc.add_paragraph('Payment Schedule:')
payments = [
    'Upon SOW signature: 25% ($12,500-$18,750)',
    'Upon Phase 1 completion: 25% ($12,500-$18,750)',
    'Upon Phase 3 completion: 25% ($12,500-$18,750)',
    'Upon deployment & handoff: 25% ($12,500-$18,750)'
]
for payment in payments:
    doc.add_paragraph(payment, style='List Bullet')
doc.add_paragraph('All invoices are due within Net 30 days of invoice date.')

# Signatures
doc.add_paragraph()
doc.add_paragraph()
sig_table = doc.add_table(rows=3, cols=2)
sig_cells = sig_table.rows[0].cells
sig_cells[0].text = 'Client Signature'
sig_cells[1].text = 'Date'
sig_cells = sig_table.rows[1].cells
sig_cells[0].text = 'Service Provider'
sig_cells[1].text = 'Date'

# Save
doc.save('SOW_TechRetail.docx')
print('✓ SOW generated: SOW_TechRetail.docx')
```

Run it:
```bash
python generate_sow.py
```

### 4. Convert to PDF (Optional)

If pandoc is available:
```bash
pip install python-pptx
pandoc SOW_TechRetail.docx -o SOW_TechRetail.pdf
```

### 5. Save to Google Drive

Use google-workspace skill:
```bash
gws drive +upload --file SOW_TechRetail.docx --folder "[folder_id]"
```

### 6. Create Related Documents

Once SOW is approved, generate companion documents:

**Proposal** (shorter, highlights value):
- Executive Summary (2-3 paragraphs)
- Problem & Opportunity
- Proposed Solution
- Timeline & Phases
- Investment & ROI
- Next Steps

**Invoice** (for billing):
- Client name, address, PO number
- Line items (phase name, deliverables, amount)
- Payment terms
- Due date
- Wire transfer / payment instructions

**Service Contract** (legal binding):
- All SOW content
- Payment terms + penalties
- IP ownership clause
- Confidentiality
- Liability limits
- Dispute resolution
- Termination clause

## Cost

- **python-docx library:** Free (open source)
- **Pandoc (for PDF conversion):** Free
- **Google Drive storage:** Free (15GB)

**Total cost per document:** $0

## Pro Tips

- **Clarity over legalese:** Use plain English; avoid jargon or legal terms unless necessary
- **Be specific:** "Responsive design for mobile, tablet, desktop" beats "responsive design"
- **Build in contingency:** Add 15-20% buffer to timeline for unexpected issues
- **Out-of-scope is critical:** Explicitly list what you will NOT do to prevent scope creep
- **Acceptance criteria prevent disputes:** Define measurable success criteria upfront
- **Assumptions protect everyone:** List client dependencies and required decisions
- **Change management saves money:** Document how scope changes will be handled
- **Get signatures:** Use DocuSign or print + scan for binding agreement
