const systems = {
  Brain:{description:'Cognition, mood, and neurotransmitter activity.',score:82,tags:['Omega-3','Antioxidants','Protein'],color:'#8e75d8',icon:'◉',location:'Located within the skull, protected by the cranium.'},
  Heart:{description:'Circulation, cardiovascular control, and resilience.',score:88,tags:['Omega-3','Fiber','Potassium'],color:'#e65d72',icon:'♥',location:'Located in the center-left of the chest between the lungs.'},
  Lungs:{description:'Gas exchange and the body’s response to inflammation.',score:79,tags:['Antioxidants','Vitamin C','Omega-3'],color:'#c9978b',icon:'◌',location:'A pair of organs filling most of the upper chest on either side of the heart.'},
  Liver:{description:'Detoxification, fat metabolism, and bile production.',score:84,tags:['Fiber','Choline','Antioxidants'],color:'#a9673d',icon:'◆',location:'Located in the upper-right abdomen, just below the diaphragm.'},
  Gut:{description:'Digestion, nutrient absorption, and the microbiome.',score:91,tags:['Fiber','Probiotics','Polyphenols'],color:'#63ae78',icon:'◎',location:'The digestive tract runs from the stomach through the abdomen to the large intestine.'},
  Skin:{description:'Protective barrier function, collagen, and inflammation.',score:86,tags:['Vitamin C','Protein','Omega-3'],color:'#c18e73',icon:'○',location:'The body’s largest organ, forming the outer protective layer.'}
};
const buttons=document.querySelectorAll('.system-option');
const organs=document.querySelectorAll('.svg-organ');
const title=document.getElementById('detailTitle');
const desc=document.getElementById('detailDescription');
const score=document.getElementById('healthScore');
const bar=document.getElementById('healthBar');
const icon=document.getElementById('detailIcon');
const tags=document.getElementById('nutritionTags');
const locationNote=document.getElementById('locationNote');
function selectSystem(name){
  const s=systems[name]; if(!s)return;
  buttons.forEach(b=>b.classList.toggle('active',b.dataset.organ===name));
  organs.forEach(o=>o.classList.toggle('selected',o.dataset.organ===name));
  title.textContent=name; desc.textContent=s.description; score.textContent=s.score;
  bar.style.width=`${s.score}%`; bar.style.background=s.color;
  icon.style.background=s.color; icon.textContent=s.icon;
  tags.innerHTML=s.tags.map(t=>`<span>${t}</span>`).join('');
  locationNote.textContent=s.location;
}
buttons.forEach(b=>b.addEventListener('click',()=>selectSystem(b.dataset.organ)));
organs.forEach(o=>o.addEventListener('click',()=>selectSystem(o.dataset.organ)));
selectSystem('Brain');
