#!/usr/bin/env node
'use strict';

const path = require('path');
const { crawl } = require('../cudy/forensic');

function parseArgs(argv) {
  const out = {};

  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];

    if (arg === '--help' || arg === '-h') {
      out.help = true;
      continue;
    }

    if (!arg.startsWith('--')) {
      throw new Error('Unknown argument: ' + arg);
    }

    const key = arg
      .slice(2)
      .replace(/-([a-z])/g, (_, c) => c.toUpperCase());

    const value = argv[++i];
    if (value == null) throw new Error('Missing value for ' + arg);
    out[key] = value;
  }

  return out;
}

function help() {
  console.log([
    'fu_6 Cudy Emulator Forensic Downloader',
    '',
    'Usage:',
    '  node bin/cudy-forensic.js --url https://support.cudy.com/emulator/C200P/ [options]',
    '',
    'Options:',
    '  --url URL',
    '  --output DIR',
    '  --max-requests N    default: 0 (unlimited)',
    '  --max-bytes N       default: 0 (unlimited)',
    '  --delay-ms N        default: 0',
    '  --timeout-ms N      default: 0 (no artificial timeout)',
    '',
    'Safety:',
    '  Full asset capture by default. GET only, same emulator subtree recursively.',
    '  Live destructive actions are not invoked; their public static emulator snapshots are kept.',
    '  No auth bypass, brute force, version guessing, timestamp spraying or POST.'
  ].join('\n'));
}

(async function main() {
  try {
    const args = parseArgs(process.argv.slice(2));

    if (args.help) {
      help();
      return;
    }

    if (!args.url) {
      help();
      process.exitCode = 2;
      return;
    }

    if (args.output) args.output = path.resolve(args.output);

    const result = await crawl(args);
    console.log(JSON.stringify(result, null, 2));
  } catch (err) {
    console.error('fu_6 error: ' + err.message);
    process.exitCode = 1;
  }
})();
