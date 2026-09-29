'use strict';

const fs = require('fs');
const fsp = fs.promises;
const path = require('path');
const crypto = require('crypto');
const http = require('http');
const https = require('https');

const DROP_QUERY_KEYS = new Set([
  'search', 'sort', 'order', 'offset', 'limit',
  'filter', 'filterOptions', 'pageNumber', 'pageSize', '_'
]);

const DANGEROUS_ROUTE = /(?:\/logout|\/reboot|\/reset|\/forget|\/revert|batchupgrade|batchadopt|\/gcom\/search)(?:[/?]|$)/i;
const ATTR_RE = /<[^>]+\b(?:href|src|action)\s*=\s*["']([^"']+)["'][^>]*>/gi;
const HTML_BASE_RE = /<base\s+[^>]*href\s*=\s*["']([^"']+)["'][^>]*>/i;
const CSS_URL_RE = /url\(\s*["']?([^"')]+)["']?\s*\)/gi;
const LUCI_RE = /["'`](\/?(?:cgi-bin\/luci|admin)\/[A-Za-z0-9_./%?=&:+-]+)["'`]/g;
const STATIC_RE = /["'`](\.\/?cgi-bin\/luci\/[A-Za-z0-9_./%?=&:+-]+\.html)["'`]/g;
const JQ_POST_RE = /\$\.post\(\s*["'`]([^"'`]+)["'`]\s*,\s*\{([^}]*)\}/g;
const SIMPLE_PAIR_RE = /([A-Za-z0-9_.-]+)\s*:\s*["'`]([^"'`]*)["'`]/g;

function sha256(buffer) {
  return crypto.createHash('sha256').update(buffer).digest('hex');
}

function sleep(ms) {
  if (!ms || ms <= 0) return Promise.resolve();
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function decodeHtmlForDiscovery(text) {
  return String(text || '')
    .replace(/&quot;/gi, '"')
    .replace(/&#34;/g, '"')
    .replace(/&#39;|&apos;/gi, "'")
    .replace(/&amp;/gi, '&')
    .replace(/&lt;/gi, '<')
    .replace(/&gt;/gi, '>');
}

function unlimitedNumber(value) {
  if (value == null || value === '' || Number(value) <= 0) return Infinity;
  return Number(value);
}

function isStaticSnapshotUrl(href, source) {
  try {
    const u = new URL(href);
    if (/\.html$/i.test(u.pathname)) return true;
  } catch (_) {}
  return /^(?:static-map|luci-map):/.test(source || '');
}

function mapQueryPath(filePath) {
  if (filePath.indexOf('?') < 0) return filePath;

  var fp = filePath;
  if (fp.indexOf('=&') >= 0 && fp.charAt(fp.length - 1) === '=') {
    fp = fp.replace(/=+$/, '');
  }

  return fp
    .replace(/=\&/g, '/')
    .replace(/\?/g, '/')
    .replace(/=/g, '/')
    .replace(/ /g, '_')
    .replace(/:/g, '_')
    .replace(/&/g, '/');
}

function emulatorBaseFromUrl(input) {
  const u = new URL(input);
  const match = u.pathname.match(/^(\/emulator\/[^/]+\/)/i);
  if (!match) throw new Error('Target must be inside /emulator/<MODEL>/');
  return new URL(match[1], u.origin);
}

function sameEmulatorScope(candidate, base) {
  try {
    const u = new URL(candidate, base);
    return u.origin === base.origin && u.pathname.startsWith(base.pathname);
  } catch (_) {
    return false;
  }
}

function resolveCandidate(raw, pageUrl, base) {
  if (!raw || typeof raw !== 'string') return null;

  let value = raw.trim();
  if (!value || /^(?:data:|mailto:|tel:|javascript:|#)/i.test(value)) return null;

  if (/^\/cgi-bin\/luci(?:\/|$)/i.test(value)) {
    return new URL(value.replace(/^\//, ''), base).href;
  }

  if (/^cgi-bin\/luci(?:\/|$)/i.test(value)) {
    return new URL(value, base).href;
  }

  if (/^admin\//i.test(value)) {
    return new URL('cgi-bin/luci/' + value, base).href;
  }

  if (/^\/admin\//i.test(value)) {
    return new URL('cgi-bin/luci' + value, base).href;
  }

  try {
    return new URL(value, pageUrl).href;
  } catch (_) {
    return null;
  }
}

function normalizeLuciUrl(raw, pageUrl, base) {
  const resolved = resolveCandidate(raw, pageUrl, base);
  if (!resolved) return null;

  try {
    const u = new URL(resolved);
    if (u.pathname.indexOf('/cgi-bin/luci') < 0) return null;
    return u.href;
  } catch (_) {
    return null;
  }
}

function bodyPairsToQuery(bodyText) {
  const params = new URLSearchParams();
  let match;

  SIMPLE_PAIR_RE.lastIndex = 0;
  while ((match = SIMPLE_PAIR_RE.exec(bodyText || ''))) {
    params.append(match[1], match[2]);
  }

  return params.toString();
}

function luciStaticRelative(urlStr, pageUrl, base, bodyParams) {
  const normalized = normalizeLuciUrl(urlStr, pageUrl, base);
  if (!normalized) return null;

  const u = new URL(normalized);

  Array.from(u.searchParams.keys()).forEach((key) => {
    if (DROP_QUERY_KEYS.has(key)) u.searchParams.delete(key);
  });

  const idx = u.pathname.lastIndexOf('/cgi-bin/luci');
  if (idx < 0) return null;

  const luciPath = u.pathname.slice(idx + 1);
  let query = u.search ? u.search.slice(1) : '';

  if (bodyParams) {
    query = query ? query + '&' + bodyParams : bodyParams;
  }

  let mapped = mapQueryPath(query ? luciPath + '?' + query : luciPath);

  if (luciPath === 'cgi-bin/luci' || luciPath === 'cgi-bin/luci/') {
    mapped = 'cgi-bin/luci/index';
  }

  if (!mapped.endsWith('.html')) mapped += '.html';

  return mapped.replace(/%(?!25)/g, '%25');
}

function toStaticEmulatorUrl(route, pageUrl, base, bodyParams) {
  const rel = luciStaticRelative(route, pageUrl, base, bodyParams || '');
  return rel ? new URL(rel, base).href : null;
}

function extractReferences(text, contentType, pageUrl, base) {
  const urls = new Set();
  const routes = new Set();
  const mapped = new Set();

  const textual = /^text\//i.test(contentType) ||
    /(?:html|json|javascript|css|xml)/i.test(contentType);

  if (!textual) return { urls, routes, mapped };

  const scanText = /html/i.test(contentType) ? decodeHtmlForDiscovery(text) : text;

  let documentBase = pageUrl;
  if (/html/i.test(contentType)) {
    const baseMatch = HTML_BASE_RE.exec(scanText);
    if (baseMatch) {
      try { documentBase = new URL(baseMatch[1], pageUrl).href; } catch (_) {}
    }
  }

  const addUrl = (raw) => {
    const resolved = resolveCandidate(raw, documentBase, base);
    if (resolved) urls.add(resolved);
  };

  let match;

  ATTR_RE.lastIndex = 0;
  while ((match = ATTR_RE.exec(scanText))) addUrl(match[1]);

  CSS_URL_RE.lastIndex = 0;
  while ((match = CSS_URL_RE.exec(scanText))) addUrl(match[1]);

  STATIC_RE.lastIndex = 0;
  while ((match = STATIC_RE.exec(scanText))) addUrl(match[1]);

  LUCI_RE.lastIndex = 0;
  while ((match = LUCI_RE.exec(scanText))) {
    const route = normalizeLuciUrl(match[1], pageUrl, base);
    if (!route) continue;

    routes.add(route);

    const staticUrl = toStaticEmulatorUrl(route, pageUrl, base);
    if (staticUrl) mapped.add(staticUrl);
  }

  // The emulator shim can map POST bodies to static path elements.
  // We never send the POST. We only derive the corresponding static GET.
  JQ_POST_RE.lastIndex = 0;
  while ((match = JQ_POST_RE.exec(scanText))) {
    const route = normalizeLuciUrl(match[1], pageUrl, base);
    if (!route) continue;

    routes.add(route);
    const bodyQuery = bodyPairsToQuery(match[2]);
    const staticUrl = toStaticEmulatorUrl(route, pageUrl, base, bodyQuery);
    if (staticUrl) mapped.add(staticUrl);
  }

  return { urls, routes, mapped };
}

function extractFindings(text) {
  const findings = new Set();
  const patterns = [
    /\b\d+\.\d+\.\d+-20\d{6}-\d{6}\b/g,
    /\b(?:R\d{1,4}|LT500D?|C200P|TR3000)\b/g,
    /\b[A-Za-z0-9_-]+-R\d+-\d+\.\d+\.\d+-20\d{6}-\d{6}-(?:flash|sysupgrade)(?:_[0-9a-f-]{36})?\.(?:zip|bin)\b/gi,
    /https?:\/\/[^\s"'<>]+/g,
    /\/cgi-bin\/luci\/[A-Za-z0-9_./%?=&:+-]+/g
  ];

  patterns.forEach((pattern) => {
    pattern.lastIndex = 0;
    let match;
    while ((match = pattern.exec(text))) {
      findings.add(match[0].slice(0, 500));
    }
  });

  return Array.from(findings);
}

function safeSegment(segment) {
  let decoded = segment;
  try {
    decoded = decodeURIComponent(segment);
  } catch (_) {}

  decoded = decoded.replace(/[^A-Za-z0-9._-]+/g, '_');
  decoded = decoded.replace(/^_+|_+$/g, '');
  return decoded || '_';
}

function outputPathForUrl(url, contentType, base) {
  const u = new URL(url);
  const parts = u.pathname.split('/').filter(Boolean).map(safeSegment);

  if (base && (u.origin !== base.origin || !u.pathname.startsWith(base.pathname))) {
    parts.unshift('_external', safeSegment(u.hostname));
  }
  let name = parts.pop() || 'index';

  if (u.search) {
    name += '__q_' + crypto.createHash('sha1').update(u.search).digest('hex').slice(0, 12);
  }

  if (!/\.[A-Za-z0-9]{1,8}$/.test(name)) {
    if (/html/i.test(contentType)) name += '.html';
    else if (/json/i.test(contentType)) name += '.json';
    else if (/javascript/i.test(contentType)) name += '.js';
    else if (/css/i.test(contentType)) name += '.css';
    else name += '.bin';
  }

  return path.join.apply(path, parts.concat(name));
}

function csvEscape(value) {
  const s = String(value == null ? '' : value);
  if (/[",\n\r]/.test(s)) return '"' + s.replace(/"/g, '""') + '"';
  return s;
}

function requestBuffer(url, options, redirectCount) {
  redirectCount = redirectCount || 0;

  return new Promise((resolve, reject) => {
    if (redirectCount > 5) {
      reject(new Error('too many redirects'));
      return;
    }

    const u = new URL(url);
    const transport = u.protocol === 'https:' ? https : http;

    const req = transport.request(u, {
      method: 'GET',
      headers: {
        'User-Agent': options.userAgent,
        'Accept': '*/*'
      }
    }, (res) => {
      const status = res.statusCode || 0;
      const location = res.headers.location;

      if (status >= 300 && status < 400 && location) {
        const next = new URL(location, u).href;
        res.resume();

        if (!sameEmulatorScope(next, options.base)) {
          reject(new Error('redirect left emulator scope: ' + next));
          return;
        }

        requestBuffer(next, options, redirectCount + 1).then(resolve, reject);
        return;
      }

      const declared = Number(res.headers['content-length'] || 0);
      if (Number.isFinite(options.maxBytes) && declared && declared > options.maxBytes) {
        res.resume();
        reject(new Error('content-length exceeds maxBytes: ' + declared));
        return;
      }

      const chunks = [];
      let size = 0;

      res.on('data', (chunk) => {
        size += chunk.length;
        if (Number.isFinite(options.maxBytes) && size > options.maxBytes) {
          req.destroy(new Error('response exceeds maxBytes'));
          return;
        }
        chunks.push(chunk);
      });

      res.on('end', () => {
        resolve({
          finalUrl: u.href,
          status,
          headers: res.headers,
          body: Buffer.concat(chunks)
        });
      });
    });

    if (Number.isFinite(options.timeoutMs) && options.timeoutMs > 0) {
      req.setTimeout(options.timeoutMs, () => {
        req.destroy(new Error('request timeout'));
      });
    }

    req.on('error', reject);
    req.end();
  });
}

async function crawl(options) {
  const start = new URL(options.url).href;
  const base = emulatorBaseFromUrl(start);
  const model = base.pathname.split('/').filter(Boolean).pop();

  const outputRoot = path.resolve(options.output || path.join('cudy-forensic-output', model));
  const rawRoot = path.join(outputRoot, 'raw');

  const settings = {
    base,
    maxBytes: unlimitedNumber(options.maxBytes),
    maxRequests: unlimitedNumber(options.maxRequests),
    delayMs: Number(options.delayMs || 0),
    timeoutMs: unlimitedNumber(options.timeoutMs),
    userAgent: options.userAgent || 'fu_6-cudy-emulator-forensic-downloader/0.1'
  };

  await fsp.mkdir(rawRoot, { recursive: true });

  const queue = [];
  const queued = new Set();
  const visited = new Set();
  const allRoutes = new Set();
  const hiddenRoutes = new Set();
  const unresolved = new Set();
  const inventory = [];
  const findingMap = {};

  function enqueue(candidate, source, leaf) {
    let href;

    try {
      href = new URL(candidate, base).href;
    } catch (_) {
      return;
    }

    const inScope = sameEmulatorScope(href, base);
    if (!inScope && !leaf) return;
    if (visited.has(href) || queued.has(href)) return;
    if (DANGEROUS_ROUTE.test(href) && !isStaticSnapshotUrl(href, source)) return;

    queued.add(href);
    queue.push({ url: href, source: source || 'discovered', leaf: Boolean(leaf && !inScope) });
  }

  enqueue(start, 'seed');
  enqueue(base.href, 'emulator-root');

  while (queue.length && visited.size < settings.maxRequests) {
    if (typeof options.shouldCancel === 'function' && options.shouldCancel()) {
      break;
    }

    const item = queue.shift();
    queued.delete(item.url);

    if (visited.has(item.url)) continue;
    visited.add(item.url);

    let response;

    try {
      const requestSettings = item.leaf
        ? Object.assign({}, settings, { base: new URL('/', new URL(item.url).origin) })
        : settings;
      response = await requestBuffer(item.url, requestSettings, 0);
    } catch (err) {
      inventory.push({
        url: item.url,
        status: '',
        content_type: '',
        content_length: '',
        bytes: '',
        sha256: '',
        saved_as: '',
        source: item.source,
        error: err.message
      });
      unresolved.add(item.url);
      await sleep(settings.delayMs);
      continue;
    }

    const contentType = String(response.headers['content-type'] || '');
    const declared = String(response.headers['content-length'] || '');
    const rel = outputPathForUrl(item.url, contentType, base);
    const out = path.join(rawRoot, rel);

    await fsp.mkdir(path.dirname(out), { recursive: true });
    await fsp.writeFile(out, response.body);

    inventory.push({
      url: item.url,
      status: response.status,
      content_type: contentType,
      content_length: declared,
      bytes: response.body.length,
      sha256: sha256(response.body),
      saved_as: path.relative(outputRoot, out),
      source: item.source,
      error: ''
    });

    if (response.status < 200 || response.status >= 300) {
      unresolved.add(item.url);
      await sleep(settings.delayMs);
      continue;
    }

    const textual = /^text\//i.test(contentType) ||
      /(?:html|json|javascript|css|xml)/i.test(contentType);

    if (!textual || item.leaf) {
      await sleep(settings.delayMs);
      continue;
    }

    const text = response.body.toString('utf8');
    const found = extractFindings(text);
    if (found.length) findingMap[item.url] = found;

    const refs = extractReferences(text, contentType, item.url, base);

    refs.urls.forEach((url) => {
      enqueue(url, 'asset:' + item.url, !sameEmulatorScope(url, base));
    });

    refs.routes.forEach((route) => {
      allRoutes.add(route);

      const staticUrl = toStaticEmulatorUrl(route, item.url, base);
      if (staticUrl) {
        hiddenRoutes.add(route);
        enqueue(staticUrl, 'luci-map:' + route);
      }

      if (sameEmulatorScope(route, base)) {
        enqueue(route, 'luci-direct:' + item.url);
      }
    });

    refs.mapped.forEach((url) => enqueue(url, 'static-map:' + item.url));

    if (typeof options.shouldCancel === 'function' && options.shouldCancel()) {
      break;
    }

    await sleep(settings.delayMs);
  }

  const columns = [
    'url', 'status', 'content_type', 'content_length',
    'bytes', 'sha256', 'saved_as', 'source', 'error'
  ];

  const csv = [
    columns.join(','),
    ...inventory.map((row) => columns.map((key) => csvEscape(row[key])).join(','))
  ].join('\n') + '\n';

  await fsp.writeFile(path.join(outputRoot, 'fu_6-inventory.csv'), csv);
  await fsp.writeFile(
    path.join(outputRoot, 'fu_6-all-luci-routes.txt'),
    Array.from(allRoutes).sort().join('\n') + '\n'
  );
  await fsp.writeFile(
    path.join(outputRoot, 'fu_6-hidden-luci-routes.txt'),
    Array.from(hiddenRoutes).sort().join('\n') + '\n'
  );
  await fsp.writeFile(
    path.join(outputRoot, 'fu_6-unresolved.txt'),
    Array.from(unresolved).sort().join('\n') + '\n'
  );
  await fsp.writeFile(
    path.join(outputRoot, 'fu_6-findings.json'),
    JSON.stringify(findingMap, null, 2) + '\n'
  );
  await fsp.writeFile(
    path.join(outputRoot, 'fu_6-run.json'),
    JSON.stringify({
      tool: 'fu_6-cudy-emulator-forensic-downloader',
      started_from: start,
      emulator_base: base.href,
      model,
      visited: visited.size,
      discovered_luci_routes: allRoutes.size,
      unresolved: unresolved.size,
      settings: {
        max_requests: Number.isFinite(settings.maxRequests) ? settings.maxRequests : null,
        max_bytes: Number.isFinite(settings.maxBytes) ? settings.maxBytes : null,
        delay_ms: settings.delayMs,
        timeout_ms: Number.isFinite(settings.timeoutMs) ? settings.timeoutMs : null
      },
      safety: {
        method: 'GET only',
        recursive_scope: 'selected emulator subtree',
        directly_referenced_external_dependencies_saved_as_leaves: true,
        live_destructive_routes_skipped_but_static_snapshots_kept: true,
        no_asset_type_filtering: true,
        no_default_request_cap: true,
        no_default_response_size_cap: true,
        no_default_delay: true,
        no_default_timeout: true,
        no_auth_bypass: true,
        no_bruteforce: true,
        no_version_or_timestamp_spraying: true
      }
    }, null, 2) + '\n'
  );

  return {
    outputRoot,
    model,
    visited: visited.size,
    routes: allRoutes.size,
    unresolved: unresolved.size
  };
}

async function discoverEmulatorModels(indexUrl, options) {
  const index = new URL(indexUrl || 'https://support.cudy.com/');
  const requestOptions = {
    base: new URL('/', index.origin),
    maxBytes: unlimitedNumber(options && options.maxBytes),
    timeoutMs: unlimitedNumber(options && options.timeoutMs),
    userAgent: (options && options.userAgent) || 'fu_6-cudy-emulator-forensic-downloader/0.1'
  };

  const response = await requestBuffer(index.href, requestOptions, 0);
  const text = response.body.toString('utf8');
  const models = new Set();
  const re = /(?:https?:\/\/support\.cudy\.com)?\/emulator\/([^/"'?&#<>]+)\//gi;
  let match;

  while ((match = re.exec(text))) {
    models.add(decodeURIComponent(match[1]));
  }

  return Array.from(models).sort();
}

async function crawlAllEmulators(options) {
  options = options || {};
  const indexUrl = options.indexUrl || 'https://support.cudy.com/';
  const outputRoot = path.resolve(options.output || 'cudy-forensic-output');
  const models = await discoverEmulatorModels(indexUrl, options);
  const results = [];

  await fsp.mkdir(outputRoot, { recursive: true });

  for (const model of models) {
    if (typeof options.shouldCancel === 'function' && options.shouldCancel()) break;

    const result = await crawl({
      url: new URL('/emulator/' + encodeURIComponent(model) + '/', new URL(indexUrl).origin).href,
      output: path.join(outputRoot, model),
      maxBytes: options.maxBytes,
      maxRequests: options.maxRequests,
      delayMs: options.delayMs,
      timeoutMs: options.timeoutMs,
      userAgent: options.userAgent,
      shouldCancel: options.shouldCancel
    });

    results.push(result);
  }

  const summary = results.map((r) => ({
    model: r.model,
    visited: r.visited,
    routes: r.routes,
    unresolved: r.unresolved,
    output_root: r.outputRoot
  }));

  await fsp.writeFile(
    path.join(outputRoot, 'fu_6-models.json'),
    JSON.stringify(summary, null, 2) + '\n'
  );

  const routeMaster = new Set();
  for (const result of results) {
    try {
      const routes = await fsp.readFile(
        path.join(result.outputRoot, 'fu_6-all-luci-routes.txt'),
        'utf8'
      );
      routes.split(/\r?\n/).filter(Boolean).forEach((r) => routeMaster.add(r));
    } catch (_) {}
  }

  await fsp.writeFile(
    path.join(outputRoot, 'fu_6-routes-master.txt'),
    Array.from(routeMaster).sort().join('\n') + '\n'
  );

  return {
    outputRoot,
    models: models.length,
    completed: results.length,
    results: summary
  };
}

module.exports = {
  crawl,
  crawlAllEmulators,
  discoverEmulatorModels,
  mapQueryPath,
  emulatorBaseFromUrl,
  sameEmulatorScope,
  resolveCandidate,
  luciStaticRelative,
  toStaticEmulatorUrl,
  extractReferences,
  bodyPairsToQuery
};
