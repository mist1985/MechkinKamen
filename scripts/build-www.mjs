/* Assembles www/ — the folder Capacitor copies into the Android APK.
   The game stays a single source file at the repo root so GitHub Pages keeps
   serving it; this only stages a copy named index.html, which is what a
   WebView expects to find. */

import { mkdir, copyFile, rm, readFile, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const www = resolve(root, 'www');

await rm(www, { recursive: true, force: true });
await mkdir(resolve(www, 'vendor'), { recursive: true });

const html = await readFile(resolve(root, 'mechkin-kamen.html'), 'utf8');
await writeFile(resolve(www, 'index.html'), html);
await copyFile(resolve(root, 'vendor/three.min.js'), resolve(www, 'vendor/three.min.js'));
await copyFile(resolve(root, 'ads.js'), resolve(www, 'ads.js'));
await copyFile(resolve(root, 'native.js'), resolve(www, 'native.js'));

console.log('www/ built — index.html + ads.js + native.js + vendor/three.min.js');
