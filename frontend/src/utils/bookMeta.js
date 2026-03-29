/**
 * Shared book metadata — single source of truth for known titles, authors, etc.
 */

export const KNOWN_BOOKS = {
  'andriesse_practical_binary_analysis': { title: 'Practical Binary Analysis', author: 'Dennis Andriesse', year: 2018, publisher: 'No Starch Press' },
  'aumasson_serious_cryptography': { title: 'Serious Cryptography', author: 'Jean-Philippe Aumasson', year: 2017, publisher: 'No Starch Press' },
  'barber_brml': { title: 'Bayesian Reasoning and Machine Learning', author: 'David Barber', year: 2012, publisher: 'Cambridge University Press' },
  'barrett_ssh_definitive_guide': { title: 'SSH, The Definitive Guide', author: 'Daniel Barrett et al.', year: 2005, publisher: "O'Reilly Media" },
  'basarat_typescript_deep_dive': { title: 'TypeScript Deep Dive', author: 'Basarat Ali Syed', year: 2020, publisher: 'Gitbook (Open Source)' },
  'bishop_prml': { title: 'Pattern Recognition and Machine Learning', author: 'Christopher M. Bishop', year: 2006, publisher: 'Springer' },
  'deisenroth_mml': { title: 'Mathematics for Machine Learning', author: 'Marc Peter Deisenroth et al.', year: 2020, publisher: 'Cambridge University Press' },
  'geron_hands_on_ml': { title: 'Hands-On Machine Learning', author: 'Aurélien Géron', year: 2019, publisher: "O'Reilly Media" },
  'goodfellow_dl': { title: 'Deep Learning', author: 'Ian Goodfellow et al.', year: 2016, publisher: 'MIT Press' },
  'hastie_esl': { title: 'The Elements of Statistical Learning', author: 'Trevor Hastie et al.', year: 2009, publisher: 'Springer' },
  'jurafsky_slp3': { title: 'Speech and Language Processing', author: 'Dan Jurafsky & James H. Martin', year: 2024, publisher: 'Stanford (Draft)' },
  'murphy_pml1': { title: 'Probabilistic Machine Learning: An Introduction', author: 'Kevin P. Murphy', year: 2022, publisher: 'MIT Press' },
  'murphy_pml2': { title: 'Probabilistic Machine Learning: Advanced Topics', author: 'Kevin P. Murphy', year: 2023, publisher: 'MIT Press' },
  'shalev-shwartz_uml': { title: 'Understanding Machine Learning', author: 'Shai Shalev-Shwartz & Shai Ben-David', year: 2014, publisher: 'Cambridge University Press' },
  'sutton_rl': { title: 'Reinforcement Learning: An Introduction', author: 'Richard S. Sutton & Andrew G. Barto', year: 2018, publisher: 'MIT Press' },
}

/**
 * Resolve a book title from a book_id.
 */
export function getBookTitle(bookId) {
  if (KNOWN_BOOKS[bookId]) return KNOWN_BOOKS[bookId].title
  // Fallback: parse from book_id
  const parts = bookId.split('_')
  if (parts.length >= 2) {
    const rest = parts.slice(1).join(' ')
    return rest.replace(/\b\w/g, c => c.toUpperCase())
  }
  return bookId.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
}

/**
 * Resolve author from a book_id.
 */
export function getBookAuthor(bookId) {
  if (KNOWN_BOOKS[bookId]) return KNOWN_BOOKS[bookId].author
  const parts = bookId.split('_')
  return parts[0].charAt(0).toUpperCase() + parts[0].slice(1)
}

/**
 * Get full book metadata (with defaults for unknown books).
 */
export function getBookMeta(bookId) {
  const known = KNOWN_BOOKS[bookId]
  return {
    title: known?.title || getBookTitle(bookId),
    author: known?.author || getBookAuthor(bookId),
    year: known?.year || '—',
    publisher: known?.publisher || '—',
  }
}
