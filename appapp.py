from flask import Flask, request, jsonify, render_template_string
import random
import time
import threading
import math

app = Flask(__name__)
LOCK = threading.Lock()
GAME = None
COLOURS = ["Red", "Blue", "Green", "Purple", "Orange", "Yellow"]

PAGE = r"""
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>DICE DUEL</title>
<style>
:root{--bg:#0b1620;--panel:#142435;--panel2:#1c3148;--line:#2b4660;--text:#f2f6fa;--muted:#9fb2c6;--accent:#5be3c1;--brass:#e5b44f}
*{box-sizing:border-box}
body{margin:0;min-height:100vh;color:var(--text);font-family:'Trebuchet MS',system-ui,sans-serif;
background:radial-gradient(circle at 15% 0,#1d3a52 0,transparent 45%),radial-gradient(circle at 90% 100%,#3a2a14 0,transparent 40%),var(--bg)}
.wrap{max-width:1050px;margin:auto;padding:12px 16px}
.brand{text-align:center;margin:2px 0 10px}
.brand h1{margin:0;font-family:Georgia,serif;font-size:clamp(26px,4vw,38px);letter-spacing:4px;color:var(--brass);text-shadow:0 3px 14px #e5b44f55}
.brand p{margin:4px;color:var(--muted);font-size:13px}
.panel{background:linear-gradient(160deg,var(--panel),#101e2d);border:1px solid var(--line);border-radius:18px;padding:18px;box-shadow:0 14px 34px #0006}
.center{max-width:520px;margin:22px auto}
.hidden{display:none!important}
h2{margin:0 0 6px;font-family:Georgia,serif}
label{display:block;color:var(--muted);font-size:14px;margin:12px 0 6px}
input,select,button{font:inherit}
input,select{width:100%;padding:11px;border-radius:10px;border:1px solid var(--line);background:#0c1825;color:#fff}
input:focus,select:focus,button:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
button{border:0;border-radius:11px;padding:11px 20px;background:linear-gradient(180deg,#7af0d3,#35c7a4);color:#08231d;font-weight:700;cursor:pointer;transition:transform .1s,filter .2s}
button:hover:not(:disabled){filter:brightness(1.1);transform:translateY(-1px)}
button:disabled{opacity:.4;cursor:not-allowed}
.secondary{background:linear-gradient(180deg,#53708f,#3c5774);color:#fff}
.row,.actions{display:flex;gap:10px;justify-content:center;align-items:center;flex-wrap:wrap}
.actions{margin:10px 0 4px}
.colors{display:flex;gap:10px;flex-wrap:wrap}
.swatch{width:36px;height:36px;border-radius:50%;border:3px solid #fff4;padding:0;box-shadow:inset 0 -5px 8px #0005,inset 0 4px 6px #fff5}
.swatch.chosen{outline:3px solid #fff;outline-offset:2px}
.hint{text-align:center;color:var(--muted);font-size:13px;margin:8px}

#gameLayout{display:grid;grid-template-columns:200px minmax(0,1fr);gap:14px;align-items:start}
.sidebar{display:grid;gap:10px}
.stat{background:var(--panel2);border:1px solid var(--line);border-radius:12px;padding:10px 12px}
.stat small{display:block;color:var(--muted);font-size:12px;margin-bottom:3px}
.stat strong{font-size:22px}
.dot{display:inline-block;width:14px;height:14px;border-radius:50%;vertical-align:-1px;margin-right:6px;border:2px solid #fff6}
.bar{height:6px;border-radius:4px;background:#0c1825;margin-top:7px;overflow:hidden}
.bar i{display:block;height:100%;width:0;background:linear-gradient(90deg,var(--accent),var(--brass))}
.turnbar{display:flex;justify-content:space-between;gap:10px;align-items:center;margin-bottom:8px}
#turnLabel{font-family:Georgia,serif;font-size:19px;letter-spacing:1px;color:var(--brass)}

/* compact board: wood frame, green felt, brass rings */
.board{position:relative;width:min(100%,calc(100vh - 290px));min-width:260px;aspect-ratio:1;margin:0 auto;
border:10px solid #6b4423;border-radius:20px;overflow:hidden;
background:radial-gradient(circle at 50% 50%,transparent 0 14%,#ffffff12 14.4% 15%,transparent 15.4% 34%,#ffffff12 34.4% 35%,transparent 35.4% 55%,#ffffff12 55.4% 56%,transparent 56.4%),
radial-gradient(circle at 50% 40%,#2b7a62,#164a3b 75%);
box-shadow:0 0 0 3px #b98a4e,inset 0 0 40px #000a,0 16px 30px #0008}
.coin{position:absolute;width:var(--cs);height:var(--cs);padding:0;border-radius:50%;transform:translate(-50%,-50%);
border:max(1px,.12vw) solid #fff9;box-shadow:0 2px 4px #0008,inset 0 -3px 4px #0004,inset 0 2px 3px #fff6;transition:transform .25s,opacity .3s}
.coin:hover:not(:disabled){transform:translate(-50%,-50%) scale(1.25);filter:none;z-index:3}
.coin.selected{outline:3px solid #fff;outline-offset:1px;transform:translate(-50%,-50%) scale(1.3);z-index:4;box-shadow:0 0 12px 3px #fffc}
.coin.gone{opacity:0;transform:translate(-50%,-50%) scale(.2);pointer-events:none}
.coin.decoy{cursor:not-allowed;opacity:.92}
.coin.ai{cursor:default}
.coin.shake{animation:shake .35s}
@keyframes shake{25%{margin-left:-4px}75%{margin-left:4px}}
#message{text-align:center;min-height:20px;color:#ffe6a3;font-size:14px;margin-top:4px}
@media(max-width:760px){.wrap{padding:8px}#gameLayout{grid-template-columns:1fr}.sidebar{grid-template-columns:repeat(3,1fr)}.stat strong{font-size:17px}.board{width:min(100%,calc(100vh - 360px))}}
@media(prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}

.quiz{background:var(--panel2);border:1px solid var(--line);border-radius:12px;padding:10px 12px;margin:10px auto 0;max-width:640px}
.quizhead{color:var(--brass);font-size:14px;margin-bottom:6px}
.qtext{font-size:15px;margin:4px 0 8px;white-space:pre-line}
.opt{display:block;width:100%;text-align:left;margin:6px 0;padding:9px 12px;background:#0c1825;color:#fff;border:1px solid var(--line);font-weight:400}
.opt.right{background:#1f7a52;border-color:#5be3c1}
.opt.wrong{background:#8a2c2c;border-color:#ff8a80}
.ailog{max-height:190px;overflow:auto;font-size:13px}
.ailog div{padding:5px 0;border-top:1px solid var(--line)}
.ok{color:#5be3c1}.bad{color:#ff8a80}
</style></head>
<body><div class="wrap">
<header class="brand"><h1>DICE DUEL</h1><p>AI-Based Decision-Making Agent for Competitive Board Games</p></header>

<section id="login" class="panel center">
<h2>Player Details</h2>
<label>Player name</label><input id="playerName" placeholder="Enter your name" maxlength="24">
<label>Date of birth</label><input id="dob" type="date">
<label>Password (optional)</label><input id="password" type="password" placeholder="Optional">
<div class="actions"><button onclick="toSetup()">Continue</button></div>
<p class="hint">Prototype only: details are not saved or used for authentication.</p>
</section>

<section id="setup" class="panel center hidden">
<h2>Game Setup</h2>
<label>Choose your coin colour</label><div class="colors" id="colors"></div>
<label>Total playable coins (even number, 2–444)</label><input id="coinCount" type="number" min="2" max="444" step="2" value="36">
<label>Selection timer: <b><span id="selValue">2</span> seconds</b></label>
<input id="selectionSeconds" type="range" min="2" max="60" step="1" value="2" oninput="selValue.textContent=this.value">
<label>Game time</label>
<select id="gameMinutes"><option value="5">5 minutes</option><option value="10" selected>10 minutes</option><option value="15">15 minutes</option></select>
<p class="hint">Each round you answer 6 AI questions. Every correct answer lets you collect 1 coin within the selection timer. The game ends when time is up or both players have collected all their coins; the higher score wins.</p>
<div class="actions"><button onclick="startToss()">Continue to Coin Toss</button></div>
</section>

<section id="toss" class="panel center hidden">
<h2>Coin Toss</h2><p>Choose Heads or Tails. If your choice matches the toss, you start first.</p>
<div class="row"><button onclick="doToss('Heads')">Heads</button><button onclick="doToss('Tails')">Tails</button></div>
<p id="tossResult" class="hint"></p>
</section>

<section id="game" class="hidden">
<div id="gameLayout">
<aside class="sidebar">
<div class="stat"><small>GAME TIME LEFT</small><strong id="gameTime">--</strong></div>
<div class="stat"><small>SELECTION TIME</small><strong id="turnTime">--</strong><div class="bar"><i id="bar"></i></div></div>
<div class="stat"><small>YOUR SCORE</small><strong id="humanScore">0</strong></div>
<div class="stat"><small>AI SCORE</small><strong id="aiScore">0</strong></div>
<div class="stat"><small>YOUR COINS LEFT</small><strong id="humanLeft">0</strong></div>
<div class="stat"><small>AI COINS LEFT</small><strong id="aiLeft">0</strong></div>
<div class="stat"><small>COLOURS</small><span class="dot" id="hDot"></span><span id="humanColour">—</span><br><span class="dot" id="aDot"></span><span id="aiColour">—</span></div>
</aside>
<main class="panel">
<div class="turnbar"><b id="turnLabel">Waiting…</b><span id="remainingLabel" class="hint"></span></div>
<div class="board" id="board"></div>
<div class="quiz"><div class="quizhead" id="quizHead"></div><div id="quizBody"></div></div>
<div class="actions"><button id="startBtn" onclick="startRound()">Start Round (6 Questions)</button><button class="secondary" id="finishBtn" onclick="finishTurn()" disabled>Finish Turn</button></div>
<div id="message"></div>
</main></div></section>

<section id="result" class="panel center hidden"><h2>Game Over</h2><h1 id="winner"></h1><p id="reason" class="hint"></p><p id="finalScores"></p><div class="actions"><button onclick="location.reload()">New Game</button></div></section>
</div>
<script>
const palette=['Red','Blue','Green','Purple','Orange','Yellow'];
const hex={Red:'#e74c3c',Blue:'#3498db',Green:'#2ecc71',Purple:'#9b59b6',Orange:'#e67e22',Yellow:'#f1c40f'};
let chosen='Red',state=null,selected=[],turnDeadline=0,turnLen=0,turnTicker=null,gameDeadline=0,gameTicker=null,aiBusy=false,answering=false,ended=false;
const els={};
const $=id=>document.getElementById(id);
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const fmt=s=>{s=Math.ceil(s);return Math.floor(s/60)+':'+String(s%60).padStart(2,'0')};
function show(id){['login','setup','toss','game','result'].forEach(x=>$(x).classList.toggle('hidden',x!==id))}
function buildPalette(){
  $('colors').innerHTML='';
  palette.forEach(c=>{const b=document.createElement('button');b.className='swatch'+(chosen===c?' chosen':'');
    b.style.background=hex[c];b.title=c;b.onclick=()=>{chosen=c;buildPalette()};$('colors').appendChild(b)})
}
buildPalette();
function toSetup(){if(!$('playerName').value.trim()){alert('Enter your name');return}show('setup')}
async function api(path,body={}){
  const r=await fetch(path,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
  const d=await r.json();if(!r.ok)throw Error(d.error||'Request failed');
  const s=d.state||d;if(s&&s.time_left!==undefined)gameDeadline=Date.now()+s.time_left*1000;
  return d
}
async function startToss(){
  const n=Number($('coinCount').value);
  if(n<2||n>444||n%2){alert('Choose an even number from 2 to 444');return}
  try{await api('/api/setup',{name:$('playerName').value.trim(),colour:chosen,coins:n,selection_seconds:Number($('selectionSeconds').value),game_minutes:Number($('gameMinutes').value)});show('toss')}
  catch(e){alert(e.message)}
}
async function doToss(choice){
  state=await api('/api/toss',{choice});
  $('tossResult').textContent=`Toss: ${state.toss}. ${state.first==='human'?'You':'AI'} start first.`;
  setTimeout(()=>{show('game');startGameClock();afterState()},1200)
}
function startGameClock(){
  clearInterval(gameTicker);
  gameTicker=setInterval(async()=>{
    const left=Math.max(0,(gameDeadline-Date.now())/1000);
    $('gameTime').textContent=fmt(left);$('gameTime').style.color=left<30?'#ff8a80':'';
    if(left<=0&&!ended){clearInterval(gameTicker);try{state=await api('/api/state')}catch(e){}endGame()}
  },250)
}
async function startRound(){
  try{state=await api('/api/start_round');selected=[];afterState();$('message').textContent='Answer all 6 questions — each correct answer = 1 coin.'}
  catch(e){$('message').textContent=e.message}
}
async function answer(i){
  if(answering||!state||state.phase!=='quiz')return;answering=true;
  try{
    const r=await api('/api/answer',{choice:i}),fb=r.feedback;
    document.querySelectorAll('.opt').forEach((b,j)=>{if(j===fb.answer)b.classList.add('right');else if(j===i)b.classList.add('wrong')});
    await sleep(900);
    state=r.state;afterState();
    const hr=state.human_result;
    if(state.phase==='idle'&&hr&&!state.over)$('message').textContent=`You got ${hr.correct}/${hr.total} correct — no coins to collect.`
  }catch(e){$('message').textContent=e.message}finally{answering=false}
}
function afterState(){
  render();
  if(state.over){endGame();return}
  if(state.turn==='human'&&state.phase==='select'){
    if(!turnTicker){selected=[];turnLen=state.selection_seconds*1000;turnDeadline=Date.now()+turnLen;startTurnClock()}
    $('message').textContent=`You got ${state.human_result.correct}/${state.human_result.total} correct — pick up to ${state.allowance} of your coins!`
  }else if(state.turn==='ai'&&state.phase==='idle')aiTurn()
}
function coinEl(c){
  let el=els[c.id];if(el)return el;
  el=document.createElement('button');el.style.left=c.x+'%';el.style.top=c.y+'%';
  el.onclick=()=>pick(c.id);$('board').appendChild(el);els[c.id]=el;return el
}
function pick(id){
  if(!state||state.turn!=='human'||state.phase!=='select')return;
  const c=state.coins.find(k=>k.id===id);
  if(c.owner==='neutral'){const el=els[id];el.classList.remove('shake');void el.offsetWidth;el.classList.add('shake');$('message').textContent='That is a decoy coin!';return}
  if(c.owner!=='human')return;
  const i=selected.indexOf(id);
  if(i>=0)selected.splice(i,1);
  else{if(selected.length>=state.allowance)return;selected.push(id)}
  render();
  if(selected.length===state.allowance)finishTurn()
}
function renderQuiz(){
  const head=$('quizHead'),body=$('quizBody');body.innerHTML='';
  if(state.phase==='quiz'&&state.question){
    const q=state.question;
    head.textContent=`Question ${q.n} of ${q.total} — each correct answer earns 1 coin`;
    const t=document.createElement('div');t.className='qtext';t.textContent=q.text;body.appendChild(t);
    q.options.forEach((o,i)=>{const b=document.createElement('button');b.className='opt';b.textContent=o;b.onclick=()=>answer(i);body.appendChild(b)});
    return
  }
  const hr=state.human_result,al=state.ai_log;
  head.textContent=hr?`Your last round: ${hr.correct}/${hr.total} correct`:'Press “Start Round” to get 6 questions';
  if(al){
    const h=document.createElement('div');h.className='qtext';
    h.textContent=`AI's last round: ${al.correct}/${al.items.length} correct, collected ${al.collected} coin(s)`;body.appendChild(h);
    const box=document.createElement('div');box.className='ailog';
    al.items.forEach((it,i)=>{
      const d=document.createElement('div'),s=document.createElement('span');
      s.className=it.correct?'ok':'bad';s.textContent=it.correct?'✓ ':'✗ ';d.appendChild(s);
      let t=`Q${i+1}: ${it.text.replace(/\n/g,' ')} — AI chose: ${it.options[it.pick]}`;
      if(!it.correct)t+=` (correct: ${it.options[it.answer]})`;
      d.appendChild(document.createTextNode(t));box.appendChild(d)});
    body.appendChild(box)
  }
}
function render(){
  if(!state)return;
  $('board').style.setProperty('--cs',state.coin_size+'%');
  $('humanScore').textContent=state.scores.human;$('aiScore').textContent=state.scores.ai;
  $('humanLeft').textContent=state.left.human;$('aiLeft').textContent=state.left.ai;
  $('humanColour').textContent=state.human_colour;$('aiColour').textContent=state.ai_colour;
  $('hDot').style.background=hex[state.human_colour];$('aDot').style.background=hex[state.ai_colour];
  $('turnLabel').textContent=state.turn==='human'?'YOUR TURN':'AI TURN';
  $('remainingLabel').textContent=`Selection limit: ${state.selection_seconds}s`;
  state.coins.forEach(c=>{
    const el=coinEl(c);
    if(c.owner.startsWith('collected')){
      if(!el.classList.contains('gone')){el.classList.add('gone');el.disabled=true;setTimeout(()=>el.remove(),400)}return}
    const col=c.owner==='human'?hex[state.human_colour]:c.owner==='ai'?hex[state.ai_colour]:hex[c.decoy];
    el.className='coin'+(c.owner==='neutral'?' decoy':'')+(c.owner==='ai'?' ai':'')+(selected.includes(c.id)?' selected':'');
    el.style.background=`radial-gradient(circle at 35% 30%,#fff9,${col} 45%,${col})`;
    el.title=c.owner==='human'?'Your coin':c.owner==='ai'?'AI coin':'Decoy';
  });
  renderQuiz();
  $('startBtn').disabled=state.turn!=='human'||state.phase!=='idle'||state.over;
  $('finishBtn').disabled=state.turn!=='human'||state.phase!=='select'||state.over
}
function startTurnClock(){
  clearInterval(turnTicker);
  turnTicker=setInterval(()=>{
    const left=Math.max(0,(turnDeadline-Date.now())/1000);
    $('turnTime').textContent=left.toFixed(1)+'s';$('bar').style.width=(left*1000/turnLen*100)+'%';
    if(left<=0){clearInterval(turnTicker);finishTurn(true)}
  },100)
}
async function finishTurn(timeout=false){
  if(!state||state.phase!=='select'||state.turn!=='human')return;
  clearInterval(turnTicker);turnTicker=null;
  try{
    state=await api('/api/human_finish',{ids:selected,timeout});selected=[];
    $('turnTime').textContent='--';$('bar').style.width='0';$('message').textContent='';
    afterState()
  }catch(e){$('message').textContent=e.message}
}
async function aiTurn(){
  if(aiBusy||!state||state.over||state.turn!=='ai'||state.phase!=='idle')return;
  aiBusy=true;$('message').textContent='AI is answering 6 questions…';
  try{
    await sleep(900);
    state=await api('/api/ai_turn');render();
    const l=state.ai_log;
    $('message').textContent=`AI answered ${l.correct}/${l.items.length} correctly and collected ${l.collected} coin(s).`;
    if(state.over)setTimeout(endGame,1500);
    else if(state.turn==='ai'){aiBusy=false;setTimeout(aiTurn,2500)}
    else $('message').textContent+=' Your turn — press Start Round.'
  }catch(e){$('message').textContent=e.message}finally{aiBusy=false}
}
function endGame(){
  if(ended)return;ended=true;
  clearInterval(turnTicker);clearInterval(gameTicker);show('result');
  const h=state.scores.human,a=state.scores.ai;
  $('winner').textContent=h>a?'YOU WIN!':a>h?'AI WINS!':'DRAW!';
  $('reason').textContent=state.reason||'Time is up!';
  $('finalScores').textContent=`Your score: ${h} | AI score: ${a}`
}
</script></body></html>
"""

CATS = {
    "SR": "Search Algorithms", "LG": "Logic & Knowledge Representation",
    "ML": "Machine Learning", "NN": "Neural Networks",
    "PR": "Probability & Uncertainty", "AG": "Agents & Reinforcement Learning",
    "GM": "Game Playing", "CS": "Constraint Satisfaction",
    "PL": "Planning", "NL": "NLP & Perception",
}

# Principles of AI facts: CATEGORY::Term::Description  (170 facts -> 510 MCQs -> 500 used)
FACTS = """
SR::Breadth-First Search::Explores all nodes at the current depth before going deeper
SR::Depth-First Search::Expands the deepest node first using a stack
SR::Uniform-Cost Search::Expands the node with the lowest path cost g(n)
SR::Depth-Limited Search::DFS with a fixed maximum depth
SR::Iterative Deepening::Repeats depth-limited search with increasing limits
SR::Bidirectional Search::Searches from the start and from the goal at the same time
SR::Greedy Best-First Search::Expands the node with the lowest heuristic value h(n)
SR::A* Search::Expands the node with the lowest f(n) = g(n) + h(n)
SR::Admissible Heuristic::A heuristic that never overestimates the true cost to the goal
SR::Consistent Heuristic::A heuristic satisfying h(n) ≤ c(n,n') + h(n')
SR::Hill Climbing::Moves to the best neighbouring state and may get stuck in local maxima
SR::Simulated Annealing::Accepts worse moves with a probability that decreases over time
SR::Genetic Algorithm::Evolves a population using selection, crossover and mutation
SR::Local Beam Search::Keeps the k best states at each step
SR::Branching Factor::Maximum number of successors of a node
SR::Frontier::The set of generated nodes that have not yet been expanded
SR::Local Maximum::A peak higher than its neighbours but lower than the global best
LG::Propositional Logic::Logic whose statements are true or false, joined by connectives
LG::First-Order Logic::Logic with objects, predicates, functions and quantifiers
LG::Modus Ponens::From P and P → Q, infer Q
LG::Modus Tollens::From P → Q and ¬Q, infer ¬P
LG::Resolution::Inference rule that derives a new clause from two clauses with complementary literals
LG::Unification::Finding a substitution that makes two logical expressions identical
LG::Conjunctive Normal Form::A conjunction of clauses, each clause being a disjunction of literals
LG::Horn Clause::A clause with at most one positive literal
LG::Forward Chaining::Data-driven inference that starts from the known facts
LG::Backward Chaining::Goal-driven inference that starts from the query
LG::Tautology::A sentence that is true in every model
LG::Satisfiable Sentence::A sentence that is true in at least one model
LG::Entailment::KB ⊨ α means α is true in every model where KB is true
LG::Soundness::An inference procedure derives only sentences that are entailed
LG::Completeness::An inference procedure can derive every sentence that is entailed
LG::Semantic Network::Graph of nodes and labelled links representing concepts and relations
LG::Ontology::A formal specification of the concepts and relations in a domain
ML::Supervised Learning::Learning from labelled input-output examples
ML::Unsupervised Learning::Finding structure in unlabelled data
ML::Reinforcement Learning::Learning which actions to take through rewards and penalties
ML::Overfitting::Model fits the training data too closely and generalises poorly
ML::Underfitting::Model is too simple to capture the pattern in the data
ML::Cross-Validation::Splitting data into folds to estimate generalisation performance
ML::Decision Tree::Tree that splits data on attributes to reach a prediction
ML::Information Gain::Reduction in entropy after splitting on an attribute
ML::Entropy::A measure of impurity or uncertainty in a set of examples
ML::k-Nearest Neighbours::Classifies a point by the majority vote of its k closest examples
ML::k-Means::Clustering that assigns points to the nearest of k centroids
ML::Linear Regression::Fits a straight line to predict a continuous value
ML::Logistic Regression::Predicts class probability using the sigmoid function
ML::Support Vector Machine::Classifier that maximises the margin between classes
ML::Regularization::Penalty added to the loss to reduce overfitting
ML::Gradient Descent::Optimisation that moves parameters against the gradient of the loss
ML::Bias–Variance Tradeoff::Balance between oversimplified and overly sensitive models
NN::Perceptron::Single-layer neuron that outputs a thresholded weighted sum
NN::Activation Function::Non-linear function applied to a neuron's weighted input
NN::Sigmoid::Activation that squashes values into the range 0 to 1
NN::ReLU::Activation defined as max(0, x)
NN::Softmax::Converts a vector of scores into a probability distribution
NN::Backpropagation::Algorithm that propagates error gradients backwards to update weights
NN::Epoch::One full pass through the training dataset
NN::Learning Rate::Step size used when updating weights
NN::Dropout::Randomly disables neurons during training to reduce overfitting
NN::Convolutional Neural Network::Network using convolution filters, mainly for images
NN::Recurrent Neural Network::Network with loops that processes sequences
NN::LSTM::Recurrent unit with gates to handle long-term dependencies
NN::Transformer::Architecture based on self-attention instead of recurrence
NN::Vanishing Gradient::Gradients shrink towards zero in deep networks, slowing learning
NN::Batch Normalization::Normalises layer inputs to stabilise and speed up training
NN::Autoencoder::Network trained to compress and reconstruct its input
NN::Loss Function::Quantity that measures the error the network tries to minimise
PR::Bayes' Theorem::P(A|B) = P(B|A)·P(A) / P(B)
PR::Prior Probability::Probability of an event before seeing new evidence
PR::Posterior Probability::Probability of an event after updating with evidence
PR::Conditional Independence::Two variables are independent once a third is known
PR::Bayesian Network::Directed acyclic graph encoding conditional dependencies among variables
PR::Naive Bayes::Classifier assuming features are conditionally independent given the class
PR::Markov Chain::Process where the next state depends only on the current state
PR::Hidden Markov Model::Model with hidden states that emit observable outputs
PR::Conditional Probability::Probability of an event given that another has occurred
PR::Joint Probability::Probability of two events occurring together
PR::Marginalization::Summing out variables to obtain a smaller distribution
PR::Expected Utility::Probability-weighted average utility of an action's outcomes
PR::Maximum Likelihood::Choosing parameters that make the observed data most probable
PR::Kalman Filter::Estimates a system's state from noisy measurements over time
PR::Particle Filter::Approximates a belief state using weighted random samples
PR::Variable Elimination::Exact inference algorithm for Bayesian networks
PR::Dempster–Shafer Theory::Evidence theory using belief and plausibility instead of single probabilities
AG::Rational Agent::Agent that acts to maximise its expected performance measure
AG::PEAS::Performance measure, Environment, Actuators, Sensors
AG::Simple Reflex Agent::Chooses actions only from the current percept using condition-action rules
AG::Model-Based Agent::Agent that maintains an internal state of the world
AG::Goal-Based Agent::Agent that chooses actions to achieve a desired goal
AG::Utility-Based Agent::Agent that picks actions maximising a measure of happiness
AG::Learning Agent::Agent that improves through a critic and a learning element
AG::Fully Observable Environment::Sensors give access to the complete state at each time
AG::Stochastic Environment::Next state is not fully determined by the current state and action
AG::Episodic Environment::Each decision is independent of previous episodes
AG::Q-Learning::Off-policy RL algorithm that learns action values Q(s,a)
AG::Policy::Mapping from states to actions
AG::Reward::Numerical feedback signal from the environment
AG::Discount Factor::Weight that reduces the value of future rewards
AG::Exploration–Exploitation Trade-off::Balance between trying new actions and using the best known one
AG::Multi-Agent System::Several agents interacting in a shared environment
AG::Markov Decision Process::Framework of states, actions, transitions and rewards
GM::Minimax::Algorithm that maximises own score assuming the opponent minimises it
GM::Alpha-Beta Pruning::Skips branches that cannot affect the minimax decision
GM::Zero-Sum Game::One player's gain equals the other player's loss
GM::Nash Equilibrium::No player gains by changing strategy alone
GM::Evaluation Function::Estimates the utility of a non-terminal game state
GM::Expectimax::Minimax variant with chance nodes
GM::Monte Carlo Tree Search::Uses random simulations to guide game tree search
GM::Prisoner's Dilemma::Game where individual rationality leads to a worse joint outcome
GM::Dominant Strategy::Strategy that is best regardless of the opponent's choice
GM::Game Tree::Tree of states where levels alternate between players
GM::Terminal Test::Check that determines whether the game is over
GM::Horizon Effect::Depth limit hides threats that lie just beyond the search
GM::Quiescence Search::Extends search in unstable positions before evaluating
GM::Move Ordering::Examining the best moves first to improve pruning
GM::Perfect Information Game::Every player sees the full game state, e.g. chess
GM::Mixed Strategy::Choosing actions randomly according to probabilities
GM::Pareto Optimality::No player can improve without making another worse off
CS::Constraint Satisfaction Problem::Problem defined by variables, domains and constraints
CS::Backtracking Search::DFS that assigns one variable at a time and undoes violations
CS::Forward Checking::Removes inconsistent values from neighbours' domains after an assignment
CS::Arc Consistency::Every value of a variable has a supporting value in each neighbour
CS::AC-3::Algorithm that enforces consistency across all arcs of a constraint graph
CS::MRV Heuristic::Choose the variable with the fewest remaining legal values
CS::Degree Heuristic::Choose the variable involved in the most constraints on unassigned variables
CS::Least Constraining Value::Choose the value that rules out the fewest options for neighbours
CS::Min-Conflicts::Local search that reassigns a variable to the value causing the fewest conflicts
CS::Constraint Graph::Graph with variables as nodes and constraints as edges
CS::Map Colouring::Classic problem of colouring regions so that neighbours differ
CS::N-Queens::Classic problem of placing queens so that none attack each other
CS::Node Consistency::Every value in a variable's domain satisfies its unary constraints
CS::Path Consistency::Consistency over pairs of variables with respect to a third variable
CS::Global Constraint::Constraint involving many variables, such as Alldiff
CS::Cutset Conditioning::Remove variables so that the remaining constraint graph is a tree
CS::Conflict-Directed Backjumping::Jumps back to a variable that caused the failure
PL::STRIPS::Planning language with preconditions, add lists and delete lists
PL::PDDL::Standard language for describing planning domains and problems
PL::Precondition::Condition that must hold before an action can be applied
PL::Effect::Change an action makes to the world state
PL::Partial-Order Planning::Plan that leaves the order of independent actions unspecified
PL::Forward State-Space Planning::Planning that searches from the initial state towards the goal
PL::Regression Planning::Planning that searches backward from the goal
PL::Planning Graph::Layered structure alternating proposition levels and action levels
PL::GraphPlan::Planner that extracts a plan from a layered graph structure
PL::Mutex::Pair of actions or propositions that cannot hold together
PL::Frame Problem::Difficulty of specifying what does not change after an action
PL::Hierarchical Task Network::Planning by decomposing high-level tasks into subtasks
PL::Delete Relaxation::Ignoring delete lists to compute a planning heuristic
PL::Causal Link::Link showing that one action achieves a precondition of another
PL::Closed World Assumption::Anything not known to be true is assumed false
PL::Conditional Planning::Plans with branches for different contingencies
PL::Replanning::Revising the plan when execution diverges from expectation
NL::Tokenization::Splitting text into words or sub-word units
NL::Stemming::Chopping word endings to reach a root form
NL::Lemmatization::Reducing a word to its dictionary base form
NL::Stop Words::Very common words often removed before analysis
NL::TF-IDF::Weights terms by frequency in a document and rarity across documents
NL::Bag of Words::Text representation that ignores order and counts word occurrences
NL::Word Embedding::Dense vector representation capturing word meaning
NL::Word2Vec::Model that learns embeddings by predicting words from their context
NL::N-gram::Sequence of n consecutive words used in language models
NL::Part-of-Speech Tagging::Labelling words as nouns, verbs, adjectives and so on
NL::Named Entity Recognition::Identifying people, places and organisations in text
NL::Sentiment Analysis::Determining the opinion or emotion expressed in text
NL::Machine Translation::Automatically converting text from one language to another
NL::Attention Mechanism::Lets a model focus on the most relevant parts of the input
NL::Edge Detection::Finding the boundaries of objects in an image
NL::Computer Vision::Field enabling machines to interpret images and video
NL::Speech Recognition::Converting spoken audio into text
"""

QUESTIONS_PER_ROUND = 6
BANK_SIZE = 500
AI_ACCURACY = 0.75          # chance the AI agent answers each question correctly
GAME_MINUTES = (5, 10, 15)


def build_bank():
    facts = [tuple(p.strip() for p in line.split("::")) for line in FACTS.strip().splitlines()]
    bank = []

    def add(text, correct, wrong):
        opts = [correct] + wrong
        random.shuffle(opts)
        bank.append({"q": text, "o": opts, "a": opts.index(correct)})

    for cat, term, desc in facts:
        same = [f for f in facts if f[0] == cat and f[1] != term]
        add("Which term matches this description?\n“%s”" % desc, term,
            [f[1] for f in random.sample(same, 3)])
        add("What best describes “%s”?" % term, desc,
            [f[2] for f in random.sample(same, 3)])
        others = [c for c in CATS if c != cat]
        add("“%s” belongs to which topic of Principles of AI?" % term, CATS[cat],
            [CATS[c] for c in random.sample(others, 3)])
    random.shuffle(bank)
    return bank[:BANK_SIZE]


QUESTIONS = build_bank()


def left_counts():
    return {"human": sum(1 for c in GAME["coins"] if c["owner"] == "human"),
            "ai": sum(1 for c in GAME["coins"] if c["owner"] == "ai")}


def check_over():
    """Game ends when time is up or both players have collected all their coins."""
    if not GAME or GAME["over"]:
        return
    if GAME["end_time"] and time.time() >= GAME["end_time"]:
        GAME["over"], GAME["reason"] = True, "Time is up!"
    else:
        l = left_counts()
        if l["human"] == 0 and l["ai"] == 0:
            GAME["over"], GAME["reason"] = True, "Both players have collected all their coins."


def next_turn(just):
    other = "ai" if just == "human" else "human"
    GAME["phase"] = "idle"
    check_over()
    if GAME["over"]:
        return
    # a player with no coins left is skipped
    GAME["turn"] = other if left_counts()[other] > 0 else just


def draw_questions():
    unused = [i for i in range(len(QUESTIONS)) if i not in GAME["used"]]
    if len(unused) < QUESTIONS_PER_ROUND:
        GAME["used"].clear()
        unused = list(range(len(QUESTIONS)))
    ids = random.sample(unused, QUESTIONS_PER_ROUND)
    GAME["used"].update(ids)
    return ids


def public_state():
    if not GAME:
        return {}
    check_over()
    end = GAME["end_time"]
    s = {
        "coins": GAME["coins"], "turn": GAME["turn"], "phase": GAME["phase"],
        "scores": GAME["scores"], "human_colour": GAME["human_colour"],
        "ai_colour": GAME["ai_colour"], "selection_seconds": GAME["selection_seconds"],
        "over": GAME["over"], "reason": GAME["reason"], "toss": GAME.get("toss"),
        "first": GAME.get("first"), "left": left_counts(), "coin_size": GAME["coin_size"],
        "allowance": GAME["allowance"], "human_result": GAME["human_result"],
        "ai_log": GAME["ai_log"], "question": None,
        "time_left": max(0.0, end - time.time()) if end else GAME["game_minutes"] * 60,
    }
    if GAME["phase"] == "quiz":
        r = GAME["round"]
        q = QUESTIONS[r["qids"][r["idx"]]]
        s["question"] = {"n": r["idx"] + 1, "total": QUESTIONS_PER_ROUND, "text": q["q"], "options": q["o"]}
    return s


@app.get("/")
def index():
    return render_template_string(PAGE)


@app.post("/api/setup")
def setup():
    global GAME
    d = request.get_json(force=True)
    try:
        count = int(d["coins"])
        selection = int(d["selection_seconds"])
        minutes = int(d.get("game_minutes", 10))
        name, colour = str(d["name"])[:24], str(d["colour"])
        if not name or count < 2 or count > 444 or count % 2:
            raise ValueError()
        if not 2 <= selection <= 60 or colour not in COLOURS or minutes not in GAME_MINUTES:
            raise ValueError()
    except Exception:
        return jsonify(error="Check your setup values."), 400

    ai_colour = random.choice([c for c in COLOURS if c != colour])
    spare = [c for c in COLOURS if c not in (colour, ai_colour)]
    half = count // 2
    decoys = max(8, round(count * 0.15))      # extra look-alike coins to confuse the player

    owners = ["human"] * half + ["ai"] * half + ["neutral"] * decoys
    random.shuffle(owners)
    total = len(owners)

    # jittered grid: coins are spread over the whole board and never overlap
    cols = math.ceil(math.sqrt(total))
    cell = 88.0 / cols
    slots = [(r, c) for r in range(cols) for c in range(cols)]
    random.shuffle(slots)
    coin_size = round(max(2.6, min(7.5, cell * 0.72)), 2)
    jitter = (cell - coin_size) * 0.45

    coins = []
    for i, owner in enumerate(owners):
        r, c = slots[i]
        coin = {"id": i, "owner": owner,
                "x": round(6 + cell * (c + 0.5) + random.uniform(-jitter, jitter), 2),
                "y": round(6 + cell * (r + 0.5) + random.uniform(-jitter, jitter), 2)}
        if owner == "neutral":
            coin["decoy"] = random.choice(spare)
        coins.append(coin)

    with LOCK:
        GAME = {"name": name, "human_colour": colour, "ai_colour": ai_colour, "coins": coins,
                "turn": "toss", "phase": "idle", "scores": {"human": 0, "ai": 0},
                "selection_seconds": selection, "over": False, "reason": None,
                "coin_size": coin_size, "game_minutes": minutes, "end_time": None,
                "used": set(), "round": None, "allowance": 0,
                "human_result": None, "ai_log": None}
    return jsonify(ok=True)


@app.post("/api/toss")
def toss():
    if not GAME:
        return jsonify(error="Set up the game first."), 400
    d = request.get_json(force=True)
    choice = d.get("choice")
    if choice not in ("Heads", "Tails"):
        return jsonify(error="Choose Heads or Tails."), 400
    with LOCK:
        result = random.choice(("Heads", "Tails"))
        first = "human" if choice == result else "ai"
        GAME.update(toss=result, first=first, turn=first, phase="idle",
                    end_time=time.time() + GAME["game_minutes"] * 60)
        return jsonify(public_state())


@app.post("/api/start_round")
def start_round():
    with LOCK:
        check_over()
        if not GAME or GAME["over"] or GAME["turn"] != "human" or GAME["phase"] != "idle":
            return jsonify(error="It is not time to start a round."), 400
        GAME["round"] = {"qids": draw_questions(), "idx": 0, "correct": 0}
        GAME["phase"] = "quiz"
        return jsonify(public_state())


@app.post("/api/answer")
def answer():
    with LOCK:
        if not GAME or GAME["over"] or GAME["phase"] != "quiz" or GAME["turn"] != "human":
            return jsonify(error="No active question."), 400
        d = request.get_json(force=True)
        try:
            choice = int(d.get("choice"))
        except (TypeError, ValueError):
            return jsonify(error="Invalid answer."), 400
        r = GAME["round"]
        q = QUESTIONS[r["qids"][r["idx"]]]
        ok = choice == q["a"]
        r["correct"] += int(ok)
        r["idx"] += 1
        fb = {"correct": ok, "answer": q["a"], "choice": choice}
        if r["idx"] >= QUESTIONS_PER_ROUND:
            GAME["human_result"] = {"correct": r["correct"], "total": QUESTIONS_PER_ROUND}
            # one coin per correct answer, never more than the coins the player still has
            GAME["allowance"] = min(r["correct"], left_counts()["human"])
            if GAME["allowance"] > 0:
                GAME["phase"] = "select"
            else:
                next_turn("human")
        return jsonify(state=public_state(), feedback=fb)


def valid_human_ids(ids):
    valid = {c["id"] for c in GAME["coins"] if c["owner"] == "human"}
    chosen = []
    for x in ids:
        try:
            x = int(x)
        except (TypeError, ValueError):
            continue
        if x in valid and x not in chosen:
            chosen.append(x)
    return chosen[:GAME["allowance"]]


@app.post("/api/human_finish")
def human_finish():
    with LOCK:
        if not GAME or GAME["turn"] != "human" or GAME["phase"] != "select":
            return jsonify(error="No active human selection."), 400
        d = request.get_json(force=True)
        ids = valid_human_ids(d.get("ids", []))
        for c in GAME["coins"]:
            if c["id"] in ids:
                c["owner"] = "collected_human"
        GAME["scores"]["human"] += len(ids)
        GAME["allowance"] = 0
        next_turn("human")
        return jsonify(public_state())


@app.post("/api/ai_turn")
def ai_turn():
    with LOCK:
        check_over()
        if not GAME or GAME["over"] or GAME["turn"] != "ai" or GAME["phase"] != "idle":
            return jsonify(error="It is not the AI turn."), 400

        # the AI agent answers 6 system questions; each answer is shown to the player
        log, correct = [], 0
        for i in draw_questions():
            q = QUESTIONS[i]
            ok = random.random() < AI_ACCURACY
            pick = q["a"] if ok else random.choice([j for j in range(len(q["o"])) if j != q["a"]])
            correct += int(ok)
            log.append({"text": q["q"], "options": q["o"], "pick": pick, "answer": q["a"], "correct": ok})

        candidates = [c for c in GAME["coins"] if c["owner"] == "ai"]
        k = min(correct, len(candidates))

        # Heuristic: prefer coins nearer the centre and near other AI coins.
        def utility(c):
            centre = ((c["x"] - 50) ** 2 + (c["y"] - 50) ** 2) ** 0.5
            cluster = sum(1 for o in candidates if o["id"] != c["id"] and
                          ((o["x"] - c["x"]) ** 2 + (o["y"] - c["y"]) ** 2) ** 0.5 < 22)
            return -centre + cluster * 7 + random.random() * 2

        picked_ids = {c["id"] for c in sorted(candidates, key=utility, reverse=True)[:k]}
        for c in GAME["coins"]:
            if c["id"] in picked_ids:
                c["owner"] = "collected_ai"
        GAME["scores"]["ai"] += k
        GAME["ai_log"] = {"items": log, "correct": correct, "collected": k}
        next_turn("ai")
        return jsonify(public_state())


@app.route("/api/state", methods=["GET", "POST"])
def state():
    if not GAME:
        return jsonify({})
    with LOCK:
        return jsonify(public_state())


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
