Social Media Metrics Scraper
Extract key engagement metrics across major social media platforms in a single, unified workflow. Supports YouTube, TikTok, Instagram, Facebook, Twitter/X, and LinkedIn (including shortlinks like lnkd.in).

🚀 Features
Multi-Platform Support: Scrape metrics seamlessly from 6 major platforms:
YouTube (youtube.com, youtu.be)
TikTok (tiktok.com)
Instagram (instagram.com)
Facebook (facebook.com, fb.watch, /share/ redirects)
Twitter / X (twitter.com, x.com)
LinkedIn (linkedin.com, lnkd.in)
Unified Output Schema: Returns a standardized dataset regardless of the platform scrapers used under the hood.
Shortlink Resolution: Automatically routes and expands shortlinks (lnkd.in, youtu.be, fb.watch) to extract metrics without manual expansion.
Smart View Estimation: Automatically calculates engagement-based estimated reach for platforms/posts where raw views aren't publicly exposed by native platform interfaces (e.g., non-video Facebook posts).

📥 Input Parameters
Provide an array of URLs in the input configuration:
{
  "urls": [
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "https://www.instagram.com/p/C_12345/",
    "https://lnkd.in/p/dYKQERcw",
    "https://www.facebook.com/share/p/1CE6KAUK77/"
  ]
}


📊 Output Format
Each processed post generates a standardized result in your Apify Dataset:
[
  {
    "url": "https://lnkd.in/p/dYKQERcw",
    "author": "Tech Leader",
    "likes": 245,
    "comments": 38,
    "shares": 12,
    "views": 3200
  },
  {
    "url": "https://www.facebook.com/share/p/1CE6KAUK77/",
    "author": "Tuko.co.ke",
    "likes": 187,
    "comments": 58,
    "shares": 0,
    "views": 7350
  }
]

Dataset Schema Reference
Field
Type
Description
url
String
The target URL provided in the input
author
String
Page, channel, or user handle
likes
Integer
Total likes / reactions
comments
Integer
Total comment count
shares
Integer
Total share or repost count
views
Integer
Total view count (or calculated engagement fallback estimate)



💡 Notes & Limitations
Facebook Views: Facebook does not publicly expose view counts for standard text, photo, or link posts. For these post types, the Actor calculates a metric based on total engagement (likes, comments, shares) using an industry-standard ~3% reach estimation model.
Public Data: The scraper extracts data from publicly available web pages. Private or restricted posts requiring authentication will not return complete metrics.

🔌 Integrations
Connect this Actor with automated pipelines using:
n8n / Make.com / Zapier
Apify API (Python / JavaScript SDKs)
Export formats: JSON, CSV, Excel, XML, Google Sheets
