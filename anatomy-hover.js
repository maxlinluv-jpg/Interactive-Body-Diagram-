(() => {
  const root = document.getElementById('threeRoot');
  if (!root) return;
  const tip = document.createElement('div');
  tip.className = 'organ-hover-tip';
  tip.innerHTML = '<strong>Explore the anatomy</strong><span>Move over an organ</span>';
  root.appendChild(tip);

  // The 3D scene is owned by simulator.js. This helper provides a visual hover
  // guide without changing the existing click/drag controls.
  const regions = [
    ['Brain', .50, .18, .13, .10],
    ['Lungs', .50, .36, .25, .20],
    ['Heart', .48, .42, .12, .13],
    ['Liver', .57, .51, .28, .12],
    ['Stomach', .42, .57, .16, .16],
    ['Pancreas', .50, .61, .22, .07],
    ['Gut', .50, .70, .32, .25]
  ];

  function move(e) {
    const r = root.getBoundingClientRect();
    const x = (e.clientX-r.left)/r.width;
    const y = (e.clientY-r.top)/r.height;
    let found = null;
    for (const [name,cx,cy,rx,ry] of regions) {
      const dx=(x-cx)/rx, dy=(y-cy)/ry;
      if (dx*dx+dy*dy <= 1) { found=name; break; }
    }
    if (!found || e.buttons) {
      tip.classList.remove('show');
      root.style.cursor = e.buttons ? 'grabbing' : 'grab';
      return;
    }
    tip.querySelector('strong').textContent = found;
    tip.querySelector('span').textContent = 'Move or click to explore';
    tip.style.left = `${e.clientX-r.left+16}px`;
    tip.style.top = `${e.clientY-r.top+16}px`;
    tip.classList.add('show');
    root.style.cursor='pointer';
  }
  root.addEventListener('pointermove', move);
  root.addEventListener('pointerleave', () => tip.classList.remove('show'));
})();
