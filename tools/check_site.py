"""Check Cha In source and optional Workers HTTP deployment (Python stdlib only)."""

import argparse
from collections import Counter
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote, urljoin, urlsplit
from urllib.robotparser import RobotFileParser
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
CANONICAL = "https://chaincafe.my/"
STAGING = "chaincafe.brianchu1986.workers.dev"


class Document(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.elements = []
        self.headings = []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        self.elements.append((tag, dict(attrs)))
        if re.fullmatch(r"h[1-6]", tag):
            self.headings.append(int(tag[1]))

    def attrs(self, tag):
        return [attrs for name, attrs in self.elements if name == tag]


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def check_robots(source):
    robots = RobotFileParser()
    robots.parse(source.splitlines())
    for bot in ("Googlebot", "Bingbot", "OAI-SearchBot"):
        require(robots.can_fetch(bot, CANONICAL), f"{bot} blocked")
    require(robots.site_maps() == [CANONICAL + "sitemap.xml"], "Sitemap directive")


def check_sitemap(source):
    tree = ET.fromstring(source)
    urls = tree.findall("{http://www.sitemaps.org/schemas/sitemap/0.9}url")
    require([u.findtext("{http://www.sitemaps.org/schemas/sitemap/0.9}loc") for u in urls]
            == [CANONICAL], "Sitemap must list the canonical homepage only")


def source_checks():
    for path in sorted(PUBLIC.rglob("*.html")):
        source = path.read_text(encoding="utf-8")
        doc = Document(source)
        ids = [a["id"] for _, a in doc.elements if "id" in a]
        require(not [k for k, v in Counter(ids).items() if v > 1], f"Duplicate IDs: {path}")
        require(doc.headings.count(1) == 1, f"One H1 required: {path}")
        require(all(b <= a + 1 for a, b in zip(doc.headings, doc.headings[1:])), f"Heading jump: {path}")
        require(len(doc.attrs("main")) == 1, f"Main landmark: {path}")
        for img in doc.attrs("img"):
            require(all(k in img for k in ("alt", "width", "height")), f"Image attributes: {path}")
        for tag, attrs in doc.elements:
            for key in ("href", "src"):
                if key not in attrs:
                    continue
                url = urlsplit(attrs[key])
                if url.scheme or url.netloc:
                    continue
                target = PUBLIC / unquote(url.path.lstrip("/")) if url.path.startswith("/") else path.parent / unquote(url.path)
                if not url.path:
                    target = path
                elif target.is_dir():
                    target /= "index.html"
                require(target.is_file(), f"Missing local target: {attrs[key]} in {path}")
                if url.fragment:
                    target_ids = [a.get("id") for _, a in Document(target.read_text(encoding="utf-8")).elements]
                    require(unquote(url.fragment) in target_ids, f"Missing fragment: {attrs[key]}")
        robots = [a.get("content", "") for a in doc.attrs("meta") if a.get("name") == "robots"]
        require((path == PUBLIC / "index.html") == (not any("noindex" in v for v in robots)), f"Indexing policy: {path}")
        canonicals = [a.get("href") for a in doc.attrs("link") if a.get("rel") == "canonical"]
        if path.name != "404.html":
            route = path.parent.relative_to(PUBLIC).as_posix()
            expected = CANONICAL if route == "." else CANONICAL + route + "/"
            require(canonicals == [expected], f"Canonical: {path}")
        print(f"PASS HTML structure, IDs, headings, images, links, indexing: {path.relative_to(ROOT)}")
    homepage = (PUBLIC / "index.html").read_text(encoding="utf-8")
    graph = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', homepage, re.S)[1])["@graph"]
    require([n["@type"] for n in graph] == ["CafeOrCoffeeShop", "WebSite", "WebPage"], "Entity graph types")
    require([n["@id"] for n in graph] == [CANONICAL + "#" + s for s in ("cafe", "website", "webpage")], "Stable IDs")
    cafe = graph[0]
    require(cafe["legalName"] == "CHA IN F & B PLT" and cafe["identifier"]["value"] == "LLP0017890-LGN", "Legal entity")
    require(cafe["telephone"] == "+60176151036", "Telephone")
    require(cafe["openingHoursSpecification"]["opens"] == "12:00" and cafe["openingHoursSpecification"]["closes"] == "21:30", "Hours")
    require(len(set(cafe["openingHoursSpecification"]["dayOfWeek"])) == 7, "Daily hours")
    forbidden = ("foundingDate", "aggregateRating", "reviews", "priceRange", "servesCuisine", "offers", "FAQPage")
    require(not any(f'"{key}"' in json.dumps(graph) for key in forbidden), "Unverified schema fields")
    require('datetime="2018-10-01"' in homepage and "Effective registration date" in homepage, "Visible registration date")
    check_robots((PUBLIC / "robots.txt").read_text())
    check_sitemap((PUBLIC / "sitemap.xml").read_text())
    css = (PUBLIC / "styles.css").read_text()
    require(set(re.findall(r"var\((--[\w-]+)", css)) <= set(re.findall(r"(--[\w-]+)\s*:", css)), "Undefined CSS custom property")
    print("PASS JSON-LD, business facts, robots, sitemap, CSS variables")


def request(base, path, host=None, follow=False):
    # curl uses Windows system TLS trust. Do not disable certificate verification.
    cmd = ["curl", "--silent", "--show-error", "--max-time", "25", "--dump-header", "-", "--url", base.rstrip("/") + path]
    if follow:
        cmd += ["--location", "--max-redirs", "5"]
    if host:
        cmd += ["--header", "Host: " + host]
    result = subprocess.run(cmd, capture_output=True)
    require(result.returncode == 0, result.stderr.decode(errors="replace"))
    data = result.stdout
    # Handle interim responses and followed redirects without exposing cookies.
    while data.startswith(b"HTTP/"):
        raw, data = data.split(b"\r\n\r\n", 1)
        lines = raw.decode(errors="replace").splitlines()
        status = int(lines[0].split()[1])
        headers = dict((k.lower(), v.strip()) for k, v in (line.split(":", 1) for line in lines[1:] if ":" in line))
    return status, headers, data


def http_checks(base):
    hostname = urlsplit(base).hostname
    require(hostname in ("localhost", "127.0.0.1", "chaincafe.my", STAGING), "Unexpected test host")
    staging = hostname == STAGING
    security = ("content-security-policy", "x-content-type-options", "referrer-policy", "permissions-policy", "cross-origin-opener-policy")
    paths = {"/": 200, "/terms/": 200, "/refund-policy/": 200, "/robots.txt": 200, "/sitemap.xml": 200, "/nonexistent-test-path": 404}
    paths.update({"/" + p.relative_to(PUBLIC).as_posix(): 200 for p in PUBLIC.rglob("*") if p.is_file() and (p.suffix == ".webp" or p.name in ("styles.css", "script.js"))})
    for path, expected in paths.items():
        status, headers, body = request(base, path)
        require(status == expected, f"{path}: expected {expected}, got {status}")
        require(all(k in headers for k in security), f"{path}: missing security headers")
        require(("noindex" in headers.get("x-robots-tag", "")) == staging, f"{path}: wrong hostname indexing header")
        if path in ("/", "/terms/", "/refund-policy/", "/nonexistent-test-path"):
            local = "404.html" if expected == 404 else path.strip("/") + "/index.html" if path != "/" else "index.html"
            require(body == (PUBLIC / local).read_bytes(), f"{path}: deployed HTML differs from source")
        if path == "/robots.txt":
            check_robots(body.decode())
        if path == "/sitemap.xml":
            check_sitemap(body.decode())
        print(f"PASS HTTP {status}, headers/content: {path}")
    for line in (PUBLIC / "_redirects").read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        source, destination, code = line.split()
        status, headers, _ = request(base, source)
        require(status == int(code) and urljoin(base, headers.get("location", "")) == urljoin(base, destination), f"Legacy redirect: {source}")
        require(request(base, source, follow=True)[0] == 200, f"Redirect target: {source}")
        print(f"PASS redirect {source} -> {destination} ({code})")
    if hostname in ("localhost", "127.0.0.1"):
        for host, should_noindex in ((STAGING, True), ("chaincafe.my", False)):
            for path in ("/", "/assets/cover.webp", "/nonexistent-test-path"):
                _, headers, _ = request(base, path, host=host)
                require(("noindex" in headers.get("x-robots-tag", "")) == should_noindex, f"Host-specific noindex: {host}{path}")
        print("PASS staging noindex and production indexability using local Host headers")
    if hostname == "chaincafe.my":
        for redirect_base in ("https://www.chaincafe.my", "http://www.chaincafe.my", "http://chaincafe.my"):
            for path in ("/", "/terms/?x=1", "/refund-policy/?x=1&source=qa%20check"):
                status, headers, _ = request(redirect_base, path)
                expected = CANONICAL.rstrip("/") + path
                require(status == 301 and headers.get("location") == expected,
                        f"Canonical host/HTTPS redirect: {redirect_base}{path}")
                require(request(redirect_base, path, follow=True)[0] == 200,
                        f"Canonical redirect destination: {redirect_base}{path}")
                print(f"PASS canonical 301 with path/query preserved: {redirect_base}{path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", help="Wrangler localhost or the exact Cha In production/diagnostic host")
    args = parser.parse_args()
    source_checks()
    if args.base_url:
        http_checks(args.base_url)
