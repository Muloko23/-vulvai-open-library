// Checks that the offline app engine gives the same results as the Python engine.
// Run: node tests/engine_parity.test.js  (after: python -m openlibrary.cli export)
const fs = require("fs");
const path = require("path");
const vm = require("vm");
const assert = require("assert");

const root = path.join(__dirname, "..");
const ctx = {};
vm.createContext(ctx);
vm.runInContext(fs.readFileSync(path.join(root, "app/engine.js"), "utf8") + "\nthis.Engine = Engine;", ctx);
const Engine = ctx.Engine;
const bundle = JSON.parse(fs.readFileSync(path.join(root, "app/library.json"), "utf8"));
const modules = Object.fromEntries(bundle.modules.map(m => [m.id, m]));
const index = Engine.buildIndex(modules, bundle.stopwords);
const t = bundle.mastery_threshold;

assert.strictEqual(Engine.nextModule(modules, {}, t).id, "body_basics");
assert.strictEqual(Engine.nextModule(modules, { body_basics: 90, menstruation_basics: 40 }, t).id, "menstruation_basics");
assert.strictEqual(Engine.ask(index, bundle, "Why does my stomach hurt so much on my period?").source, "menstruation_basics.faq[1]");
assert.strictEqual(Engine.ask(index, bundle, "It burns when I pee").source, "care_seeking.faq[0]");
assert.strictEqual(Engine.ask(index, bundle, "What is the capital of France?").source, null);
assert.ok(Engine.ask(index, bundle, "I think I might be pregnant").routed);
assert.ok(Engine.ask(index, bundle, "My uncle touched me and said keep it secret").categories.includes("abuse"));
assert.ok(!Engine.ask(index, bundle, "Is white discharge normal?").routed);
assert.strictEqual(Engine.ask(index, bundle, "My discharge smells and itches").source, "care_seeking.faq[2]");
console.log("engine parity: all checks passed");
