// Controls load independently of WebGL: analysis still works if 3D fails.
const $ = id => document.getElementById(id);
const moods = {
  happy: ['😊', '#bf7800', '#fff7e6', "That's wonderful! Keep enjoying the moment!"],
  sad: ['😢', '#3971ad', '#eef4fb', 'Be gentle with yourself today.'],
  angry: ['😡', '#b64e36', '#edf7f5', 'Take a slow breath. Give yourself a moment.'],
  love: ['❤️', '#b9345b', '#fff0f5', 'Let that warmth brighten your day.'],
  surprised: ['😲', '#6042db', '#f2eeff', 'An unexpected moment! Stay curious.'],
  neutral: ['😐', '#64748b', '#f4f6f8', "I'm not sure how you're feeling, but that's completely okay."]
};
let current = null;
let drawMood = null;
let pending = null;
let requestVersion = 0;

function cancelAnalysis() {
  requestVersion++;
  pending?.abort();
  pending = null;
  $('analyze').disabled = false;
  $('analyze').textContent = 'Analyze my mood →';
}

function showMood(key, message, source = 'Text analysis') {
  if (!moods[key]) throw new Error('Invalid emotion returned by analyzer');
  current = key;
  const [emoji, accent, background, defaultMessage] = moods[key];
  // Draw first, then apply accessible textual state independently.
  if (drawMood) drawMood(key);
  else $('scene').textContent = emoji;
  document.documentElement.style.setProperty('--accent', accent);
  document.documentElement.style.setProperty('--bg', background);
  $('label').textContent = key.toUpperCase();
  $('message').textContent = message || defaultMessage;
  $('status').textContent = `Mood detected: ${key}`;
  $('confidence').textContent = source;
  document.querySelectorAll('.pick').forEach(button => {
    button.classList.toggle('active', button.dataset.key === key);
    button.setAttribute('aria-pressed', String(button.dataset.key === key));
  });
}

for (const [key, [emoji]] of Object.entries(moods)) {
  const button = document.createElement('button');
  button.className = 'pick';
  button.dataset.key = key;
  button.textContent = `${emoji} ${key[0].toUpperCase()}${key.slice(1)}`;
  button.setAttribute('aria-pressed', 'false');
  button.onclick = () => {
    cancelAnalysis();
    $('validation').textContent = '';
    showMood(key, null, 'Emoji selection');
  };
  $('picker').appendChild(button);
}

$('analyze').onclick = async () => {
  cancelAnalysis();
  const text = $('feeling').value.trim();
  $('validation').textContent = '';
  if (!text) {
    $('validation').textContent = "Please enter how you're feeling first.";
    $('feeling').focus();
    return;
  }
  if (location.protocol === 'file:') {
    $('validation').textContent = 'Start python main.py and use the browser window it opens.';
    return;
  }
  const version = requestVersion;
  pending = new AbortController();
  const signal = pending.signal;
  const timeout = setTimeout(() => pending?.abort(), 10000);
  $('analyze').disabled = true;
  $('analyze').textContent = 'Analyzing…';
  try {
    const response = await fetch('/api/analyze', {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({text}), signal
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const result = await response.json();
    if (version === requestVersion) showMood(result.key, result.message);
  } catch (error) {
    if (version === requestVersion) {
      $('validation').textContent = 'Could not reach the Python analyzer. Run python main.py, keep its terminal open, and use the URL it prints (not VS Code Live Server).';
    }
  } finally {
    clearTimeout(timeout);
    if (version === requestVersion) cancelAnalysis();
  }
};

function reset() {
  cancelAnalysis();
  $('feeling').value = '';
  $('validation').textContent = '';
  showMood('neutral');
  current = null;
  $('label').textContent = 'Welcome to MoodSense';
  $('message').textContent = "Tell us how you're feeling or choose an emoji.";
  $('status').textContent = 'Ready to listen';
  $('confidence').textContent = 'Waiting for input';
  document.querySelectorAll('.pick').forEach(button => {
    button.classList.remove('active');
    button.setAttribute('aria-pressed', 'false');
  });
}
$('reset').onclick = reset;
$('message').setAttribute('aria-live', 'polite');
$('feeling').maxLength = 5000;
reset();

// Failure here must never stop the controls above from working.
import('./app.js').then(module => {
  drawMood = module.applyVisual;
  const previous = current;
  if (previous) showMood(previous, $('message').textContent, $('confidence').textContent);
  else reset();
}).catch(error => {
  console.warn('3D scene unavailable; using emoji fallback.', error);
  $('scene').textContent = moods[current || 'neutral'][0];
});
