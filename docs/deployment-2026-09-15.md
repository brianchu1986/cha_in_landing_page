# Deployment and SEO audit — 15 September 2026

## Outcome

Prepared and locally validated a Cloudflare Workers Static Assets configuration. **No authenticated Wrangler deployment, DNS change, Custom Domain attachment, redirect-rule change or production cutover was initiated by this agent.** After the requested Git push, the existing Workers endpoint began serving the committed source and passed remote checks. Its deployment mechanism remains unverified without account access; do not assume there is no external build integration merely because the repository has no workflow file.

Wrangler **4.131.2** reported: `You are not authenticated. Please run wrangler login.` Deployment stopped as requested. No credentials were requested, printed or added to the application. The initial npm certificate-chain error was resolved by using Node's system certificate store (`NODE_OPTIONS=--use-system-ca` for the command process); TLS verification remained enabled. The older cached Wrangler 4.125.0 also reported no authentication before the latest version was installed successfully.

Starting repository: `main`, clean, commit `54c82d718ad1ccb806523b995e10fb4228239687`. Remote: `https://github.com/brianchu1986/cha_in_landing_page`. No AGENTS.md, package.json, Wrangler configuration or GitHub Actions configuration was present. README previously described a planned Pages deployment.

## Public routing observations and rollback boundary

Observed during this audit, before any production changes:

| Host / record | Observed value or behaviour |
| --- | --- |
| `chaincafe.my` A | `124.217.251.156`, observed TTL 897 seconds |
| `chaincafe.my` AAAA | No answer record returned |
| `chaincafe.my` CNAME | No answer record returned |
| `www.chaincafe.my` CNAME | `chaincafe.my`, observed TTL 899 seconds |
| Authoritative NS | `ns1.hawkdns.net`, `ns2.hawkdns.net` |
| `http://chaincafe.my/` | HTTP 404, `nginx/1.24.0 (Ubuntu)` |
| `https://chaincafe.my/` | curl exit 60, `SEC_E_WRONG_PRINCIPAL`: certificate hostname validation failed |
| `https://www.chaincafe.my/` | HTTP 200, nginx, title `Cha In Cafe`, no canonical link found |
| `https://www.chaincafe.my/contact_us?source=qa` | HTTP 200, title `Cha In Cafe - Contact us`; no apex redirect |
| Expected Workers hostname | HTTP 200; homepage matches starting commit after line-ending normalization |

These are public DNS/HTTP observations, **not an authenticated zone inventory**. Proxy settings, account/zone identity, DNS record IDs, existing Page Rules, Redirect Rules, Bulk Redirects, Pages associations, Worker route associations and deployment/version IDs remain unknown. The observations indicate an external origin and nameservers, but cannot establish all Cloudflare account settings or rule layers.

There is no complete, safe cutover rollback snapshot yet. No rollback was needed because no production configuration changed. Before cutover, capture the exact record content, types, TTLs, proxy settings, rule definitions and enabled states, custom-domain/route associations, and previous Worker version. Preserve mail and verification DNS. External nameservers require an explicit zone-readiness assessment and complete DNS migration plan before changing them. Do not infer that an active Cloudflare zone exists from the working workers.dev hostname.

`www` already exists and should retain support. After apex HTTPS works, configure a host-specific 301 to the apex with path and query preserved. Its present 200 behaviour does not satisfy that requirement.

## SEO / AIEO findings and scoped changes

| Area | Finding / action |
| --- | --- |
| Title and description | Existing descriptive brand, Yong Peng and Johor wording retained. No keyword rewrite. |
| H1 / headings | One H1 per page, no skipped ascending heading levels. |
| Canonical / social metadata | Existing apex canonical and OG/Twitter image URLs retained; 1200 × 630 social image dimensions verified. |
| Site name | WebSite name aligned to `Cha In Café 茶颖`; short `Cha In Café` preserved as an alternative. |
| JSON-LD | CafeOrCoffeeShop / WebSite / WebPage graph and all three stable IDs retained. Added the existing visible 1672 × 941 hero photograph as `image`. |
| NAP / hours | Visible name, full Yong Peng address, phone and daily 12:00–21:30 hours match the supplied facts and schema. |
| Legal operator | CHA IN F & B PLT / LLP0017890-LGN and effective registration 1 October 2018 remain visible. No foundingDate added. |
| Quick Answers | Existing visible answers cover identity/location/hours/contact/ordering/operator/registration; retained. No FAQPage schema. |
| Accessibility / semantics | Added valid group roles to two labelled divs; removed unnecessary unheaded legal article wrappers; added 404 skip link; fixed undefined `--pink-light`. Legal wording and policy dates are unchanged. |
| Internal links | Added homepage footer link to Refund Policy. Existing anchors, legal links and six legacy redirects validate. |
| Images / payload | WebP images and intrinsic dimensions retained; no new image files, bundles or external page dependencies. |
| Crawl policy | Existing OAI-SearchBot and wildcard Allow rules retained. Googlebot/Bingbot allowed; GPTBot policy unchanged. |
| Sitemap | Homepage only, canonical apex; lastmod updated from 2026-08-11 to 2026-09-15 for metadata/link changes. |
| Legal / 404 indexing | Existing `noindex, follow` retained. No production-wide noindex. |
| Duplicate content | Exact-host workers.dev noindex rule passed local tests and became live after the Git push. Apex HTTPS and www routing remain launch blockers. |
| Unsupported claims | No ratings, reviews, founding date, cuisine, prices, offers, delivery or halal claims added. |
| AI-specific files | No llms.txt, hidden AI content, doorway pages or IndexNow infrastructure added. |

## Architecture prepared

`wrangler.jsonc`: Worker `chaincafe`, compatibility date `2026-09-15`, assets `./public`, `not_found_handling: 404-page`, `html_handling: auto-trailing-slash`, `workers_dev: true`, `preview_urls: false`. Static assets only; no authored Worker JavaScript, framework or environment variables. `_headers` and `_redirects` are parsed natively.

Production routes are deliberately absent while authentication, zone state and staging deployment are unverified. The README documents the later `{ "pattern": "chaincafe.my", "custom_domain": true }` route. The apex must serve its own canonical site through a Custom Domain, never redirect to workers.dev.

## Existing remote Worker baseline

URL inspected: **https://chaincafe.brianchu1986.workers.dev/**. This is a pre-existing endpoint. The following table records its state **before the Git push**.

| Requests | Result |
| --- | --- |
| `/`, `/terms/`, `/refund-policy/` | 200; canonical URLs use chaincafe.my |
| `/robots.txt`, `/sitemap.xml` | 200; expected allow policy and apex sitemap URLs |
| `/contact_us`, `/contact_us/` | 301 → `/#contact` |
| `/terms_and_conditions`, `/terms_and_conditions/` | 301 → `/terms/` |
| `/refund_policy`, `/refund_policy/` | 301 → `/refund-policy/` |
| `/nonexistent-test-path` | 404 |
| CSS, JS, all four WebP files | 200 |
| Security headers | CSP, nosniff, referrer, permissions and opener policy present |
| workers.dev X-Robots-Tag | **Missing**; existing homepage has no HTML noindex either |
| Legal pages | HTML `noindex, follow` present |
| Browser | Homepage/hero render; JSON-LD parses; no captured warning/error logs on homepage inspection |
| Googlebot / Bingbot / OAI-SearchBot user-agent requests | 200 from this connection; this is not verification from actual crawler IP ranges |

Before the push, the remote sitemap had `2026-08-11`, and the new source/noindex rule was absent.

## Remote update observed after Git push

Implementation commit `d5b313c25b1afc0a0ce910f171cc66b8dc955871` was pushed successfully to `origin/main` after a conflict-free fetch/rebase. A subsequent HEAD response showed a changed ETag and **`X-Robots-Tag: noindex`**. The full checker then passed against the real Workers URL:

- All four served HTML documents, including the missing-page body, exactly matched the committed local source.
- Homepage/legal/robots/sitemap/CSS/JS/images returned 200; the nonexistent path returned 404.
- All six legacy redirects returned the expected 301 and followed to 200.
- All checked asset/page responses carried staging noindex and the five security headers.
- Canonicals and sitemap URLs retained `chaincafe.my`; the current sitemap now has `2026-09-15`.
- Browser reload showed the new site name and refund link, a loaded hero, working mobile menu and no captured homepage warning/error logs. The remote page was inspected at actual 360- and 1280-pixel widths; the complete five-width review below was local.

The endpoint is now serving the implementation, but no authenticated build/deployment/version record was available to identify how it updated. The requested push preceded the update; that observation alone does not prove the deployment trigger. No authenticated `wrangler deploy` was run. Production cutover remains blocked by authentication, zone/routing inventory and apex TLS failure, which was rechecked after the update.

## Production and ordering endpoints

All nine requested apex HTTPS paths failed certificate validation: `/`, `/terms/`, `/refund-policy/`, `/contact_us`, `/terms_and_conditions`, `/refund_policy`, `/robots.txt`, `/sitemap.xml`, `/this-path-does-not-exist`. Browser navigation to the apex also failed. No TLS bypass was used. Consequently, production canonical/noindex, asset behaviour, crawler access and responsive post-cutover checks cannot be certified.

Niaga **HEAD and followed GET returned 200**. Browser rendered the Cha In storefront, featured menu and ordering links. Selecting Order Now opened the ordering-method selection page. No purchase, checkout, payment or message was submitted; transaction success was not tested. Landing-page ordering copy and WhatsApp fallback remain appropriate. No Niaga application changes were made.

WhatsApp, Google Maps directions and Facebook links resolved to HTTP 200. Telephone links use `tel:+60176151036`. Successful HTTP resolution does not establish message delivery or a completed telephone call.

## Local validation and performance

- Latest Wrangler 4.131.2 configuration schema validation: pass.
- `npx wrangler@latest deploy --dry-run`: pass; no bindings; no remote deployment. Output reported 0.37 KiB upload / 0.26 KiB gzip for the generated deployment module; **these are not site payload measurements**.
- Python preview at `http://localhost:8001/`; Wrangler preview at `http://127.0.0.1:8787/`.
- `python tools/check_site.py --base-url http://127.0.0.1:8787`: pass. Covers structure, one H1, heading levels, duplicate IDs, image attributes, local files/fragments, canonicals, legal noindex, JSON-LD/business facts, robots, sitemap, CSS variables, 12 page/asset HTTP checks, all six redirects and followed destinations.
- Local Host-header tests for homepage, image and 404: workers.dev gets `X-Robots-Tag: noindex`; apex gets no X-Robots-Tag noindex.
- Nu HTML validator: all four HTML documents have **zero errors and zero warnings** after fixes.
- Image dimensions verified using Pillow: logo 192 × 192; wordmark 455 × 111; social card 1200 × 630; cover 1672 × 941.
- `node --check public/script.js`: pass. No script changes.
- Responsive browser review: 360, 390, 768, 1024 and 1440 pixels; no page-level horizontal overflow. Homepage/hero, business facts, footer and mobile legal/404 views inspected. Enter and Space toggle the mobile menu; selecting Visit/Home closes it and navigates. No captured homepage console warnings/errors. This is local QA, not post-cutover production QA.
- Homepage HTML + CSS + JS + hero + logo source bytes: **167,775 → 168,083**, **+308 bytes / +0.184%**. These are uncompressed source sizes, not transfer timing or Core Web Vitals.
- No Lighthouse installation was found on PATH or in the npm execution cache. No Lighthouse scores are reported; valid production HTTPS is also unavailable.
- Secret-pattern scan: no detected credential/private-key patterns in scoped source files. This is a heuristic scan, not proof that arbitrary secrets cannot exist.
- `git diff --check`: pass; final diff reviewed before commit.

## Commands and next operator steps

Commands included `git status`, `git log --oneline -10`, `git remote -v`, `git rev-parse HEAD`, repository/ancestor instruction checks, source reads, `Resolve-DnsName`, `curl -I` / followed GETs, `npx wrangler@latest whoami`, `npm view wrangler version`, `npx wrangler@latest deploy --dry-run`, Python and Wrangler preview commands, source/HTTP checker, Nu validation, JSON/XML/schema parsing, `node --check`, image/payload inspection, secret-pattern scan and `git diff --check` / `git diff`. The remote checker was also run successfully after the push. Git commit/rebase/push results are reported in the final handoff.

Next steps, in order:

1. Establish secure Wrangler authentication and unambiguous account/zone access.
2. Inventory the external DNS zone, existing Cloudflare routing and Worker associations; capture a complete rollback snapshot.
3. Resolve Cloudflare zone readiness without disturbing unrelated services or DNS records.
4. Inspect the build/deployment integration and confirm the existing Worker version/configuration corresponds to this source. It already passes public HTTP checks; if a further staging deploy is needed, keep production routing unchanged and reverify the emitted URL and noindex.
5. After every staging check passes, attach the apex as the Worker Custom Domain and verify HTTPS and all production checks. Then preserve www through a 301 with path/query retention.
6. Verify a Google Search Console domain property; submit `https://chaincafe.my/sitemap.xml`; inspect the homepage; request indexing when appropriate; monitor indexing and query data. Also verify Bing Webmaster Tools and submit the sitemap.
7. Run production Lighthouse and compare Google Business Profile/Facebook business details. No Search Console/Bing account integration was available for this task.

## First-party references consulted

Checked on 15 September 2026. Google states that normal SEO foundations apply to AI Overviews/AI Mode; no special AI text file or schema is required. OpenAI documents search-crawler and training-crawler controls independently. Cloudflare documents HTTPS absolute-host header patterns and native static asset routing. These support the limited changes above; they do not guarantee indexing or ranking.

- [Google AI features and your website](https://developers.google.com/search/docs/appearance/ai-features)
- [Google LocalBusiness structured data](https://developers.google.com/search/docs/appearance/structured-data/local-business)
- [Schema.org CafeOrCoffeeShop](https://schema.org/CafeOrCoffeeShop)
- [Google site names](https://developers.google.com/search/docs/appearance/site-names)
- [Google canonical URLs](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls)
- [Google sitemaps and meaningful lastmod dates](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap)
- [Google robots.txt](https://developers.google.com/search/docs/crawling-indexing/robots/intro)
- [OpenAI crawler documentation](https://developers.openai.com/api/docs/bots)
- [Bing: sitemaps in AI-powered search](https://blogs.bing.com/webmaster/July-2025/Keeping-Content-Discoverable-with-Sitemaps-in-AI-Powered-Search)
- [Workers Static Assets](https://developers.cloudflare.com/workers/static-assets/)
- [Workers headers, including exact-host noindex](https://developers.cloudflare.com/workers/static-assets/headers/)
- [Workers redirects](https://developers.cloudflare.com/workers/static-assets/redirects/)
- [Workers HTML handling](https://developers.cloudflare.com/workers/static-assets/routing/advanced/html-handling/)
- [Workers Custom Domains](https://developers.cloudflare.com/workers/configuration/routing/custom-domains/)
- [Wrangler configuration](https://developers.cloudflare.com/workers/wrangler/configuration/)
- [Workers best practices](https://developers.cloudflare.com/workers/best-practices/workers-best-practices/)
