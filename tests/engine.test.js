const {test} = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const {parse, decode, compare, details, query, exportCSV} = require("../src/engine");
const examples = ["before","after"].map(side=>parse(fs.readFileSync(path.join(__dirname,"../examples/catalog-"+side+".csv"),"utf8")));
test("warehouse reference and reordered headers",()=>{
  const result=compare(...examples,["SKU","Depot"]);
  assert.deepEqual(result.counts,{changed:3,added:1,removed:1,same:4});
  assert.equal(query(result,"changed","").flatMap(r=>[...details(result,r)]).length,4);
  assert.equal(query(result,"changed","cl-101").length,1);
  assert.equal(compare(parse("a,b\nx,1\ny,2"),parse("b,a\n2,y\n1,x"),["a"]).counts.same,2);
});
test("quoted separators, doubled quotes, embedded CRLF and blank records",()=>{
  assert.deepEqual(parse('\uFEFFa;b\r\n\r\n"x;y";"z""q\r\ns"\r\n').rows,[["x;y",'z"q\r\ns']]);
  assert.equal(parse("A\tB\n\t").rows[0][1],"");
  assert.deepEqual(parse('x\n""').rows,[[""]]);
});
test("header-only sources and schema differences are distinct",async()=>{
  const d=compare(parse("ID,old"),parse("new,ID\nv,001"),["ID"]);
  assert.deepEqual(d.schema.map(c=>c.h),["old","new"]);
  const csv=await (exportCSV(d,["ID"])).text();
  assert.match(csv,/column_removed/);assert.match(csv,/column_added/);assert.match(csv,/"001"/);
  const s=compare(parse("a,b\nx,2"),parse("a,c\nx,3"),["a"]);
  assert.equal(s.counts.same,1);
});
test("nonunique or blank identifiers stop with source and record numbers",()=>{
  for(const [csv,expected] of [["a,b\nx,1\nx,2",["B",2,3]],["a,b\n ,0",["B",2]]]){
    assert.throws(()=>compare(parse("a,b"),parse(csv),["a"]),err=>{assert.deepEqual(err.args,expected);return true;});
  }
  assert.throws(()=>compare(...examples,[]),/key/);
});
test("no accidental normalization or tuple collisions",()=>{
  const a=parse('a,b,c\n01,x,one\n1,x,two\n"a,b",c,three\na,"b,c",four\n__proto__,q,five');
  const d=compare(a,a,["a","b"]);assert.equal(d.counts.same,5);
  assert.equal(compare(parse("k,v\nX,1.0"),parse("k,v\nX,1.00"),["k"]).counts.changed,1);
});
test("malformed inputs are rejected",()=>{
  for(const csv of ['a,b\n1','a,a\n1,2',',b','a,b\nx,"unterminated','a,b\nx,"abc"x','a,b\nx,b"ad','\n'])
    assert.throws(()=>parse(csv));
  assert.throws(()=>parse(Array(257).fill("x").join(",")),/cellLimit/);
  assert.throws(()=>parse("a,b\n"+"x,y\n".repeat(250000)),/cellLimit/);
});
test("encoding and input size guards",()=>{
  assert.equal(decode(new Uint8Array([0xcf,0xf0]),"windows-1251").value,"Пр");
  assert.equal(decode(new Uint8Array([0xff,0xfe,65,0]),"auto").value,"A");
  assert.equal(decode(new Uint8Array([0xfe,0xff,0,65]),"auto").value,"A");
  assert.throws(()=>decode(new Uint8Array([0xff]),"auto"),/encoding/);
  assert.throws(()=>decode(new Uint8Array([0]),"auto"),/binary/);
  assert.throws(()=>decode(new ArrayBuffer(12*1024*1024+1),"auto"),/fileSize/);
});
test("export quotes every field and prefixes formula-like data and keys",async()=>{
  const d=compare(parse('id,x\n"=k","=a"'),parse('id,x\n"=k","  @b"'),["id"]);
  assert.deepEqual(parse(await (exportCSV(d,["id"])).text()).rows,[["changed","'=k","x","'=a","'  @b"]]);
});
