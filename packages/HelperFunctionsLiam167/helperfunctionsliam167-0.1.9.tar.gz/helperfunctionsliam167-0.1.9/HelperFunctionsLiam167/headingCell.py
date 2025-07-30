from IPython.display import display, HTML


def display_link_cards(
    analysis_title: str,
    jira_url: str,
    jira_title: str,
    ppt_url: str,
    ppt_title: str,
    other_links: list,
    accordion_icon: str = "https://www.freeiconspng.com/uploads/link-icon-png-14.png"
):
    """
    Display a set of styled link cards in a Jupyter notebook.

    Parameters:
    - analysis_title: Title displayed above the cards (HTML heading).
    - jira_url: URL to the Jira ticket.
    - jira_title: Text label for the Jira link.
    - ppt_url: URL to the PowerPoint presentation.
    - ppt_title: Text label for the PPT link.
    - other_links: List of dicts with keys 'title' and 'url' for additional links.
    - accordion_icon: Icon URL for the "Other Links" accordion header.
    """
    # Build HTML for additional links
    links_html = "".join([
        f'<li style="margin-bottom:8px;">'
        f'<a href="{link["url"]}" target="_blank" '
        f'style="color:#222;text-decoration:underline;font-size:1em;">{link["title"]}</a></li>'
        for link in other_links
    ])

    html = f"""
<h1 class = "title">{analysis_title}</h1>
<style>
.title {{ font-size:4rem; margin-bottom:20px;}}
.link-cards-flex {{ display: flex; gap: 32px; flex-wrap: wrap; justify-content: flex-start; }}
.link-card {{ min-width:320px; max-width:380px; padding:20px; border-radius:18px; box-shadow:0 4px 18px #e5e5e580; display: flex; align-items: center; background: #fff; text-decoration:none; }}
.link-card.jira {{ border:1.5px solid #0052CC; background: #0052CC; color: #fff; }}
.link-card.ppt  {{ border:1.5px solid #D24726; background: #D24726; color: #fff; }}
.link-card img {{ margin-right:20px; border-radius:12px; border:1.5px solid #fff; background:white; width:60px; }}
.accordion-card {{ min-width:320px; max-width:380px; padding:0; border-radius:18px; box-shadow:0 4px 18px #e5e5e580; border:1.5px solid #2D3436; background:#fff; display:flex; flex-direction:column; }}
.accordion-header {{ display:flex; align-items:center; cursor:pointer; border-radius:18px; padding:20px; background:#2D3436; color:#fff; font-weight:bold; font-size:1.15em; user-select:none; }}
.accordion-header:hover {{ background:#636e72; }}
.accordion-header img {{ margin-right:20px; border-radius:12px; border:1.5px solid #2D3436; background:white; width:60px; }}
.caret {{ margin-left:auto; font-size:1.4em; transition: transform 0.3s; display:flex; align-items:center; }}
.caret.open {{ transform: rotate(180deg); }}
.panel {{ padding:0 20px; background:#fff; border-radius:0 0 18px 18px; max-height:0; overflow:hidden; color:#333; box-shadow:0 4px 18px #e5e5e520; transition:max-height 0.4s cubic-bezier(0.4,0,0.2,1); }}
.panel.open {{ max-height:350px; }}
</style>
<div class="link-cards-flex">
  <a href="{jira_url}" target="_blank" class="link-card jira">
    <img src="https://img.icons8.com/color/60/000000/jira.png" alt="Jira"/>
    <div>
      <div style="font-size:1.2em;font-weight:bold;margin-bottom:5px;">{jira_title}</div>
      <div>Click to open in a new tab</div>
    </div>
  </a>
  <a href="{ppt_url}" target="_blank" class="link-card ppt">
    <img src="https://img.icons8.com/color/60/000000/microsoft-powerpoint-2019--v1.png" alt="PPT"/>
    <div>
      <div style="font-size:1.2em;font-weight:bold;margin-bottom:5px;">{ppt_title}</div>
      <div>Click to open in a new tab</div>
    </div>
  </a>
  <div class="accordion-card">
    <div class="accordion-header" tabindex="0">
      <img src="{accordion_icon}" alt="Links"/>
      <span>Other Links</span>
      <span class="caret">&#9660;</span>
    </div>
    <div class="panel">
      <ul style="list-style-type:disc; margin:12px 0 0 12px; padding:0;">
        {links_html}
      </ul>
    </div>
  </div>
</div>
<script>
(function() {{
  var acc = document.querySelector('.accordion-header');
  var panel = document.querySelector('.panel');
  var caret = acc.querySelector('.caret');
  function toggle() {{
    panel.classList.toggle('open');
    caret.classList.toggle('open');
  }}
  acc.onclick = toggle;
  acc.onkeyup = function(e) {{ if(e.key==='Enter'||e.key===' ') toggle(); }};
}})();
</script>
"""
    display(HTML(html))
