#!/usr/bin/env node
"use strict";

const fs = require("fs");
const http = require("http");
const path = require("path");
const { spawn } = require("child_process");
const { chromium } = require("playwright");

const ROOT = path.resolve(__dirname, "..");
const DEFAULT_CHROMIUM = "/usr/bin/chromium";
const CHROMIUM_CANDIDATES = [
  DEFAULT_CHROMIUM,
  "/usr/bin/google-chrome",
  "/usr/bin/google-chrome-stable",
  "/usr/bin/chromium-browser",
  "/snap/bin/chromium",
];
const DEFAULT_PORT = 8123;
const VIEWPORTS = [
  { name: "mobile", width: 390, height: 844, isMobile: true, hasTouch: true },
  { name: "tablet", width: 768, height: 1024, isMobile: true, hasTouch: true },
  { name: "desktop", width: 1280, height: 900, isMobile: false, hasTouch: false },
];

function usage() {
  console.error("Usage: node scripts/visual_qa.js <slug> [--port 8123] [--base-url http://host:port] [--out tmp/screenshots] [--chromium /usr/bin/chromium]");
}

function findChromiumPath() {
  if (process.env.CHROMIUM_PATH) return process.env.CHROMIUM_PATH;

  for (const candidate of CHROMIUM_CANDIDATES) {
    if (fs.existsSync(candidate)) return candidate;
  }

  return DEFAULT_CHROMIUM;
}

function parseArgs(argv) {
  const args = {
    slug: null,
    port: DEFAULT_PORT,
    baseUrl: null,
    outDir: path.join(ROOT, "tmp", "screenshots"),
    chromiumPath: findChromiumPath(),
  };

  for (let i = 2; i < argv.length; i += 1) {
    const arg = argv[i];
    if (!args.slug && !arg.startsWith("--")) {
      args.slug = arg;
    } else if (arg === "--port") {
      args.port = Number(argv[++i]);
    } else if (arg === "--base-url") {
      args.baseUrl = argv[++i];
    } else if (arg === "--out") {
      args.outDir = path.resolve(argv[++i]);
    } else if (arg === "--chromium") {
      args.chromiumPath = argv[++i];
    } else {
      usage();
      process.exit(2);
    }
  }

  if (!args.slug || !Number.isInteger(args.port) || args.port < 1) {
    usage();
    process.exit(2);
  }

  return args;
}

function waitForServer(url, timeoutMs = 8000) {
  const deadline = Date.now() + timeoutMs;

  return new Promise((resolve, reject) => {
    function attempt() {
      const req = http.get(url, (res) => {
        res.resume();
        resolve();
      });
      req.on("error", () => {
        if (Date.now() >= deadline) {
          reject(new Error(`Timed out waiting for ${url}`));
          return;
        }
        setTimeout(attempt, 200);
      });
      req.setTimeout(1000, () => {
        req.destroy();
      });
    }
    attempt();
  });
}

function isGenericResourceConsoleError(msg) {
  return msg.includes("Failed to load resource: the server responded with a status of");
}

function startServer(port) {
  const child = spawn("python3", ["-m", "http.server", String(port)], {
    cwd: ROOT,
    stdio: ["ignore", "pipe", "pipe"],
  });

  let stderr = "";
  child.stderr.on("data", (chunk) => {
    stderr += chunk.toString();
  });

  child.on("exit", (code) => {
    if (code !== null && code !== 0) {
      console.error(`Preview server exited with ${code}: ${stderr.trim()}`);
    }
  });

  return child;
}

async function getVisiblePage(page) {
  return page.evaluate(() => {
    const visible = Array.from(document.querySelectorAll(".page")).filter((el) => !el.hidden);
    return visible.map((el) => ({
      dataPage: el.getAttribute("data-page"),
      className: el.className,
      text: el.textContent.trim().replace(/\s+/g, " ").slice(0, 120),
    }));
  });
}

async function waitForVisiblePage(page, expectedIndex) {
  await page.waitForFunction((index) => {
    const visible = Array.from(document.querySelectorAll(".page")).filter((el) => !el.hidden);
    return visible.length === 1 && visible[0].getAttribute("data-page") === String(index);
  }, expectedIndex, { timeout: 3000 });

  // Let transition cleanup, image decoding, and webfont layout settle before capture.
  await page.waitForTimeout(150);
}

async function inspectPage(page) {
  return page.evaluate(() => {
    const visible = Array.from(document.querySelectorAll(".page")).filter((el) => !el.hidden);
    const brokenImages = Array.from(document.images)
      .filter((img) => img.complete && img.naturalWidth === 0)
      .map((img) => img.getAttribute("src"));

    const visibleOverflow = visible.map((el) => {
      const rect = el.getBoundingClientRect();
      return {
        dataPage: el.getAttribute("data-page"),
        width: Math.round(rect.width),
        height: Math.round(rect.height),
        scrollWidth: el.scrollWidth,
        scrollHeight: el.scrollHeight,
        overflowsX: el.scrollWidth > Math.ceil(rect.width) + 2,
        overflowsY: el.scrollHeight > Math.ceil(rect.height) + 2,
      };
    });

    return {
      title: document.title,
      pageCount: document.querySelectorAll(".page").length,
      visiblePages: visible.map((el) => el.getAttribute("data-page")),
      bodyOverflowsX: document.documentElement.scrollWidth > window.innerWidth + 2,
      documentWidth: document.documentElement.scrollWidth,
      viewportWidth: window.innerWidth,
      brokenImages,
      visibleOverflow,
    };
  });
}

async function runViewport(browser, args, viewport, baseUrl, report) {
  const context = await browser.newContext({
    viewport: { width: viewport.width, height: viewport.height },
    isMobile: viewport.isMobile,
    hasTouch: viewport.hasTouch,
    deviceScaleFactor: 1,
  });
  const page = await context.newPage();
  const viewportReport = {
    name: viewport.name,
    width: viewport.width,
    height: viewport.height,
    screenshots: [],
    consoleErrors: [],
    failedRequests: [],
    checks: [],
  };

  page.on("console", (msg) => {
    if (msg.type() === "error" && !isGenericResourceConsoleError(msg.text())) {
      viewportReport.consoleErrors.push(msg.text());
    }
  });
  page.on("requestfailed", (request) => {
    viewportReport.failedRequests.push({
      url: request.url(),
      failure: request.failure() ? request.failure().errorText : "unknown",
    });
  });
  page.on("response", (response) => {
    if (response.status() >= 400) {
      viewportReport.failedRequests.push({
        url: response.url(),
        status: response.status(),
      });
    }
  });

  const url = `${baseUrl}/books/${args.slug}/`;
  await page.goto(url, { waitUntil: "networkidle" });
  await page.emulateMedia({ reducedMotion: "reduce" });

  const pageCount = await page.locator(".page").count();
  if (pageCount < 1) throw new Error(`No .page elements found at ${url}`);
  if ((await page.locator("#nav-next").count()) !== 1) throw new Error("Expected exactly one #nav-next");
  if ((await page.locator("#nav-prev").count()) !== 1) throw new Error("Expected exactly one #nav-prev");

  const screenshotDir = path.join(args.outDir, args.slug, viewport.name);
  fs.mkdirSync(screenshotDir, { recursive: true });

  for (let i = 0; i < pageCount; i += 1) {
    await waitForVisiblePage(page, i);
    const details = await inspectPage(page);
    const screenshotPath = path.join(screenshotDir, `page-${String(i).padStart(2, "0")}.png`);
    await page.screenshot({ path: screenshotPath, fullPage: true });
    viewportReport.screenshots.push(path.relative(ROOT, screenshotPath));
    viewportReport.checks.push({ page: i, ...details });

    if (i < pageCount - 1) {
      await page.keyboard.press("ArrowRight");
    }
  }

  const lastVisible = await getVisiblePage(page);
  if (lastVisible.length !== 1 || lastVisible[0].dataPage !== String(pageCount - 1)) {
    throw new Error(`Expected final page ${pageCount - 1}, found ${JSON.stringify(lastVisible)}`);
  }

  report.viewports.push(viewportReport);
  await context.close();
}

function summarize(report) {
  const failures = [];
  for (const viewport of report.viewports) {
    for (const err of viewport.consoleErrors) failures.push(`${viewport.name}: console error: ${err}`);
    for (const req of viewport.failedRequests) failures.push(`${viewport.name}: failed request: ${req.url}`);
    for (const check of viewport.checks) {
      if (check.visiblePages.length !== 1) failures.push(`${viewport.name} page ${check.page}: expected one visible page`);
      if (check.bodyOverflowsX) failures.push(`${viewport.name} page ${check.page}: document overflows horizontally (${check.documentWidth} > ${check.viewportWidth})`);
      for (const src of check.brokenImages) failures.push(`${viewport.name} page ${check.page}: broken image ${src}`);
      for (const item of check.visibleOverflow) {
        if (item.overflowsX) failures.push(`${viewport.name} page ${check.page}: visible page ${item.dataPage} overflows horizontally`);
      }
    }
  }
  return failures;
}

async function main() {
  const args = parseArgs(process.argv);
  const bookDir = path.join(ROOT, "books", args.slug);
  if (!fs.existsSync(path.join(bookDir, "index.html"))) {
    throw new Error(`Book site not found: ${path.join(bookDir, "index.html")}`);
  }
  if (!fs.existsSync(args.chromiumPath)) {
    throw new Error(`Chromium not found at ${args.chromiumPath}; pass --chromium or set CHROMIUM_PATH`);
  }

  fs.mkdirSync(args.outDir, { recursive: true });

  let server = null;
  const baseUrl = args.baseUrl || `http://127.0.0.1:${args.port}`;
  if (!args.baseUrl) {
    server = startServer(args.port);
    await waitForServer(`${baseUrl}/books/${args.slug}/`);
  }

  const report = {
    slug: args.slug,
    baseUrl,
    generatedAt: new Date().toISOString(),
    chromiumPath: args.chromiumPath,
    viewports: [],
  };

  let browser = null;
  try {
    browser = await chromium.launch({
      executablePath: args.chromiumPath,
      headless: true,
      args: ["--no-sandbox", "--disable-dev-shm-usage"],
    });

    for (const viewport of VIEWPORTS) {
      await runViewport(browser, args, viewport, baseUrl, report);
    }
  } finally {
    if (browser) await browser.close();
    if (server) server.kill();
  }

  const reportDir = path.join(args.outDir, args.slug);
  const reportPath = path.join(reportDir, "report.json");
  fs.writeFileSync(reportPath, `${JSON.stringify(report, null, 2)}\n`);

  const failures = summarize(report);
  console.log(`Visual QA screenshots: ${path.relative(ROOT, reportDir)}`);
  console.log(`Visual QA report: ${path.relative(ROOT, reportPath)}`);

  if (failures.length > 0) {
    console.error("Visual QA found issues:");
    for (const failure of failures) console.error(`- ${failure}`);
    process.exit(1);
  }

  console.log("Visual QA completed without detected issues.");
}

main().catch((err) => {
  console.error(err.stack || err.message);
  process.exit(1);
});
