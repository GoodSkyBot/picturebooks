/* Minimalist Template - Navigation, Audio, and Interactions */
(function () {
  "use strict";

  var pages = document.querySelectorAll(".page");
  var totalPages = pages.length;
  var currentIndex = 0;
  var navPrev = document.getElementById("nav-prev");
  var navNext = document.getElementById("nav-next");
  var tapPrev = document.getElementById("tap-prev");
  var tapNext = document.getElementById("tap-next");
  var swipeHint = document.getElementById("swipe-hint");
  var btnFullscreen = document.getElementById("btn-fullscreen");
  var currentAudio = null;
  var isAnimating = false;

  var ANIM_DURATION = 350;

  function showPage(index, direction) {
    if (index < 0 || index >= totalPages || isAnimating) return;
    stopAudio();
    isAnimating = true;

    var oldPage = pages[currentIndex];
    var newPage = pages[index];

    newPage.hidden = false;

    if (direction === "next") {
      newPage.classList.add("page--slide-in-next");
      oldPage.classList.add("page--slide-out-prev");
    } else if (direction === "prev") {
      newPage.classList.add("page--slide-in-prev");
      oldPage.classList.add("page--slide-out-next");
    } else {
      newPage.classList.add("page--fade-in");
      oldPage.classList.add("page--fade-out");
    }

    void newPage.offsetWidth;

    setTimeout(function () {
      oldPage.hidden = true;
      oldPage.classList.remove("page--slide-out-prev", "page--slide-out-next", "page--fade-out");
      newPage.classList.remove("page--slide-in-next", "page--slide-in-prev", "page--fade-in");
      isAnimating = false;
    }, ANIM_DURATION);

    currentIndex = index;
    updateNav();
  }

  function updateNav() {
    if (navPrev) navPrev.hidden = currentIndex === 0;
    if (navNext) navNext.hidden = currentIndex === totalPages - 1;
  }

  function goNext() {
    if (currentIndex < totalPages - 1 && !isAnimating) {
      showPage(currentIndex + 1, "next");
      dismissHint();
    }
  }

  function goPrev() {
    if (currentIndex > 0 && !isAnimating) {
      showPage(currentIndex - 1, "prev");
      dismissHint();
    }
  }

  // Nav buttons
  if (navPrev) navPrev.addEventListener("click", goPrev);
  if (navNext) navNext.addEventListener("click", goNext);

  function isInteractiveTarget(target) {
    return !!(target && target.closest("button, a, [data-audio], input, select, textarea, [role='button']"));
  }

  // Tap zones
  if (tapPrev) {
    tapPrev.addEventListener("click", function (e) {
      if (isInteractiveTarget(e.target)) return;
      goPrev();
      ripple(tapPrev);
    });
  }
  if (tapNext) {
    tapNext.addEventListener("click", function (e) {
      if (isInteractiveTarget(e.target)) return;
      goNext();
      ripple(tapNext);
    });
  }

  function ripple(el) {
    el.classList.remove("ripple");
    void el.offsetWidth;
    el.classList.add("ripple");
    setTimeout(function () {
      el.classList.remove("ripple");
    }, 400);
  }

  // Keyboard navigation
  document.addEventListener("keydown", function (e) {
    if (e.key === "ArrowRight" || e.key === "Right") goNext();
    else if (e.key === "ArrowLeft" || e.key === "Left") goPrev();
  });

  // Swipe support
  var touchStartX = 0;
  var touchStartY = 0;
  var touchStartTime = 0;

  document.addEventListener("touchstart", function (e) {
    touchStartX = e.changedTouches[0].clientX;
    touchStartY = e.changedTouches[0].clientY;
    touchStartTime = Date.now();
  }, { passive: true });

  document.addEventListener("touchend", function (e) {
    var dx = e.changedTouches[0].clientX - touchStartX;
    var dy = e.changedTouches[0].clientY - touchStartY;
    var dt = Date.now() - touchStartTime;

    if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy) && dt < 500) {
      if (dx < 0) goNext();
      else goPrev();
    }
  }, { passive: true });

  // Swipe hint dismissal
  var hintDismissed = false;
  function dismissHint() {
    if (!hintDismissed && swipeHint) {
      hintDismissed = true;
      swipeHint.style.opacity = "0";
      setTimeout(function () {
        swipeHint.style.display = "none";
      }, 300);
    }
  }

  if (swipeHint) {
    setTimeout(dismissHint, 4000);
  }

  // Fullscreen
  if (btnFullscreen) {
    btnFullscreen.addEventListener("click", function () {
      var book = document.getElementById("book");
      if (!document.fullscreenElement) {
        if (book.requestFullscreen) book.requestFullscreen();
        else if (book.webkitRequestFullscreen) book.webkitRequestFullscreen();
      } else {
        if (document.exitFullscreen) document.exitFullscreen();
        else if (document.webkitExitFullscreen) document.webkitExitFullscreen();
      }
    });
  }

  // Audio playback
  function stopAudio() {
    if (currentAudio) {
      currentAudio.pause();
      currentAudio.currentTime = 0;
      document.querySelectorAll(".btn-read.playing, .extra.playing").forEach(function (btn) {
        btn.classList.remove("playing");
      });
      currentAudio = null;
    }
  }

  function playAudio(src, btn) {
    if (currentAudio && btn && btn.classList.contains("playing")) {
      stopAudio();
      return;
    }
    stopAudio();
    currentAudio = new Audio(src);
    if (btn) btn.classList.add("playing");
    currentAudio.addEventListener("ended", function () {
      if (btn) btn.classList.remove("playing");
      currentAudio = null;
    });
    currentAudio.addEventListener("error", function () {
      if (btn) btn.classList.remove("playing");
      currentAudio = null;
    });
    currentAudio.play();
  }

  // Read-to-me buttons
  document.querySelectorAll(".btn-read").forEach(function (btn) {
    btn.addEventListener("click", function (e) {
      e.stopPropagation();
      var src = btn.getAttribute("data-audio");
      if (src) playAudio(src, btn);
    });
  });

  // Extra fact audio
  document.querySelectorAll(".extra[data-audio]").forEach(function (btn) {
    btn.addEventListener("click", function (e) {
      e.stopPropagation();
      var src = btn.getAttribute("data-audio");
      if (src) playAudio(src, btn);
    });
  });

  // Init
  updateNav();
})();
