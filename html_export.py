from pathlib import Path
import html

def generate_interactive_html_table(data, out_path="interactive_table.html", title="Interactive Table"):
    """
    Generate a standalone HTML file with a sortable, filterable table from a list of dicts.
    - data: list[dict]  (each dict should have the same keys; extra/missing keys are handled)
    - out_path: str or Path
    - title: page/table title
    """
    out_path = Path(out_path)

    if not data:
        raise ValueError("data must be a non-empty list of dictionaries")

    # Derive columns from the first row to preserve order; include any keys that appear later
    columns = list(data[0].keys())
    for row in data[1:]:
        for k in row.keys():
            if k not in columns:
                columns.append(k)

    def escape_cell(x):
        if x is None:
            return ""
        s = str(x)
        # escape HTML and keep newlines as <br> for readability
        return html.escape(s).replace("\n", "<br>")

    # Build table rows
    rows_html = []
    for row in data:
        tds = [f"<td data-col='{html.escape(col)}'>{escape_cell(row.get(col, ''))}</td>" for col in columns]
        rows_html.append("<tr>" + "".join(tds) + "</tr>")

    # Headers and filter inputs
    ths_html = [f"<th data-col='{html.escape(col)}' class='sortable'>{html.escape(col)}"
                f"<span class='sort-indicator'></span></th>" for col in columns]
    filters_html = [f"<th><input class='col-filter' data-col='{html.escape(col)}' "
                    f"placeholder='Filter {html.escape(col)}' /></th>" for col in columns]

    template = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{html.escape(title)}</title>
<style>
  :root {{
    --bg: #0b0c10; --card: #16181d; --text: #e6e6e6; --muted: #9aa3ab;
    --accent: #7aa2f7; --border: #2a2f36;
  }}
  html, body {{ margin:0; padding:0; background:var(--bg); color:var(--text);
    font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial; }}
  .wrapper {{ max-width: 1100px; margin: 32px auto; padding: 0 16px; }}
  .card {{ background: var(--card); border:1px solid var(--border); border-radius:16px; box-shadow:0 10px 30px rgba(0,0,0,.35); overflow:hidden; }}
  .header {{ display:flex; flex-wrap:wrap; gap:12px; align-items:center; justify-content:space-between;
    padding:16px; border-bottom:1px solid var(--border); }}
  .title {{ font-weight:700; font-size:18px; letter-spacing:.2px; }}
  .controls {{ display:flex; gap:10px; align-items:center; }}
  input[type="text"] {{ background:#0f1217; color:var(--text); border:1px solid var(--border);
    border-radius:10px; padding:10px 12px; outline:none; width:220px; }}
  input[type="text"]::placeholder {{ color: var(--muted); }}
  button {{ background:#0f1217; color:var(--text); border:1px solid var(--border); border-radius:10px; padding:10px 12px; cursor:pointer; }}
  table {{ width:100%; border-collapse:separate; border-spacing:0; }}
  thead th {{ position:sticky; top:0; background:#13161c; z-index:1; }}
  th, td {{ text-align:left; padding:12px 14px; border-bottom:1px solid var(--border); vertical-align:top; font-size:14px; }}
  tr:hover td {{ background: rgba(122,162,247,0.06); }}
  th.sortable {{ user-select:none; cursor:pointer; }}
  .sort-indicator {{ margin-left:8px; opacity:.7; font-size:12px; }}
  tfoot td {{ padding:10px 14px; color:var(--muted); font-size:13px; }}
  .badge {{ background: rgba(122,162,247,0.12); color: var(--accent);
    border:1px solid rgba(122,162,247,0.3); padding:2px 8px; border-radius:999px; font-size:12px; margin-left:8px; }}
</style>
</head>
<body>
  <div class="wrapper">
    <div class="card">
      <div class="header">
        <div class="title">{html.escape(title)} <span id="rowCount" class="badge"></span></div>
        <div class="controls">
          <input id="globalSearch" type="text" placeholder="Global search…"/>
          <button id="resetBtn">Reset filters</button>
        </div>
      </div>
      <div style="overflow:auto;">
        <table id="dataTable">
          <thead>
            <tr>
              {''.join(ths_html)}
            </tr>
            <tr>
              {''.join(filters_html)}
            </tr>
          </thead>
          <tbody>
            {''.join(rows_html)}
          </tbody>
          <tfoot>
            <tr><td colspan="{len(columns)}">Tip: click a header to sort ↑/↓, type in the filter inputs to filter by column, or use the global search.</td></tr>
          </tfoot>
        </table>
      </div>
    </div>
  </div>

<script>
(function() {{
  const table = document.getElementById('dataTable');
  const tbody = table.querySelector('tbody');
  const ths = Array.from(table.querySelectorAll('thead tr:first-child th.sortable'));
  const filterInputs = Array.from(table.querySelectorAll('.col-filter'));
  const globalSearch = document.getElementById('globalSearch');
  const resetBtn = document.getElementById('resetBtn');
  const rowCountEl = document.getElementById('rowCount');

  let sortState = {{ col: null, dir: 1 }}; // 1 asc, -1 desc
  let rows = Array.from(tbody.querySelectorAll('tr'));

  function cssEscape(str) {{
    if (window.CSS && typeof window.CSS.escape === 'function') return window.CSS.escape(str);
    return String(str).replace(/[^a-zA-Z0-9_-]/g, '\\\\$&');
  }}

  function textContentOfCell(tr, colName) {{
    const td = tr.querySelector(`td[data-col="${{cssEscape(colName)}}"]`);
    return (td ? td.textContent : '').trim();
  }}

  // Natural-ish compare so "SRS-2" < "SRS-10"
  function naturalCompare(a, b) {{
    const ax = [], bx = [];
    a.replace(/(\\d+)|(\\D+)/g, (_, $1, $2) => ax.push([$1 || Infinity, $2 || ""]));
    b.replace(/(\\d+)|(\\D+)/g, (_, $1, $2) => bx.push([$1 || Infinity, $2 || ""]));
    while (ax.length && bx.length) {{
      const an = ax.shift(), bn = bx.shift();
      const nn = (an[0] - bn[0]) || an[1].localeCompare(bn[1]);
      if (nn) return nn;
    }}
    return ax.length - bx.length;
  }}

  function applySort() {{
    if (!sortState.col) return;
    const col = sortState.col, dir = sortState.dir;
    rows.sort((r1, r2) => naturalCompare(textContentOfCell(r1, col), textContentOfCell(r2, col)) * dir);
    ths.forEach(th => th.querySelector('.sort-indicator').textContent = '');
    const activeTh = ths.find(th => th.dataset.col === col);
    if (activeTh) activeTh.querySelector('.sort-indicator').textContent = dir === 1 ? '↑' : '↓';
  }}

  function rowMatchesFilters(tr) {{
    for (const input of filterInputs) {{
      const needle = input.value.toLowerCase().trim();
      if (!needle) continue;
      const col = input.dataset.col;
      const hay = textContentOfCell(tr, col).toLowerCase();
      if (!hay.includes(needle)) return false;
    }}
    const gq = globalSearch.value.toLowerCase().trim();
    if (gq) {{
      const hay = tr.textContent.toLowerCase();
      if (!hay.includes(gq)) return false;
    }}
    return true;
  }}

  function render() {{
    applySort();
    tbody.innerHTML = '';
    let visible = 0;
    for (const tr of rows) {{
      if (rowMatchesFilters(tr)) {{
        tbody.appendChild(tr);
        visible++;
      }}
    }}
    rowCountEl.textContent = visible + ' / ' + rows.length + ' rows';
  }}

  ths.forEach(th => {{
    th.addEventListener('click', () => {{
      const col = th.dataset.col;
      sortState = (sortState.col === col) ? {{ col, dir: -sortState.dir }} : {{ col, dir: 1 }};
      render();
    }});
  }});

  filterInputs.forEach(inp => inp.addEventListener('input', render));
  globalSearch.addEventListener('input', render);

  resetBtn.addEventListener('click', () => {{
    filterInputs.forEach(inp => inp.value = '');
    globalSearch.value = '';
    sortState = {{ col: null, dir: 1 }};
    ths.forEach(th => th.querySelector('.sort-indicator').textContent = '');
    render();
  }});

  render();
}})();
</script>
</body>
</html>
"""
    out_path.write_text(template, encoding="utf-8")
    return str(out_path)

# --- Example usage with your sample data ---
if __name__ == "__main__":
    data = [
        {'ID': 'SRS-1', 'Title': 'test',   'Description': 'test desc\n',   'Labels': '\n'},
        {'ID': 'SRS-2', 'Title': 'test 2', 'Description': 'test desc 2\n', 'Labels': '\n'},
        {'ID': 'SRS-3', 'Title': 'test 3', 'Description': '\n',            'Labels': '\n'}
    ]
    path = generate_interactive_html_table(data, "requirements_table.html", title="SRS Items")
    print(f"HTML written to: {path}")
