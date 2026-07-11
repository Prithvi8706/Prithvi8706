#!/usr/bin/env python3
"""Generates assets/telemetry.svg — a silver liquid-glass stats panel from live GitHub data.
Runs unauthenticated (stars/repos/followers/languages) or with GITHUB_TOKEN (adds contributions)."""
import json, os, sys, datetime, urllib.request

USER = "Prithvi8706"
TOKEN = os.environ.get("GITHUB_TOKEN", "")

def api(url, payload=None):
    req = urllib.request.Request(url, data=json.dumps(payload).encode() if payload else None)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "telemetry-builder")
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    if payload:
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

try:
    user = api(f"https://api.github.com/users/{USER}")
    repos = api(f"https://api.github.com/users/{USER}/repos?per_page=100&type=owner")
except Exception as e:
    print(f"API unavailable ({e}); writing placeholder telemetry", file=sys.stderr)
    user, repos = {"followers": 0, "public_repos": 0}, []

stars = sum(r["stargazers_count"] for r in repos)
followers = user.get("followers", 0)
public_repos = user.get("public_repos", len(repos))

langs = {}
for r in repos:
    if r.get("fork"):
        continue
    l = r.get("language")
    if l:
        langs[l] = langs.get(l, 0) + 1
top = sorted(langs.items(), key=lambda x: -x[1])[:4]
if not top:
    top = [("Python", 4), ("TypeScript", 3), ("Jupyter", 2), ("PowerShell", 1)]
lang_total = sum(v for _, v in top) or 1

contrib = None
if TOKEN:
    q = {"query": 'query{user(login:"%s"){contributionsCollection{contributionCalendar{totalContributions}}}}' % USER}
    try:
        g = api("https://api.github.com/graphql", q)
        contrib = g["data"]["user"]["contributionsCollection"]["contributionCalendar"]["totalContributions"]
    except Exception:
        contrib = None

if contrib is not None:
    hero_num, hero_label = f"{contrib:,}", "CONTRIBUTIONS · PAST YEAR"
else:
    hero_num, hero_label = f"{public_repos}", "PUBLIC REPOSITORIES"

stamp = datetime.date.today().isoformat()

# language bars (max width 300)
bars = ""
by = 118
for name, count in top:
    w = max(24, int(300 * count / lang_total))
    bars += f'''
    <text x="640" y="{by}" class="mono" font-size="10.5" letter-spacing="1.5" fill="#98989d">{name.upper()}</text>
    <rect x="640" y="{by+8}" width="300" height="4" rx="2" fill="#1c1c1f"/>
    <rect x="640" y="{by+8}" width="{w}" height="4" rx="2" fill="#c7c7cc" fill-opacity="0.75">
      <animate attributeName="width" from="0" to="{w}" dur="1.4s" begin="0.4s" fill="freeze" calcMode="spline" keySplines="0.22 1 0.36 1" keyTimes="0;1" values="0;{w}"/>
    </rect>'''
    by += 40

svg = f'''<svg viewBox="0 0 1000 300" width="100%" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="GitHub telemetry">
  <defs>
    <radialGradient id="tMist" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#f5f5f7" stop-opacity="0.09"/>
      <stop offset="100%" stop-color="#f5f5f7" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="tEdge" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#ffffff" stop-opacity="0"/>
      <stop offset="50%" stop-color="#ffffff" stop-opacity="0.45"/>
      <stop offset="100%" stop-color="#ffffff" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="tSweep" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#ffffff" stop-opacity="0"/>
      <stop offset="50%" stop-color="#ffffff" stop-opacity="0.06"/>
      <stop offset="100%" stop-color="#ffffff" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="tNum" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#ffffff"/>
      <stop offset="60%" stop-color="#e5e5ea"/>
      <stop offset="100%" stop-color="#98989d"/>
    </linearGradient>
    <filter id="tBlur" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="34"/></filter>
    <clipPath id="tClip"><rect x="20" y="20" width="960" height="260" rx="24"/></clipPath>
  </defs>
  <style>
    .sans {{ font-family: -apple-system, 'SF Pro Display', 'Segoe UI', 'Helvetica Neue', Arial, sans-serif; }}
    .mono {{ font-family: 'SF Mono', ui-monospace, 'Cascadia Code', Consolas, Menlo, monospace; }}
    @keyframes td {{ 0%,100%{{transform:translate(0,0)}} 50%{{transform:translate(50px,18px)}} }}
    .tm {{ animation: td 27s ease-in-out infinite; }}
    .tm2 {{ animation: td 35s ease-in-out infinite reverse; }}
    @keyframes tsw {{ 0%{{transform:translateX(-260px)}} 100%{{transform:translateX(1040px)}} }}
    .tsweep {{ animation: tsw 8.5s cubic-bezier(.4,0,.2,1) infinite; }}
  </style>

  <rect width="1000" height="300" fill="#0a0a0a"/>
  <rect x="20" y="20" width="960" height="260" rx="24" fill="#f5f5f7" fill-opacity="0.045"
    stroke="#ffffff" stroke-opacity="0.13" stroke-width="1"/>
  <rect x="48" y="20.5" width="904" height="1.3" fill="url(#tEdge)"/>
  <g clip-path="url(#tClip)">
    <g filter="url(#tBlur)">
      <g class="tm"><ellipse cx="180" cy="260" rx="200" ry="90" fill="url(#tMist)"/></g>
      <g class="tm2"><ellipse cx="840" cy="60" rx="200" ry="90" fill="url(#tMist)"/></g>
    </g>
    <g class="tsweep"><rect x="0" y="0" width="220" height="300" fill="url(#tSweep)" transform="skewX(-18)"/></g>
  </g>

  <text x="64" y="92" class="mono" font-size="10.5" letter-spacing="3.5" fill="#98989d">TELEMETRY</text>

  <text x="64" y="182" class="sans" font-size="72" font-weight="200" letter-spacing="2" fill="url(#tNum)">{hero_num}</text>
  <text x="64" y="212" class="mono" font-size="10.5" letter-spacing="3" fill="#8e8e93">{hero_label}</text>

  <rect x="380" y="70" width="1" height="160" fill="#c7c7cc" opacity="0.12"/>

  <g class="sans">
    <text x="424" y="112" font-size="26" font-weight="300" fill="#f5f5f7">{stars}</text>
    <text x="424" y="130" class="mono" font-size="9.5" letter-spacing="2.5" fill="#8e8e93">STARS</text>
    <text x="424" y="182" font-size="26" font-weight="300" fill="#f5f5f7">{public_repos}</text>
    <text x="424" y="200" class="mono" font-size="9.5" letter-spacing="2.5" fill="#8e8e93">REPOSITORIES</text>
    <text x="424" y="252" font-size="26" font-weight="300" fill="#f5f5f7">{followers}</text>
    <text x="424" y="270" class="mono" font-size="9.5" letter-spacing="2.5" fill="#8e8e93">FOLLOWERS</text>
  </g>

  <rect x="600" y="70" width="1" height="160" fill="#c7c7cc" opacity="0.12"/>

  <text x="640" y="92" class="mono" font-size="10.5" letter-spacing="3.5" fill="#98989d">LANGUAGES</text>
  {bars}

  <text x="952" y="264" text-anchor="end" class="mono" font-size="9" letter-spacing="2" fill="#5a5a5e">SYNC {stamp}</text>
</svg>
'''

out = os.path.join(os.path.dirname(__file__), "..", "assets", "telemetry.svg")
with open(out, "w") as f:
    f.write(svg)
print(f"telemetry.svg written — {hero_label.lower()}: {hero_num}, stars {stars}, repos {public_repos}, followers {followers}, langs {[n for n,_ in top]}")
