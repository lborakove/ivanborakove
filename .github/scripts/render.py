#!/usr/bin/env python3
"""
Render the profile's dynamic SVGs from the GitHub GraphQL API (stdlib only).

  bughunt.svg   - a pixel-art hacker hunts bugs and eats commits across the
                  contribution graph (maze-chase style, fully SMIL/CSS animated)
  neofetch.svg  - neofetch-style telemetry card with live account stats

Usage:  GH_TOKEN=... GH_LOGIN=lborakove python3 render.py <out_dir>
"""
from __future__ import annotations

import datetime as dt
import json
import os
import random
import sys
import urllib.request
from html import escape

# ───────────────────────────── palette ─────────────────────────────
BG0, BG1 = "#05070a", "#0b1117"
BORDER = "#1b2a22"
GREEN, CYAN, MAG, RED, YEL = "#39ff14", "#00e5ff", "#ff2bd6", "#ff3b5c", "#ffd84d"
TXT, DIM, FAINT = "#d7dde4", "#6b7785", "#2a3540"
LEVEL = {
    "NONE": "#161b22",
    "FIRST_QUARTILE": "#0e4429",
    "SECOND_QUARTILE": "#006d32",
    "THIRD_QUARTILE": "#26a641",
    "FOURTH_QUARTILE": "#39d353",
}
PWNED = "#0a1f12"
FONT = "'JetBrains Mono','Fira Code','DejaVu Sans Mono',Menlo,Consolas,'Courier New',monospace"

# ───────────────────────────── sprites ─────────────────────────────
# Hooded hacker (original pixel art). m = mouth (animated), g = glowing eyes.
HACKER = [
    "....hhh....",
    "..hhHHHhh..",
    ".hHHHHHHHh.",
    ".hHHfffHHh.",
    "hHHfffffHHh",
    "hHfgfffgfHh",
    "hHfffffffHh",
    "hHHfmmmfHHh",
    ".hHHfffHHh.",
    "hhHHHHHHHhh",
    "hHHHHHHHHHh",
]
HACKER_COL = {"h": "#5b7089", "H": "#2b3846", "f": "#020304", "g": GREEN}

BUG = [
    "a.....a",
    ".a...a.",
    ".rrrrr.",
    "lrwrwrl",
    ".rrrrr.",
    "lrrrrrl",
    ".l...l.",
]
BUG_COL = {"a": "#ff8fa3", "r": RED, "w": "#ffffff", "l": "#c81e3c"}


def sprite(rows, colors, px, skip=""):
    out = []
    for y, row in enumerate(rows):
        x = 0
        while x < len(row):
            c = row[x]
            if c == "." or c in skip:
                x += 1
                continue
            run = 1
            while x + run < len(row) and row[x + run] == c:
                run += 1
            out.append(
                f'<rect x="{x * px:g}" y="{y * px:g}" width="{run * px:g}" height="{px:g}" fill="{colors[c]}"/>'
            )
            x += run
    return "".join(out)


def mouth(rows, px, color):
    out = []
    for y, row in enumerate(rows):
        for x, c in enumerate(row):
            if c == "m":
                out.append(f'<rect x="{x * px:g}" y="{y * px:g}" width="{px:g}" height="{px:g}" fill="{color}"/>')
    return "".join(out)


# ───────────────────────────── data ─────────────────────────────
QUERY = """
query($login: String!) {
  user(login: $login) {
    login
    createdAt
    followers { totalCount }
    repositories(first: 100, ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC) {
      totalCount
      nodes {
        stargazerCount
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name color } }
        }
      }
    }
    contributionsCollection {
      totalCommitContributions
      totalPullRequestContributions
      totalIssueContributions
      totalPullRequestReviewContributions
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount contributionLevel weekday } }
      }
    }
  }
}
"""


def fetch(login: str, token: str) -> dict:
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode(),
        headers={"Authorization": f"bearer {token}", "User-Agent": "profile-renderer"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        payload = json.load(r)
    if payload.get("errors"):
        raise SystemExit(f"GraphQL error: {payload['errors']}")
    return payload["data"]["user"]


def streaks(days):
    days = sorted(days, key=lambda d: d["date"])
    best = run = 0
    for d in days:
        run = run + 1 if d["contributionCount"] > 0 else 0
        best = max(best, run)
    cur = 0
    seq = list(reversed(days))
    if seq and seq[0]["contributionCount"] == 0:
        seq = seq[1:]  # today not counted yet
    for d in seq:
        if d["contributionCount"] == 0:
            break
        cur += 1
    return cur, best


# ───────────────────────────── bughunt.svg ─────────────────────────────
def render_bughunt(user) -> str:
    cal = user["contributionsCollection"]["contributionCalendar"]
    weeks = cal["weeks"]
    W, H = 880, 250
    STEP, CELL = 15, 11
    GX, GY = (W - len(weeks) * STEP) // 2 + 2, 74

    def center(col, row):
        return GX + col * STEP + CELL / 2, GY + row * STEP + CELL / 2

    cells, contrib = [], []
    for c, wk in enumerate(weeks):
        for d in wk["contributionDays"]:
            r = d["weekday"]
            cells.append((c, r, d))
            if d["contributionCount"] > 0:
                contrib.append((c, r, d["contributionCount"]))

    # bugs: seeded by ISO week so the level changes every week
    today = dt.date.today()
    rng = random.Random(f"{user['login']}-{today.isocalendar()[0]}-{today.isocalendar()[1]}")
    occupied = {(c, r) for c, r, _ in contrib}
    free = [(c, r) for c, r, _ in cells if (c, r) not in occupied and c > 1]
    n_bugs = min(12, len(free))
    # spread bugs across the width
    bugs = []
    if n_bugs:
        bands = len(weeks) / n_bugs
        for i in range(n_bugs):
            band = [p for p in free if int(p[0] // bands) == i and p not in bugs] or free
            bugs.append(rng.choice(band))

    # targets: every bug + the busiest commit cells (capped for loop length)
    commit_targets = [(c, r) for c, r, _ in sorted(contrib, key=lambda t: -t[2])[:40]]
    targets = [("bug", p) for p in bugs] + [("commit", p) for p in commit_targets]

    # greedy nearest-neighbour tour with Manhattan moves (maze-chase feel)
    pos = (-1, 3)
    path = [center(*pos)]
    order = []
    remaining = targets[:]
    while remaining:
        nxt = min(remaining, key=lambda t: abs(t[1][0] - pos[0]) + abs(t[1][1] - pos[1]) * 1.2)
        remaining.remove(nxt)
        (tc, tr) = nxt[1]
        if tr != pos[1]:
            path.append(center(pos[0], tr))  # vertical first, then horizontal
        path.append(center(tc, tr))
        order.append(nxt)
        pos = (tc, tr)
    path.append(center(len(weeks), pos[1]))  # exit stage right

    # timing
    seglen = [abs(b[0] - a[0]) + abs(b[1] - a[1]) for a, b in zip(path, path[1:])]
    total_len = sum(seglen) or 1
    speed = max(140.0, total_len / 34.0)  # px/s, cap route at ~34 s
    T_START = 1.2
    T_RUN = total_len / speed
    T_END = T_START + T_RUN
    T = T_END + 3.6  # hold for the "report submitted" screen

    # time at which each target is reached
    reach = {}
    acc, k = 0.0, 0
    pts = path[1:]
    for i, p in enumerate(pts):
        acc += seglen[i]
        while k < len(order) and center(*order[k][1]) == p:
            reach[order[k][1], order[k][0]] = T_START + acc / speed
            k += 1

    def f(t):
        return f"{min(max(t / T, 0.0), 1.0):.5f}"

    def kt(*ts):
        vals, last = [], 0.0
        for t in ts:
            v = max(min(max(t / T, 0.0), 1.0), last)
            vals.append(v)
            last = v
        return ";".join(f"{v:.5f}" for v in vals)

    anim = f'dur="{T:.2f}s" repeatCount="indefinite"'
    out = []

    # grid
    grid = []
    for c, r, d in cells:
        x, y = GX + c * STEP, GY + r * STEP
        col = LEVEL.get(d["contributionLevel"], LEVEL["NONE"])
        key = ((c, r), "commit")
        if key in reach:
            t = reach[key]
            grid.append(
                f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" fill="{col}">'
                f'<animate attributeName="fill" values="{col};{col};#eaffe0;{PWNED};{PWNED}" '
                f'keyTimes="{kt(0, t, t + 0.05, t + 0.35, T)}" {anim}/></rect>'
            )
        else:
            grid.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" fill="{col}"/>')
    out.append("<g>" + "".join(grid) + "</g>")

    # bugs
    bug_px = 1.6
    bsz = 7 * bug_px
    bug_svg = sprite(BUG, BUG_COL, bug_px)
    found_times = []
    for i, p in enumerate(bugs):
        cx, cy = center(*p)
        t = reach[(p, "bug")]
        found_times.append(t)
        out.append(
            f'<g transform="translate({cx - bsz / 2:.1f},{cy - bsz / 2:.1f})">'
            f'<g class="wig" style="animation-delay:-{i * 0.13:.2f}s">{bug_svg}</g>'
            f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="{kt(0, t, t + 0.06, T)}" {anim}/></g>'
            # +1 popup
            f'<text x="{cx:.1f}" y="{cy - 6:.1f}" text-anchor="middle" class="pop" opacity="0">+BUG'
            f'<animate attributeName="opacity" values="0;0;1;0;0" keyTimes="{kt(0, t, t + 0.05, t + 0.9, T)}" {anim}/>'
            f'<animate attributeName="y" values="{cy - 6:.1f};{cy - 6:.1f};{cy - 22:.1f};{cy - 22:.1f}" '
            f'keyTimes="{kt(0, t, t + 0.9, T)}" {anim}/></text>'
            # burst ring
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="2" fill="none" stroke="{RED}" stroke-width="1.5" opacity="0">'
            f'<animate attributeName="r" values="2;2;14;14" keyTimes="{kt(0, t, t + 0.45, T)}" {anim}/>'
            f'<animate attributeName="opacity" values="0;0;.9;0;0" keyTimes="{kt(0, t, t + 0.02, t + 0.45, T)}" {anim}/>'
            f"</circle>"
        )

    # IDS sweep (independent loop)
    gw = len(weeks) * STEP
    out.append(
        f'<rect x="{GX - 6}" y="{GY - 4}" width="22" height="{7 * STEP + 6}" fill="url(#ids)" opacity=".55">'
        f'<animate attributeName="x" values="{GX - 6};{GX + gw - 16};{GX - 6}" dur="11s" repeatCount="indefinite"/></rect>'
    )

    # hacker
    hpx = 2.0
    hs = 11 * hpx
    body = sprite(HACKER, HACKER_COL, hpx, skip="m")
    m_open = mouth(HACKER, hpx, GREEN)
    m_shut = mouth(HACKER, hpx, HACKER_COL["f"])
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in path)
    out.append(
        f'<g opacity="1"><g transform="translate({-hs / 2:.1f},{-hs / 2:.1f})" filter="url(#glow)">'
        f'{body}<g class="m1">{m_open}</g><g class="m2">{m_shut}</g></g>'
        f'<animateMotion path="{d}" keyPoints="0;0;1;1" keyTimes="{kt(0, T_START, T_END, T)}" '
        f'calcMode="linear" {anim}/></g>'
    )

    # HUD — header
    out.append(
        f'<text x="24" y="31" class="t" fill="{DIM}">~/bughunt <tspan fill="{CYAN}">$</tspan> '
        f'<tspan fill="{TXT}">./hunt --target</tspan> <tspan fill="{GREEN}">contribution-graph</tspan></text>'
    )
    # bug counter (discrete)
    n = len(bugs)
    times = sorted(found_times)
    counter = []  # one stacked <text> per value, each visible in its own time window
    for i in range(n + 1):
        t0 = times[i - 1] if i > 0 else 0.0
        t1 = times[i] if i < n else T + 1
        if i == 0:
            vals, keys = "1;1;0;0", kt(0, t1, t1 + 0.001, T)
        elif i == n:
            vals, keys = "0;0;1;1", kt(0, t0, t0 + 0.001, T)
        else:
            vals, keys = "0;0;1;1;0;0", kt(0, t0, t0 + 0.001, t1, t1 + 0.001, T)
        counter.append(
            f'<text x="{W - 24}" y="31" text-anchor="end" class="t hud" fill="{RED}" opacity="{1 if i == 0 else 0}">'
            f'{i:02d}/{n:02d}<animate attributeName="opacity" values="{vals}" keyTimes="{keys}" {anim}/></text>'
        )
    out.append("".join(counter))
    out.append(f'<text x="{W - 80}" y="31" text-anchor="end" class="t" fill="{DIM}">BUGS FOUND</text>')

    # progress bar
    bx, by, bw = 24, H - 40, 300
    out.append(
        f'<text x="{bx}" y="{by - 8}" class="s" fill="{DIM}">SCAN PROGRESS</text>'
        f'<rect x="{bx}" y="{by}" width="{bw}" height="6" rx="3" fill="{FAINT}"/>'
        f'<rect x="{bx}" y="{by}" width="0" height="6" rx="3" fill="url(#bar)">'
        f'<animate attributeName="width" values="0;0;{bw};{bw}" keyTimes="{kt(0, T_START, T_END, T)}" {anim}/></rect>'
    )
    # legend
    lx = W - 24
    legend = [("pwned", PWNED, None), ("bug", RED, None), ("commit", LEVEL["THIRD_QUARTILE"], None)]
    for label, col, _ in legend:
        tw = len(label) * 7.3
        out.append(f'<text x="{lx}" y="{by + 7}" text-anchor="end" class="s" fill="{DIM}">{label}</text>')
        out.append(f'<rect x="{lx - tw - 16:.1f}" y="{by - 2}" width="10" height="10" rx="2" fill="{col}" stroke="{FAINT}"/>')
        lx -= tw + 32
    total = cal["totalContributions"]
    out.append(
        f'<text x="{W - 24}" y="{by - 8}" text-anchor="end" class="s" fill="{DIM}">'
        f'{total} contributions last year · {n} new bugs spawned this week</text>'
    )

    # mission complete overlay
    out.append(
        f'<g opacity="0"><rect x="{W / 2 - 230}" y="{GY + 22}" width="460" height="60" rx="8" '
        f'fill="#05070a" fill-opacity=".92" stroke="{GREEN}"/>'
        f'<text x="{W / 2}" y="{GY + 48}" text-anchor="middle" class="big" fill="{GREEN}">ALL BUGS TRIAGED</text>'
        f'<text x="{W / 2}" y="{GY + 69}" text-anchor="middle" class="s" fill="{TXT}">'
        f'report submitted · remediation verified · restarting hunt…</text>'
        f'<animate attributeName="opacity" values="0;0;1;1;0" keyTimes="{kt(0, T_END + 0.2, T_END + 0.4, T - 0.3, T)}" {anim}/></g>'
    )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" xml:space="preserve" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="A pixel hacker hunting bugs across the contribution graph">
<title>bughunt // contribution graph</title>
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{BG0}"/><stop offset="1" stop-color="{BG1}"/></linearGradient>
  <linearGradient id="bar" x1="0" x2="1"><stop offset="0" stop-color="{GREEN}"/><stop offset="1" stop-color="{CYAN}"/></linearGradient>
  <linearGradient id="ids" x1="0" x2="1"><stop offset="0" stop-color="{RED}" stop-opacity="0"/><stop offset=".5" stop-color="{RED}" stop-opacity=".22"/><stop offset="1" stop-color="{RED}" stop-opacity="0"/></linearGradient>
  <pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#fff" opacity=".03"/></pattern>
  <filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feDropShadow dx="0" dy="0" stdDeviation="1.6" flood-color="{GREEN}" flood-opacity=".55"/></filter>
</defs>
<style>
  text {{ font-family: {FONT}; }}
  .t {{ font-size: 13px; }} .s {{ font-size: 11px; letter-spacing: .5px; }}
  .hud {{ font-weight: 700; font-size: 15px; }}
  .big {{ font-size: 20px; font-weight: 800; letter-spacing: 4px; }}
  .pop {{ font-size: 9px; font-weight: 700; fill: {RED}; }}
  .m1 {{ animation: m1 .32s steps(1) infinite; }} .m2 {{ animation: m2 .32s steps(1) infinite; }}
  @keyframes m1 {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0; }} }}
  @keyframes m2 {{ 0% {{ opacity: 0; }} 50% {{ opacity: 1; }} }}
  .wig {{ animation: wig .5s steps(1) infinite; }}
  @keyframes wig {{ 0% {{ transform: translate(0,0); }} 50% {{ transform: translate(.6px,-.4px); }} }}
</style>
<rect width="{W}" height="{H}" rx="12" fill="url(#bg)"/>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="12" fill="none" stroke="{BORDER}"/>
<line x1="0" y1="48" x2="{W}" y2="48" stroke="#121c16"/>
{chr(10).join(out)}
<rect width="{W}" height="{H}" rx="12" fill="url(#scan)"/>
</svg>
'''


# ───────────────────────────── neofetch.svg ─────────────────────────────
def render_neofetch(user) -> str:
    W, H = 880, 330
    cc = user["contributionsCollection"]
    cal = cc["contributionCalendar"]
    days = [d for w in cal["weeks"] for d in w["contributionDays"]]
    cur, best = streaks(days)
    repos = user["repositories"]
    stars = sum(r["stargazerCount"] for r in repos["nodes"])

    created = dt.datetime.fromisoformat(user["createdAt"].replace("Z", "+00:00")).date()
    today = dt.date.today()
    total_m = (today.year - created.year) * 12 + today.month - created.month - (today.day < created.day)
    years, months = divmod(max(total_m, 0), 12)

    wd = [0] * 7
    for d in days:
        wd[d["weekday"]] += d["contributionCount"]
    busiest = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"][wd.index(max(wd))] if any(wd) else "—"

    langs = {}
    for r in repos["nodes"]:
        for e in r["languages"]["edges"]:
            n = e["node"]["name"]
            langs.setdefault(n, [0, e["node"]["color"] or DIM])
            langs[n][0] += e["size"]
    total_size = sum(v[0] for v in langs.values()) or 1
    top = sorted(langs.items(), key=lambda kv: -kv[1][0])[:6]

    # big pixel hacker on the left
    px = 12
    hs = 11 * px
    hx, hy = 50, 76
    big = sprite(HACKER, HACKER_COL, px, skip="m")
    m_open = mouth(HACKER, px, GREEN)
    laptop = (
        f'<rect x="{hx - 14}" y="{hy + hs + 4}" width="{hs + 28}" height="10" rx="2" fill="#3b4652"/>'
        f'<rect x="{hx + 8}" y="{hy + hs - 26}" width="{hs - 16}" height="30" rx="2" fill="#11181f" stroke="#3b4652" stroke-width="2"/>'
        f'<text x="{hx + hs / 2}" y="{hy + hs - 6}" text-anchor="middle" class="code" fill="{GREEN}">'
        f'<tspan class="type">$ sudo -l</tspan></text>'
    )

    kx, vx, y0, lh = 260, 380, 50, 22
    rows = [
        ("Role", "AppSec Engineer · Penetration Tester"),
        ("Uptime", f"{years}y {months}m on GitHub"),
        ("Focus", "web · api · mobile · active directory · llm/rag"),
        ("Repos", f"{repos['totalCount']} public"),
        ("Contribs", f"{cal['totalContributions']} in the last year"),
        ("Activity", f"{cc['totalCommitContributions']} commits · {cc['totalPullRequestContributions']} PRs · "
                     f"{cc['totalIssueContributions']} issues · {cc['totalPullRequestReviewContributions']} reviews"),
        ("Streak", f"current {cur}d · longest {best}d · busiest {busiest}"),
        ("Shell", "bash on ubuntu · burp · python · ./exploit --responsibly"),
    ]
    txt = [
        f'<text x="{kx}" y="{y0}" class="t"><tspan fill="{GREEN}" font-weight="700">{escape(user["login"])}</tspan>'
        f'<tspan fill="{TXT}">@</tspan><tspan fill="{GREEN}" font-weight="700">github</tspan></text>',
        f'<text x="{kx}" y="{y0 + 12}" class="t" fill="{FAINT}">{"─" * 44}</text>',
    ]
    for i, (k, v) in enumerate(rows):
        y = y0 + 34 + i * lh
        txt.append(
            f'<text x="{kx}" y="{y}" class="t"><tspan fill="{CYAN}" font-weight="700">{k}</tspan></text>'
            f'<text x="{vx}" y="{y}" class="t" fill="{TXT}">{escape(v)}</text>'
        )

    # language bar
    ly = y0 + 34 + len(rows) * lh + 4
    txt.append(f'<text x="{kx}" y="{ly + 8}" class="t"><tspan fill="{CYAN}" font-weight="700">Stack</tspan></text>')
    bx, bw = vx, W - vx - 40
    x = bx
    bar = [f'<clipPath id="lb"><rect x="{bx}" y="{ly}" width="{bw}" height="10" rx="5"/></clipPath><g clip-path="url(#lb)">']
    for name, (size, color) in top:
        w = bw * size / total_size
        bar.append(f'<rect x="{x:.1f}" y="{ly}" width="{w + .5:.1f}" height="10" fill="{color}"/>')
        x += w
    if x < bx + bw:
        bar.append(f'<rect x="{x:.1f}" y="{ly}" width="{bx + bw - x:.1f}" height="10" fill="{FAINT}"/>')
    bar.append("</g>")
    lx = bx
    for name, (size, color) in top:
        label = f"{name} {100 * size / total_size:.0f}%"
        bar.append(f'<circle cx="{lx + 4}" cy="{ly + 26}" r="4" fill="{color}"/>'
                   f'<text x="{lx + 12}" y="{ly + 30}" class="s" fill="{DIM}">{escape(label)}</text>')
        lx += 12 + len(label) * 6.9 + 16
    txt.extend(bar)

    # neofetch colour blocks
    pal = ["#0d1117", RED, GREEN, YEL, "#3b82f6", MAG, CYAN, TXT]
    blocks = "".join(f'<rect x="{kx + i * 26}" y="{H - 30}" width="26" height="12" fill="{c}"/>' for i, c in enumerate(pal))

    return f'''<svg xmlns="http://www.w3.org/2000/svg" xml:space="preserve" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="neofetch-style GitHub telemetry">
<title>telemetry // neofetch</title>
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{BG0}"/><stop offset="1" stop-color="{BG1}"/></linearGradient>
  <radialGradient id="halo"><stop offset="0" stop-color="{GREEN}" stop-opacity=".18"/><stop offset="1" stop-color="{GREEN}" stop-opacity="0"/></radialGradient>
  <pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#fff" opacity=".03"/></pattern>
  <filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feDropShadow dx="0" dy="0" stdDeviation="3" flood-color="{GREEN}" flood-opacity=".6"/></filter>
</defs>
<style>
  text {{ font-family: {FONT}; }}
  .t {{ font-size: 14px; }} .s {{ font-size: 11.5px; }} .code {{ font-size: 10px; }}
  .eyes {{ animation: blink 5s infinite steps(1); }}
  @keyframes blink {{ 0%, 92%, 100% {{ opacity: 1; }} 94% {{ opacity: 0; }} }}
  .mo {{ animation: talk 1.6s infinite steps(1); }}
  @keyframes talk {{ 0%, 60%, 100% {{ opacity: 1; }} 70%, 90% {{ opacity: .25; }} }}
  .float {{ animation: float 4s ease-in-out infinite; }}
  @keyframes float {{ 0%, 100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-4px); }} }}
  .type {{ animation: type 3.5s steps(1) infinite; }}
  @keyframes type {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: .35; }} }}
</style>
<rect width="{W}" height="{H}" rx="12" fill="url(#bg)"/>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="12" fill="none" stroke="{BORDER}"/>
<circle cx="{hx + hs / 2}" cy="{hy + hs / 2}" r="110" fill="url(#halo)"/>
<g class="float">
  <g transform="translate({hx},{hy})" filter="url(#glow)">{big}<g class="mo">{m_open}</g></g>
  {laptop}
</g>
<line x1="232" y1="30" x2="232" y2="{H - 30}" stroke="{FAINT}" stroke-dasharray="2 4"/>
{"".join(txt)}
{blocks}
<rect width="{W}" height="{H}" rx="12" fill="url(#scan)"/>
</svg>
'''


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "dist"
    login = os.environ.get("GH_LOGIN") or "lborakove"
    token = os.environ["GH_TOKEN"]
    user = fetch(login, token)
    os.makedirs(out, exist_ok=True)
    for name, fn in (("bughunt.svg", render_bughunt), ("neofetch.svg", render_neofetch)):
        with open(os.path.join(out, name), "w", encoding="utf-8") as fh:
            fh.write(fn(user))
        print("wrote", name)


if __name__ == "__main__":
    main()
