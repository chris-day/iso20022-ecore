// Use the vendored full bundle; avoid the theme's CDN-backed Mermaid loader.
mermaid.initialize({startOnLoad: false, securityLevel: "strict", theme: "neutral"});
async function renderDiagrams() {
  for (const [index, node] of [...document.querySelectorAll('.local-diagram')].entries()) {
    if (node.dataset.rendered) continue;
    const source = node.textContent;
    try {
      const {svg} = await mermaid.render(`local-diagram-${index}`, source);
      node.innerHTML = svg;
      node.dataset.rendered = 'true';
      node.setAttribute('aria-label', 'Model relationship diagram');
    } catch (error) {
      node.dataset.error = String(error);
      console.error(error);
    }
  }
}
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', renderDiagrams);
else renderDiagrams();
