# Cha In Café 茶颖 landing site

Static café information for **https://chaincafe.my/**. Online ordering links to **https://chaincafe.niagaai.my/**, with WhatsApp as a contact fallback.

## Architecture and deployment status

- Cloudflare **Workers Static Assets**, Worker name `chaincafe`, assets in `./public`.
- Semantic HTML, WebP, local CSS and minimal vanilla JavaScript. No framework, Worker JavaScript, build step, analytics, tracking, fonts service, cookies or application environment variables.
- `wrangler.jsonc` sets `404-page` and `auto-trailing-slash` handling. Unknown URLs must return the branded page with HTTP **404**.
- Intended production: `chaincafe.my` → Worker Custom Domain → static assets. Canonical, social and structured-data URLs stay on `https://chaincafe.my/`.
- `workers_dev: true` retains diagnostics; `preview_urls: false` disables additional version preview URLs. `public/_headers` sends `X-Robots-Tag: noindex` only on `chaincafe.brianchu1986.workers.dev`.
- **Cutover is pending.** On 15 September 2026, Wrangler reported no authentication. After the Git push, the Workers URL began serving the new source and passed remote checks, including staging noindex. The deployment mechanism is unverified. The apex still failed HTTPS certificate validation and used external authoritative nameservers. See [deployment audit](docs/deployment-2026-09-15.md).
- No production route is configured yet. Add it only after inspecting account/zone/routing and passing staging checks. This repository has no automatic deployment workflow; a Git push does not establish a Worker deployment.

## Local preview and validation

```powershell
python -m http.server 8001 -d public
```

Open `http://localhost:8001/`. Python does **not** apply Cloudflare headers, redirects or branded missing-page handling. Use Wrangler on a separate port to test asset routing:

```powershell
npx wrangler@latest dev --ip 127.0.0.1 --port 8787
```

Leave the preview running and run checks in another terminal:

```powershell
python tools/check_site.py
python tools/check_site.py --base-url http://127.0.0.1:8787
node --check public/script.js
npx wrangler@latest deploy --dry-run
git diff --check
```

The checker validates source content and optionally HTTP routes, assets, security headers, canonical URLs and crawler policy. Also use an HTML conformance validator and review a browser at 360, 390, 768, 1024 and 1440 pixels, including keyboard navigation and console errors.

## Deploy and attach the production domain

1. Run `npx wrangler@latest whoami`. Stop deployment if authentication or permissions are missing. Authenticate securely outside the repository; never store deployment credentials in `.env`, `.env.example`, source, logs or Git.
2. Inspect the existing `chaincafe` Worker and all `chaincafe.my` DNS records, Pages domains, Worker routes/Custom Domains, Page Rules, Redirect Rules and applicable Bulk Redirects. Confirm account and zone identity. Record the rollback snapshot below. Public DNS cannot reveal the complete configuration.
3. Confirm the Worker is not already serving production traffic before the initial staging upload. Deploy the route-free configuration:

   ```powershell
   npx wrangler@latest deploy
   ```

4. Read the actual URL from Wrangler output. Expected diagnostic URL: `https://chaincafe.brianchu1986.workers.dev/`. Verify it with the checker and browser:

   ```powershell
   python tools/check_site.py --base-url https://chaincafe.brianchu1986.workers.dev
   ```

5. Confirm an active Cloudflare zone and preserve existing DNS, including mail and verification records. The observed external nameservers need investigation; a nameserver migration requires a complete zone inventory and migration plan. Do not blindly replace apex records or change nameservers.
6. After staging passes and any conflict has a safe rollback, add this top-level Wrangler field and redeploy:

   ```json
   "routes": [
     { "pattern": "chaincafe.my", "custom_domain": true }
   ]
   ```

   Cloudflare Custom Domains manage the necessary DNS record and certificate. An existing CNAME may conflict: replace only the exact conflicting record when safe. Never redirect `chaincafe.my` to `workers.dev`.
7. `www.chaincafe.my` currently exists. Preserve support with a hostname-specific **301** to `https://chaincafe.my/<same path>`, preserving query strings, after the apex works. Configure this in the inspected hosting/Cloudflare routing state; path-only `_redirects` rules are not hostname routing.
8. Verify production using the checker, `curl -I`, `curl -L` and a browser. Keep staging noindex. Production homepage must have neither an HTML nor HTTP `noindex` directive.

## Post-deployment checks

```powershell
python tools/check_site.py --base-url https://chaincafe.my
curl.exe -I https://chaincafe.my/
curl.exe -L https://chaincafe.my/contact_us
curl.exe -I https://chaincafe.brianchu1986.workers.dev/
curl.exe -I "https://www.chaincafe.my/terms/?source=verification"
```

Check `/`, `/terms/`, `/refund-policy/`, `/robots.txt`, `/sitemap.xml`, all six legacy redirects (with and without trailing slashes), and `/nonexistent-test-path`. Confirm valid HTTPS, 200 pages/assets, actual 404 status, security headers, canonical URLs and staging noindex. Cloudflare applies redirects before `_headers`; inspect their destinations too.

Review mobile navigation, keyboard focus, WhatsApp, telephone, directions and Facebook links, image loading including `cover.webp`, JSON-LD and the console. Re-test Niaga separately; a reachable storefront does not prove successful checkout. Run Lighthouse against production once valid HTTPS and the intended site are available; report actual measurements.

## Rollback

Before any production change, save a timestamped snapshot outside `public/`, without credentials:

- Relevant DNS hostname, type, content/target, TTL and proxy state.
- Nameservers, previous origin/destination, rule definitions and enabled state.
- Pages domains, Worker routes/Custom Domains and current deployment/version.
- Exact proposed changes and their inverses, including DNS record replacements.

If verification fails, restore only the exact changed association/rule/record when the reversal is unambiguous. Worker version rollback restores assets/code; it does not restore DNS or redirect rules. Stop if restoration is ambiguous. The audit's public observations are **not** a complete rollback snapshot. No DNS or production-routing changes were initiated during this preparation. The Workers endpoint updated after the Git push through an unverified deployment mechanism.

## Content, assets and indexing

- Business facts and JSON-LD live in `public/index.html`; keep name, address, phone and daily 12:00–21:30 hours consistent.
- `CHA IN F & B PLT`, `LLP0017890-LGN`, effective registration **1 October 2018**, describe the legal operator. The date is not a café opening/founding date and is not used as `foundingDate`.
- Preserve `#cafe`, `#website` and `#webpage` IDs. Add only verified facts; do not add unsupported ratings, prices, cuisine, delivery/halal claims or FAQ schema.
- `public/robots.txt` explicitly allows OAI-SearchBot and allows Googlebot/Bingbot through the wildcard group. GPTBot policy is unchanged. Robots permission does not prove that a firewall allows real crawlers.
- The sitemap lists only the indexable canonical homepage. Update `lastmod` only for significant content, link or structured-data changes.
- Terms, refund policy and the 404 template retain `noindex, follow`. They remain crawlable so engines can read that directive.
- No `llms.txt`, hidden AI-only content or IndexNow service is required for this implementation.
- Local WebP assets: `cha-in-mark.webp` (192 × 192), `cha-in-wordmark.webp`, `cover.webp` (1672 × 941), `cha-in-social-card.webp` (1200 × 630). The hero has intrinsic dimensions and high fetch priority.
- Ordering links occur on all four HTML pages. Search for `https://chaincafe.niagaai.my/` when maintaining the destination. Keep WhatsApp fallback at `https://wa.me/60176151036`.

## Search engine follow-up

After the real production domain passes verification:

1. Add/verify the `chaincafe.my` **domain property** in Google Search Console.
2. Submit `https://chaincafe.my/sitemap.xml`.
3. Inspect `https://chaincafe.my/` and request indexing when appropriate.
4. Monitor indexing, crawl failures, site-name selection and actual query data.
5. Verify the site in Bing Webmaster Tools and submit the same sitemap.
6. Compare business details with the Google Business Profile and Facebook listing.

No Search Console/Bing account verification has been performed. Indexing, inclusion in AI answers and ranking are not guaranteed. First-party references are linked in the deployment audit.
