"use strict";

class DataError extends Error {
  constructor(code, ...args) {
    super(code);
    this.args = args;
  }
}
function fail(code, ...args) { throw new DataError(code, ...args); }
const limits = {bytes: 12 * 1024 * 1024, cells: 500000, columns: 256};

function decode(buffer, encoding) {
  const bytes = new Uint8Array(buffer);
  if (bytes.length > limits.bytes) fail("fileSize");
  if (encoding === "auto") {
    encoding = bytes[0] === 255 && bytes[1] === 254 ? "utf-16le"
      : bytes[0] === 254 && bytes[1] === 255 ? "utf-16be" : "utf-8";
  }
  let value;
  try { value = new TextDecoder(encoding, {fatal:true}).decode(bytes); }
  catch { fail("encoding"); }
  if (value.includes("\0")) fail("binary");
  return {value, encoding};
}

function delimiter(text) {
  const counts = new Map([[",",0], [";",0], ["\t",0]]);
  let quoted = false;
  for (const c of text) {
    if (c === '"') quoted = !quoted;
    if (quoted) continue;
    if (c === "\n" || c === "\r") break;
    if (counts.has(c)) counts.set(c, counts.get(c) + 1);
  }
  return [...counts].sort((a,b) => b[1]-a[1])[0][0];
}

function parse(input, choice = "auto") {
  const text = input.replace(/^\uFEFF/, "");
  const sep = choice === "auto" ? delimiter(text) : choice;
  const rows = [];
  let headers, fields = [], value = "", quoted = false, closed = false, touched = false, cells = 0;
  function pushField() {
    if (++cells > limits.cells || fields.length >= limits.columns) fail("cellLimit");
    fields.push(value);
    value = "";
    closed = false;
  }
  function endRecord() {
    if (!touched) return;
    pushField();
    if (!headers) {
      if (fields.some(h => !h.trim()) || new Set(fields).size !== fields.length) fail("header");
      headers = fields;
    } else {
      if (fields.length !== headers.length) fail("width", rows.length + 2, fields.length, headers.length);
      rows.push(fields);
    }
    fields = [];
    touched = false;
  }
  for (let i=0; i<text.length; i++) {
    const c = text[i];
    if (quoted) {
      if (c !== '"') value += c;
      else if (text[i+1] === '"') { value += c; i++; }
      else { quoted = false; closed = true; }
    } else if (c === "\r" || c === "\n") {
      endRecord();
      if (c === "\r" && text[i+1] === "\n") i++;
    } else if (c === sep) {
      touched = true;
      pushField();
    } else {
      touched = true;
      if (closed || (c === '"' && value.length)) fail("quote", rows.length + (headers ? 2 : 1));
      if (c === '"') quoted = true;
      else value += c;
    }
  }
  if (quoted) fail("quote", rows.length + (headers ? 2 : 1));
  endRecord();
  if (!headers) fail("empty");
  return {headers, rows, sep};
}

function indexTable(table, keys, side) {
  const cols = keys.map(k => table.headers.indexOf(k));
  const map = new Map();
  for (const [i, row] of table.rows.entries()) {
    const parts = cols.map(c => row[c]);
    if (parts.some(s => !s.trim())) fail("blankKey", side, i+2);
    const key = JSON.stringify(parts);
    if (map.has(key)) fail("dupKey", side, map.get(key)+2, i+2);
    map.set(key, i);
  }
  return map;
}

function compare(a, b, keys) {
  if (!keys.length || keys.some(k => !a.headers.includes(k) || !b.headers.includes(k))) fail("key");
  const left = indexTable(a, keys, "A"), right = indexTable(b, keys, "B");
  const all = [...new Set([...a.headers, ...b.headers])];
  const cols = all.map(h => ({h, x:a.headers.indexOf(h), y:b.headers.indexOf(h)}));
  const common = cols.filter(c => c.x >= 0 && c.y >= 0 && !keys.includes(c.h));
  const schema = cols.filter(c => c.x < 0 || c.y < 0);
  const records = [], counts = {changed:0, added:0, removed:0, same:0};
  const add = (key, status, x, y) => { counts[status]++; records.push({key, status, x, y}); };
  for (const [key, x] of left) {
    const y = right.get(key);
    if (y === undefined) add(key, "removed", x, null);
    else if (common.some(c => a.rows[x][c.x] !== b.rows[y][c.y])) add(key,"changed",x,y);
    else counts.same++;
  }
  for (const [key, y] of right) if (!left.has(key)) add(key, "added", null, y);
  return {records, counts, schema, cols, common, a, b};
}

function* details(diff, row) {
  const changed = row.status === "changed";
  for (const {h,x,y} of changed ? diff.common : diff.cols) {
    const before = row.x === null || x < 0 ? null : diff.a.rows[row.x][x];
    const after = row.y === null || y < 0 ? null : diff.b.rows[row.y][y];
    if (before !== after) yield [h, before, after];
  }
}
function query(diff, status, needle) {
  const s = needle.trim().toLowerCase();
  return diff.records.filter(r => {
    if (status !== "all" && status !== r.status) return false;
    if (!s || JSON.parse(r.key).some(k => k.toLowerCase().includes(s))) return true;
    for (const cells of details(diff,r)) if (cells.some(v => v !== null && v.toLowerCase().includes(s))) return true;
    return false;
  });
}
function csvCell(v) {
  let s = v ?? "";
  if (/^[\s\uFEFF]*[=+\-@\uFF1D\uFF0B\uFF0D\uFF20]/u.test(s) || /^[\t\r\n]/.test(s)) s = "'" + s;
  return '"' + s.replaceAll('"','""') + '"';
}
function exportCSV(diff, keys) {
  let length = 0;
  const chunks = [];
  function append(cells) {
    const line = cells.map(csvCell).join(",") + "\r\n";
    length += line.length;
    if (length > 24 * 1024 * 1024) fail("exportLimit");
    chunks.push(line);
  }
  append(["status", ...keys.map(k=>"key:"+k), "field", "before", "after"]);
  for (const c of diff.schema) append([c.x < 0 ? "column_added" : "column_removed", ...keys.map(()=>""), c.h,"",""]);
  for (const r of diff.records) {
    const parts = JSON.parse(r.key);
    for (const triple of details(diff,r)) append([r.status,...parts,...triple]);
  }
  return new Blob(["\uFEFF", ...chunks],{type:"text/csv;charset=utf-8"});
}
if (typeof module !== "undefined") module.exports = {decode, parse, compare, details, query, exportCSV};
