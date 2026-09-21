"""
Génère une page HTML avec une vraie identité visuelle : esthétique "console/log
technique" (le projet est né dans un terminal, on assume ce fil plutôt que de
le cacher derrière un kit SaaS générique).
"""

import webbrowser
import os
from datetime import datetime

# Palette pensée pour un fond sombre, une couleur par catégorie, cohérente
CATEGORY_STYLES = {
    "Facture":                 {"hex": "#fbbf24"},
    "Support":                 {"hex": "#38bdf8"},
    "RH":                      {"hex": "#a78bfa"},
    "Spam":                    {"hex": "#fb7185"},
    "Commercial":              {"hex": "#34d399"},
    "Newsletter-Notification": {"hex": "#94a3b8"},
    "Autre":                   {"hex": "#64748b"},
}


def generate_html_report(results, output_path="email_report.html"):
    counts = {}
    for r in results:
        counts[r["category"]] = counts.get(r["category"], 0) + 1

    total = len(results)
    avg_confidence = round(sum(r["confidence"] for r in results) / total) if total else 0

    stats_rows = ""
    for category, count in sorted(counts.items(), key=lambda x: -x[1]):
        color = CATEGORY_STYLES.get(category, CATEGORY_STYLES["Autre"])["hex"]
        pct = round((count / total) * 100) if total else 0
        stats_rows += f"""
        <button class="stat-row" data-filter="{category}">
            <span class="stat-dot" style="background:{color}"></span>
            <span class="stat-name">{category}</span>
            <span class="stat-bar-track"><span class="stat-bar-fill" style="width:{pct}%; background:{color}"></span></span>
            <span class="stat-count">{count}</span>
        </button>"""

    log_rows = ""
    for i, r in enumerate(results):
        color = CATEGORY_STYLES.get(r["category"], CATEGORY_STYLES["Autre"])["hex"]
        time_tag = f"[{i+1:02d}]"
        log_rows += f"""
        <div class="entry" data-category="{r['category']}" style="--delay:{i * 40}ms; border-left-color:{color}">
            <div class="entry-top">
                <span class="entry-index">{time_tag}</span>
                <span class="entry-tag" style="color:{color}">{r['category']}</span>
                <span class="entry-confidence">{r['confidence']}%</span>
            </div>
            <div class="entry-subject">{r['subject']}</div>
            <div class="entry-from">from {r['from']}</div>
            <div class="entry-reason">// {r['reason']}</div>
        </div>"""

    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AI Email Sorter — Log</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
    :root {{
        --bg: #0b0f17;
        --surface: #11161f;
        --border: #1f2633;
        --text: #e6eaf2;
        --muted: #7c869c;
        --accent: #5eead4;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
        background: var(--bg);
        color: var(--text);
        font-family: 'Space Grotesk', sans-serif;
        padding: 48px 24px;
    }}
    .wrap {{ max-width: 920px; margin: 0 auto; }}

    header {{ margin-bottom: 36px; }}
    .eyebrow {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 13px;
        color: var(--accent);
    }}
    h1 {{ font-size: 32px; font-weight: 700; margin-top: 6px; letter-spacing: -0.02em; }}
    .logline {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 13px;
        color: var(--muted);
        margin-top: 10px;
    }}

    .layout {{ display: grid; grid-template-columns: 260px 1fr; gap: 28px; align-items: start; }}
    @media (max-width: 720px) {{ .layout {{ grid-template-columns: 1fr; }} }}

    .panel {{
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 20px;
        position: sticky;
        top: 24px;
    }}
    .panel-title {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
        color: var(--muted);
        margin-bottom: 14px;
    }}
    .big-number {{ font-size: 40px; font-weight: 700; line-height: 1; }}
    .big-label {{ font-size: 13px; color: var(--muted); margin-top: 4px; }}
    .avg {{ margin-top: 18px; padding-top: 18px; border-top: 1px solid var(--border); }}

    .stat-row {{
        display: flex;
        align-items: center;
        gap: 8px;
        width: 100%;
        background: none;
        border: none;
        color: var(--text);
        font-family: 'Space Grotesk', sans-serif;
        font-size: 13px;
        padding: 7px 0;
        cursor: pointer;
        text-align: left;
    }}
    .stat-row.active .stat-name {{ color: var(--accent); }}
    .stat-dot {{ width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }}
    .stat-name {{ flex: 1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
    .stat-bar-track {{ width: 40px; height: 4px; background: var(--border); border-radius: 2px; overflow: hidden; flex-shrink: 0; }}
    .stat-bar-fill {{ display: block; height: 100%; }}
    .stat-count {{ font-family: 'JetBrains Mono', monospace; color: var(--muted); width: 20px; text-align: right; flex-shrink: 0; }}

    .entry {{
        background: var(--surface);
        border: 1px solid var(--border);
        border-left: 3px solid;
        border-radius: 6px;
        padding: 16px 18px;
        margin-bottom: 10px;
        opacity: 0;
        animation: rise 0.4s ease forwards;
        animation-delay: var(--delay);
    }}
    @keyframes rise {{
        from {{ opacity: 0; transform: translateY(6px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    .entry-top {{
        display: flex;
        align-items: center;
        gap: 12px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
        margin-bottom: 8px;
    }}
    .entry-index {{ color: var(--muted); }}
    .entry-tag {{ font-weight: 600; }}
    .entry-confidence {{ margin-left: auto; color: var(--muted); }}
    .entry-subject {{ font-size: 15px; font-weight: 500; margin-bottom: 4px; }}
    .entry-from {{ font-family: 'JetBrains Mono', monospace; font-size: 12px; color: var(--muted); margin-bottom: 8px; }}
    .entry-reason {{ font-size: 13px; color: var(--muted); line-height: 1.5; }}

    .entry.hidden {{ display: none; }}
</style>
</head>
<body>
<div class="wrap">
    <header>
        <div class="eyebrow">ai-email-sorter</div>
        <h1>Inbox triage log</h1>
        <div class="logline">$ python automate_email_sorter.py — {total} emails traités — {datetime.now().strftime('%d/%m/%Y %H:%M')}</div>
    </header>

    <div class="layout">
        <aside class="panel">
            <div class="panel-title">résumé</div>
            <div class="big-number">{total}</div>
            <div class="big-label">emails classés</div>
            <div class="avg">
                <div class="big-number" style="font-size:24px;">{avg_confidence}%</div>
                <div class="big-label">confiance moyenne</div>
            </div>
            <div class="avg">
                {stats_rows}
            </div>
        </aside>

        <main id="log">
            {log_rows}
        </main>
    </div>
</div>

<script>
    const rows = document.querySelectorAll('.stat-row');
    const entries = document.querySelectorAll('.entry');
    let active = null;

    rows.forEach(row => {{
        row.addEventListener('click', () => {{
            const filter = row.dataset.filter;
            if (active === filter) {{
                active = null;
                rows.forEach(r => r.classList.remove('active'));
                entries.forEach(e => e.classList.remove('hidden'));
            }} else {{
                active = filter;
                rows.forEach(r => r.classList.toggle('active', r.dataset.filter === filter));
                entries.forEach(e => e.classList.toggle('hidden', e.dataset.category !== filter));
            }}
        }});
    }});
</script>
</body>
</html>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    webbrowser.open(f"file://{os.path.abspath(output_path)}")
    print(f"\nRapport généré et ouvert : {output_path}")