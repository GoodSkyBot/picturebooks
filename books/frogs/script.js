const sheets = Array.from(document.querySelectorAll('.sheet'));
const prevButton = document.getElementById('prevButton');
const nextButton = document.getElementById('nextButton');
const progressLabel = document.getElementById('progressLabel');
const progressFill = document.getElementById('progressFill');
const bookStage = document.getElementById('bookStage');
const jumpButtons = Array.from(document.querySelectorAll('[data-jump]'));
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

let currentIndex = 0;
let isTransitioning = false;
let touchStartX = null;
let touchStartY = null;

function getPageLabel(index) {
  if (index === 0) {
    return 'Cover';
  }

  if (index === sheets.length - 1) {
    return 'Credits and Sources';
  }

  return `Page ${index} of ${sheets.length - 2}`;
}

function updateProgress() {
  const progress = (currentIndex / (sheets.length - 1)) * 100;
  progressLabel.textContent = getPageLabel(currentIndex);
  progressFill.style.width = `${progress}%`;
  prevButton.disabled = currentIndex === 0;
  nextButton.disabled = currentIndex === sheets.length - 1;
}

function showOnly(index) {
  sheets.forEach((sheet, sheetIndex) => {
    sheet.hidden = sheetIndex !== index;
    sheet.classList.toggle('is-current', sheetIndex === index);
    sheet.setAttribute('aria-hidden', sheetIndex === index ? 'false' : 'true');
  });

  currentIndex = index;
  updateProgress();
}

function clearAnimationClasses(sheet) {
  sheet.classList.remove(
    'is-turning-forward',
    'is-entering-forward',
    'is-turning-backward',
    'is-entering-backward'
  );
}

function finishTransition(fromSheet, toSheet, targetIndex) {
  clearAnimationClasses(fromSheet);
  clearAnimationClasses(toSheet);
  fromSheet.hidden = true;
  fromSheet.classList.remove('is-current');
  fromSheet.setAttribute('aria-hidden', 'true');
  toSheet.hidden = false;
  toSheet.classList.add('is-current');
  toSheet.setAttribute('aria-hidden', 'false');
  currentIndex = targetIndex;
  isTransitioning = false;
  updateProgress();
}

function goTo(targetIndex) {
  if (isTransitioning || targetIndex === currentIndex || targetIndex < 0 || targetIndex >= sheets.length) {
    return;
  }

  const forward = targetIndex > currentIndex;
  const fromSheet = sheets[currentIndex];
  const toSheet = sheets[targetIndex];

  if (prefersReducedMotion.matches) {
    showOnly(targetIndex);
    return;
  }

  isTransitioning = true;
  clearAnimationClasses(fromSheet);
  clearAnimationClasses(toSheet);

  toSheet.hidden = false;
  toSheet.setAttribute('aria-hidden', 'false');

  fromSheet.classList.add(forward ? 'is-turning-forward' : 'is-turning-backward');
  toSheet.classList.add(forward ? 'is-entering-forward' : 'is-entering-backward');

  window.setTimeout(() => finishTransition(fromSheet, toSheet, targetIndex), 580);
}

function goNext() {
  goTo(currentIndex + 1);
}

function goPrevious() {
  goTo(currentIndex - 1);
}

prevButton.addEventListener('click', goPrevious);
nextButton.addEventListener('click', goNext);

jumpButtons.forEach((button) => {
  button.addEventListener('click', () => {
    const targetIndex = Number.parseInt(button.dataset.jump || '', 10);
    if (!Number.isNaN(targetIndex)) {
      goTo(targetIndex);
    }
  });
});

document.addEventListener('keydown', (event) => {
  if (event.key === 'ArrowRight') {
    event.preventDefault();
    goNext();
  }

  if (event.key === 'ArrowLeft') {
    event.preventDefault();
    goPrevious();
  }
});

bookStage.addEventListener(
  'touchstart',
  (event) => {
    const touch = event.changedTouches[0];
    touchStartX = touch.clientX;
    touchStartY = touch.clientY;
  },
  { passive: true }
);

bookStage.addEventListener(
  'touchend',
  (event) => {
    if (touchStartX === null || touchStartY === null) {
      return;
    }

    const touch = event.changedTouches[0];
    const deltaX = touch.clientX - touchStartX;
    const deltaY = touch.clientY - touchStartY;

    touchStartX = null;
    touchStartY = null;

    if (Math.abs(deltaX) < 44 || Math.abs(deltaX) < Math.abs(deltaY)) {
      return;
    }

    if (deltaX < 0) {
      goNext();
    } else {
      goPrevious();
    }
  },
  { passive: true }
);

prefersReducedMotion.addEventListener('change', () => {
  if (!isTransitioning) {
    showOnly(currentIndex);
  }
});

showOnly(0);
