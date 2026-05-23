# Grade 3 English Results Dashboard
Flask + Jinja2 dashboard for Grade 3 English section results.

# Setup

1. Install dependencies:
   ```bash
   pip install pandas plotly flask
   ```

2. Place Excel files in the `data/` folder:
   - `English_Boys_Pink.xlsx`
   - `English_Boys_White.xlsx`
   - `English_Boys_Yellow.xlsx`

3. Run the app:
   ```bash
   python app.py
   ```

4. Open browser at: http://127.0.0.1:5000

#Pages

| URL | Description |
|-----|-------------|
| `/` | Overview dashboard — all sections, stats, charts |
| `/section/Pink` | Section Pink — student list + charts |
| `/section/White` | Section White — student list + charts |
| `/section/Yellow` | Section Yellow — student list + charts |

# Features
- Overall and per-section stats (count, average, percentage, grade)
- Grade distribution doughnut charts
- Section rank + overall rank per student
