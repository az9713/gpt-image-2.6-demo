'use strict';
const quality=document.getElementById('quality-choice');
quality.addEventListener('change',()=>{
  const option=quality.selectedOptions[0];
  const image=document.getElementById('quality-image');
  image.src=option.value;image.alt=`Sunburst ${option.dataset.quality}-quality scene`;
  document.getElementById('quality-original').href=option.value;
  document.getElementById('quality-meta').textContent=option.dataset.meta;
});
const range=document.getElementById('markup-range');
range.addEventListener('input',()=>{
  document.getElementById('markup-reveal').style.clipPath=`inset(0 ${100-Number(range.value)}% 0 0)`;
  document.getElementById('markup-divider').style.left=`${range.value}%`;
});
document.querySelectorAll('.play').forEach(button=>button.addEventListener('click',()=>{
  const image=button.closest('figure').querySelector('img');
  const playing=button.getAttribute('aria-pressed')==='true';
  image.src=playing?image.dataset.still:image.dataset.gif;
  button.setAttribute('aria-pressed',String(!playing));
  button.textContent=playing?'Play animation':'Show still frame';
}));
const vectorModel=document.getElementById('vector-model');
const vectorVersion=document.getElementById('vector-version');
function updateVector(){
  const base=vectorModel.value;
  const version=vectorVersion.value;
  const path=version==='original'?`image_26_experiment/outputs/${base}.svg`:`image_26_experiment/derived/${base}-${version}.svg`;
  document.querySelectorAll('#vector-sizes img').forEach(image=>{
    image.src=path;image.alt=`${base} ${version} at ${image.dataset.size} pixels`;
  });
}
vectorModel.addEventListener('change',updateVector);vectorVersion.addEventListener('change',updateVector);
document.getElementById('vector-bg').addEventListener('click',event=>{
  const light=document.getElementById('vector-sizes').classList.toggle('light');
  event.currentTarget.setAttribute('aria-pressed',String(light));
  event.currentTarget.textContent=light?'Use dark preview background':'Use light preview background';
});
const navLinks=Array.from(document.querySelectorAll('.rail nav a'));
if('IntersectionObserver' in window){
  const observer=new IntersectionObserver(entries=>{
    const visible=entries.filter(entry=>entry.isIntersecting).sort((a,b)=>b.intersectionRatio-a.intersectionRatio)[0];
    if(visible)navLinks.forEach(link=>link.classList.toggle('active',link.hash===`#${visible.target.id}`));
  },{rootMargin:'-5% 0px -55% 0px',threshold:[0,.1,.3]});
  document.querySelectorAll('section[id]').forEach(section=>observer.observe(section));
}
