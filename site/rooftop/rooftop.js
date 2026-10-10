const stage = document.querySelector('#stage');
const ambient = document.querySelector('#ambient');
const performance = document.querySelector('#performance');
const resting = document.querySelector('#resting-actors');
const reducedPose = document.querySelector('#reduced-pose');
const status = document.querySelector('#status');
const motionButton = document.querySelector('#motion');
const resetButton = document.querySelector('#reset');
const actions = [...document.querySelectorAll('[data-action]')];
const preference = matchMedia('(prefers-reduced-motion: reduce)');
let reduced = preference.matches;
let paused = false;
let busy = false;
let seated = false;
let clip = null;
let token = 0;
let reducedTimer = null;
let greeted = false;

function say(message) { status.textContent = message; }
function updateControls() {
  stage.classList.toggle('momo-seated', seated);
  stage.setAttribute('aria-busy', String(busy));
  actions.forEach(button => {
    button.disabled = busy || (seated && button.dataset.action === 'momo');
    if (button.dataset.action === 'momo') button.setAttribute('aria-pressed', String(seated));
  });
  resetButton.hidden = !seated || busy;
  motionButton.textContent = paused ? 'Resume motion' : reduced ? 'Reduced motion' : 'Pause motion';
  motionButton.setAttribute('aria-pressed', String(paused));
  motionButton.disabled = reduced;
}

function setRest() {
  resting.src = `assets/rest-${seated ? 'seated' : 'ground'}.png`;
  stage.classList.toggle('momo-seated', seated);
}

function waitForVideo(video, url) {
  return new Promise((resolve, reject) => {
    let timeout;
    const cleanup = () => {
      clearTimeout(timeout);
      video.removeEventListener('canplay', ready);
      video.removeEventListener('error', failed);
    };
    const ready = () => { cleanup(); resolve(); };
    const failed = () => { cleanup(); reject(new Error('Video could not load')); };
    video.addEventListener('canplay', ready, { once: true });
    video.addEventListener('error', failed, { once: true });
    timeout = setTimeout(() => { cleanup(); reject(new Error('Video load timed out')); }, 20000);
    video.src = url;
    video.load();
  });
}

async function beginAmbient() {
  if (reduced || ambient.src) return;
  try {
    await waitForVideo(ambient, 'assets/mascot-ambient.mp4');
    if (!reduced) ambient.classList.add('ready');
    if (!reduced && !paused && !document.hidden) {
      await ambient.play();
    }
  } catch {
    // The complete static composition and all navigation remain available.
    ambient.classList.remove('ready');
  }
}

function finish() {
  if (clip === 'momo-climb') seated = true;
  setRest();
  performance.pause();
  performance.classList.remove('ready');
  reducedPose.hidden = true;
  busy = false;
  clip = null;
  greeted = false;
  updateControls();
  say(seated ? 'Momo is settled in. Okarun is ready for another lap.' : 'Back on his rooftop. Tap Momo to see her climb.');
}

async function perform(action) {
  if (busy || (action === 'momo' && seated)) return;
  const mine = ++token;
  busy = true;
  paused = false;
  clip = action === 'momo' ? 'momo-climb' : `okarun-${seated ? 'seated' : 'ground'}`;
  if (action === 'momo') { const seatedPoster = new Image(); seatedPoster.src = 'assets/rest-seated.png'; }
  updateControls();
  if (reduced) {
    reducedPose.src = `assets/${action === 'momo' ? 'momo-power' : seated ? 'okarun-hello-seated' : 'okarun-hello'}.png`;
    reducedPose.hidden = false;
    say(action === 'momo' ? 'Momo reaches the roof with her psychic hands.' : 'Okarun visits the cat. “Yo!”');
    reducedTimer = setTimeout(() => { if (mine === token) finish(); }, 1700);
    return;
  }
  say(action === 'momo' ? 'Momo is getting a hand up…' : 'Okarun is getting ready…');
  try {
    await waitForVideo(performance, `assets/${clip}.mp4`);
    if (mine !== token) return;
    performance.currentTime = 0;
    performance.classList.add('ready');
    if (!document.hidden && !paused) await performance.play();
    if (!ambient.paused || (!paused && !document.hidden)) {
      ambient.play().catch(() => {});
    }
    say(action === 'momo' ? 'A little psychokinesis goes a long way.' : 'He’ll be right back.');
  } catch {
    if (mine !== token) return;
    busy = false;
    clip = null;
    performance.classList.remove('ready');
    updateControls();
    say('That scene couldn’t load. Tap again to retry; the playground is still available.');
  }
}

actions.forEach(button => button.addEventListener('click', () => perform(button.dataset.action)));
performance.addEventListener('ended', finish);
performance.addEventListener('timeupdate', () => {
  if (clip?.startsWith('okarun') && performance.currentTime >= 5.12 && !greeted) {
    greeted = true;
    say('“Yo!”');
  }
});
motionButton.addEventListener('click', () => {
  paused = !paused;
  for (const video of [ambient, performance]) {
    if (paused) video.pause();
    else if (video === ambient || busy) video.play().catch(() => {});
  }
  updateControls();
  say(paused ? 'Motion paused.' : 'Motion resumed.');
});

function cancel() {
  token += 1;
  clearTimeout(reducedTimer);
  performance.pause();
  performance.classList.remove('ready');
  reducedPose.hidden = true;
  busy = false;
  clip = null;
  greeted = false;
  setRest();
  updateControls();
}
resetButton.addEventListener('click', () => {
  cancel();
  seated = false;
  setRest();
  updateControls();
  say('Back to the beginning. Tap either character.');
});
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && busy) {
    cancel();
    say('Scene stopped. Everyone is back in place.');
  }
});
document.addEventListener('visibilitychange', () => {
  if (document.hidden) { ambient.pause(); performance.pause(); }
  else if (!paused && !reduced) {
    ambient.play().catch(() => {});
    if (busy && performance.readyState >= 3) performance.play().catch(() => {});
  }
});
preference.addEventListener('change', event => {
  reduced = event.matches;
  cancel();
  if (reduced) { ambient.pause(); ambient.classList.remove('ready'); }
  else { beginAmbient(); if (ambient.readyState >= 3) { ambient.play().catch(() => {}); ambient.classList.add('ready'); } }
  updateControls();
});

window.__rooftopTest = { snapshot: () => ({
  busy, seated, clip, paused, reduced, greeted,
  ambientTime: ambient.currentTime, performanceTime: performance.currentTime,
  ambientPaused: ambient.paused, performancePaused: performance.paused,
  sources: { ambient: ambient.currentSrc, performance: performance.currentSrc },
}) };
updateControls();
beginAmbient();
