/* Simulated DOM integration test. Does NOT replace real browser testing. */
const fs=require('fs'),vm=require('vm'),path=require('path'),assert=require('assert');
const root=path.resolve(__dirname,'..');
function element(name='', props={}) {
 const handlers={};let classes=new Set((props.className||'').split(/\s+/).filter(Boolean));
 return {tagName:name,style:{},attributes:{},textContent:'',disabled:false,value:props.value||'',handlers,
  classList:{toggle(c,on){if(on)classes.add(c);else classes.delete(c)},contains(c){return classes.has(c)}},
  setAttribute(k,v){this.attributes[k]=v},getAttribute(k){return this.attributes[k]},
  addEventListener(n,fn){handlers[n]=fn},appendChild(n){(this.children??=[]).push(n)},
  get checked(){return !!this._checked},set checked(v){this._checked=v},
  dispatch(n,arg={}){handlers[n]?.(arg)} };
}
let slides=Array.from({length:10},(_,i)=>element('SECTION',{className:i===0?'slide active':'slide'}));
let ids={prev:element('BUTTON'),next:element('BUTTON'),bar:element('DIV'),progressLabel:element('DIV'),priceChart:element('svg'),quiz:element('FORM'),quizResult:element('OUTPUT')};
let inputs={};let doc=element('DOCUMENT');doc.activeElement=element('BODY');
doc.querySelectorAll=q=>q==='.slide'?slides:[];
doc.getElementById=id=>ids[id];
doc.querySelector=q=>{let m=q.match(/^input\[name="(q\d)"\]:checked$/);return m?inputs[m[1]]||null:null};
doc.createElementNS=(ns,tag)=>element(tag);
let history={replaceState(a,b,hash){ctx.location.hash=hash}};
let win=element('WINDOW');
let ctx={document:doc,window:win,location:{hash:''},history,console};
vm.createContext(ctx); vm.runInContext(fs.readFileSync(path.join(root,'slides/script.js'),'utf8'),ctx);
let checks=[];function check(label,cond){checks.push({name:label,result:cond?'PASS':'FAIL'});assert(cond,label)}
check('initial_slide',ids.progressLabel.textContent==='01 / 10' && ids.prev.disabled && !ids.next.disabled);
ids.next.dispatch('click');check('next_button',ids.progressLabel.textContent==='02 / 10'&&slides[1].classList.contains('active'));
ids.prev.dispatch('click');check('previous_button',ids.progressLabel.textContent==='01 / 10');
let evt=()=>({preventDefault(){this.prevented=true},key:'ArrowRight'});let e=evt();doc.dispatch('keydown',e);check('right_arrow',ids.progressLabel.textContent==='02 / 10'&&e.prevented);
doc.activeElement=element('BUTTON');doc.dispatch('keydown',evt());check('keyboard_when_button_focused',ids.progressLabel.textContent==='03 / 10');
ctx.location.hash='#1';win.dispatch('hashchange');check('header_hash_navigation',ids.progressLabel.textContent==='01 / 10');
ctx.location.hash='#3';win.dispatch('hashchange');check('direct_fragment_navigation',ids.progressLabel.textContent==='03 / 10');
doc.activeElement=element('INPUT');doc.dispatch('keydown',evt());check('keyboard_ignores_input_focus',ids.progressLabel.textContent==='03 / 10');doc.activeElement=element('BODY');
for(let i=0;i<20;i++)ids.next.dispatch('click');check('upper_boundary',ids.progressLabel.textContent==='10 / 10'&&ids.next.disabled);
for(let i=0;i<20;i++)ids.prev.dispatch('click');check('lower_boundary',ids.progressLabel.textContent==='01 / 10'&&ids.prev.disabled);
check('chart_has_three_points',ids.priceChart.children.filter(c=>c.tagName==='circle').length===3);
let submit=()=>ids.quiz.dispatch('submit',{preventDefault(){}});
submit();check('quiz_missing_answers',ids.quizResult.textContent.includes('3 題未作答'));
inputs={q1:{value:'b'},q2:{value:'a'},q3:{value:'c'}};submit();check('quiz_all_correct',ids.quizResult.textContent.includes('3 / 3'));
inputs.q3={value:'b'};submit();check('quiz_incorrect_answer',ids.quizResult.textContent.includes('2 / 3'));
const result={test_environment:'Node.js isolated DOM simulation, NOT real browser',checks,passed:checks.filter(x=>x.result==='PASS').length,failed:checks.filter(x=>x.result==='FAIL').length};
fs.writeFileSync(path.join(root,'logs/runs/2026-11-14-interaction-simulation.json'),JSON.stringify(result,null,2));
console.log(JSON.stringify(result,null,2));
