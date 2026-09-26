const { createRequire } = require("node:module");
const requireFrontend = createRequire(
  require("node:path").resolve(__dirname, "../frontend/package.json"),
);
const { chromium } = requireFrontend("playwright");
const fs = require("fs");
const path = require("path");
const root = path.resolve(__dirname, "..");

(async () => {
  const credentials = fs.readFileSync(
    path.join(root, ".local/bootstrap-credentials.txt"),
    "utf8",
  );
  const password = credentials.match(/^investigator: (.+)$/m)[1].trim();
  const browser = await chromium.launch({
    channel:
      process.env.ATLAS_BROWSER_CHANNEL ||
      (process.platform === "win32" ? "msedge" : undefined),
    headless: true,
  });
  const page = await browser.newPage({
    viewport: { width: 1440, height: 1050 },
    deviceScaleFactor: 1,
  });
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  const output = path.join(root, "tmp/browser");
  fs.mkdirSync(output, { recursive: true });
  await page.goto("http://127.0.0.1:8787", { waitUntil: "networkidle" });
  await page.screenshot({
    path: path.join(output, "login.png"),
    fullPage: true,
  });
  await page.getByLabel("Username", { exact: true }).fill("investigator");
  await page.getByLabel("Password", { exact: true }).fill(password);
  await page.getByRole("button", { name: "Sign in", exact: true }).click();
  await page
    .getByRole("heading", { name: "Investigations", exact: true })
    .waitFor();
  await page.screenshot({
    path: path.join(output, "cases.png"),
    fullPage: true,
  });
  await page.getByRole("button", { name: "Open training case" }).click();
  await page
    .getByRole("heading", { name: "Custody frontier · training investigation" })
    .waitFor();
  await page
    .getByRole("heading", { name: "Example Exchange Alpha" })
    .waitFor({ timeout: 20000 });
  await page
    .getByRole("button", { name: "Plan within a request budget" })
    .click();
  await page.getByLabel("HTTP request budget", { exact: true }).fill("4");
  await page.getByRole("button", { name: "Save", exact: true }).click();
  await page.getByRole("dialog").waitFor({ state: "hidden" });
  await page.getByText(/Advisory only; nothing fetched/).waitFor();
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.screenshot({
    path: path.join(output, "investigation.png"),
    fullPage: true,
  });
  await page.getByRole("button", { name: "Inspect evidence" }).first().click();
  await page.getByRole("button", { name: "Challenge source" }).click();
  await page.getByText("More evidence required", { exact: true }).waitFor();
  await page.screenshot({
    path: path.join(output, "challenge.png"),
    fullPage: true,
  });
  await page.getByRole("button", { name: "Evidence", exact: true }).click();
  const downloadEvent = page.waitForEvent("download");
  await page.getByRole("link", { name: "Signed evidence bundle" }).click();
  const download = await downloadEvent;
  const bundlePath = path.join(output, "browser-evidence.zip");
  await download.saveAs(bundlePath);
  await page
    .getByRole("button", { name: "Verify evidence", exact: true })
    .click();
  await page
    .getByLabel("Evidence ZIP (maximum 10 MB)")
    .setInputFiles(bundlePath);
  await page.getByRole("button", { name: "Verify bundle" }).click();
  await page
    .getByText("Integrity valid · replay matched", { exact: true })
    .waitFor();
  await page.screenshot({
    path: path.join(output, "verify.png"),
    fullPage: true,
  });
  await page.getByRole("button", { name: "Data & coverage" }).click();
  await page
    .getByRole("heading", { name: "Data & coverage", exact: true })
    .waitFor();
  await page.screenshot({
    path: path.join(output, "coverage.png"),
    fullPage: true,
  });
  await page.setViewportSize({ width: 390, height: 844 });
  await page
    .getByRole("button", { name: "Investigations", exact: true })
    .click();
  await page.screenshot({
    path: path.join(output, "mobile.png"),
    fullPage: true,
  });
  const overflow = await page.evaluate(
    () => document.documentElement.scrollWidth > window.innerWidth,
  );
  fs.writeFileSync(
    path.join(output, "results.json"),
    JSON.stringify(
      {
        browser: "Microsoft Edge via Playwright",
        checks: [
          "login",
          "case creation",
          "durable analysis",
          "custody result",
          "budgeted advisory query plan",
          "assumption challenge",
          "bundle download",
          "bundle verify",
          "coverage page",
          "mobile viewport",
        ],
        pageErrors: errors,
        mobileOverflow: overflow,
      },
      null,
      2,
    ),
  );
  console.log(
    JSON.stringify({ pageErrors: errors, mobileOverflow: overflow, output }),
  );
  await browser.close();
  if (errors.length || overflow) process.exitCode = 1;
})().catch((e) => {
  console.error(e);
  process.exit(1);
});
