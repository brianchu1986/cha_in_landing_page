# Cha In Café 茶颖 landing site

Static café information for **https://chaincafe.my/**. Online ordering links to **https://chaincafe.niagaai.my/**, with WhatsApp as a contact fallback.

## Architecture and deployment status

- Cloudflare **Workers Static Assets**, Worker name `chaincafe`, assets in `./public`.
- Semantic HTML, WebP, local CSS and minimal vanilla JavaScript. No framework, Worker JavaScript, build step, analytics, tracking, fonts service, cookies or application environment variables.
- `.env.example` documents the optional CLI-only `NODE_OPTIONS=--use-system-ca` setting used for Node's Windows certificate trust. It is not a Worker binding or application requirement; certificate verification stays enabled.
- `wrangler.jsonc` sets `404-page` and `auto-trailing-slash` handling. Unknown URLs must return the branded page with HTTP **404**.
- Production: `chaincafe.my` → Worker Custom Domain → static assets. Canonical, social and structured-data URLs stay on `https://chaincafe.my/`.
- `workers_dev: true` retains diagnostics; `preview_urls: false` disables additional version preview URLs. `public/_headers` sends `X-Robots-Tag: noindex` only on `chaincafe.brianchu1986.workers.dev`.
- **Production is live and verified.** Cloudflare activated on 15 September 2026 after the registrar nameserver migration. The apex Custom Domain serves valid HTTPS. A Cloudflare Single Redirect sends www and HTTP apex traffic to canonical HTTPS, preserving path and query strings. Mail remains on the old server; FTP has an independent DNS-only A record. See the current [cutover and rollback record](docs/production-cutover-2026-09-15.md); the earlier [preparation audit](docs/deployment-2026-09-15.md) is historical.
- Wrangler includes the apex Custom Domain route. The Cloudflare dashboard confirmed an existing Workers Builds integration with this GitHub repository's `main` branch, no build command, and deployment command `npx wrangler deploy`. There is no repository GitHub Actions deployment workflow. Verify the actual Cloudflare build/deployment and live responses after a push.

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

## Deploy updates

The current configuration updates the live apex and diagnostic workers.dev endpoint together. Run local checks and the dry-run before deploying. Confirm authentication and account identity; keep deployment credentials outside the repository.

```powershell
npx.cmd wrangler@latest whoami
python tools/check_site.py
node --check public/script.js
npx.cmd wrangler@latest deploy --dry-run
npx.cmd wrangler@latest deploy
python tools/check_site.py --base-url https://chaincafe.brianchu1986.workers.dev
python tools/check_site.py --base-url https://chaincafe.my
```

Cloudflare manages the apex Worker DNS record and certificate. Keep the existing Custom Domain route in `wrangler.jsonc`; do not recreate the old apex A record while the Worker is live. Keep `ftp` and `mail` at `124.217.251.156`, DNS-only, and preserve MX and verification records. The initial migration resolved Cloudflare error 100117 by replacing only the recorded old apex A record before attaching the Custom Domain.

The active **Cha In canonical HTTPS apex** Single Redirect matches `(http.host eq "www.chaincafe.my") or (http.host eq "chaincafe.my" and not ssl)`, redirects with 301 to `concat("https://chaincafe.my", http.request.uri.path)`, and preserves query strings. The existing www CNAME to the apex is proxied. These dashboard rules are documented in the cutover record and are not managed by the static `_redirects` file.

Managed robots.txt configuration is disabled so Cloudflare serves `public/robots.txt` unchanged. Keep staging noindex and production homepage indexable.

## Post-deployment checks

```powershell
python tools/check_site.py --base-url https://chaincafe.my
curl.exe -I https://chaincafe.my/
curl.exe -L https://chaincafe.my/contact_us
curl.exe -I https://chaincafe.brianchu1986.workers.dev/
curl.exe -I "https://www.chaincafe.my/terms/?source=verification"
```

Check `/`, `/terms/`, `/refund-policy/`, `/robots.txt`, `/sitemap.xml`, all six legacy redirects (with and without trailing slashes), and `/nonexistent-test-path`. Confirm valid HTTPS, 200 pages/assets, actual 404 status, security headers, canonical URLs and staging noindex. Cloudflare applies redirects before `_headers`; inspect their destinations too.

Review mobile navigation, keyboard focus, WhatsApp, telephone, directions and Facebook links, image loading including `cover.webp`, JSON-LD and the console. Re-test Niaga separately; a reachable storefront does not prove successful checkout. Cloudflare's one-time production Lighthouse test on 15 September 2026 scored **100 desktop / 99 mobile**, with **CLS 0** on both; full measurements are in the cutover record. These are synthetic results for that run.

## Rollback

Before any production change, save a timestamped snapshot outside `public/`, without credentials:

- Relevant DNS hostname, type, content/target, TTL and proxy state.
- Nameservers, previous origin/destination, rule definitions and enabled state.
- Pages domains, Worker routes/Custom Domains and current deployment/version.
- Exact proposed changes and their inverses, including DNS record replacements.

If verification fails, restore only the exact changed association/rule/record when the reversal is unambiguous. Worker version rollback restores assets/code; it does not restore DNS or redirect rules. Stop if restoration is ambiguous. Use the complete [pre-change snapshot and rollback procedure](docs/production-cutover-2026-09-15.md), which includes the old authoritative zone, origin and Worker version. The old Shinjiru zone remains available. Returning to that origin would also return to its pre-existing invalid apex certificate.

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

Completed on 15 September 2026 after production verification:

- Google Search Console **Domain Property `chaincafe.my`** verified through an apex TXT record. The sitemap reports **Success**, with **1 discovered page**.
- Live homepage inspection passed: available to Google, indexable, successful fetch, and user-declared canonical `https://chaincafe.my/`. Google accepted **one** indexing request. The stored index report still describes the old site's duplicate/www canonical; it is not evidence that the new homepage has been indexed.
- Bing Webmaster Tools verified through its site-specific DNS CNAME. The same sitemap was submitted and is **Processing**. Google import was canceled when it requested additional access across all verified Search Console sites.
- Google Business Profile phone and physical address match. Its existing **Cha In 茶穎** name was preserved. The Tuesday correction is published, making all seven days **12:00–21:30**. The verified apex website was submitted to replace the Facebook website field and is pending Google's review; the Facebook social profile remains intact.

Preserve both search-engine verification DNS records. Monitor sitemap processing, indexing/canonical selection and the business-profile website review; avoid repeating indexing requests without new evidence. Indexing, inclusion in AI answers and ranking are not guaranteed. Actual dashboard results and first-party references are recorded in the [cutover log](docs/production-cutover-2026-09-15.md).
