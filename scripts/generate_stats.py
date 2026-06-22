import os
import json
import urllib.request
import urllib.error
from pathlib import Path

GH_USER = "SaiKarthikGardas"
LC_USER = "KarthiXcode"
TOKEN = os.environ.get("GH_TOKEN", "")

def gh_get(url):
    req = urllib.request.Request(url)
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    req.add_header("User-Agent", "stats-card-bot")
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read())
    except Exception:
        return {}

def lc_get(username):
    query = """
    query($username: String!) {
      matchedUser(username: $username) {
        submitStats {
          acSubmissionNum {
            difficulty
            count
          }
        }
      }
    }
    """
    data = json.dumps({"query": query, "variables": {"username": username}}).encode()
    req = urllib.request.Request(
        "https://leetcode.com/graphql",
        data=data,
        headers={"Content-Type": "application/json", "User-Agent": "stats-card-bot"}
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            result = json.loads(r.read())
            subs = result["data"]["matchedUser"]["submitStats"]["acSubmissionNum"]
            counts = {s["difficulty"]: s["count"] for s in subs}
            return {
                "total": counts.get("All", 0),
                "easy": counts.get("Easy", 0),
                "medium": counts.get("Medium", 0),
                "hard": counts.get("Hard", 0),
            }
    except Exception:
        return {"total": 0, "easy": 0, "medium": 0, "hard": 0}

def build_svg(gh, lc):
    stars = gh.get("stars", 0)
    repos = gh.get("repos", 0)
    followers = gh.get("followers", 0)
    total = lc["total"]
    easy = lc["easy"]
    medium = lc["medium"]
    hard = lc["hard"]

    max_lc = max(total, 1)
    easy_pct = round((easy / max_lc) * 100)
    med_pct = round((medium / max_lc) * 100)
    hard_pct = round((hard / max_lc) * 100)

    easy_w = max(4, round((easy / max(easy + medium + hard, 1)) * 260))
    med_w = max(4, round((medium / max(easy + medium + hard, 1)) * 260))
    hard_w = max(4, round((hard / max(easy + medium + hard, 1)) * 260))

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="680" height="280" viewBox="0 0 680 280">
  <defs>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600&amp;display=swap');
      .card {{ font-family: 'Fira Code', monospace; }}
    </style>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#0d1117"/>
      <stop offset="100%" stop-color="#0a1628"/>
    </linearGradient>
    <linearGradient id="border-grad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#58a6ff"/>
      <stop offset="50%" stop-color="#7dcfff"/>
      <stop offset="100%" stop-color="#58a6ff"/>
    </linearGradient>
    <filter id="glow">
      <feGaussianBlur stdDeviation="3" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse">
      <path d="M 24 0 L 0 0 0 24" fill="none" stroke="#ffffff" stroke-width="0.15" stroke-opacity="0.08"/>
    </pattern>
  </defs>

  <!-- Background -->
  <rect width="680" height="280" rx="16" fill="url(#bg)"/>
  <rect width="680" height="280" rx="16" fill="url(#grid)"/>

  <!-- Glowing border -->
  <rect x="1" y="1" width="678" height="278" rx="15" fill="none" stroke="url(#border-grad)" stroke-width="1.5" opacity="0.7"/>

  <!-- Title row -->
  <text x="32" y="44" font-family="'Fira Code', monospace" font-size="13" fill="#7dcfff" opacity="0.8">// sai karthik gardas</text>
  <text x="32" y="66" font-family="'Fira Code', monospace" font-size="20" font-weight="600" fill="#ffffff" filter="url(#glow)">Stats Card</text>

  <!-- Divider -->
  <line x1="32" y1="80" x2="648" y2="80" stroke="#58a6ff" stroke-width="0.5" opacity="0.3"/>

  <!-- GitHub stats - 3 metric boxes -->
  <!-- Box 1: Stars -->
  <rect x="32" y="98" width="180" height="72" rx="8" fill="#0e2040" stroke="#58a6ff" stroke-width="0.5" stroke-opacity="0.4"/>
  <text x="52" y="120" font-family="'Fira Code', monospace" font-size="11" fill="#7dcfff" opacity="0.7">GitHub Stars</text>
  <text x="52" y="148" font-family="'Fira Code', monospace" font-size="26" font-weight="600" fill="#ffffff">{stars}</text>

  <!-- Box 2: Repos -->
  <rect x="226" y="98" width="180" height="72" rx="8" fill="#0e2040" stroke="#58a6ff" stroke-width="0.5" stroke-opacity="0.4"/>
  <text x="246" y="120" font-family="'Fira Code', monospace" font-size="11" fill="#7dcfff" opacity="0.7">Public Repos</text>
  <text x="246" y="148" font-family="'Fira Code', monospace" font-size="26" font-weight="600" fill="#ffffff">{repos}</text>

  <!-- Box 3: Followers -->
  <rect x="420" y="98" width="228" height="72" rx="8" fill="#0e2040" stroke="#58a6ff" stroke-width="0.5" stroke-opacity="0.4"/>
  <text x="440" y="120" font-family="'Fira Code', monospace" font-size="11" fill="#7dcfff" opacity="0.7">Followers</text>
  <text x="440" y="148" font-family="'Fira Code', monospace" font-size="26" font-weight="600" fill="#ffffff">{followers}</text>

  <!-- Divider -->
  <line x1="32" y1="188" x2="648" y2="188" stroke="#58a6ff" stroke-width="0.5" opacity="0.2"/>

  <!-- LeetCode section label -->
  <text x="32" y="210" font-family="'Fira Code', monospace" font-size="11" fill="#ffa116" opacity="0.9">LeetCode — {total} solved</text>

  <!-- Easy bar -->
  <text x="32" y="232" font-family="'Fira Code', monospace" font-size="10" fill="#00b8a3">Easy</text>
  <rect x="80" y="222" width="260" height="10" rx="5" fill="#1a2a1a"/>
  <rect x="80" y="222" width="{easy_w}" height="10" rx="5" fill="#00b8a3"/>
  <text x="350" y="232" font-family="'Fira Code', monospace" font-size="10" fill="#00b8a3">{easy} ({easy_pct}%)</text>

  <!-- Medium bar -->
  <text x="32" y="252" font-family="'Fira Code', monospace" font-size="10" fill="#ffa116">Med</text>
  <rect x="80" y="242" width="260" height="10" rx="5" fill="#2a1a00"/>
  <rect x="80" y="242" width="{med_w}" height="10" rx="5" fill="#ffa116"/>
  <text x="350" y="252" font-family="'Fira Code', monospace" font-size="10" fill="#ffa116">{medium} ({med_pct}%)</text>

  <!-- Hard bar -->
  <text x="32" y="272" font-family="'Fira Code', monospace" font-size="10" fill="#ef4743">Hard</text>
  <rect x="80" y="262" width="260" height="10" rx="5" fill="#2a0000"/>
  <rect x="80" y="262" width="{hard_w}" height="10" rx="5" fill="#ef4743"/>
  <text x="350" y="272" font-family="'Fira Code', monospace" font-size="10" fill="#ef4743">{hard} ({hard_pct}%)</text>
</svg>"""
    return svg

def main():
    print("Fetching GitHub data...")
    user_data = gh_get(f"https://api.github.com/users/{GH_USER}")
    repos_data = gh_get(f"https://api.github.com/users/{GH_USER}/repos?per_page=100")

    stars = sum(r.get("stargazers_count", 0) for r in repos_data) if isinstance(repos_data, list) else 0
    gh = {
        "stars": stars,
        "repos": user_data.get("public_repos", 0),
        "followers": user_data.get("followers", 0),
    }
    print(f"  Stars: {gh['stars']}, Repos: {gh['repos']}, Followers: {gh['followers']}")

    print("Fetching LeetCode data...")
    lc = lc_get(LC_USER)
    print(f"  Total: {lc['total']}, Easy: {lc['easy']}, Medium: {lc['medium']}, Hard: {lc['hard']}")

    svg = build_svg(gh, lc)

    # Save to repo root (script runs from repo root in GitHub Actions)
    out_path = Path("stats.svg")
    out_path.write_text(svg, encoding="utf-8")
    print(f"stats.svg generated at {out_path.resolve()}")

if __name__ == "__main__":
    main()
