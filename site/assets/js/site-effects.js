// Particle starfield
tsParticles.load("tsparticles", {
  fullScreen: false,
  particles: {
    number: { value: 70, density: { enable: true, area: 900 } },
    color: { value: "#64b5f6" },
    opacity: { value: 0.3, random: { enable: true, minimumValue: 0.1 } },
    size: { value: { min: 1, max: 3 }, random: true },
    links: { enable: true, color: "#64b5f6", opacity: 0.08, distance: 150, width: 1 },
    move: { enable: true, speed: 0.8, direction: "none", random: true, straight: false, outModes: "out" }
  },
  interactivity: {
    events: { onHover: { enable: true, mode: "grab" }, resize: true },
    modes: { grab: { distance: 140, links: { opacity: 0.15 } } }
  },
  detectRetina: true,
  responsive: [{ maxWidth: 768, options: { particles: { number: { value: 30 } } } }]
});

// Scroll animations
AOS.init({ duration: 800, easing: 'ease-out-cubic', once: true, offset: 60 });

// Typed hero (homepage only)
var typedEl = document.querySelector('.typed-target');
if (typedEl) {
  new Typed(typedEl, {
    strings: ['SOC Analyst', 'Detection Engineering', 'Security Automation', 'Enterprise Security'],
    typeSpeed: 50, backSpeed: 30, backDelay: 2000, loop: true, showCursor: true, cursorChar: '|'
  });
}
