/* Learning engine for the offline app.
 * Mirrors openlibrary/pathway.py, safety.py, and retrieval.py so the same
 * rules run on a shared phone with no connection. Safety phrases, stopwords,
 * and messages come from the exported library bundle, so Python and the app
 * never drift apart.
 */
const Engine = (() => {
  const text = (value, lang = "en") => (value && (value[lang] || value.en)) || "";

  function nextModule(modules, scores, threshold) {
    const low = Object.entries(scores)
      .filter(([id, s]) => modules[id] && s < threshold)
      .sort((a, b) => a[1] - b[1]);
    if (low.length) return { id: low[0][0], reason: "review" };
    const mastered = new Set(Object.entries(scores).filter(([, s]) => s >= threshold).map(([id]) => id));
    const open = Object.values(modules)
      .filter(m => !(m.id in scores) && m.prerequisites.every(p => mastered.has(p)))
      .sort((a, b) => a.level - b.level || a.id.localeCompare(b.id));
    return open.length ? { id: open[0].id, reason: "new" } : { id: null, reason: "done" };
  }

  function scoreQuiz(module, answers) {
    if (!module.quiz.length) return 100;
    const correct = module.quiz.filter((q, i) => q.answer === answers[i]).length;
    return Math.round((100 * correct) / module.quiz.length);
  }

  const escape = s => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

  function safetyCheck(question, categories) {
    const t = question.toLowerCase().replace(/\s+/g, " ").trim();
    return Object.entries(categories)
      .filter(([, phrases]) => phrases.some(p => new RegExp(`\\b${escape(p)}\\b`).test(t)))
      .map(([cat]) => cat);
  }

  function buildIndex(modules, stopwords, lang = "en") {
    const stop = new Set(stopwords);
    const stem = t => (t.length > 4 && /(ch|sh|x)es$/.test(t)) ? t.slice(0, -2)
      : (t.length > 3 && t.endsWith("s") && !t.endsWith("ss")) ? t.slice(0, -1) : t;
    const tokens = s => (s.toLowerCase().match(/[a-zऀ-ॿ]+/g) || []).filter(t => !stop.has(t)).map(stem);
    const entries = [];
    for (const m of Object.values(modules)) {
      m.faq.forEach((item, i) => {
        const doc = [text(item.question, lang), text(item.answer, lang), item.keywords.join(" ")].join(" ");
        const tf = {};
        tokens(doc).forEach(t => (tf[t] = (tf[t] || 0) + 1));
        entries.push({ id: `${m.id}.faq[${i}]`, answer: text(item.answer, lang),
                       keywords: new Set(item.keywords.map(k => stem(k.toLowerCase()))), tf,
                       len: Object.values(tf).reduce((a, b) => a + b, 0) });
      });
    }
    const n = entries.length || 1;
    const avg = entries.reduce((a, e) => a + e.len, 0) / n;
    const df = {};
    entries.forEach(e => Object.keys(e.tf).forEach(t => (df[t] = (df[t] || 0) + 1)));
    const idf = t => Math.log(1 + (n - df[t] + 0.5) / (df[t] + 0.5));
    return { entries, avg, idf, tokens };
  }

  function ask(index, bundle, question, minScore = 1.0) {
    const flagged = safetyCheck(question, bundle.safety.categories);
    if (flagged.length) return { text: bundle.safety.message, routed: true, categories: flagged };
    const q = index.tokens(question);
    let best = null, bestScore = 0;
    for (const e of index.entries) {
      let s = 0;
      for (const t of q) {
        const f = e.tf[t] || 0;
        if (f) s += index.idf(t) * (f * 2.5) / (f + 1.5 * (0.25 + 0.75 * e.len / index.avg));
      }
      s += 0.5 * q.filter(t => e.keywords.has(t)).length;
      if (s > bestScore) { best = e; bestScore = s; }
    }
    if (!best || bestScore < minScore) return { text: bundle.no_match_message, routed: false, source: null };
    return { text: best.answer, routed: false, source: best.id };
  }

  return { text, nextModule, scoreQuiz, safetyCheck, buildIndex, ask };
})();
