import * as THREE from "three";

// A soft 3D head with a hand-drawn expression layer. Small quadratic curves
// give the mouth rounded, gentle corners instead of a heavy half-ring.
const host = document.getElementById("scene");
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(32, 1, .1, 50);
camera.position.set(0, .12, 6);
const renderer = new THREE.WebGLRenderer({antialias: true, alpha: true});
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.setClearColor(0, 0);
host.replaceChildren(renderer.domElement);
scene.add(new THREE.HemisphereLight(0xffffff, 0xc5b1a9, 2.5));
const light = new THREE.DirectionalLight(0xfff5eb, 3);
light.position.set(-3, 4, 5);
scene.add(light);

const palettes = {
  happy: 0xffdf94, sad: 0xcbdff4, angry: 0xffc5af,
  love: 0xffd1df, surprised: 0xe1d4ff, neutral: 0xffe7bd
};
let current = "neutral";
const character = new THREE.Group();
scene.add(character);
const skin = new THREE.MeshStandardMaterial({color: palettes.neutral, roughness: .65});
const head = new THREE.Mesh(new THREE.SphereGeometry(1.13, 64, 48), skin);
head.scale.set(1, .96, .85);
character.add(head);

const canvas = document.createElement("canvas");
canvas.width = canvas.height = 512;
const ctx = canvas.getContext("2d");
const texture = new THREE.CanvasTexture(canvas);
texture.colorSpace = THREE.SRGBColorSpace;
const expression = new THREE.Mesh(
  new THREE.PlaneGeometry(1.85, 1.85),
  new THREE.MeshBasicMaterial({map: texture, transparent: true, depthWrite: false})
);
expression.position.z = .97;
character.add(expression);
const targetColor = new THREE.Color(palettes.neutral);
const reducedMotion = matchMedia("(prefers-reduced-motion: reduce)");

function stroke(points, width = 9, color = "#65483e") {
  ctx.strokeStyle = color;
  ctx.lineWidth = width;
  ctx.lineCap = "round";
  ctx.beginPath();
  ctx.moveTo(points[0], points[1]);
  ctx.quadraticCurveTo(...points.slice(2));
  ctx.stroke();
}

function heart(x, y, size) {
  ctx.save();
  ctx.translate(x, y);
  ctx.scale(size, size);
  ctx.fillStyle = "#d85a7f";
  ctx.beginPath();
  ctx.moveTo(0, .75);
  ctx.bezierCurveTo(-1.6, -.2, -.85, -1.3, 0, -.55);
  ctx.bezierCurveTo(.85, -1.3, 1.6, -.2, 0, .75);
  ctx.fill();
  ctx.restore();
}

function draw(time) {
  ctx.clearRect(0, 0, 512, 512);
  // Blush is translucent and softly feathered.
  for (const x of [126, 386]) {
    const blush = ctx.createRadialGradient(x, 282, 2, x, 282, 40);
    blush.addColorStop(0, current === "sad" ? "#e69da966" : "#ef899c88");
    blush.addColorStop(1, "#ef899c00");
    ctx.fillStyle = blush;
    ctx.fillRect(x - 42, 240, 84, 84);
  }
  const blink = !reducedMotion.matches && time % 4.3 > 4.13;
  for (const x of [174, 338]) {
    if (blink) {
      stroke([x - 20, 224, x, 232, x + 20, 224], 8);
    } else if (current === "love") {
      heart(x, 224, 29);
    } else {
      const height = current === "surprised" ? 31 : 25;
      ctx.fillStyle = "#443b40";
      ctx.beginPath();
      ctx.ellipse(x, 222, 20, height, 0, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = "#ffffff";
      ctx.beginPath();
      ctx.ellipse(x - 6, 212, 6, 8, -.3, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = "#ffffff99";
      ctx.beginPath();
      ctx.arc(x + 7, 233, 3, 0, Math.PI * 2);
      ctx.fill();
    }
  }
  if (current === "sad") {
    // Inner brows lift in concern; the mouth stays small and subtle.
    stroke([151, 177, 172, 178, 192, 163], 6, "#8a7b89");
    stroke([320, 163, 340, 178, 361, 177], 6, "#8a7b89");
    stroke([235, 319, 256, 298, 277, 319], 7);
    const dropY = 260 + (reducedMotion.matches ? 0 : Math.sin(time * 1.7) * 3);
    ctx.fillStyle = "#82bce4bb";
    ctx.beginPath();
    ctx.moveTo(365, dropY - 13);
    ctx.bezierCurveTo(349, dropY + 5, 356, dropY + 15, 365, dropY + 15);
    ctx.bezierCurveTo(374, dropY + 15, 381, dropY + 5, 365, dropY - 13);
    ctx.fill();
  } else if (current === "angry") {
    stroke([151, 168, 173, 171, 194, 184], 7);
    stroke([318, 184, 340, 171, 361, 168], 7);
    stroke([236, 319, 256, 306, 276, 319], 8);
  } else if (current === "surprised") {
    stroke([151, 170, 174, 151, 195, 170], 6);
    stroke([317, 170, 338, 151, 361, 170], 6);
    ctx.fillStyle = "#65483e";
    ctx.beginPath();
    ctx.ellipse(256, 311, 16, 22 + (reducedMotion.matches ? 0 : Math.sin(time * 2) * 2), 0, 0, Math.PI * 2);
    ctx.fill();
  } else if (current === "happy") {
    // A tiny open smile with a pink tongue.
    ctx.fillStyle = "#65483e";
    ctx.beginPath();
    ctx.moveTo(221, 300);
    ctx.quadraticCurveTo(256, 310, 291, 300);
    ctx.bezierCurveTo(283, 349, 229, 349, 221, 300);
    ctx.fill();
    ctx.save();
    ctx.clip();
    ctx.fillStyle = "#ef9aa7";
    ctx.beginPath();
    ctx.ellipse(256, 337, 23, 12, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
  } else if (current === "love") {
    stroke([231, 303, 256, 332, 281, 303], 8);
  } else {
    stroke([239, 310, 256, 314, 273, 310], 7);
  }
  texture.needsUpdate = true;
}

function resize() {
  const width = Math.max(host.clientWidth, 1), height = Math.max(host.clientHeight, 1);
  camera.aspect = width / height;
  camera.updateProjectionMatrix();
  renderer.setSize(width, height, false);
}
const observer = new ResizeObserver(resize);
observer.observe(host);
resize();

export function applyVisual(key) {
  current = Object.hasOwn(palettes, key) ? key : "neutral";
  targetColor.setHex(palettes[current]);
  host.setAttribute("aria-label", current + " animated face");
  host.setAttribute("role", "img");
  draw(0);
}

let previous = 0;
renderer.setAnimationLoop(milliseconds => {
  const time = milliseconds / 1000;
  const delta = Math.min(time - previous, .1);
  previous = time;
  skin.color.lerp(targetColor, 1 - Math.exp(-delta * 7));
  character.position.y = reducedMotion.matches ? 0 : Math.sin(time * 1.6) * .035;
  character.rotation.z = reducedMotion.matches ? 0 : Math.sin(time * .8) * .025;
  draw(time);
  renderer.render(scene, camera);
});
window.addEventListener("pagehide", () => {
  renderer.setAnimationLoop(null);
  observer.disconnect();
  head.geometry.dispose();
  skin.dispose();
  expression.geometry.dispose();
  expression.material.dispose();
  texture.dispose();
  renderer.dispose();
}, {once: true});
