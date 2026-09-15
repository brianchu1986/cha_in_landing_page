# Cha In production cutover — 15 September 2026

## Outcome

Production is live at **https://chaincafe.my/** through Worker `chaincafe`, with valid HTTPS and canonical 301 redirects preserving path/query. Cloudflare is Active. Staging remains noindex. Production HTTP, source/SEO and five-width browser checks passed. Lighthouse performance scored **100 desktop / 99 mobile**, with CLS 0.

Google's Domain Property is verified, the sitemap reports Success, live inspection passed, and one indexing request was accepted. Bing DNS verification completed and its sitemap also reports Success with one discovered URL. Google Business Profile's daily hours and apex website are published. Search index inclusion and Google's final canonical selection remain unconfirmed.

The dated sections below retain the original observations and transition states for rollback/audit purposes; later results supersede earlier pending observations.

## Pre-change rollback snapshot

Captured before changing authoritative nameservers, production DNS/routing, or the Worker deployment. Starting commit: `9275516c26d879ed5104a051b35bc3e96b46cd2a` (clean `main`).

### Registrar and authoritative DNS

Authenticated Shinjiru domain management showed `chaincafe.my` Active. Nameservers: `ns1.hawkdns.net` and `ns2.hawkdns.net`; nameserver fields 3–5 empty. No registrar settings were changed during inventory.

Shinjiru DNS Manager showed **five records total** (2 A, 2 CNAME, 1 MX). No AAAA, ALIAS, CAA, SRV or TXT records existed in that inventory, including no SPF, DKIM, DMARC or verification TXT records.

| Name | Type | Content | TTL | Proxy |
| --- | --- | --- | --- | --- |
| `chaincafe.my` | A | `124.217.251.156` | 1800 | Not proxied (external DNS) |
| `mail.chaincafe.my` | A | `124.217.251.156` | 1800 | Not proxied |
| `chaincafe.my` | MX | Priority 0, `mail.chaincafe.my` | 1800 | Not applicable |
| `www.chaincafe.my` | CNAME | `chaincafe.my` | 1800 | Not proxied |
| `ftp.chaincafe.my` | CNAME | `chaincafe.my` | 1800 | Not proxied |

Authoritative queries to `ns1.hawkdns.net` confirmed all five values/TTLs and both NS records (TTL 1800). SOA: primary `ns1.hawkdns.net`, serial `2024100816`, SOA TTL 3600. A public DS lookup returned no DS answer (parent SOA only), so there was no published DNSSEC chain to disable. The DNS manager exposed no DNSSEC control.

The old web origin is `124.217.251.156`. Apex HTTPS failed hostname validation; www served the previous nginx site. Shinjiru reported “No SSL Detected.” No origin server settings or certificates are modified by this migration.

### Cloudflare and Worker

Before onboarding, the account's complete seven-zone inventory contained no `chaincafe.my` zone. Therefore no prior zone-level Cloudflare SSL mode, DNS, redirect rules or Pages DNS association applied to this domain. Account Bulk Redirects showed no lists.

Worker `chaincafe` had only `chaincafe.brianchu1986.workers.dev`, **no Custom Domains and no routes**, zero bindings, static assets only, compatibility date `2026-09-15`, previews disabled. Current version before this run: `ea083f24-dcae-473c-b525-73dcc8a94946`, deployed at `2026-09-15T05:46:10.182Z`.

The dashboard confirmed its existing GitHub integration: `brianchu1986/cha_in_landing_page`, production branch `main`, root `/`, no build command, deploy command `npx wrangler deploy`, version command `npx wrangler versions upload`. No build variables, runtime variables, secrets or deploy hooks were configured. The previous Git pushes triggered successful builds corresponding to their commits. The existing build integration and credential configuration are left unchanged.

Legacy redirects are the six entries in `public/_redirects`: contact paths to `/#contact`, terms paths to `/terms/`, refund paths to `/refund-policy/`, all 301. No apex redirect to workers.dev is configured or intended.

### Rollback procedure

1. Restore Shinjiru nameservers to exactly `ns1.hawkdns.net`, `ns2.hawkdns.net`, with fields 3–5 empty. The old authoritative zone and origin must remain available throughout the migration.
2. If rolling back within Cloudflare instead, remove only newly added Cha In routing/custom-domain and www redirect configuration, then restore the five records above, DNS-only and TTL 1800. Preserve any subsequently added verification TXT records unless intentionally retiring verification.
3. Restore `ftp` to its original apex CNAME only when the apex again resolves to the old origin. During the new website deployment, FTP must retain the old server destination independently of the apex.
4. If Worker content needs rollback, use the captured prior Worker version, and separately restore routing/DNS. Worker version rollback does not restore zone rules, nameservers or DNS.
5. Recheck DNS, mail host resolution, www, TLS and site responses after rollback. The old apex certificate was already invalid; returning to the old origin does not fix it.

## Migration log

- Added only `chaincafe.my` to Cloudflare and selected the Free plan with automatic DNS scanning. The scan found the same five records. Selected no AI training crawler block. After activation, the dashboard exposed its default managed robots setting as Content Signals Policy; this is recorded separately from the crawler blocking control.
- Set all imported eligible records to DNS-only and restored TTL 1800. Direct DNS queries to assigned Cloudflare server `bingo.ns.cloudflare.com` confirmed all five records match the old zone before nameserver migration.
- At approximately 06:45 UTC, Shinjiru saved nameservers `bingo.ns.cloudflare.com` and `jimmy.ns.cloudflare.com`, with fields 3–5 empty. The re-opened Nameservers tab displayed “Changes Saved Successfully!” and the exact new values. No other registrar settings changed. Cloudflare activation check requested; Worker Custom Domain cutover still awaits Active status. Staging QA passed.
- Authenticated `npx.cmd --yes wrangler@latest deploy` succeeded: `c65a6b37-b249-475c-88b9-e6981fc66cb4`, workers.dev only. Wrangler found 17 asset files and no changed assets to upload.
- The new zone's SSL mode is Full, DNSSEC is off, Page Rules are empty, and no existing Single Redirects were present. The canonical redirect form passed validation but has **not** been saved or deployed. Intended rule: `(http.host eq "www.chaincafe.my") or (http.host eq "chaincafe.my" and not ssl)`; dynamic destination `concat("https://chaincafe.my", http.request.uri.path)`; status 301; preserve query string. Activate after the apex works and the existing www DNS record is proxied. Rollback is to disable/remove only this newly added rule.
- At 06:57 UTC, the `.my` authoritative parent still delegated to HawkDNS (delegation TTL 86400). Public recursive resolvers also retained the old delegation. Registrar success and registry/public propagation are recorded separately; no repeated registrar mutation was made.
- At approximately 07:07 UTC, preserved the FTP endpoint by changing only `ftp.chaincafe.my` from CNAME apex to A `124.217.251.156`, DNS-only, TTL 1800, in the new Cloudflare zone. The saved table and direct query to `bingo.ns.cloudflare.com` confirmed the result. The MX remains priority 0 `mail.chaincafe.my`, TTL 1800. The apex and www still point to the old origin while activation is pending.

## Verification completed before cutover

- Source checker, local Wrangler HTTP checker, JavaScript syntax check and authenticated staging HTTP checker passed. Staging returned expected statuses and security headers for all 12 tested pages/assets, six correct legacy 301 redirects, true HTTP 404, exact deployed HTML matching local source, and hostname-specific `X-Robots-Tag: noindex`. The canonical remains the apex.
- Staging homepage browser QA passed at actual viewport widths 360, 390, 768, 1024 and 1440. Images loaded, the hero's natural dimensions were 1672 × 941, and each document width stayed within the viewport. Screenshots showed the intended layout. Mobile keyboard navigation opened the menu and selecting Visit closed it. Captured console warnings/errors were empty. No Lighthouse or numeric CLS score was obtained.
- Niaga returned HTTP 200 on a real followed GET. The Order Online CTA opened the correct Cha In storefront, which rendered successfully with an empty cart. No ordering, cart or checkout actions were performed.

## Google Business Profile comparison

Authenticated management access showed the verified **Cha In 茶穎** listing. Its phone matches `017-6151036`; the address identifies the same No. 13, Jalan Kota 7/1 location, with formatting differences. The existing name uses traditional Chinese and omits “Café”; it was preserved. Category, ownership, reviews, descriptions and other profile settings were left unchanged.

The initial website field pointed to the known Facebook page. After production verification, submitted `https://chaincafe.my/` as the website. Google initially showed the old Facebook URL under Current and the apex URL under Pending. At approximately 08:05 UTC, a fresh editor session displayed **https://chaincafe.my/** as the current website with no pending notice, confirming publication. The Facebook social profile remains intact.

Tuesday was marked Closed, contrary to the user's explicitly supplied daily 12:00–21:30 schedule. Submitted only Tuesday 12:00–21:30; the editor confirmed all other days unchanged. Google initially displayed the edit as pending review. By the final comparison, the pending notice had disappeared and the current Hours section showed **all seven days 12:00–21:30**, confirming publication.

## Continuation state at 07:10 UTC

Cloudflare still reports Pending; the `.my` parent still delegates to HawkDNS. A fresh HTTPS GET to the apex fails certificate hostname validation (`curl` error 60). No Worker Custom Domain or canonical redirect has been deployed. Search Console and Bing actions are gated on a verified production site and have not started.

The same Codex task has an active continuation named **Finish Cha In deployment after DNS propagation**, checking every 15 minutes and remaining quiet while propagation is unchanged. It is instructed to finish the authorized cutover, production verification, Search Console, Bing, Business Profile website update, documentation, tests and requested Git commit/rebase/push, then pause itself. There are no additional agents. The relevant browser pages are retained for continuation. The work is ongoing; no completion commit or push has been claimed.

## Activation continuation

- At 07:26 UTC the `.my` authoritative parent returned both assigned Cloudflare nameservers, TTL 86400. The Cloudflare zone overview subsequently displayed “Your domain is now protected by Cloudflare,” replacing its pending activation instructions.
- Before changing the robots overlay, the activated zone showed **Block AI training bots: Do not block (allow crawlers)** and **Manage your robots.txt: Content Signals Policy**. The intended change is only to disable managed robots.txt configuration so the repository file is served unchanged. This is independent of DNS, origin TLS and security controls; rollback of the overlay is to select Content Signals Policy again.
- Selected **Disable robots.txt configuration** and confirmed the selected value `off`. The AI training crawler blocking setting remains unchanged.
- Refreshed Wrangler authentication and all staging HTTP checks successfully. Added the documented apex `custom_domain: true` route to Wrangler; dry-run passed. The first production deploy uploaded successfully but domain attachment failed with Cloudflare error 100117 because the old externally managed apex A record still exists. The CLI explicitly reported a partial trigger update; the apex remained unchanged. Resolve only that exact apex A conflict using the captured rollback value, then verify the resulting Custom Domain.
- The dashboard confirmed the same conflict. Removed only apex A `124.217.251.156` (DNS-only, TTL 1800), verified the remaining four records, and immediately retried the prepared **Add domain** action for the root `chaincafe.my`. The Worker Domains table then showed `chaincafe.my` as Production in zone `chaincafe.my`. A normal HTTPS GET returned **200** from Cloudflare with certificate verification enabled. No apex redirect to workers.dev was introduced. A subsequent Wrangler deployment is being used to confirm configuration consistency.
- The subsequent authenticated Wrangler deployment succeeded completely: version `46c0f585-262a-4aa0-ae25-b2d18c7eaae7`, listing both the staging URL and `chaincafe.my (custom domain)`. Cloudflare DNS shows the apex as **Worker → chaincafe, Proxied, Auto**.
- Changed only the existing www CNAME's proxy status to Proxied (TTL Auto), retaining its apex target. Deployed **Cha In canonical HTTPS apex**, rule `6d1c31ab4c154882b02a06beda669f09`. The rules table shows **Active**, 301, the exact recorded filter and dynamic destination; Preserve query string was checked before submission.
- Full production checker passed all 12 page/asset statuses and security headers, four exact HTML/source comparisons, six legacy 301 redirects, and nine canonical redirects across HTTPS www, HTTP www and HTTP apex. Path/query preservation includes `/terms/?x=1` and encoded query values. The homepage has no HTTP or HTML noindex directive, while staging remains noindex.
- Production browser screenshots and DOM dimensions passed at actual widths 360, 390, 768, 1024 and 1440. Hero loaded at natural 1672 × 941; header logo rendered. Mobile keyboard menu opened with Enter and closed on Visit. Terms and refund pages rendered correctly at 390px. Browser confirmed one H1, the approved title/apex canonical, and all three JSON-LD entity IDs; captured warnings/errors were empty. No speculative content/performance changes were made.
- The production Order Online CTA opened the correct Niaga host. Its first visit displayed an expired-session logout notice; a read-only navigation to the public root then rendered the Cha In Cafe storefront with Cart 0, without signing in or interacting with ordering. A subsequent production CTA click directly opened the working storefront with Cart 0, and a separate followed HTTP GET returned 200. This external session behavior was observed without changing Niaga.

## Search Console

After production passed HTTP and browser verification, the authenticated property selector showed no existing `chaincafe.my` property. Created the Domain Property and chose **Any DNS provider → TXT**. Added only Google's provided apex verification TXT to Cloudflare (DNS-only, Auto/300 seconds); the authoritative server returned it. Google displayed **Ownership verified**, method **Domain name provider**. Preserve the TXT to retain verification. No broad DNS-account access grant was needed.

Submitted `https://chaincafe.my/sitemap.xml`. Google displayed **Sitemap submitted successfully** and its table showed **Success**, last read 15 September 2026, **1 discovered page**, 0 videos. Homepage URL Inspection was then started.

The stored index inspection described the previous site as **Duplicate without user-selected canonical**, with Google selecting `https://www.chaincafe.my/` and no user-declared canonical. This was historical crawl data, not a live result for the new deployment.

The live test at **15 September 2026, 15:45:42 Malaysia time** succeeded: **URL is available to Google**, **Page can be indexed**, smartphone inspection tool, crawl allowed Yes, fetch Successful, indexing allowed Yes, and user-declared canonical `https://chaincafe.my/`. Google-selected canonical is determined after indexing. Submitted **one** indexing request; Google confirmed **Indexing requested** and addition to its priority crawl queue. Index inclusion or ranking has not been claimed.

## Production Lighthouse performance

The local DevTools/Lighthouse tooling was unavailable, but Cloudflare's authenticated Synthetic Monitoring provided a one-time Lighthouse browser test. Ran the canonical homepage once from **Jurong West, Singapore** at **15:47 Malaysia time**, without enabling analytics, recurring tests or paid upgrades. Test ID: `4afd8300-208c-4e34-8b03-8c71fd4e2a17`.

| Metric | Desktop | Mobile |
| --- | --- | --- |
| Lighthouse performance score | 100 | 99 |
| Time to first byte | 36 ms | 28 ms |
| First contentful paint | 456 ms | 1,563 ms |
| Largest contentful paint | 466 ms | 1,983 ms |
| Time to interactive | 466 ms | 1,983 ms |
| Total blocking time | 0 ms | 0 ms |
| Speed index | 544 ms | 1,563 ms |
| Cumulative layout shift | 0 | 0 |

These are synthetic results for this run, not real-user measurements. No speculative performance changes or suggested Cloudflare product toggles were applied. [Cloudflare's testing documentation](https://developers.cloudflare.com/speed/observatory/run-speed-test/) describes these Lighthouse reports.

## Bing Webmaster Tools

After Search Console succeeded, attempted its preferred Google import flow. Google requested new read access across all verified Search Console sites. Canceled before granting that additional scope and used Bing's supported site-specific CNAME verification instead. No other site was imported or modified.

Added only `27b20dc7e94e38866444e1d9575fd17c.chaincafe.my` → `verify.bing.com`, DNS-only, Auto/300 seconds. Both the saved DNS table and an authoritative query confirmed it. Bing verification completed, `chaincafe.my` became available in the website selector, and its authenticated dashboard and Sitemaps section were accessible.

Submitted `https://chaincafe.my/sitemap.xml` once. The resulting table initially showed Processing. A fresh Sitemaps page at approximately 08:04 UTC showed **Success**, submitted and last crawled **15 September 2026**, with **1 discovered URL**. This confirms sitemap processing, not search index inclusion. No IndexNow infrastructure or extra URL submissions were added.

## DNS after cutover and verification

Authoritative nameservers: `bingo.ns.cloudflare.com`, `jimmy.ns.cloudflare.com`. The old Shinjiru zone remains available for rollback. Current Cloudflare records:

| Name | Type | Content | TTL | Proxy |
| --- | --- | --- | --- | --- |
| `chaincafe.my` | Worker | `chaincafe` | Auto | Proxied |
| `www.chaincafe.my` | CNAME | `chaincafe.my` | Auto | Proxied |
| `mail.chaincafe.my` | A | `124.217.251.156` | 1800 | DNS-only |
| `ftp.chaincafe.my` | A | `124.217.251.156` | 1800 | DNS-only |
| `chaincafe.my` | MX | Priority 0, `mail.chaincafe.my` | 1800 | DNS-only |
| `chaincafe.my` | TXT | Google's issued `google-site-verification` value | Auto/300 | DNS-only |
| `27b20dc7e94e38866444e1d9575fd17c.chaincafe.my` | CNAME | `verify.bing.com` | Auto/300 | DNS-only |

Keep the verification records to retain ownership. No existing mail or verification records were removed. FTP continues resolving to the original server independently of the new apex.

## Release validation and Git procedure

The only runtime configuration change is the apex Custom Domain route in `wrangler.jsonc`; the deployed HTML/assets remain unchanged. `tools/check_site.py` now also checks nine canonical host/HTTPS redirects and exact path/query preservation. `.env.example` documents the optional Windows CLI certificate-store setting without credentials. README and the historical audit link to this current record.

Validation commands used: `python tools/check_site.py`, local/staging/production `--base-url` variants, `node --check public/script.js`, `git diff --check`, authenticated `npx.cmd --yes wrangler@latest whoami`, `deploy --dry-run`, and `deploy`. DNS verification used read-only `nslookup`; TLS/endpoint checks used `curl.exe` with certificate verification enabled. Browser checks covered dashboards, five viewport widths, navigation, legal pages, links, image loading and console output. Four HTML documents passed the earlier HTML conformance check without errors or warnings.

Required release sequence: inspect status/diff and credentials scope, `git add -A`, commit `feat: complete Cha In production deployment`, `git fetch origin`, `git rebase origin/main`, then `git push origin HEAD:main` without force. Verify the connected Cloudflare build and production/staging responses after that push. The final task handoff records the resulting commit, push and post-push validation outcomes; this avoids placing a self-referential release hash in its own commit.

The first completion commit **92293545abcd1d2860124985dfe1be0537c313bf** pushed successfully to `main` without conflicts. Cloudflare build **6906a15d-d338-4213-aad6-c40e79c4882c**, displaying that exact commit and subject, completed successfully in **28 seconds**. Wrangler confirmed its deployment at **08:02:59 UTC**, version **5667b921-c0ee-41ba-9201-55159f647c5f**, receiving 100% of traffic. Full production and staging HTTP checks passed again afterward. The production browser retained its canonical, one H1, loaded hero and clean warning/error console. Production robots.txt matched the repository byte for byte. The subsequent documentation update records Bing's completed processing and Google's published website edit, which became available after the first push.

## Current first-party references

- [Cloudflare full DNS setup](https://developers.cloudflare.com/dns/zone-setups/full-setup/setup/)
- [Cloudflare Workers Custom Domains](https://developers.cloudflare.com/workers/configuration/routing/custom-domains/)
- [Single Redirect settings](https://developers.cloudflare.com/rules/url-forwarding/single-redirects/settings/)
- [Shinjiru nameserver changes](https://247livesupport.biz/help/en-us/40-client-area/495-how-to-change-name-server-ns)
- [Shinjiru .MY domain management](https://www.shinjiru.com.my/domain/mydomain/)
