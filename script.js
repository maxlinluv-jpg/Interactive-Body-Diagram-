const systems = {
  Brain: {
    description: 'Cognition, mood, and neurotransmitter activity.', score: 82,
    tags: ['Omega-3', 'Antioxidants', 'Protein'], color: '#8e75d8', icon: '◉'
  },
  Heart: {
    description: 'Circulation, cardiovascular control, and resilience.', score: 88,
    tags: ['Omega-3', 'Fiber', 'Potassium'], color: '#e65d72', icon: '♥'
  },
  Lungs: {
    description: 'Gas exchange and the body’s response to inflammation.', score: 79,
    tags: ['Antioxidants', 'Vitamin C', 'Omega-3'], color: '#c9a18c', icon: '◌'
  },
  Liver: {
    description: 'Detoxification, fat metabolism, and bile production.', score: 84,
    tags: ['Fiber', 'Choline', 'Antioxidants'], color: '#b9793d', icon: '◆'
  },
  Gut: {
    description: 'Digestion, nutrient absorption, and the microbiome.', score: 91,
    tags: ['Fiber', 'Probiotics', 'Polyphenols'], color: '#65b57c', icon: '◎'
  },
  Skin: {
    description: 'Protective barrier function, collagen, and inflammation.', score: 86,
    tags: ['Vitamin C', 'Protein', 'Omega-3'], color: '#d3a47d', icon: '○'
  }
};

const systemButtons = document.querySelectorAll('.system-option');
const organs = document.querySelectorAll('.organ');
const title = document.getElementById('detailTitle');
const description = document.getElementById('detailDescription');
const score = document.getElementById('healthScore');
const bar = document.getElementById('healthBar');
const icon = document.getElementById('detailIcon');
const tags = document.getElementById('nutritionTags');
const toast = document.getElementById('toast');

function showToast(message) {
  toast.textContent = message;
  toast.classList.add('show');
  clearTimeout(showToast.timer);
  showToast.timer = setTimeout(() => toast.classList.remove('show'), 2200);
}

function selectSystem(name) {
  const system = systems[name];
  if (!system) return;

  systemButtons.forEach(button => {
    button.classList.toggle('active', button.dataset.organ === name);
  });
  organs.forEach(button => {
    button.classList.toggle('selected', button.dataset.organ === name);
  });

  title.textContent = name;
  description.textContent = system.description;
  score.textContent = system.score;
  bar.style.width = `${system.score}%`;
  bar.style.background = system.color;
  icon.style.background = system.color;
  icon.textContent = system.icon;
  tags.innerHTML = system.tags.map(tag => `<span>${tag}</span>`).join('');
}

systemButtons.forEach(button => {
  button.addEventListener('click', () => selectSystem(button.dataset.organ));
});

organs.forEach(button => {
  button.addEventListener('click', () => {
    selectSystem(button.dataset.organ);
    document.getElementById('detailsPanel').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  });
});

document.querySelectorAll('.food-card').forEach(card => {
  card.addEventListener('click', () => {
    showToast(`${card.dataset.food} selected — choose a body system to explore its connection.`);
  });
});

document.getElementById('startButton').addEventListener('click', () => {
  document.getElementById('bodyStage').scrollIntoView({ behavior: 'smooth', block: 'center' });
});

document.getElementById('resetButton').addEventListener('click', () => {
  selectSystem('Brain');
  showToast('Model reset.');
});

document.getElementById('learnButton').addEventListener('click', () => {
  document.getElementById('nutrition').scrollIntoView({ behavior: 'smooth' });
});

document.getElementById('helpButton').addEventListener('click', () => {
  showToast('Click an organ or body-system card to explore it.');
});

selectSystem('Brain');
