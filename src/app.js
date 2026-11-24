"use strict";
const $ = id => document.getElementById(id);
const make = (tag, value, cls) => {
  const el = document.createElement(tag);
  if (value !== undefined) el.textContent = value;
  if (cls) el.className = cls;
  return el;
};
function preference(k, value) {
  try {
    if (value === undefined) return localStorage.getItem("tallyrill-"+k);
    localStorage.setItem("tallyrill-"+k,value);
  } catch { /* Storage is optional in local HTML. */ }
}
let lang = preference("lang") || (navigator.language.startsWith("ru") ? "ru" : "en");
let theme = preference("theme") || (matchMedia("(prefers-color-scheme:dark)").matches ? "dark" : "light");
const t = k => labels[k][lang === "ru" ? 1 : 0];
const files=[null,null], enc=["auto","auto"], sep=["auto","auto"];
let meta=[], keys=[], worker, sample=false, autoRun=false, busy=false, report, page, seq=0, timer;
let message="", args=[], side="", bad=false;
const workerURL=URL.createObjectURL(new Blob([$("worker").textContent],{type:"text/javascript"}));

function notice(code="", values=[], prefix="", error=false) {
  message=code; args=values; side=prefix; bad=error;
  $("notice").dataset.bad=error;
  $("notice").textContent = code ? (prefix ? prefix+" · " : "") + t(code).replace(/\{(\d+)\}/g,(_,i)=>values[i]) : "";
}
function dropReport() {
  clearTimeout(timer);
  report=null; page=null; seq++;
  $("entries").replaceChildren();
  $("result").hidden=true;
  $("search").value="";
  $("filter").value="all";
}
function selectOptions(select, items, current) {
  select.replaceChildren(...items.map(([value,label])=>new Option(label,value,false,value===current)));
}
function drawFile(i) {
  const el=make("div",undefined,"file");
  const top=make("div",undefined,"filetop");
  top.append(make("b","AB"[i],"badge"),make("h3",t(i?"after":"before")));
  const pick=make("label",files[i]?.name || t("pick"),"pick");
  const input=make("input");
  input.type="file"; input.id="file"+i; input.accept=".csv,.tsv,.txt";
  input.setAttribute("aria-label",t(i?"after":"before"));
  const take=file=>{
    if (!file) return;
    files[i]=file; sample=false; autoRun=false; reload();
  };
  input.onchange=()=>take(input.files[0]); pick.append(input);
  el.ondragover=e=>{e.preventDefault();el.classList.add("over");};
  el.ondragleave=()=>el.classList.remove("over");
  el.ondrop=e=>{e.preventDefault();el.classList.remove("over");take(e.dataTransfer.files[0]);};
  const info=meta[i];
  const summary=info ? info.count+" "+t("rows")+" · "+info.headers.length+" "+t("cols")+" · "+info.encoding.toUpperCase() : t("filetype");
  const details=make("details");details.open=Boolean(document.querySelectorAll(".file details")[i]?.open);
  details.append(make("summary",t("settings")));
  const options=make("div",undefined,"opts");
  for (const [name,model,items] of [
    ["enc",enc,[["auto",t("auto")],["utf-8","UTF-8"],["windows-1251","Windows-1251"],["utf-16le","UTF-16 LE"],["utf-16be","UTF-16 BE"]]],
    ["sep",sep,[["auto",t("auto")],[",",t("comma")],[";",t("semi")],["\t",t("tab")]]]
  ]) {
    const label=make("label",t(name)), select=make("select");
    select.id=name+i; selectOptions(select,items,model[i]);
    select.onchange=()=>{model[i]=select.value; autoRun=false;reload();};
    label.append(select);options.append(label);
  }
  details.append(options);el.append(top,pick,make("p",summary,"meta"),details);
  return el;
}
function common() {return meta[0] && meta[1] ? meta[0].headers.filter(h=>meta[1].headers.includes(h)) : [];}
function updateRun() {
  $("run").disabled=busy || !keys.length || !common().length;
  $("hint").textContent=t(meta.every(Boolean) && meta.length===2 ? (common().length ? "keyReady":"noCommon") : "chooseBoth");
}
function drawInputs() {
  $("inputs").replaceChildren(drawFile(0),drawFile(1));
  $("reset").hidden=!files.some(Boolean);
  const cols=common();
  $("keybox").hidden=!cols.length;
  $("keys").replaceChildren(...cols.map(c=>{
    const label=make("label");const input=make("input");input.type="checkbox";input.value=c;input.checked=keys.includes(c);
    input.onchange=()=>{
      sample=false; dropReport(); keys=cols.filter(h=>[...$("keys").querySelectorAll(":checked")].some(box=>box.value===h));
      notice();updateRun();
    };
    input.disabled=busy;
    label.append(input,document.createTextNode(c));return label;
  }));
  updateRun();
}
function drawReport() {
  if (!report) return;
  $("result").hidden=false;
  $("stats").replaceChildren(...["changed","added","removed","same"].map(k=>{
    const stat=make("div",undefined,"stat");stat.append(make("b",report.counts[k]),make("span",t(k)));return stat;
  }));
  const schema=report.schema;
  $("schema").hidden=!schema.length;
  $("schema").textContent=[["schemaPlus",schema.filter(c=>c.x<0)],["schemaMinus",schema.filter(c=>c.y<0)]]
    .filter(([,v])=>v.length).map(([k,v])=>t(k)+" · "+v.map(c=>c.h).join(", ")).join("\n");
  if (!page) return;
  const entries=page.rows.map(row=>{
    const article=make("article",undefined,"entry"),head=make("h3");
    head.append(make("span",row.key.join(" / ")),make("span",t(row.status),"tag "+row.status));
    const table=make("table"), tr=table.createTHead().insertRow();
    for(const k of ["field","old","new"]) tr.append(make("th",t(k)));
    const body=table.createTBody();
    for(const cells of row.cells){
      const line=body.insertRow();
      for(const v of cells) line.insertCell().textContent=v===null?t("absent"):v===""?t("blank"):v;
    }
    article.append(head,table);return article;
  });
  if (!entries.length) entries.push(make("p",t(Object.keys(report.counts).filter(k=>k!=="same").every(k=>!report.counts[k])?"identical":"noMatch"),"entry"));
  $("entries").replaceChildren(...entries);
  $("prev").disabled=page.start===0; $("next").disabled=page.start+12>=page.total;
  $("pageinfo").textContent=page.total ? (page.start+1)+"–"+Math.min(page.total,page.start+12)+" "+t("of")+" "+page.total : "0";
}
function localize() {
  document.documentElement.lang=lang;
  document.title="TallyRill · "+t("heading");
  document.documentElement.dataset.theme=theme;
  $("lang").textContent=lang==="ru"?"English":"Русский";
  $("theme").textContent=t(theme==="dark"?"light":"dark");
  document.querySelectorAll("[data-t]").forEach(el=>el.textContent=t(el.dataset.t));
  selectOptions($("filter"),["all","changed","added","removed"].map(k=>[k,t(k)]),$("filter").value || "all");
  drawInputs();drawReport();notice(message,args,side,bad);
}
function pageAt(start=0) {
  if (report) worker.postMessage({op:"page", seq:++seq, start, status:$("filter").value, search:$("search").value});
}
function run() {
  if ($("run").disabled) return;
  dropReport();busy=true;drawInputs();notice("working");
  worker.postMessage({op:"compare", keys});
}
function reload() {
  worker?.terminate();busy=files.some(Boolean);dropReport();meta=[];drawInputs();
  notice(busy?"loading":"");
  if (!busy) return;
  worker=new Worker(workerURL);
  worker.onerror=()=>{busy=false;drawInputs(); notice("unexpected",[],"",true);};
  worker.onmessage=({data:d})=>{
    if(d.op==="loaded"){
      meta=d.meta;const cols=common();
      keys=keys.filter(k=>cols.includes(k));
      if(!keys.length && cols.length) keys=[cols[0]];
      busy=false;notice();drawInputs();
      if(autoRun){autoRun=false;run();}
    } else if (d.op==="compared"){
      busy=false;report=d;page=null;drawInputs();drawReport();pageAt();notice(sample?"sampleDone":"finished");
      $("result").scrollIntoView({block:"start"});
    } else if(d.op==="page" && d.seq===seq && report){page=d;drawReport();}
    else if(d.op==="export"){
      $("export").disabled=false;
      const url=URL.createObjectURL(d.blob),a=make("a");a.href=url;a.download="TallyRill-changes.csv";a.click();
      setTimeout(()=>URL.revokeObjectURL(url),60000);notice("download");
    } else if(d.op==="error"){
      busy=false;autoRun=false;$("export").disabled=false;drawInputs();notice(d.code,d.args,d.side,true);
    }
  };
  $("export").disabled=false;
  worker.postMessage({op:"load",files,enc,sep});
}
$("run").onclick=run;
$("reset").onclick=()=>{files.fill(null);enc.fill("auto");sep.fill("auto");keys=[];sample=false;autoRun=false;reload();};
$("sample").onclick=()=>{
  for(const [i,csv] of samples.entries()) files[i]=new File([csv],i?"catalog-after.csv":"catalog-before.csv",{type:"text/csv"});
  enc.fill("auto");sep.fill("auto");keys=["SKU","Depot"];sample=true;autoRun=true;reload();
};
$("filter").onchange=()=>pageAt();
$("search").oninput=()=>{clearTimeout(timer);timer=setTimeout(()=>pageAt(),120);};
$("prev").onclick=()=>pageAt(Math.max(0,page.start-12));
$("next").onclick=()=>pageAt(page.start+12);
$("export").onclick=()=>{$("export").disabled=true;notice("preparing");worker.postMessage({op:"export"});};
$("lang").onclick=()=>{lang=lang==="ru"?"en":"ru";preference("lang",lang);localize();};
$("theme").onclick=()=>{theme=theme==="dark"?"light":"dark";preference("theme",theme);localize();};
localize();
