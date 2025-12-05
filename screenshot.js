const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();

  // Устанавливаем размер viewport для десктопа
  await page.setViewport({ width: 1920, height: 1080 });

  // Открываем страницу
  await page.goto('https://timly-hr.ru/demo-results', {
    waitUntil: 'networkidle0',
  });

  // Делаем скриншот
  await page.screenshot({
    path: 'frontend/public/demo-screenshot.png',
    fullPage: true,
  });

  console.log('Screenshot saved to frontend/public/demo-screenshot.png');

  await browser.close();
})();
