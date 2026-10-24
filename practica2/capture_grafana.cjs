// Captura el tablero privado desde la propia VM. Requiere Playwright/Chromium.
// No imprime las credenciales ni las incluye en el archivo generado.
const fs = require('fs');
const { chromium } = require('playwright');

const values = Object.fromEntries(
  fs.readFileSync(process.env.SAVIA_ENV_FILE || '.env', 'utf8')
    .split(/\r?\n/)
    .filter(line => line && !line.startsWith('#') && line.includes('='))
    .map(line => {
      const pos = line.indexOf('=');
      return [line.slice(0, pos), line.slice(pos + 1)];
    })
);
const base = process.env.GRAFANA_URL || 'http://127.0.0.1:3000';
const output = process.env.CAPTURE_FILE || '/out/grafana-aws-2026-10-24.png';

(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  try {
    const page = await browser.newPage({ viewport: { width: 1600, height: 1050 }, deviceScaleFactor: 1 });
    await page.goto(`${base}/login`, { waitUntil: 'domcontentloaded' });
    await page.locator('input[name="user"]').fill(values.GRAFANA_USER);
    await page.locator('input[name="password"]').fill(values.GRAFANA_PASSWORD);
    await page.locator('button[type="submit"]').click();
    await page.waitForURL(url => !url.pathname.endsWith('/login'), { timeout: 30000 });
    await page.goto(`${base}/d/savia-practica2/savia-iot-invernadero-de-tomates?orgId=1&from=now-2h&to=now&kiosk`, { waitUntil: 'domcontentloaded' });
    await page.getByText('Temperatura del aire interior (simulada)').waitFor({ timeout: 30000 });
    await page.waitForTimeout(10000);
    const title = await page.title();
    const body = await page.locator('body').innerText();
    if (!title.includes('Savia IoT') || !body.includes('Humedad relativa del aire interior')) {
      throw new Error('El tablero esperado no se mostró completo');
    }
    await page.screenshot({ path: output, fullPage: true });
    console.log(`Captura guardada: ${output}; bytes=${fs.statSync(output).size}; paneles visibles=4`);
  } finally {
    await browser.close();
  }
})().catch(err => { console.error(err.message); process.exitCode = 1; });
