// Exporte chaque SVG en PNG (x2) avec Chromium.
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs'), path = require('path');
(async () => {
  const dir = path.join(__dirname, '..', 'livrables');
  const proxy = process.env.HTTPS_PROXY ? { server: process.env.HTTPS_PROXY } : undefined;
  const browser = await chromium.launch({ proxy });
  const page = await browser.newPage({ deviceScaleFactor: 2, ignoreHTTPSErrors: true });
  for (const f of fs.readdirSync(path.join(dir, 'svg')).filter(f => f.endsWith('.svg'))) {
    const svg = fs.readFileSync(path.join(dir, 'svg', f), 'utf8');
    await page.setContent(`<html><head><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600&family=IBM+Plex+Mono:wght@600&display=swap"><style>body{margin:0}</style></head><body>${svg}</body></html>`, { waitUntil: 'networkidle' }).catch(() => {});
    await page.evaluate(() => document.fonts.ready);
    const el = await page.$('svg');
    await el.screenshot({ path: path.join(dir, 'png', f.replace('.svg', '.png')) });
    console.log('png', f, await page.evaluate(() => document.fonts.check('12px "IBM Plex Sans"')));
  }
  await browser.close();
})();
