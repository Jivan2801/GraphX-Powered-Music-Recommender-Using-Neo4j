import pandas as pd
from pathlib import Path
import webbrowser

def main():
    # 1. Find the latest recommendations file
    recs_dir = Path("data_processed/recs")
    if not recs_dir.exists():
        print("No recommendations found. Run app/generate_recs.py first.")
        return

    csv_files = list(recs_dir.glob("*.csv"))
    if not csv_files:
        print("No CSV files found in data_processed/recs.")
        return

    # Pick the most recent one
    latest_csv = max(csv_files, key=lambda p: p.stat().st_mtime)
    print(f"Generating report for: {latest_csv}")

    df = pd.read_csv(latest_csv)

    # 2. Generate HTML
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Music Recommendations</title>
        <style>
            :root {{
                --bg-color: #0f172a;
                --card-bg: #1e293b;
                --text-primary: #f8fafc;
                --text-secondary: #94a3b8;
                --accent: #38bdf8;
                --accent-hover: #0ea5e9;
                --border: #334155;
            }}
            
            body {{
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                background-color: var(--bg-color);
                color: var(--text-primary);
                margin: 0;
                padding: 40px;
                line-height: 1.6;
            }}

            .container {{
                max-width: 1200px;
                margin: 0 auto;
            }}

            header {{
                margin-bottom: 40px;
                text-align: center;
            }}

            h1 {{
                font-size: 2.5rem;
                font-weight: 700;
                background: linear-gradient(to right, var(--accent), #818cf8);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 10px;
            }}

            p.subtitle {{
                color: var(--text-secondary);
                font-size: 1.1rem;
            }}

            .card {{
                background-color: var(--card-bg);
                border-radius: 16px;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
                border: 1px solid var(--border);
                overflow: hidden;
            }}

            table {{
                width: 100%;
                border-collapse: collapse;
                text-align: left;
            }}

            th {{
                background-color: rgba(255, 255, 255, 0.05);
                padding: 16px 24px;
                font-weight: 600;
                color: var(--text-secondary);
                text-transform: uppercase;
                font-size: 0.85rem;
                letter-spacing: 0.05em;
                border-bottom: 1px solid var(--border);
            }}

            td {{
                padding: 16px 24px;
                border-bottom: 1px solid var(--border);
            }}

            tr:last-child td {{
                border-bottom: none;
            }}

            tr:hover td {{
                background-color: rgba(56, 189, 248, 0.05);
            }}

            .rank {{
                font-family: monospace;
                color: var(--text-secondary);
            }}

            .score {{
                font-weight: 600;
                color: var(--accent);
            }}

            .meta {{
                font-size: 0.9rem;
                color: var(--text-secondary);
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>Your Music Recommendations</h1>
                <p class="subtitle">Personalized top picks based on your listening history</p>
            </header>
            
            <div class="card">
                <table>
                    <thead>
                        <tr>
                            <th>Rank</th>
                            <th>Song / Artist</th>
                            <th>Genre / Year</th>
                            <th>Features</th>
                            <th>Score</th>
                        </tr>
                    </thead>
                    <tbody>
    """
    
    for i, row in df.iterrows():
        rank = i + 1
        name = row.get('name', 'Unknown')
        artist = row.get('artist', 'Unknown')
        genre = row.get('genre', 'Unknown')
        year = row.get('year', '')
        
        final_score = float(row.get('final_score', 0))
        cf = float(row.get('cf_score', 0))
        playcount = int(float(row.get('total_playcount', 0)))
        
        html_content += f"""
                        <tr>
                            <td class="rank">#{rank:02d}</td>
                            <td>
                                <div><strong>{name}</strong></div>
                                <div class="meta">{artist}</div>
                            </td>
                            <td>
                                <div>{genre}</div>
                                <div class="meta">{year}</div>
                            </td>
                            <td class="meta">
                                CF: {cf:.0f} | Plays: {playcount}
                            </td>
                            <td class="score">{final_score:.4f}</td>
                        </tr>
        """

    html_content += """
                    </tbody>
                </table>
            </div>
        </div>
    </body>
    </html>
    """

    output_path = Path("recommendations_report.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"Report generated: {output_path.absolute()}")
    
    # Try to open automatically
    webbrowser.open(output_path.absolute().as_uri())

if __name__ == "__main__":
    main()
