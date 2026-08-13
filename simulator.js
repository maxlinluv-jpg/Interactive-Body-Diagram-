const foods = {
  // Traditional-pattern examples — labels describe the role used in this educational model, not a claim that these foods belong to one universal "traditional diet."
  Salmon:{category:'Traditional',icon:'◒',sub:'Fish · Protein · Omega-3',carbs:0,protein:25,fat:13,fiber:0,sugar:0,glycemic:0,orac:120,omega:2.2,effects:['Heart +','Brain +','Protein']},
  Lentils:{category:'Traditional',icon:'◉',sub:'Legume · Fiber · Protein',carbs:20,protein:9,fat:.4,fiber:8,sugar:2,glycemic:5,orac:500,omega:.1,effects:['Gut +','Fiber +','Glucose ↘']},
  Oats:{category:'Traditional',icon:'▤',sub:'Whole grain · Fiber',carbs:27,protein:5,fat:3,fiber:4,sugar:1,glycemic:12,orac:180,omega:.1,effects:['Gut +','Glucose ↘','Energy +']},
  Blueberries:{category:'Traditional',icon:'●',sub:'Fruit · Fiber · Polyphenols',carbs:14,protein:1,fat:.5,fiber:2.4,sugar:10,glycemic:6,orac:2400,omega:.1,effects:['Brain +','Gut +','Antioxidants +']},
  Spinach:{category:'Traditional',icon:'◓',sub:'Leafy green · Folate · Iron',carbs:4,protein:3,fat:.4,fiber:2.2,sugar:.4,glycemic:1,orac:1500,omega:.1,effects:['Gut +','Skin +','Micronutrients +']},
  Walnuts:{category:'Traditional',icon:'◓',sub:'Nut · Unsaturated fat',carbs:14,protein:15,fat:65,fiber:7,sugar:3,glycemic:2,orac:1100,omega:9.1,effects:['Heart +','Brain +','Fiber +']},
  Yogurt:{category:'Traditional',icon:'○',sub:'Fermented dairy · Protein',carbs:5,protein:10,fat:4,fiber:0,sugar:4,glycemic:2,orac:50,omega:.1,effects:['Gut +','Protein +','Calcium +']},
  // Modern-pattern examples — these are illustrative examples of commonly consumed processed foods, not a judgment on every modern diet.
  Soda:{category:'Modern',icon:'○',sub:'Sugar-sweetened beverage',carbs:39,protein:0,fat:0,fiber:0,sugar:39,glycemic:28,orac:0,omega:0,effects:['Glucose ↑','Added sugar','Fiber 0']},
  Chips:{category:'Modern',icon:'◇',sub:'Packaged snack · Sodium',carbs:26,protein:3,fat:10,fiber:2,sugar:1,glycemic:10,orac:20,omega:.1,effects:['Energy dense','Sodium','Fiber +']},
  Donut:{category:'Modern',icon:'○',sub:'Refined grain · Added sugar',carbs:22,protein:3,fat:11,fiber:1,sugar:10,glycemic:16,orac:20,omega:.2,effects:['Added sugar','Energy dense','Glucose ↑']},
  Nuggets:{category:'Modern',icon:'◆',sub:'Processed poultry · Coating',carbs:14,protein:15,fat:13,fiber:1,sugar:1,glycemic:7,orac:30,omega:.2,effects:['Protein +','Sodium','Processed']},
  Cereal:{category:'Modern',icon:'▦',sub:'Packaged grain · Varies by product',carbs:30,protein:3,fat:2,fiber:2,sugar:9,glycemic:15,orac:40,omega:.1,effects:['Carbohydrate','Added sugar may vary','Fiber varies']},
  Fries:{category:'Modern',icon:'≡',sub:'Fried potato · Sodium',carbs:34,protein:4,fat:17,fiber:4,sugar:0,glycemic:18,orac:40,omega:.2,effects:['Energy dense','Sodium','Carbohydrate']}
};

const organs={
  Brain:{desc:'Cognition, mood, memory, and neurotransmitter activity.',score:82,color:'#9177d8',location:'Within the skull, protected by the cranium.',tags:['Omega-3','Antioxidants','Protein']},
  Heart:{desc:'Circulation, cardiac rhythm, and cardiovascular control.',score:88,color:'#df6072',location:'Center-left of the chest, between the lungs.',tags:['Omega-3','Fiber','Potassium']},
  Lungs:{desc:'Oxygen and carbon-dioxide exchange across the respiratory system.',score:79,color:'#c9938b',location:'Paired organs filling most of the upper chest on either side of the heart.',tags:['Antioxidants','Vitamin C','Omega-3']},
  Liver:{desc:'Metabolism, bile production, nutrient processing, and detoxification.',score:84,color:'#a86b43',location:'Upper-right abdomen, beneath the diaphragm.',tags:['Fiber','Choline','Antioxidants']},
  Stomach:{desc:'Mixes food with digestive fluids before contents continue through the intestine.',score:85,color:'#d59a85',location:'Upper-left abdomen, below the diaphragm.',tags:['Protein','Fiber','Balanced meals']},
  Gut:{desc:'Digestion, nutrient absorption, immune signaling, and the microbiome.',score:91,color:'#69b47b',location:'Digestive tract extending through the abdomen from stomach to colon.',tags:['Fiber','Probiotics','Polyphenols']},
  Skin:{desc:'The body’s outer barrier and a major interface with the environment.',score:86,color:'#c18e73',location:'The outer protective layer covering the entire body.',tags:['Vitamin C','Protein','Omega-3']}
};

let totals={carbs:0,protein:0,fat:0,fiber:0,sugar:0,glycemic:0,orac:0,omega:0};
let log=[];let daytime=true;let activeCategory='All';let digestionTimers=[];
const $=id=>document.getElementById(id);
const foodList=$('foodList');

function createFoodCard(name,f){
  const b=document.createElement('button');
  b.className='food-card-web';b.draggable=true;b.dataset.food=name;b.dataset.category=f.category;
  b.innerHTML=`<span class="food-symbol">${f.icon}</span><span class="food-copy"><b>${name}</b><small>${f.sub}</small></span><span class="drag-grip" aria-hidden="true">⠿</span>`;
  b.addEventListener('click',()=>feed(name));
  b.addEventListener('dragstart',e=>{e.dataTransfer.effectAllowed='copy';e.dataTransfer.setData('text/plain',name);$('mouth')?.classList.add('drop-ready');b.classList.add('dragging');$('statusText').textContent='Drop food at the mouth';});
  b.addEventListener('dragend',()=>{$('mouth')?.classList.remove('drop-ready');b.classList.remove('dragging');if($('statusText').textContent==='Drop food at the mouth')$('statusText').textContent='Ready';});
  foodList.appendChild(b);
}
Object.entries(foods).forEach(([name,f])=>createFoodCard(name,f));

function filterFoods(category){
  activeCategory=category;
  document.querySelectorAll('.food-filter').forEach(x=>x.classList.toggle('active',x.dataset.category===category));
  document.querySelectorAll('.food-card-web').forEach(card=>card.hidden=category!=='All'&&card.dataset.category!==category);
}

document.querySelectorAll('.food-filter').forEach(b=>b.addEventListener('click',()=>filterFoods(b.dataset.category)));

function selectOrgan(name){
  const o=organs[name];if(!o)return;
  document.querySelectorAll('.organ').forEach(x=>x.classList.toggle('selected',x.dataset.organ===name));
  $('detailIcon').style.background=o.color;$('detailTitle').textContent=name;$('detailDescription').textContent=o.desc;$('healthScore').textContent=o.score;$('healthBar').style.width=o.score+'%';$('healthBar').style.background=o.color;$('locationNote').textContent=o.location;$('nutritionTags').innerHTML=o.tags.map(x=>`<span>${x}</span>`).join('');
}
document.querySelectorAll('.organ').forEach(x=>x.addEventListener('click',()=>selectOrgan(x.dataset.organ)));

function setJourney(percent,stage){$('digestionBar').style.width=percent+'%';$('digestionStage').textContent=stage;}
function clearDigestionTimers(){digestionTimers.forEach(clearTimeout);digestionTimers=[];}

function feed(name){
  const f=foods[name];if(!f)return;
  clearDigestionTimers();
  Object.keys(totals).forEach(k=>totals[k]+=f[k]||0);log.unshift({name,effects:f.effects,category:f.category});
  $('statusText').textContent=`Digesting ${name}`;$('digestionIcon').textContent=f.icon;
  const particle=$('foodParticle');particle.classList.remove('travel');void particle.offsetWidth;particle.classList.add('travel');
  $('mouth')?.classList.add('processing');
  setJourney(5,'1 · Mouth — chewing and saliva');render();
  digestionTimers=[
    setTimeout(()=>setJourney(20,'2 · Esophagus — swallowing and transport'),2200),
    setTimeout(()=>setJourney(40,'3 · Stomach — mixing and mechanical digestion'),4800),
    setTimeout(()=>setJourney(62,'4 · Small intestine — most nutrient absorption'),7600),
    setTimeout(()=>setJourney(82,'5 · Large intestine — water and microbiome activity'),10400),
    setTimeout(()=>{setJourney(100,'6 · Nutrients enter circulation');$('statusText').textContent='Session updated';$('mouth')?.classList.remove('processing');$('speech').textContent=`${name} completed the educational digestion journey. Review the Nutrition and Systems tabs to see the modeled changes.`;render();},13800)
  ];
}

function render(){
  const round=n=>Math.round(n*10)/10;
  $('macroCards').innerHTML=[['Carbs',totals.carbs,'g'],['Protein',totals.protein,'g'],['Fat',totals.fat,'g'],['Fiber',totals.fiber,'g']].map(x=>`<div class="macro"><b>${round(x[1])}</b><span>${x[0]} ${x[2]}</span></div>`).join('');
  $('glucoseValue').textContent=round(totals.glycemic);$('glucoseBar').style.width=Math.min(100,totals.glycemic/1.5)+'%';
  $('oracValue').textContent=Math.round(totals.orac);$('oracBar').style.width=Math.min(100,totals.orac/30)+'%';
  $('systemMeters').innerHTML=[['Energy',Math.min(100,55+totals.carbs*.5),'#e5b62f'],['Gut Health',Math.min(100,65+totals.fiber*2+log.length*2),'#69b47b'],['Inflammation model',Math.max(5,35+totals.sugar*.7-totals.orac/100),'#df6072'],['Brain nutrition',Math.min(100,65+totals.omega*5+totals.orac/250),'#9177d8'],['Heart nutrition',Math.min(100,70+totals.omega*4+totals.fiber*1.2),'#df6072']].map(x=>`<div class="meter-line"><div><span>${x[0]}</span><b>${Math.round(x[1])}</b></div><div class="progress"><span style="width:${x[1]}%;background:${x[2]}"></span></div></div>`).join('');
  $('effectLog').innerHTML=log.length?log.slice(0,8).map(x=>`<div class="log-item"><b>${x.name}</b><span>${x.category} · ${x.effects.join(' · ')}</span></div>`).join(''):'<span>No foods added yet.</span>';
  if(log.length&&!$('speech').textContent.includes('completed'))$('speech').textContent=`Your model is processing ${log.length} food item${log.length>1?'s':''}. Follow the stages above.`;
}

document.querySelectorAll('.tab').forEach(b=>b.addEventListener('click',()=>{document.querySelectorAll('.tab').forEach(x=>x.classList.remove('active'));b.classList.add('active');document.querySelectorAll('.tab-content').forEach(x=>x.classList.add('hidden'));$(b.dataset.tab+'Tab').classList.remove('hidden')}));
$('timeButton').addEventListener('click',()=>{daytime=!daytime;$('timeButton').textContent=daytime?'☀ Daytime':'☾ Evening';$('speech').textContent=daytime?'Daytime mode: energy and glucose responses are emphasized.':'Evening mode: the model emphasizes sleep and circadian considerations.'});
$('resetButton').addEventListener('click',()=>{clearDigestionTimers();Object.keys(totals).forEach(k=>totals[k]=0);log=[];$('digestionBar').style.width='0';$('digestionStage').textContent='Waiting for food';$('statusText').textContent='Ready';$('foodParticle').classList.remove('travel');$('mouth')?.classList.remove('processing');$('speech').textContent='Your organs will respond as food moves through the model.';render();selectOrgan('Brain')});

const mouth=$('mouth');
if(mouth){
  mouth.addEventListener('dragover',e=>{e.preventDefault();e.dataTransfer.dropEffect='copy';mouth.classList.add('drop-ready');});
  mouth.addEventListener('dragleave',()=>mouth.classList.remove('drop-ready'));
  mouth.addEventListener('drop',e=>{e.preventDefault();mouth.classList.remove('drop-ready');const name=e.dataTransfer.getData('text/plain');if(name)feed(name);});
}

selectOrgan('Brain');render();filterFoods('All');
