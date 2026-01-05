const form = document.getElementById('search-form');
const modal = document.getElementById('movie-modal');

if (form) {
  form.addEventListener('submit', () => {
    document.body.classList.add('is-loading');
  });
}

const openModal = (card) => {
  if (!modal) return;
  const title = card.dataset.title || '';
  const year = card.dataset.year || '-';
  const rating = card.dataset.rating || '-';
  const similarity = card.dataset.similarity || '';
  const genres = card.dataset.genres || 'Genres unavailable';
  const tagline = card.dataset.tagline || '';
  const director = card.dataset.director || 'Director unavailable';
  const cast = card.dataset.cast || 'Cast unavailable';
  const overview = card.dataset.overview || 'No overview available.';

  const titleEl = document.getElementById('modal-title');
  const subEl = document.getElementById('modal-sub');
  const overviewEl = document.getElementById('modal-overview');
  const metaEl = document.getElementById('modal-meta');

  if (titleEl) titleEl.textContent = title;
  if (subEl) {
    const similarityText = similarity ? `Similarity ${similarity}` : 'Similarity unavailable';
    subEl.textContent = `${year} - Rating ${rating} - ${similarityText}`;
  }
  if (overviewEl) overviewEl.textContent = overview;
  if (metaEl) {
    const taglineLine = tagline ? `Tagline: ${tagline}` : 'Tagline unavailable';
    metaEl.textContent = `${taglineLine} | ${genres} | Director: ${director} | Cast: ${cast}`;
  }

  modal.classList.add('is-open');
  modal.setAttribute('aria-hidden', 'false');
};

const closeModal = () => {
  if (!modal) return;
  modal.classList.remove('is-open');
  modal.setAttribute('aria-hidden', 'true');
};

const cards = document.querySelectorAll('.card');
if (cards.length) {
  cards.forEach((card) => {
    card.addEventListener('click', () => openModal(card));
  });
}

if (modal) {
  modal.addEventListener('click', (event) => {
    if (event.target && event.target.dataset.close === 'true') {
      closeModal();
    }
  });
}

document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape') {
    closeModal();
  }
});
