# Cha In Café 茶颖 landing site

Production-ready static landing site for `chaincafe.my`. It introduces Cha In Café, directs online orders to the Niaga AI storefront, keeps local visit/contact information easy to find, and preserves important routes from the previous site.

## Architecture

- Plain semantic HTML and modern CSS
- No framework, build pipeline, JavaScript dependency, analytics, cookies, backend, or environment variables
- All deployable files live in `public/`
- Cloudflare Pages is the intended host; GitHub is the source repository

The site includes the homepage, Terms & Conditions, Refund & Returns Policy, branded 404 page, search-engine files, security headers, and legacy redirects.

## Preview locally

From the repository root, run:

```powershell
python -m http.server 8001 -d public
```

Then open `http://localhost:8001/`.

Python's basic server does not apply Cloudflare's `_redirects` or `_headers`; those take effect on a Pages deployment. Visit `/terms/`, `/refund-policy/`, and `/404.html` directly during local review.

## Important URLs

- Canonical website: `https://chaincafe.my/`
- Online ordering: `https://chaincafe.niagaai.my/`
- WhatsApp: `https://wa.me/60176151036`
- Facebook: `https://www.facebook.com/Cha.In.my/`

## Cloudflare Pages configuration

In the Cloudflare Dashboard:

1. Open **Workers & Pages**.
2. Choose **Create** → **Pages** → **Connect to Git**.
3. Connect GitHub and select `brianchu1986/cha_in_landing_page`.
4. Use these build settings:

   - Production branch: `main`
   - Framework preset: `None`
   - Build command: `exit 0` (or leave blank if the current UI accepts it)
   - Build output directory: `public`

Every push to `main` will create a new production deployment after the Git integration is active. Pull requests and non-production branches can be used for preview deployments.

## Custom-domain cutover

Do not change the current live domain until the Pages preview has been visually verified.

After preview approval:

1. Add `chaincafe.my` as the production custom domain in the Pages project.
2. Optionally add `www.chaincafe.my`.
3. Configure a Cloudflare redirect from `www` to `https://chaincafe.my/`, preserving the path and query string.
4. Configure a host-based Cloudflare redirect from the production `*.pages.dev` hostname to `https://chaincafe.my/`, also preserving the path and query string, to avoid duplicate public URLs.
5. Verify HTTPS, the apex domain, both legacy redirects, and the canonical tags after cutover.

No GitHub Pages `CNAME` file is used.

## Maintaining business details

Business content is maintained in:

- `public/index.html`: customer-facing details and JSON-LD structured data
- `public/terms/index.html`: published Terms & Conditions
- `public/refund-policy/index.html`: published refund policy
- `public/sitemap.xml`: canonical public routes

When an address, phone number, or opening hour changes, update both the visible homepage content and JSON-LD in `public/index.html`. Update the policy date when legal content changes.

## Images and brand assets

Assets are in `public/assets/`:

- `cha-in-mark.webp`: owned Cha In character mark migrated from the current site
- `cha-in-wordmark.webp`: owned Cha In wordmark migrated from the current site
- `cover.webp`: 1672 × 941 homepage hero image, loaded eagerly as the page's primary visual
- `cha-in-social-card.webp`: 1200 × 630 social-sharing image used only by Open Graph and Twitter metadata

The hero uses the owned `cover.webp` product photograph with intrinsic dimensions and eager loading to minimize layout shift and support LCP performance. Keep the source image local, truthfully described, and free of third-party dependencies when replacing it.

## Changing the order destination

The Niaga AI order URL appears in the homepage and 404 page. To change it later, search the repository for:

```text
https://chaincafe.niagaai.my/
```

Replace every occurrence, then test the header, hero, ordering notice, footer, mobile menu, and 404 links before publishing.

## Post-launch SEO checklist

After the production custom-domain cutover:

1. Verify `chaincafe.my` in Google Search Console.
2. Submit `https://chaincafe.my/sitemap.xml` in the Sitemaps report.
3. Inspect `https://chaincafe.my/` with URL Inspection and request indexing when appropriate.
4. Monitor indexing, crawl issues, site-name selection, and real search queries without assuming inclusion or ranking.
5. Verify that the name, address, phone number, and opening hours match the Google Business Profile, Facebook page, and other current public listings.
6. Add the site to Bing Webmaster Tools and submit the same sitemap. IndexNow is intentionally omitted because this small static site changes infrequently.
7. Confirm Cloudflare preview URLs return `X-Robots-Tag: noindex`.
8. After attaching the custom domain, use Cloudflare Bulk Redirects to send the production `*.pages.dev` hostname to `https://chaincafe.my/` while preserving the path and query string.

The Terms & Conditions and Refund Policy remain publicly accessible but use `noindex, follow`; the sitemap therefore lists only the indexable homepage. The 404 page also remains `noindex`.
