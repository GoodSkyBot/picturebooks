(function () {
  "use strict";

  var pages = Array.from(document.querySelectorAll(".page"));
  var prevBtn = document.getElementById("prevBtn");
  var nextBtn = document.getElementById("nextBtn");
  var startBtn = document.getElementById("startReading");
  var current = 0;
  var total = pages.length;
  var turning = false;
  var turnDuration = 480;

  // Read CSS variable for animation duration
  var root = getComputedStyle(document.documentElement);
  var ms = parseFloat(root.getPropertyValue("--turn-ms"));
  if (ms && ms > 1) turnDuration = ms;

  function updateButtons() {
    prevBtn.disabled = current === 0;
    nextBtn.disabled = current === total - 1;
  }

  function showPage(index) {
    pages.forEach(function (p, i) {
      if (i === index) {
        p.hidden = false;
      } else {
        p.hidden = true;
      }
    });
    current = index;
    updateButtons();
  }

  function goForward() {
    if (current >= total - 1 || turning) return;
    turning = true;
    var oldPage = pages[current];
    var newPage = pages[current + 1];

    newPage.hidden = false;
    oldPage.classList.add("turn-out-forward");
    newPage.classList.add("turn-in-forward");

    setTimeout(function () {
      oldPage.classList.remove("turn-out-forward");
      newPage.classList.remove("turn-in-forward");
      oldPage.hidden = true;
      current++;
      updateButtons();
      turning = false;
    }, turnDuration);
  }

  function goBackward() {
    if (current <= 0 || turning) return;
    turning = true;
    var oldPage = pages[current];
    var newPage = pages[current - 1];

    newPage.hidden = false;
    oldPage.classList.add("turn-out-backward");
    newPage.classList.add("turn-in-backward");

    setTimeout(function () {
      oldPage.classList.remove("turn-out-backward");
      newPage.classList.remove("turn-in-backward");
      oldPage.hidden = true;
      current--;
      updateButtons();
      turning = false;
    }, turnDuration);
  }

  // Button handlers
  nextBtn.addEventListener("click", goForward);
  prevBtn.addEventListener("click", goBackward);
  startBtn.addEventListener("click", goForward);

  // Keyboard
  document.addEventListener("keydown", function (e) {
    if (e.key === "ArrowRight" || e.key === "Right") goForward();
    if (e.key === "ArrowLeft" || e.key === "Left") goBackward();
  });

  // Swipe
  var touchStartX = 0;
  var touchStartY = 0;
  var swiping = false;

  document.addEventListener("touchstart", function (e) {
    touchStartX = e.changedTouches[0].clientX;
    touchStartY = e.changedTouches[0].clientY;
    swiping = true;
  }, { passive: true });

  document.addEventListener("touchend", function (e) {
    if (!swiping) return;
    swiping = false;
    var dx = e.changedTouches[0].clientX - touchStartX;
    var dy = e.changedTouches[0].clientY - touchStartY;
    // Only count horizontal swipes
    if (Math.abs(dx) < 40 || Math.abs(dy) > Math.abs(dx)) return;
    if (dx < 0) goForward();
    else goBackward();
  }, { passive: true });

  // Initialize
  showPage(0);
})();
