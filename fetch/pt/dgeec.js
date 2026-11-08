// Open DGEEC's short link in a headless browser; record API calls, links and the page text.
const { chromium } = require('playwright');
const fs = require('fs');
const OUT = process.argv[2];
(async () => {
  const b = await chromium.launch(); const p = await b.newPage();
  const calls = [];
  p.on('response', (r) => calls.push([r.url(), r.status(), r.headers()['content-type'] || '']));
  await p.goto('https://www.dgeec.medu.pt/l/Z9on6', { waitUntil: 'networkidle', timeout: 120000 });
  await p.waitForTimeout(6000);
  const links = await p.$$eval('a', (els) => els.map((e) => [e.href, (e.innerText || '').trim().slice(0, 120)]));
  fs.writeFileSync(`${OUT}/page.txt`, await p.innerText('body'));
  fs.writeFileSync(`${OUT}/browse.json`, JSON.stringify({ url: p.url(), title: await p.title(), links, calls: calls.filter((c) => c[0].includes('/api/')) }, null, 1));
  await b.close();
})().catch((e) => { fs.writeFileSync(`${OUT}/browse_error.txt`, String(e.stack || e)); process.exit(0); });
