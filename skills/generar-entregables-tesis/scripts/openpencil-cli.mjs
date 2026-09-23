#!/usr/bin/env node
import { execFileSync } from "node:child_process";
import { existsSync, realpathSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { pathToFileURL } from "node:url";
import fs from "node:fs/promises";

function resolveCliDist() {
  if (process.env.OPENPENCIL_CLI_DIST) {
    return resolve(process.env.OPENPENCIL_CLI_DIST);
  }

  const bin = process.env.OPENPENCIL_BIN || execFileSync("which", ["openpencil"], {
    encoding: "utf8",
  }).trim();
  const realBin = realpathSync(bin);
  const candidate = resolve(dirname(realBin), "../dist/index.mjs");
  if (!existsSync(candidate)) {
    throw new Error(`No se encuentra OpenPencil CLI dist: ${candidate}`);
  }
  return candidate;
}

globalThis.Bun = {
  file(path) {
    return { text: () => fs.readFile(path, "utf8") };
  },
  write(path, data) {
    return fs.writeFile(path, data);
  },
};

await import(pathToFileURL(resolveCliDist()).href);
