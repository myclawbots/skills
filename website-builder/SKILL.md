---
name: website_builder
description: Generate responsive websites from specifications. Write HTML/CSS/JS directly, preview, and save to Google Drive or deploy.
author:
  name: MyClawBots
  url: https://myclawbots.ai
license: MIT
category: content
tags: [website, html, landing-page, deploy]
suggested_template: content_creator
---

# Website Builder

## Overview
Generate responsive websites from specifications. Write HTML/CSS/JS directly, preview, and save to Google Drive or deploy.

**You write the website code yourself** using modern HTML, CSS (flexbox/grid), and JavaScript. This skill teaches structure and patterns.

## Dependencies

| Dependency | Required? | Why |
|---|---|---|
| `google-workspace` skill | Optional | For saving files to Google Drive |
| External libraries | No | Agent writes HTML/CSS/JS directly; no libraries required |
| Vercel/Netlify CLI | Optional | For deployment (if user wants to deploy) |

**Pre-flight checks:**
- Verify Google Workspace for Drive saving (optional)
- If user wants deployment, check availability of Vercel or Netlify CLI tools
- Local preview: Python 3 simple HTTP server is built-in (no install needed)

## Capabilities
- Create responsive single-page or multi-page websites
- Use modern CSS (Tailwind via CDN, custom CSS)
- Add interactive elements (forms, modals, sliders)
- SEO-ready with meta tags and structured data
- Mobile-first design approach
- Deploy to Vercel, Netlify, or GitHub Pages
- Save to Google Drive

## Step-by-Step Workflow

### 1. Gather Requirements
- Website type (landing page, portfolio, business, event, coming soon)
- Industry/niche
- Brand info (name, colors, logo)
- Desired sections (hero, features, testimonials, pricing, about, FAQ, contact)
- Content for each section
- CTA (call-to-action) text and destination

### 2. Plan Structure

Basic website architecture:
```
index.html (main page)
├── <head> (meta tags, SEO, styles)
├── <nav> (navigation)
├── <main>
│   ├── Hero section
│   ├── Features/Benefits
│   ├── About/Story
│   ├── Testimonials
│   ├── Pricing (if applicable)
│   ├── FAQ
│   └── Contact/CTA
└── <footer>
```

### 3. Write HTML/CSS/JS

Example landing page:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TaskFlow - Organize Your Work</title>
    <meta name="description" content="TaskFlow is the all-in-one platform for teams that want to work smarter.">

    <!-- SEO Meta Tags -->
    <meta property="og:title" content="TaskFlow - Productivity Made Simple">
    <meta property="og:description" content="Real-time collaboration, automated workflows, advanced analytics.">
    <meta property="og:type" content="website">

    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>

    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
        }
        .btn-primary {
            background-color: #1e40af;
            color: white;
            padding: 12px 24px;
            border-radius: 6px;
            text-decoration: none;
            display: inline-block;
            transition: background-color 0.3s;
        }
        .btn-primary:hover {
            background-color: #1e3a8a;
        }
        .hero-gradient {
            background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
        }
        .section-padding {
            padding: 60px 20px;
        }
    </style>
</head>
<body>

<!-- Navigation -->
<nav class="sticky top-0 bg-white shadow-sm z-50">
    <div class="max-w-6xl mx-auto px-4 py-4 flex justify-between items-center">
        <div class="text-2xl font-bold text-blue-700">TaskFlow</div>
        <div class="flex gap-6">
            <a href="#features" class="text-gray-700 hover:text-blue-700">Features</a>
            <a href="#pricing" class="text-gray-700 hover:text-blue-700">Pricing</a>
            <a href="#contact" class="text-gray-700 hover:text-blue-700">Contact</a>
        </div>
    </div>
</nav>

<!-- Hero Section -->
<section class="hero-gradient text-white section-padding">
    <div class="max-w-4xl mx-auto text-center">
        <h1 class="text-5xl font-bold mb-4">Organize Your Work. Boost Your Productivity.</h1>
        <p class="text-xl mb-8 text-blue-100">TaskFlow is the all-in-one platform for teams that want to work smarter.</p>
        <a href="#signup" class="bg-orange-500 hover:bg-orange-600 text-white px-8 py-3 rounded-lg font-bold inline-block transition">
            Start Free Trial
        </a>
    </div>
</section>

<!-- Features Section -->
<section id="features" class="section-padding bg-gray-50">
    <div class="max-w-6xl mx-auto">
        <h2 class="text-4xl font-bold text-center mb-12">Powerful Features</h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
            <!-- Feature 1 -->
            <div class="bg-white p-8 rounded-lg shadow-sm hover:shadow-md transition">
                <div class="text-4xl mb-4">🤝</div>
                <h3 class="text-xl font-bold mb-2">Real-time Collaboration</h3>
                <p class="text-gray-600">Work together seamlessly with instant updates and shared visibility.</p>
            </div>

            <!-- Feature 2 -->
            <div class="bg-white p-8 rounded-lg shadow-sm hover:shadow-md transition">
                <div class="text-4xl mb-4">⚡</div>
                <h3 class="text-xl font-bold mb-2">Automated Workflows</h3>
                <p class="text-gray-600">Automate repetitive tasks and focus on what matters most.</p>
            </div>

            <!-- Feature 3 -->
            <div class="bg-white p-8 rounded-lg shadow-sm hover:shadow-md transition">
                <div class="text-4xl mb-4">📊</div>
                <h3 class="text-xl font-bold mb-2">Advanced Analytics</h3>
                <p class="text-gray-600">Get actionable insights with comprehensive reporting dashboards.</p>
            </div>
        </div>
    </div>
</section>

<!-- Pricing Section -->
<section id="pricing" class="section-padding">
    <div class="max-w-6xl mx-auto">
        <h2 class="text-4xl font-bold text-center mb-12">Simple Pricing</h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
            <!-- Plan 1 -->
            <div class="border rounded-lg p-8">
                <h3 class="text-2xl font-bold mb-4">Starter</h3>
                <p class="text-4xl font-bold text-blue-700 mb-2">$29<span class="text-sm text-gray-600">/month</span></p>
                <ul class="text-gray-600 mb-8 space-y-2">
                    <li>✓ Up to 3 projects</li>
                    <li>✓ 5 team members</li>
                    <li>✓ Basic analytics</li>
                </ul>
                <a href="#signup" class="btn-primary w-full text-center">Get Started</a>
            </div>

            <!-- Plan 2 (Featured) -->
            <div class="border-2 border-blue-700 rounded-lg p-8 bg-blue-50">
                <p class="text-sm font-bold text-blue-700 mb-2">POPULAR</p>
                <h3 class="text-2xl font-bold mb-4">Professional</h3>
                <p class="text-4xl font-bold text-blue-700 mb-2">$79<span class="text-sm text-gray-600">/month</span></p>
                <ul class="text-gray-600 mb-8 space-y-2">
                    <li>✓ Unlimited projects</li>
                    <li>✓ 50 team members</li>
                    <li>✓ Advanced analytics</li>
                    <li>✓ Automations</li>
                </ul>
                <a href="#signup" class="btn-primary w-full text-center">Start Free Trial</a>
            </div>

            <!-- Plan 3 -->
            <div class="border rounded-lg p-8">
                <h3 class="text-2xl font-bold mb-4">Enterprise</h3>
                <p class="text-4xl font-bold text-blue-700 mb-2">Custom</p>
                <ul class="text-gray-600 mb-8 space-y-2">
                    <li>✓ Everything in Pro</li>
                    <li>✓ Dedicated support</li>
                    <li>✓ Custom integrations</li>
                    <li>✓ SLA guarantee</li>
                </ul>
                <a href="#contact" class="btn-primary w-full text-center">Contact Sales</a>
            </div>
        </div>
    </div>
</section>

<!-- Contact Section -->
<section id="contact" class="section-padding bg-gray-50">
    <div class="max-w-2xl mx-auto text-center">
        <h2 class="text-4xl font-bold mb-8">Ready to Get Started?</h2>
        <form class="bg-white p-8 rounded-lg shadow-sm">
            <input type="email" placeholder="your@email.com" class="w-full mb-4 px-4 py-2 border border-gray-300 rounded-lg" required>
            <button type="submit" class="btn-primary w-full">Sign Up Free</button>
        </form>
    </div>
</section>

<!-- Footer -->
<footer class="bg-gray-900 text-gray-400 py-8">
    <div class="max-w-6xl mx-auto px-4 text-center">
        <p>&copy; 2026 TaskFlow. All rights reserved.</p>
    </div>
</footer>

</body>
</html>
```

### 4. Test Responsiveness

Open the file in browser and test:
- Desktop (1920px)
- Tablet (768px)
- Mobile (375px)
- Landscape mode

Use browser dev tools (F12) to test media queries.

### 5. Optimize for SEO

Include in `<head>`:
```html
<meta name="description" content="Clear, compelling summary (150-160 chars)">
<meta name="keywords" content="relevant, keywords, here">
<meta property="og:image" content="https://example.com/preview.png">
<meta name="theme-color" content="#1e40af">
<link rel="canonical" href="https://yourdomain.com">
```

### 6. Start Local Server for Preview

```bash
# Python 3
python3 -m http.server 8080

# Or use Python 2
python -m SimpleHTTPServer 8080
```

Visit `http://localhost:8080/index.html` to preview.

### 7. Save to Google Drive

```bash
gws drive +upload --file index.html --folder "[folder_id]"
```

Or upload entire website folder as ZIP:
```bash
zip -r website.zip index.html assets/
gws drive +upload --file website.zip --folder "[folder_id]"
```

### 8. Deploy

#### Option A: Netlify
```bash
# Install Netlify CLI
npm install -g netlify-cli

# Deploy
netlify deploy --prod --dir=.
```

#### Option B: Vercel
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel --prod
```

#### Option C: GitHub Pages
Push to GitHub repo, enable Pages in settings.

## Cost

- **HTML/CSS/JS writing:** Free (you write the code)
- **Tailwind CSS:** Free (CDN)
- **Hosting (Netlify/Vercel):** Free tier or $20+/month
- **Custom domain:** ~$10-15/year
- **SSL certificate:** Free (auto on Netlify/Vercel)

**Total cost per website:** $0-15/year (after initial development).

## Pro Tips

- **Mobile-first approach:** Design for mobile first, then add tablet/desktop enhancements
- **Performance matters:** Compress images, minimize CSS/JS, lazy-load images
- **Forms require backend:** Use Netlify Forms, Formspree, or similar for email capture
- **Analytics:** Add Google Analytics in `<head>`
- **Fast load time:** Aim for under 2 seconds on standard broadband
- **Accessibility:** Use semantic HTML, alt text for images, sufficient color contrast
- **Test on real devices:** Browser emulation doesn't catch everything
- **Keep designs clean:** Whitespace and clear hierarchy improve usability
