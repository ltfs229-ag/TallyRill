let tables = [], diff, keys, lastFilter, matches;
onmessage = async ({data}) => {
  try {
    if (data.op === "load") {
      diff = null;
      tables = [];
      for (const [i,file] of data.files.entries()) {
        if (!file) { tables.push(null); continue; }
        try {
          if (file.size > limits.bytes) fail("fileSize");
          const {value,encoding} = decode(await file.arrayBuffer(), data.enc[i]);
          const table = parse(value, data.sep[i]);
          table.encoding = encoding;
          tables.push(table);
        } catch(e) { e.side = i ? "B" : "A"; throw e; }
      }
      const meta = tables.map(t => t && ({headers:t.headers, count:t.rows.length, encoding:t.encoding, sep:t.sep}));
      postMessage({op:"loaded", meta});
    } else if (data.op === "compare") {
      diff = null;
      keys = data.keys;
      diff = compare(...tables, keys);
      lastFilter = null;
      postMessage({op:"compared", counts:diff.counts, schema:diff.schema});
    } else if (data.op === "page") {
      const f = JSON.stringify([data.status,data.search]);
      if (lastFilter !== f) { matches = query(diff,data.status,data.search); lastFilter = f; }
      const rows = matches.slice(data.start,data.start + 12).map(r => ({
        key:JSON.parse(r.key), status:r.status, cells:[...details(diff,r)]
      }));
      postMessage({op:"page", seq:data.seq, rows, total:matches.length, start:data.start});
    } else if (data.op === "export") postMessage({op:"export", blob:exportCSV(diff,keys)});
  } catch(e) {
    postMessage({op:"error", action:data.op, code:e instanceof DataError ? e.message : "unexpected", args:e.args || [], side:e.side});
  }
};
