# Summary of Crawlability Rules for nytimes.com (from robots.txt)

Date of Analysis: May 14, 2025

Content URL `https://www.nytimes.com/robots.txt`.

## 0. Crawalabilty Rules

The `robots.txt` file begins with a prominent legal notice. Key points:

1. Personal, Non-Commercial Use: New York Times content is for personal, non-commercial use under their Terms of Service.

2. Prohibition on Automated Scraping/Data Mining: "Use of any device, tool, or process designed to data mine or scrape the content using automated means is prohibited without prior written permission from The New York Times Company."

3. Specifically Prohibited Uses Include:\*\*
   1. Text and data mining activities (e.g., under EU Copyright Directive Art. 4).
   2. Development of any software, machine learning, artificial intelligence (AI), and/or large language models (LLMs). (to train)
   3. Creating or providing archived or cached data sets containing their content.
   4. Any commercial purposes.

## 1. Specific User-Agent Directives

### Googlebot (User-agent: Googlebot)

Googlebot is generally permitted to crawl for indexing purposes, but with numerous disallows:
------> Disallowed paths include:\*_ `/ads/`, `/adx/bin/`, various `/athletic/` paths (like `wp-admin` except `admin-ajax.php`, `async-_`, `checkout`, `login`, `report`, `discuss`, `register`, API/GraphQL endpoints, etc.), `/card/panel/`, `/panel/`, `/puzzles/leaderboards/invite/_`, most `/svc`except specific games and crosswords,`/video/embedded/_`, `/search`, `/multiproduct/`, `/hd/`, `/inyt/`, various query parameters (`*?*query=`, `*?*login=`, etc.), `\*.pdf$`.

- Specific disallows for Googlebot also include `/athletic*` URLs with `adgroupid`, `campaignid`, `ad_id`, `access_token`, `amp_reader_id`, `source=`, `embed=1`.
- **Allowed paths include:** `/athletic/wp/wp-admin/admin-ajax.php`, `/athletic/search/$` (base search page), `/athletic/login/$`, `/svc/crosswords`, `/svc/games`, `/svc/letter-boxed`, `/svc/spelling-bee`, `/svc/vertex`, `/svc/wordle`, `/ads/public/`.

### AI and Data Collection Bots (Explicitly Disallowed from All Content - `Disallow: /`)

A significant number of bots, particularly those associated with AI model training and large-scale data collection, are !!completely disallowed!! from accessing any part of the site. This reinforces the legal notice.

- `anthropic-ai`
- `Applebot-Extended`
- `Bytespider`
- `CCBot` (Common Crawl)
- `ChatGPT-User` (OpenAI)
- `ClaudeBot`, `Claude-Web` (Anthropic)
- `cohere-ai`
- `Google-Extended` (Google AI)
- `GPTBot` (OpenAI)
- `OAI-SearchBot`
- `PerplexityBot`
- And many others like `Amazonbot`, `DataForSeoBot`, `Diffbot`, `FacebookBot`, `FriendlyCrawler`, `ImagesiftBot`, `magpie-crawler`, `Meta-ExternalAgent`, `NewsNow`, `news-please`, `omgili`, `omgilibot`, `peer39_crawler`, `Quora-Bot`, `Timpibot`, `TurnitinBot`, `YouBot`.

### Scrapy (User-agent: Scrapy)

- **`User-agent: Scrapy Disallow: /`**
- This means using the Scrapy framework with its default user agent is **explicitly prohibited** from crawling any part of `nytimes.com`.

### Other Specific Bots

- `Google-CloudVertexBot`: `Disallow: /` but `Allow: /wirecutter/` (allowed only for Wirecutter section).
- `facebookexternalhit`, `Twitterbot`: `Allow: /*?*smid=` (likely for social media sharing previews).
- `AwarioRssBot`: No explicit `Disallow`, implies allowed by default (but subject to ToS).
- `AwarioSmartBot`: `Disallow: /`.

## 3. Crawl-delay Directive

No `Crawl-delay` directive was found in the `robots.txt` file. However, the absence of a crawl-delay does not imply permission to crawl rapidly, especially given the site's explicit prohibitions on automated scraping. Responsible crawling practices (if undertaken despite ToS) would necessitate self-imposed delays.

## 4. Sitemaps

Numerous sitemap files are listed, providing structured access to various sections of the website:

- `Sitemap: https://www.nytimes.com/sitemaps/new/news.xml.gz`
- `Sitemap: https://www.nytimes.com/sitemaps/new/sitemap.xml.gz`
- `Sitemap: https://www.nytimes.com/sitemaps/new/collections.xml.gz`
- `Sitemap: https://www.nytimes.com/sitemaps/new/video.xml.gz`
- `Sitemap: https://www.nytimes.com/sitemaps/new/cooking.xml.gz`
- `Sitemap: https://www.nytimes.com/sitemaps/new/recipe-collects.xml.gz`
- `Sitemap: https://www.nytimes.com/sitemaps/new/regions.xml`
- `Sitemap: https://www.nytimes.com/sitemaps/new/best-sellers.xml`
- `Sitemap: https://www.nytimes.com/sitemaps/new/weather.xml.gz`
- `Sitemap: https://www.nytimes.com/sitemaps/new/espanol.xml.gz`
- `Sitemap: https://www.nytimes.com/sitemaps/new/espanol-collects.xml.gz`
- `Sitemap: https://www.nytimes.com/wirecutter/sitemapindex.xml`
- `Sitemap: https://www.nytimes.com/athletic/sitemap-authors.xml`
- `Sitemap: https://www.nytimes.com/athletic/sitemap-verticals.xml`
- `Sitemap: https://www.nytimes.com/athletic/sitemap-teams.xml`
- `Sitemap: https://www.nytimes.com/athletic/sitemap-cities.xml`
- `Sitemap: https://www.nytimes.com/athletic/sitemap.xml`
- `Sitemap: https://www.nytimes.com/games-assets/v2/assets/sitemap/games.xml`

These sitemaps could be a primary source for discovering article URLs if one were to proceed with scraping (while being mindful of the ToS). (teroms of services)

**Conclusion on Crawlability:**
Technically, some paths are "crawlable" for certain user agents like Googlebot. However, for general automated tools, especially those used for data extraction or AI-related purposes (including `Scrapy`, `ChatGPT-User`, `GPTBot`, etc.), `nytimes.com` is highly restrictive, both through `robots.txt` directives and, more importantly, its overarching Terms of Service. The sitemaps offer a way to find content, but accessing and processing it automatically is broadly prohibited.

######THE OFFICIAL : # New York Times content is made available for your personal, non-commercial

# use subject to our Terms of Service here:

# https://help.nytimes.com/hc/en-us/articles/115014893428-Terms-of-Service.

# Use of any device, tool, or process designed to data mine or scrape the content

# using automated means is prohibited without prior written permission from

# The New York Times Company. Prohibited uses include but are not limited to:

# (1) text and data mining activities under Art. 4 of the EU Directive on Copyright in

# the Digital Single Market;

# (2) the development of any software, machine learning, artificial intelligence (AI),

# and/or large language models (LLMs);

# (3) creating or providing archived or cached data sets containing our content to others; and/or

# (4) any commercial purposes.

# Contact https://nytlicensing.com/contact/ for assistance.

User-agent: _
User-agent: Googlebot
Disallow: /ads/
Disallow: /adx/bin/
Disallow: /athletic/wp/wp-admin/
Allow: /athletic/wp/wp-admin/admin-ajax.php
Disallow: /athletic/async-_
Disallow: /athletic/search/_
Allow: /athletic/search/$
Disallow: /athletic/checkout/
Disallow: /athletic/checkout?plan_id_
Allow: /athletic/checkout/$
Disallow: /athletic/checkout2*
Disallow: /athletic/login/
Disallow: /athletic/login?login_source*
Disallow: /athletic/login?ref_page*
Allow: /athletic/login/$
Disallow: /athletic/login2/
Disallow: /athletic/login2?login*source*
Disallow: /athletic/login2?ref_page*
Allow: /athletic/login2/$
Disallow: /athletic/report/
Disallow: /athletic/*/discuss/*
Disallow: /athletic/register/
Disallow: /athletic/register?welcome_redirect*
Disallow: /athletic/register2/
Disallow: /athletic/register2?welcome_redirect*
Disallow: /athletic/betmgm-redirect*
Disallow: /athletic/cdn-cgi/
Disallow: /athletic/verizon/*
Disallow: /athletic/forgot-password/*
Allow: /athletic/forgot-password/$
Disallow: /athletic/forgot-password2/*
Allow: /athletic/forgot-password2/$
Disallow: /athletic/amp-social-login_
Disallow: /athletic/track-analytics/
Disallow: /athletic/amp-auth/
Disallow: /athletic/rss-feed/
Disallow: /athletic/*?*rss=1
Disallow: /athletic/global-color-test.php
Disallow: /athletic/global-font-test.php
Disallow: /athletic/graphql*
Disallow: /athletic/api*
Disallow: /athletic/ip*
Disallow: /athletic/call-set-cookie-with-context/*
Disallow: /athletic/get-current-user/
Disallow: /athletic/pv.json
Disallow: /athletic/following-feed-test/_
Disallow: /athletic_/boxscore/_
Disallow: /athletic/feed-test/
Disallow: /athletic_/signed-mp3-redirect-url/_
Disallow: /athletic/embedded-interactive/_
Disallow: /athletic/interactive/_
Disallow: /card/panel/
Disallow: /panel/
Disallow: /puzzles/leaderboards/invite/_
Disallow: /svc
Allow: /svc/crosswords
Allow: /svc/games
Allow: /svc/letter-boxed
Allow: /svc/spelling-bee
Allow: /svc/vertex
Allow: /svc/wordle
Disallow: /video/embedded/_
Disallow: /search
Disallow: /multiproduct/
Disallow: /hd/
Disallow: /inyt/
Disallow: /_?_query=
Disallow: /_.pdf$
Disallow: /*?*login=
Disallow: /*?*searchResultPosition=
Disallow: /*?*campaignId=
Disallow: /*?*mcubz=
Disallow: /*?*smprod=
Disallow: /*?*ProfileID=
Disallow: /*?*ListingID=
Disallow: /*?*campaign*id=
Disallow: /*?*hybrid=
Disallow: /*?*entry=
Disallow: /*?*embed=
Disallow: /*?ls=
Disallow: /*?*&ls=
Disallow: /wirecutter/wp-admin/
Disallow: /wirecutter/*.zip$
Disallow: /wirecutter/*.csv$
Disallow: /wirecutter/deals/beta
Disallow: /wirecutter/data-requests
Disallow: /wirecutter/search
Disallow: /wirecutter/_?s=
Disallow: /wirecutter/_&xid=
Disallow: /wirecutter/_?q=
Disallow: /wirecutter/_?l=
Disallow: /wirecutter/\_?merchant=
Disallow: /search
Disallow: /subscription/*?*source=
Disallow: /subscription/*?*onboarded=
Disallow: /*?*smid=
Disallow: /*?*partner=
Disallow: /*?*utm_source=
Allow: /wirecutter/*?*utm_source=
Allow: /ads/public/
Allow: /svc/news/v3/all/pshb.rss

# Googlebot Specific Rules

User-agent: Googlebot
Disallow: /athletic*adgroupid*
Disallow: /athletic*campaignid*
Disallow: /athletic*ad_id*
Disallow: /athletic*access_token*
Disallow: /athletic*amp_reader_id*
Disallow: /athletic*/?source=*
Disallow: /athletic/*?*embed=1

# Disallow Rules

User-agent: Amazonbot
Disallow: /

User-agent: anthropic-ai
Disallow: /

User-agent: Applebot-Extended
Disallow: /

User-agent: AwarioRssBot
User-agent: AwarioSmartBot
Disallow: /

User-agent: Bytespider
Disallow: /

User-agent: CCBot
Disallow: /

User-agent: ChatGPT-User
Disallow: /

User-agent: ClaudeBot
Disallow: /

User-agent: Claude-Web
Disallow: /

User-agent: cohere-ai
Disallow: /

User-agent: DataForSeoBot
Disallow: /

User-agent: Diffbot
Disallow: /

User-agent: DuckAssistBot
Disallow: /

User-agent: FacebookBot
Disallow: /

User-agent: FriendlyCrawler
Disallow: /

User-agent: Google-CloudVertexBot
Disallow: /
Allow: /wirecutter/

User-agent: Google-Extended
Disallow: /

User-agent: GPTBot
Disallow: /

User-agent: ImagesiftBot
Disallow: /

User-agent: magpie-crawler
Disallow: /

User-agent: Meta-ExternalAgent
User-agent: meta-externalagent
Disallow: /

User-agent: Meta-ExternalFetcher
User-agent: meta-externalfetcher
Disallow: /

User-agent: NewsNow
Disallow: /

User-agent: news-please
Disallow: /

User-agent: OAI-SearchBot
Disallow: /

User-agent: omgili
Disallow: /

User-agent: omgilibot
Disallow: /

User-agent: peer39_crawler
User-agent: peer39_crawler/1.0
Disallow: /

User-agent: PerplexityBot
Disallow: /

User-agent: Quora-Bot
Disallow: /

User-agent: Scrapy
Disallow: /

User-agent: Timpibot
Disallow: /

User-agent: TurnitinBot
Disallow: /

User-agent: YouBot
Disallow: /

# Other Bot Rules

User-agent: facebookexternalhit
Allow: /*?*smid=

User-agent: Twitterbot
Allow: /*?*smid=

# Sitemaps

Sitemap: https://www.nytimes.com/sitemaps/new/news.xml.gz
Sitemap: https://www.nytimes.com/sitemaps/new/sitemap.xml.gz
Sitemap: https://www.nytimes.com/sitemaps/new/collections.xml.gz
Sitemap: https://www.nytimes.com/sitemaps/new/video.xml.gz
Sitemap: https://www.nytimes.com/sitemaps/new/cooking.xml.gz
Sitemap: https://www.nytimes.com/sitemaps/new/recipe-collects.xml.gz
Sitemap: https://www.nytimes.com/sitemaps/new/regions.xml
Sitemap: https://www.nytimes.com/sitemaps/new/best-sellers.xml
Sitemap: https://www.nytimes.com/sitemaps/new/weather.xml.gz
Sitemap: https://www.nytimes.com/sitemaps/new/espanol.xml.gz
Sitemap: https://www.nytimes.com/sitemaps/new/espanol-collects.xml.gz
Sitemap: https://www.nytimes.com/wirecutter/sitemapindex.xml
Sitemap: https://www.nytimes.com/athletic/sitemap-authors.xml
Sitemap: https://www.nytimes.com/athletic/sitemap-verticals.xml
Sitemap: https://www.nytimes.com/athletic/sitemap-teams.xml
Sitemap: https://www.nytimes.com/athletic/sitemap-cities.xml
Sitemap: https://www.nytimes.com/athletic/sitemap.xml
Sitemap: https://www.nytimes.com/games-assets/v2/assets/sitemap/games.xml
