#!/usr/bin/env node
/// <reference types="node" />
import fs from 'fs/promises';
import path from 'path';
import { spawnSync } from 'child_process';
import http from 'http';
import https from 'https';
import { fileURLToPath } from 'url';

const OPENAPI_URL = process.env.OPENAPI_URL ?? 'http://localhost:8000/openapi.json';
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const root = path.resolve(__dirname, '..');
const inputPath = path.join(root, 'openapi', 'openapi.json');
const outputDir = path.join(root, 'src', 'utils', 'api');

function downloadToFile(urlStr: string, filePath: string): Promise<void> {
  return new Promise((resolve, reject) => {
    try {
      const url = new URL(urlStr);
      const lib = url.protocol === 'https:' ? https : http;
      const req = lib.get(url, (res: http.IncomingMessage) => {
        const status = res.statusCode ?? 0;
        if (status < 200 || status >= 300) {
          reject(new Error(`Failed to fetch ${urlStr}: ${status} ${res.statusMessage}`));
          res.resume();
          return;
        }
        const chunks: Buffer[] = [];
        res.on('data', (c: Buffer) => chunks.push(c));
        res.on('end', () => {
          fs.mkdir(path.dirname(filePath), { recursive: true })
            .then(() => fs.writeFile(filePath, Buffer.concat(chunks).toString('utf8'), 'utf8'))
            .then(() => resolve())
            .catch((err) => reject(err));
        });
      });
      req.on('error', reject);
    } catch (err) {
      reject(err);
    }
  });
}

async function main(): Promise<number> {
  try {
    console.log(`Downloading OpenAPI JSON from: ${OPENAPI_URL}`);
    await downloadToFile(OPENAPI_URL, inputPath);
    console.log(`Saved OpenAPI to ${inputPath}`);

    // remove previous generated api folder to avoid stale files left behind
    try {
      await fs.rm(outputDir, { recursive: true, force: true });
      console.log(`Removed existing API output dir: ${outputDir}`);
    } catch (rmErr) {
      console.warn(`Warning: failed to remove ${outputDir}:`, rmErr);
    }

    const args = [
      'openapi-typescript-codegen',
      '--input', inputPath,
      '--output', outputDir,
      '--client', 'axios',
    ];

    console.log('Running codegen with npx', args.join(' '));
    const r = spawnSync('npx', args, { stdio: 'inherit' });
    if (r.error) {
      console.error('Failed to run npx:', r.error);
    }

    // always try to remove the downloaded openapi.json after generation
    try {
      await fs.rm(inputPath, { force: true });
      console.log(`Removed downloaded OpenAPI file: ${inputPath}`);
    } catch (delErr) {
      console.warn(`Warning: failed to remove downloaded OpenAPI file ${inputPath}:`, delErr);
    }

    return r.status ?? (r.error ? 1 : 0);
  } catch (err) {
    console.error(err);
    return 1;
  }
}

// execute
main().then((code) => process.exit(code)).catch((e) => { console.error(e); process.exit(1); });
