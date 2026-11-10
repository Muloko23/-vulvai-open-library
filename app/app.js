/* Know My Body: offline demo app.
 * Progress is stored on the device only, under a random learner code.
 */
(async () => {
  const view = document.getElementById("view");
  const bundle = await (await fetch("library.json")).json();
  const modules = Object.fromEntries(bundle.modules.map(m => [m.id, m]));
  const index = Engine.buildIndex(modules, bundle.stopwords);
  const T = Engine.text;
  const ICON = { audio: "🎧", video: "🎬", story_card: "📖", case_scenario: "🤔", group_activity: "👭" };
  const LABEL = { audio: "Listen", video: "Watch", story_card: "Story", case_scenario: "What would you do?", group_activity: "Group activity" };

  const store = {
    get() { try { return JSON.parse(localStorage.getItem("kmb") || "null"); } catch { return null; } },
    set(v) { try { localStorage.setItem("kmb", JSON.stringify(v)); } catch { /* storage unavailable */ } }
  };
  let state = store.get() || { learner: newCode(), scores: {} };
  store.set(state);
  document.getElementById("learner").textContent = `Code ${state.learner}`;

  function newCode() {
    const a = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";
    return Array.from(crypto.getRandomValues(new Uint32Array(6)), n => a[n % a.length]).join("");
  }
  const el = (tag, attrs = {}, ...kids) => {
    const n = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) k.startsWith("on") ? n.addEventListener(k.slice(2), v) : n.setAttribute(k, v);
    kids.flat().forEach(k => n.append(k));
    return n;
  };
  const speak = s => {
    if (!("speechSynthesis" in window)) return;
    speechSynthesis.cancel();
    speechSynthesis.speak(new SpeechSynthesisUtterance(s));
  };

  function home() {
    const rec = Engine.nextModule(modules, state.scores, bundle.mastery_threshold);
    const cards = Object.values(modules).sort((a, b) => a.level - b.level || a.id.localeCompare(b.id)).map(m => {
      const s = state.scores[m.id];
      const unlocked = m.prerequisites.every(p => (state.scores[p] ?? 0) >= bundle.mastery_threshold);
      const status = s === undefined ? (unlocked ? "Ready" : "Locked") : s >= bundle.mastery_threshold ? "Done" : "Try again";
      return el("button", { class: `card ${status.toLowerCase().replace(" ", "")}`, ...(unlocked ? {} : { disabled: "" }),
        onclick: () => module(m.id) }, el("strong", {}, T(m.title)), el("span", {}, status));
    });
    view.replaceChildren(
      rec.id
        ? el("section", { class: "next" }, el("p", {}, rec.reason === "review" ? "Let's practise this again" : "Your next lesson"),
            el("h2", {}, T(modules[rec.id].title)), el("button", { class: "primary", onclick: () => module(rec.id) }, "Start"))
        : el("section", { class: "next" }, el("h2", {}, "You finished every lesson. Well done!")),
      el("h3", {}, "All lessons"), el("div", { class: "grid" }, cards));
  }

  /* Video lessons play a narrated, captioned clip. Stories, scenarios, and
   * activities show an illustration. Everything is bundled for offline use. */
  function media(l) {
    if (l.video) return el("video", { controls: "", playsinline: "", preload: "metadata", src: l.video,
      poster: l.image || "", class: "clip" });
    if (l.image) return el("img", { src: l.image, alt: "", class: "art" });
    return "";
  }

  function module(id) {
    const m = modules[id];
    let i = 0;
    const show = () => {
      view.querySelectorAll("audio, video").forEach(a => a.pause());
      if (i >= m.lessons.length) return quiz(m);
      const l = m.lessons[i];
      view.replaceChildren(el("p", { class: "crumb" }, T(m.title), ` · ${i + 1} of ${m.lessons.length}`),
        el("section", { class: `lesson ${l.format}` },
          el("p", { class: "format" }, `${ICON[l.format]} ${LABEL[l.format]}`),
          media(l),
          el("p", { class: "script" }, T(l.script)),
          l.audio && !l.video
            ? el("audio", { controls: "", preload: "none", src: l.audio, class: "narration" })
            : l.video ? "" : el("button", { class: "ghost", onclick: () => speak(T(l.script)) }, "▶ Play audio")),
        el("button", { class: "primary", onclick: () => { i++; show(); } }, i + 1 < m.lessons.length ? "Next" : "Quiz"));
    };
    show();
  }

  function quiz(m) {
    const answers = [];
    view.replaceChildren(el("p", { class: "crumb" }, `${T(m.title)} · Quiz`),
      ...m.quiz.map((q, qi) => el("fieldset", { class: "q" }, el("legend", {}, T(q.question)),
        ...q.options.map((o, oi) => el("label", {}, el("input", { type: "radio", name: `q${qi}`,
          onchange: () => (answers[qi] = oi) }), T(o))))),
      el("button", { class: "primary", onclick: () => {
        const score = Engine.scoreQuiz(m, answers);
        state.scores[m.id] = score; store.set(state);
        const passed = score >= bundle.mastery_threshold;
        view.replaceChildren(el("section", { class: "next" },
          el("h2", {}, passed ? "Great work!" : "Good try!"),
          el("p", {}, `You scored ${score}%. ${passed ? "You can move on." : "Let's go over it once more."}`),
          ...m.quiz.map(q => el("p", { class: "review" }, `✔ ${T(q.question)} ${T(q.options[q.answer])}`)),
          el("button", { class: "primary", onclick: home }, "Continue")));
      } }, "Check my answers"));
  }

  function askView() {
    const out = el("div", { class: "answer" });
    const input = el("textarea", { rows: "3", placeholder: "Ask anything about your body. Only you will see this." });
    view.replaceChildren(el("h2", {}, "Ask a private question"),
      el("p", { class: "muted" }, "Answers come only from lessons checked by doctors."),
      input,
      el("button", { class: "primary", onclick: () => {
        const r = Engine.ask(index, bundle, input.value);
        out.className = `answer ${r.routed ? "routed" : ""}`;
        out.replaceChildren(el("p", {}, r.text),
          r.routed ? el("p", { class: "muted" }, "We will let your facilitator know so she can talk with you in private.") : "",
          el("button", { class: "ghost", onclick: () => speak(r.text) }, "▶ Play audio"));
      } }, "Ask"), out);
  }

  function progress() {
    const rows = Object.values(modules).map(m => el("li", {}, T(m.title),
      el("span", {}, state.scores[m.id] === undefined ? "Not started" : `${state.scores[m.id]}%`)));
    view.replaceChildren(el("h2", {}, "My progress"), el("ul", { class: "progress" }, rows),
      el("p", { class: "muted" }, `Learner code ${state.learner}. Your progress is saved on this phone only.`),
      el("button", { class: "ghost", onclick: () => { state = { learner: newCode(), scores: {} }; store.set(state);
        document.getElementById("learner").textContent = `Code ${state.learner}`; home(); } }, "New learner on this phone"));
  }

  function about() {
    view.replaceChildren(el("h2", {}, "About Know My Body"),
      el("section", { class: "about", style: "background:#5b1f4f" },
        el("img", { src: "brand/vulvai_logo_white.png", alt: "VULVAi. Teach one. Heal many.", class: "logo" })),
      el("section", { class: "about" },
        el("p", {}, "VULVAi builds AI powered education and diagnostic tools for vulvovaginal and pelvic health. Its core platform, proprietary clinical algorithm, and research repository were built for clinicians and patients in the United States and remain proprietary."),
        el("p", {}, "Know My Body is VULVAi's first open source model. Together with B.Bindi and Bindi International, we are building it with girls and families in rural Rajasthan so that it is culturally competent as well as medically accurate, and so that any community in the world can adapt it for its own girls."),
        el("p", {}, "The lessons, learning engine, and safety routing in this app are open source. Content is cocreated with the community and verified by VULVAi clinicians before girls use it.")),
      el("h3", {}, "Built for girls everywhere"),
      el("section", { class: "about" },
        el("p", {}, "Rajasthan is the first site. Any community organization can bring Know My Body to its own girls in six steps: partner, listen, adapt, verify, launch, and measure."),
        el("p", {}, "The medical core stays the same everywhere. Each community changes how lessons are told, in its own languages, stories, and images. Every new site adds to the open library and to a shared body of evidence, so each launch is faster than the last.")),
      el("section", { class: "pilot" },
        el("strong", {}, "Pilot prototype"),
        el("p", {}, "This version demonstrates how the app works. Its lessons are drafts and have not yet been reviewed by the community or verified by clinicians. Some narration uses a draft synthetic voice and illustrations are drafts; in the pilot, local women record the voices in Hindi and local dialects, and girls help shape the pictures.")),
      el("p", { class: "muted" }, "Partners: B.Bindi, Bindi International, and VULVAi"));
  }

  document.querySelectorAll("[data-go]").forEach(b => b.addEventListener("click", () =>
    ({ home, ask: askView, progress, about })[b.dataset.go]()));
  if ("serviceWorker" in navigator) navigator.serviceWorker.register("sw.js").catch(() => {});
  home();
})();
