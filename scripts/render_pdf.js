const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const dir = process.argv[2];
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('file://' + path.join(dir, 'report.html'), { waitUntil: 'load' });
  await page.pdf({
    path: path.join(dir, 'NanoAOD_photon_TrigObj_unseeded_bits_issue.pdf'),
    format: 'A4', printBackground: true, preferCSSPageSize: true,
    displayHeaderFooter: true,
    headerTemplate: '<div></div>',
    footerTemplate: '<div style="font-size:7.5px;width:100%;text-align:center;color:#666;font-family:Liberation Sans, DejaVu Sans, sans-serif;">NanoAOD photon TrigObj: unseeded-leg bits of HLT_Diphoton30_22 &nbsp;&middot;&nbsp; page <span class="pageNumber"></span> of <span class="totalPages"></span></div>',
  });
  await browser.close();
})();
