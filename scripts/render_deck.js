// Render a Slides-format deck (project/deck.json + project/slides/*.html) to a standalone HTML page and a PDF.
// usage: node render_deck.js <deck root> <output base path without extension>
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const [, , root, outBase] = process.argv;
const deck = JSON.parse(fs.readFileSync(path.join(root, 'project/deck.json'), 'utf8'));
const slides = deck.order.map((id) => fs.readFileSync(path.join(root, 'project/slides', id + '.html'), 'utf8'));
const fonts = Object.values(deck.faces || {}).map((f) => f.href).filter(Boolean)
  .map((h) => `<link rel="stylesheet" href="${h}">`).join('\n');
const css = `
@page { size: 1920px 1080px; margin: 0; }
html, body { margin: 0; padding: 0; background: #2a2f3a; }
section, section * { box-sizing: border-box; }
section { position: relative; width: 1920px; height: 1080px; overflow: hidden; margin: 0 auto 24px auto;
          page-break-after: always; break-after: page; }
@media print { section { margin: 0; } }
section h1, section h2, section h3, section p, section ul, section ol { margin: 0; }
section h1 { font-size: 96px; font-weight: 600; line-height: 1.1; }
section h2 { font-size: 64px; font-weight: 600; line-height: 1.15; }
section h3 { font-size: 44px; font-weight: 600; line-height: 1.2; }
section p { font-size: 32px; line-height: 1.4; }
section ul, section ol { padding-left: 1.1em; }
section div:not([style*="display:"]) { display: flex; flex-direction: column; }
section hr { border: 0; margin: 0; height: 0; }
section table { border-collapse: collapse; width: 100%; }
section th, section td { padding: 0.35em 0.6em; border-bottom: 1px solid #D9D6CC; vertical-align: top; text-align: left; }
section aside { display: none; }
x-shape { display: block; }
x-shape[kind="arrow-right"] { clip-path: polygon(0 25%, 60% 25%, 60% 0, 100% 50%, 60% 100%, 60% 75%, 0 75%); }
x-shape[kind="arrow-down"]  { clip-path: polygon(25% 0, 75% 0, 75% 60%, 100% 60%, 50% 100%, 0 60%, 25% 60%); }
x-shape[kind="arrow-left"]  { clip-path: polygon(100% 25%, 40% 25%, 40% 0, 0 50%, 40% 100%, 40% 75%, 100% 75%); }
x-shape[kind="arrow-up"]    { clip-path: polygon(25% 100%, 75% 100%, 75% 40%, 100% 40%, 50% 0, 0 40%, 25% 40%); }
x-shape[kind="ellipse"] { border-radius: 50%; }
x-shape[kind="diamond"] { clip-path: polygon(50% 0, 100% 50%, 50% 100%, 0 50%); }
x-connector { display: none; }
`;
const script = `
document.querySelectorAll('section').forEach(function (sec) {
  var cons = sec.querySelectorAll(':scope > x-connector');
  if (!cons.length) return;
  var ns = 'http://www.w3.org/2000/svg';
  var svg = document.createElementNS(ns, 'svg');
  svg.setAttribute('width', '1920'); svg.setAttribute('height', '1080');
  svg.setAttribute('style', 'position:absolute;left:0;top:0;width:1920px;height:1080px;pointer-events:none;overflow:visible');
  var defs = document.createElementNS(ns, 'defs'); svg.appendChild(defs);
  var n = 0;
  cons.forEach(function (c) {
    var st = c.getAttribute('style') || '';
    var color = (st.match(/color:\\s*([^;]+)/) || [, '#5B6475'])[1].trim();
    var w = parseFloat((st.match(/border-width:\\s*([0-9.]+)/) || [, '2'])[1]);
    var dashed = /dashed/.test(st);
    var head = c.getAttribute('head') || 'end';
    var x1 = +c.getAttribute('x1'), y1 = +c.getAttribute('y1'), x2 = +c.getAttribute('x2'), y2 = +c.getAttribute('y2');
    var id = 'm' + (n++);
    var marker = document.createElementNS(ns, 'marker');
    marker.setAttribute('id', id); marker.setAttribute('orient', 'auto'); marker.setAttribute('markerUnits', 'strokeWidth');
    marker.setAttribute('markerWidth', '5'); marker.setAttribute('markerHeight', '5'); marker.setAttribute('refX', '4'); marker.setAttribute('refY', '2');
    var mp = document.createElementNS(ns, 'path'); mp.setAttribute('d', 'M0 0 L4 2 L0 4 Z'); mp.setAttribute('fill', color);
    marker.appendChild(mp); defs.appendChild(marker);
    var line = document.createElementNS(ns, 'line');
    var dx = x2 - x1, dy = y2 - y1, len = Math.sqrt(dx * dx + dy * dy) || 1;
    var cut = head === 'none' ? 0 : 2 * w;
    line.setAttribute('x1', x1); line.setAttribute('y1', y1);
    line.setAttribute('x2', x2 - dx / len * cut); line.setAttribute('y2', y2 - dy / len * cut);
    line.setAttribute('stroke', color); line.setAttribute('stroke-width', w); line.setAttribute('stroke-linecap', 'round');
    if (dashed) line.setAttribute('stroke-dasharray', '12 10');
    if (head !== 'none') line.setAttribute('marker-end', 'url(#' + id + ')');
    svg.appendChild(line);
  });
  sec.appendChild(svg);
});
`;
const html = `<!doctype html><html><head><meta charset="utf-8"><title>${deck.title}</title>
${fonts}
<style>${css}</style></head><body>
${slides.join('\n')}
<script>${script}</script>
</body></html>`;
fs.writeFileSync(outBase + '.html', html);
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  await page.goto('file://' + path.resolve(outBase + '.html'), { waitUntil: 'load', timeout: 60000 });
  try { await page.waitForLoadState('networkidle', { timeout: 15000 }); } catch (e) { console.log('fonts: network idle not reached, using fallbacks'); }
  await page.waitForTimeout(500);
  await page.pdf({ path: outBase + '.pdf', width: '1920px', height: '1080px', printBackground: true, preferCSSPageSize: true });
  await browser.close();
  console.log('wrote', outBase + '.html', 'and', outBase + '.pdf', '(' + slides.length + ' slides)');
})();
