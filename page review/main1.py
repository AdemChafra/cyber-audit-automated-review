import fitz  # PyMuPDF
import json
import ollama
from jinja2 import Template
import re
from collections import Counter

# Paths
pdf_path = "report.pdf"
output_json = "review_results1.json"
output_html = "review_results1.html"

def review_text(text, page_number):
    """
    Send text to Ollama (llama3) for review and return structured issues.
    """
    prompt = f"""
    Review this text from page {page_number} of an audit report.
    Return ONLY valid JSON (a list of issues). Each issue must include:
    - issue_type: one of (clarity, coherence, jargon, recommendation, formatting, missing_info)
    - severity: critical, major, minor
    - problematic_text: exact text snippet causing the issue
    - suggestion: concrete advice to fix it
    - page: page number
    - category_explanation: brief description why this is an issue
    Text:
    {text}
    """
    response = ollama.generate(model="llama3", prompt=prompt)["response"]

    try:
        return json.loads(response)
    except json.JSONDecodeError:
        match = re.search(r"\[.*\]", response, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass

    # Fallback if parsing fails
    return [{
        "issue_type": "parsing_error",
        "severity": "minor",
        "problematic_text": text[:200],
        "suggestion": response.strip(),
        "page": page_number,
        "category_explanation": "Could not parse Llama response"
    }]

# --- Process PDF ---
doc = fitz.open(pdf_path)
results = []

for i, page in enumerate(doc, start=1):
    if i > 3:  # Limit to first 10 pages
        break
    text = page.get_text("text")
    if text.strip():
        print(f"Processing page {i}...")
        chunks = [text[j:j+3000] for j in range(0, len(text), 3000)]
        page_issues = []
        for chunk in chunks:
            page_issues.extend(review_text(chunk, i))
        results.append({"page": i, "issues": page_issues})

doc.close()

# Save JSON output
with open(output_json, "w", encoding="utf-8") as f_json:
    json.dump(results, f_json, ensure_ascii=False, indent=2)

# --- Prepare summary ---
issue_counter = Counter()
for page in results:
    for issue in page["issues"]:
        issue_counter[issue["issue_type"]] += 1

# --- Generate HTML report ---
html_template = """
<html>
<head>
<meta charset="UTF-8">
<title>Audit Review Dashboard</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
<style>
body {
    font-family: 'Inter', sans-serif;
    margin: 0;
    background: #1e1e2f;
    color: #f0f0f0;
}
h1 {
    text-align: center;
    padding: 2rem 0 1rem 0;
    font-size: 2.5rem;
    font-weight: 700;
    color: #f5f5f5;
}
.summary {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    margin: 1rem auto 2rem auto;
    gap: 1rem;
}
.summary-card {
    background: #2a2a40;
    padding: 1.2rem 1.8rem;
    border-radius: 12px;
    box-shadow: 0 8px 20px rgba(0,0,0,0.3);
    text-align: center;
    min-width: 140px;
    transition: transform 0.3s, box-shadow 0.3s;
}
.summary-card:hover { transform: translateY(-5px); box-shadow: 0 12px 30px rgba(0,0,0,0.5); }
.summary-card .count { font-size: 2rem; font-weight: 700; color: #f5f5f5; }
.summary-card .label { font-size: 1rem; margin-top: 0.3rem; color: #a5a5a5; }
h2 {
    margin-top: 2rem;
    cursor: pointer;
    padding: 0.8rem 1rem;
    background: linear-gradient(90deg,#4f46e5,#3b82f6);
    border-radius: 8px;
    color: #ffffff;
    font-size: 1.3rem;
    font-weight: 600;
    transition: background 0.3s;
}
h2:hover { background: linear-gradient(90deg,#6366f1,#60a5fa); }
.content {
    display: none;
    padding: 1rem;
    margin-bottom: 1rem;
    border-radius: 10px;
    background: #2a2a40;
    box-shadow: 0 4px 15px rgba(0,0,0,0.4);
    transition: max-height 0.4s ease;
}
.issue {
    margin: 0.6rem 0;
    padding: 0.8rem 1rem;
    border-left: 6px solid #ccc;
    background: #3b3b58;
    border-radius: 8px;
    transition: transform 0.2s, box-shadow 0.2s;
}
.issue:hover { transform: translateY(-2px); box-shadow: 0 6px 15px rgba(0,0,0,0.5); }
.issue.clarity { border-color: #facc15; }
.issue.coherence { border-color: #10b981; }
.issue.jargon { border-color: #ef4444; }
.issue.recommendation { border-color: #3b82f6; }
.issue.formatting { border-color: #8b5cf6; }
.issue.missing_info { border-color: #14b8a6; }
.issue.parsing_error { border-color: #9ca3af; }
.badge {
    padding: 3px 10px;
    border-radius: 12px;
    color: #fff;
    font-size: 0.85em;
    font-weight: 600;
    margin-right: 6px;
}
.badge.clarity { background: #facc15; color:#1e1e2f; }
.badge.coherence { background: #10b981; }
.badge.jargon { background: #ef4444; }
.badge.recommendation { background: #3b82f6; }
.badge.formatting { background: #8b5cf6; }
.badge.missing_info { background: #14b8a6; }
.badge.parsing_error { background: #9ca3af; }
p { margin: 0.3rem 0; }
i { color: #d1d5db; }
.chart {
    margin-top: 0.5rem;
    height: 8px;
    display: flex;
    border-radius: 4px;
    overflow: hidden;
}
.chart-bar {
    height: 100%;
}
.chart-bar.clarity { background: #facc15; }
.chart-bar.coherence { background: #10b981; }
.chart-bar.jargon { background: #ef4444; }
.chart-bar.recommendation { background: #3b82f6; }
.chart-bar.formatting { background: #8b5cf6; }
.chart-bar.missing_info { background: #14b8a6; }
</style>
</head>
<body>

<h1>Audit Review Dashboard (First 10 Pages)</h1>

<div class="summary">
{% for issue_type, count in issue_counter.items() %}
  <div class="summary-card">
    <div class="count">{{ count }}</div>
    <div class="label">{{ issue_type|capitalize }}</div>
  </div>
{% endfor %}
</div>

{% for page in results %}
<h2>Page {{ page.page }} ({{ page.issues|length }} issues)</h2>
<div class="content">
  {% set total = page.issues|length %}
  {% set type_counts = {} %}
  {% for issue in page.issues %}
      {% set _ = type_counts.update({issue.issue_type: (type_counts.get(issue.issue_type,0)+1)}) %}
  {% endfor %}
  <div class="chart">
      {% for t, c in type_counts.items() %}
          <div class="chart-bar {{ t|lower }}" style="width:{{ (c/total)*100 }}%"></div>
      {% endfor %}
  </div>
  {% for issue in page.issues %}
    <div class="issue {{ issue.issue_type|lower }}">
      <p><span class="badge {{ issue.issue_type|lower }}">{{ issue.issue_type }}</span> - <b>{{ issue.severity }}</b></p>
      <p><b>Text:</b> {{ issue.problematic_text }}</p>
      <p><b>Suggestion:</b> {{ issue.suggestion }}</p>
      <p><i>{{ issue.category_explanation }}</i></p>
    </div>
  {% endfor %}
</div>
{% endfor %}

<script>
var coll = document.getElementsByTagName("h2");
for (var i = 0; i < coll.length; i++) {
  coll[i].addEventListener("click", function() {
    var content = this.nextElementSibling;
    content.style.display = (content.style.display === "block") ? "none" : "block";
  });
}
</script>

</body>
</html>
"""

with open(output_html, "w", encoding="utf-8") as f:
    f.write(Template(html_template).render(results=results, issue_counter=issue_counter))

print("✅ Review complete. JSON and interactive HTML report generated.")
