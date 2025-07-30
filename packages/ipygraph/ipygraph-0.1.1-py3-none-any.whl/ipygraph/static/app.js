/* Animated subtitle component */
function ComingSoon({ text }) {
  return (
    <span className="subtitle">
      {text.split("").map((ch, i) => (
        <span
          key={i}
          className="letter"
          style={{ animationDelay: `${i * 0.12}s` }}
        >
          {ch}
        </span>
      ))}
    </span>
  );
}

/* Root component */
function App() {
  return (
    <div className="center-text">
      <h1 className="title">ipyGraph</h1>
      <ComingSoon text="coming soon" />
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);

/* ----------  Particles background  ---------- */
function initParticles() {
  particlesJS("particles-js", {
    particles: {
      number: { value: 80, density: { enable: true, value_area: 800 } },
      color:  { value: "#ffffff" },
      shape:  { type: "circle" },
      opacity:{ value: 0.5 },
      size:   { value: 3 },
      line_linked: {
        enable: true,
        distance: 150,
        color: "#ffffff",
        opacity: 0.4,
        width: 1
      },
      move: { enable: true, speed: 2 }
    },
    interactivity: {
      detect_on: "canvas",
      events: {
        onhover: { enable: true, mode: "repulse" },
        onclick: { enable: true, mode: "push" }
      },
      modes: {
        repulse: { distance: 100, duration: 0.4 },
        push:    { particles_nb: 4 }
      }
    },
    retina_detect: true
  });
}

/* If the HTML is still loading, wait; otherwise run now. */
if (document.readyState === "loading") {
  window.addEventListener("DOMContentLoaded", initParticles);
} else {
  initParticles();
}
