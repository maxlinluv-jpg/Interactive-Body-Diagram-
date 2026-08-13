const foods = [
 {name:'Beans & lentils',type:'traditional',symbol:'◉',tags:['Protein','Fiber','Folate'],note:'Legumes are nutrient-dense sources of plant protein and dietary fiber.'},
 {name:'Whole grains',type:'traditional',symbol:'▤',tags:['Carbohydrate','Fiber','B vitamins'],note:'Whole grains retain the bran and germ and generally provide more fiber than refined grains.'},
 {name:'Vegetables',type:'traditional',symbol:'◒',tags:['Fiber','Potassium','Folate'],note:'Vegetables contribute vitamins, minerals, fiber, and many bioactive compounds.'},
 {name:'Fruit',type:'traditional',symbol:'●',tags:['Fiber','Vitamin C','Potassium'],note:'Whole fruit provides carbohydrate together with fiber, vitamins, minerals, and water.'},
 {name:'Fish',type:'traditional',symbol:'◇',tags:['Protein','Omega-3','Vitamin D'],note:'Fish provides high-quality protein; some fish are rich in EPA and DHA omega-3 fatty acids.'},
 {name:'Nuts & seeds',type:'traditional',symbol:'◆',tags:['Unsaturated fat','Protein','Fiber'],note:'Nuts and seeds commonly provide unsaturated fats, protein, fiber, and minerals.'},
 {name:'Sugar-sweetened drinks',type:'modern',symbol:'○',tags:['Added sugar','Low fiber'],note:'Sugary drinks can add substantial carbohydrate energy without the fiber found in whole foods.'},
 {name:'Refined grain foods',type:'modern',symbol:'▭',tags:['Carbohydrate','Variable fiber'],note:'Refining removes parts of the grain; nutrient composition varies by product and fortification.'},
 {name:'Packaged snacks',type:'modern',symbol:'□',tags:['Variable sodium','Added sugar varies'],note:'Packaged snack foods vary widely; check the Nutrition Facts label rather than assuming one profile.'},
 {name:'Fast-food meals',type:'modern',symbol:'△',tags:['Variable sodium','Saturated fat varies'],note:'Restaurant meals can vary substantially in portion size, sodium, fats, and added sugars.'}
];
const library=document.getElementById('foodLibrary');
function render(filter='all'){library.innerHTML=foods.filter(f=>filter==='all'||f.type===filter).map(f=>`<article class="food-info-card"><div class="food-symbol">${f.symbol}</div><span class="food-type">${f.type==='traditional'?'TRADITIONAL PATTERN EXAMPLE':'MODERN DIETARY EXAMPLE'}</span><h2>${f.name}</h2><p>${f.note}</p><div class="food-tags">${f.tags.map(t=>`<span>${t}</span>`).join('')}</div></article>`).join('');}
document.querySelectorAll('.filter').forEach(b=>b.addEventListener('click',()=>{document.querySelectorAll('.filter').forEach(x=>x.classList.remove('active'));b.classList.add('active');render(b.dataset.filter);}));
render();
