const { createRequire } = require("node:module");
const requireFrontend = createRequire(
  require("node:path").resolve(__dirname, "../frontend/package.json"),
);
const { chromium } = requireFrontend("playwright");
const fs = require("fs");
const path = require("path");
const root = path.resolve(__dirname, "..");
const crypto = require("node:crypto");
(async () => {
  const credentials = fs.readFileSync(
    path.join(root, ".local/bootstrap-credentials.txt"),
    "utf8",
  );
  const browser = await chromium.launch({
    channel:
      process.env.ATLAS_BROWSER_CHANNEL ||
      (process.platform === "win32" ? "msedge" : undefined),
    headless: true,
  });
  const contexts = [];
  const errors = [];
  const signing = crypto.generateKeyPairSync("ed25519");
  const signingPublic = signing.publicKey
    .export({ type: "spki", format: "der" })
    .subarray(-32)
    .toString("base64");
  const canonical = (v) =>
    JSON.stringify(
      (function sort(x) {
        if (Array.isArray(x)) return x.map(sort);
        if (x && typeof x === "object")
          return Object.fromEntries(
            Object.keys(x)
              .sort()
              .map((k) => [k, sort(x[k])]),
          );
        return x;
      })(v),
    );
  async function signIn(name) {
    const context = await browser.newContext({
      viewport: { width: 1440, height: 1000 },
    });
    contexts.push(context);
    const page = await context.newPage();
    page.on("pageerror", (e) => errors.push(e.message));
    await page.goto("http://127.0.0.1:8787");
    await page.getByLabel("Username", { exact: true }).fill(name);
    await page
      .getByLabel("Password", { exact: true })
      .fill(
        credentials.match(new RegExp("^" + name + ": (.+)$", "m"))[1].trim(),
      );
    await page.getByRole("button", { name: "Sign in", exact: true }).click();
    await page
      .getByRole("heading", { name: "Investigations", exact: true })
      .waitFor();
    return page;
  }
  const investigator = await signIn("investigator");
  const reviewer = await signIn("reviewer");
  const jurisdiction = "Synthetic UI test " + Date.now();
  await investigator
    .getByRole("button", { name: "VASP directory", exact: true })
    .click();
  await investigator.getByRole("button", { name: "Propose recipient" }).click();
  await investigator.getByLabel("Directory purpose").selectOption("training");
  await investigator
    .getByLabel("Exact service / legal entity name")
    .fill("Example Exchange Alpha");
  await investigator
    .getByLabel("Jurisdiction", { exact: true })
    .fill(jurisdiction);
  await investigator
    .getByLabel("Authorised delivery channel")
    .fill("Synthetic UI test only; no external delivery");
  await investigator
    .getByLabel("Verification source and method")
    .fill(
      "Synthetic source for UI review testing. No real VASP verification is asserted.",
    );
  await investigator
    .getByLabel("Ed25519 response public key (Base64, optional)")
    .fill(signingPublic);
  await investigator.getByRole("button", { name: "Save", exact: true }).click();
  await investigator.getByRole("dialog").waitFor({ state: "hidden" });
  await reviewer.reload();
  await reviewer
    .getByRole("button", { name: "VASP directory", exact: true })
    .click();
  const recipientRow = reviewer
    .locator(".record-row")
    .filter({ hasText: jurisdiction });
  await recipientRow
    .getByRole("button", { name: "Review", exact: true })
    .click();
  await reviewer
    .getByLabel("Review rationale and verification performed")
    .fill(
      "Independent review of synthetic UI test evidence; not operational recipient verification.",
    );
  await reviewer.getByRole("button", { name: "Record decision" }).click();
  await reviewer.getByRole("dialog").waitFor({ state: "hidden" });
  await recipientRow.getByText("approved", { exact: true }).waitFor();
  await investigator
    .getByRole("button", { name: "Investigations", exact: true })
    .click();
  await investigator.locator(".case-row").first().click();
  await investigator
    .getByRole("heading", { name: "Example Exchange Alpha" })
    .waitFor();
  await investigator
    .getByRole("button", { name: "Requests", exact: true })
    .click();
  await investigator.getByRole("button", { name: "Prepare request" }).click();
  const matchingOption = investigator
    .getByLabel("Reviewed recipient")
    .locator("option")
    .filter({ hasText: jurisdiction });
  await matchingOption.waitFor({ state: "attached" });
  await investigator
    .getByLabel("Reviewed recipient")
    .selectOption(await matchingOption.getAttribute("value"));
  await investigator
    .getByLabel("Applicable legal authority / basis")
    .fill("Synthetic workflow test only; no legal authority is claimed.");
  await investigator
    .getByLabel("Specific scope, period and requested records")
    .fill(
      "Exercise the local package review controls. Do not send any request or take any real-world action.",
    );
  await investigator.getByRole("button", { name: "Save", exact: true }).click();
  await investigator.getByRole("dialog").waitFor({ state: "hidden" });
  await reviewer
    .getByRole("button", { name: "Investigations", exact: true })
    .click();
  await reviewer.locator(".case-row").first().click();
  await reviewer.getByRole("button", { name: "Requests", exact: true }).click();
  await reviewer
    .locator(".record-row")
    .filter({ hasText: "Example Exchange Alpha" })
    .first()
    .getByRole("button", { name: "Review", exact: true })
    .click();
  await reviewer
    .getByLabel("Review rationale and verification performed")
    .fill(
      "Exact synthetic payload reviewed by separate test reviewer. Export only; no real delivery.",
    );
  await reviewer.getByRole("button", { name: "Record decision" }).click();
  await reviewer.getByRole("dialog").waitFor({ state: "hidden" });
  const output = path.join(root, "tmp/browser");
  await reviewer.screenshot({
    path: path.join(output, "reviewed-request.png"),
    fullPage: true,
  });
  const downloadEvent = reviewer.waitForEvent("download");
  await reviewer
    .getByRole("link", { name: "Export", exact: true })
    .first()
    .click();
  const download = await downloadEvent;
  const requestPath = path.join(output, "reviewed-request.json");
  await download.saveAs(requestPath);
  const request = JSON.parse(fs.readFileSync(requestPath));
  if (
    request.delivery_status !== "NOT_SENT" ||
    request.sahyog_status !== "NOT_CONNECTED"
  )
    throw Error("Export misrepresents delivery state");
  async function reopen(page, tab) {
    await page.reload();
    await page
      .getByRole("heading", { name: "Investigations", exact: true })
      .waitFor();
    await page.locator(".case-row").first().click();
    await page
      .getByRole("heading", { name: "Example Exchange Alpha" })
      .waitFor();
    await page.getByRole("button", { name: tab, exact: true }).click();
  }
  await reopen(investigator, "Requests");
  const payload = {
    schema: "atlas.service-response.v1",
    request_id: request.request_id,
    request_sha256: request.body_sha256,
    attestation: {
      chain: request.body.candidate.chain,
      address: request.body.candidate.address,
      entity: request.body.candidate.entity,
      category: "exchange",
      role: "deposit",
      valid_from: 1750000000,
      valid_to: 1750001000,
    },
  };
  const signature = crypto
    .sign(null, Buffer.from(canonical(payload)), signing.privateKey)
    .toString("base64");
  await investigator
    .getByRole("button", { name: "Import signed response" })
    .click();
  await investigator
    .getByLabel("Approved request", { exact: true })
    .selectOption(request.request_id);
  await investigator
    .getByLabel("Signed response JSON")
    .fill(JSON.stringify(payload));
  await investigator
    .getByLabel("Ed25519 signature (Base64)", { exact: true })
    .fill(signature);
  await investigator.getByRole("button", { name: "Save", exact: true }).click();
  await investigator.getByRole("dialog").waitFor({ state: "hidden" });
  await reopen(reviewer, "Evidence");
  await reviewer
    .locator(".record-row")
    .filter({ hasText: "Signed service response" })
    .getByRole("button", { name: "Review", exact: true })
    .click();
  await reviewer
    .getByLabel("Review rationale and verification performed")
    .fill(
      "Synthetic service signature, scope and validity independently checked in UI test.",
    );
  await reviewer.getByRole("button", { name: "Record decision" }).click();
  await reviewer.getByRole("dialog").waitFor({ state: "hidden" });
  await reviewer
    .locator(".record-row")
    .filter({
      has: reviewer
        .locator("strong")
        .filter({ hasText: "Example Exchange Alpha" }),
    })
    .getByText("approved", { exact: true })
    .waitFor();
  await reopen(investigator, "Overview");
  await investigator
    .getByRole("button", { name: "Reassess recorded evidence" })
    .click();
  await investigator
    .getByRole("heading", { name: "Example Exchange Alpha" })
    .waitFor({ timeout: 20000 });
  await investigator
    .getByRole("button", { name: "Evidence", exact: true })
    .click();
  await investigator
    .getByRole("button", { name: "Propose withdrawal" })
    .click();
  await investigator
    .getByLabel("Reason and supporting evidence")
    .fill(
      "Synthetic correction for the browser test: service attestation withdrawn.",
    );
  await investigator.getByRole("button", { name: "Save", exact: true }).click();
  await investigator.getByRole("dialog").waitFor({ state: "hidden" });
  await reopen(reviewer, "Evidence");
  await reviewer
    .locator(".record-row")
    .filter({ hasText: "Evidence withdrawal" })
    .getByRole("button", { name: "Review", exact: true })
    .click();
  await reviewer
    .getByLabel("Review rationale and verification performed")
    .fill(
      "Independently reviewed the synthetic withdrawal and its stated evidence.",
    );
  await reviewer.getByRole("button", { name: "Record decision" }).click();
  await reviewer.getByRole("dialog").waitFor({ state: "hidden" });
  await reopen(investigator, "Evidence");
  await investigator
    .getByText(/Supporting evidence was withdrawn after this analysis/)
    .waitFor();
  if (await investigator.getByRole("link", {name: "Report", exact: true}).count()) throw Error("Stale report export remains offered");
  if (await investigator.getByRole("link", {name: "Signed evidence bundle"}).count()) throw Error("Stale bundle export remains offered");
  await investigator.screenshot({
    path: path.join(output, "withdrawal.png"),
    fullPage: true,
  });
  await investigator
    .getByRole("button", { name: "Reassess recorded evidence" })
    .click();
  await investigator
    .getByRole("heading", { name: "Example Exchange Alpha" })
    .waitFor({ timeout: 20000 });
  if (
    await investigator
      .getByText(/Supporting evidence was withdrawn after this analysis/)
      .count()
  )
    throw Error("Reassessment retained withdrawn assertion");
  fs.writeFileSync(
    path.join(output, "review-results.json"),
    JSON.stringify(
      {
        checks: [
          "recipient proposal",
          "separate reviewer approval",
          "request preparation",
          "payload review",
          "approved export",
          "not-sent status",
          "signed scoped feedback",
          "independent assertion promotion",
          "recorded-evidence reassessment",
          "reviewed withdrawal and affected-analysis notice",
          "superseding reassessment",
        ],
        pageErrors: errors,
      },
      null,
      2,
    ),
  );
  console.log(JSON.stringify({ passed: !errors.length, pageErrors: errors }));
  await browser.close();
  if (errors.length) process.exitCode = 1;
})().catch((e) => {
  console.error(e);
  process.exit(1);
});
