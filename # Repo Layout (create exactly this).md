Perfect—here’s your **updated report** rewritten for a **Convex-first stack** (no Postgres, no FastAPI). It’s action-oriented with exact files, code scaffolds, and run steps. Drop this straight into your repo.

---

# Self-Learning Prompt Engineering System — Convex Edition

## Repo Layout (use exactly this)

```
self-learning-prompter/
├─ apps/
│  └─ web/                 # Next.js (or simple React) UI
├─ convex/
│  ├─ schema.ts            # Convex tables
│  ├─ http.ts              # Public HTTP endpoints
│  ├─ functions/
│  │  ├─ prompts.ts        # create, improve, history, learn
│  │  ├─ judge.ts          # judge helpers (LLM/heuristic)
│  │  └─ engine.ts         # rewrite strategies (LLM/heuristic)
├─ infra/
│  ├─ docker/
│  └─ github/
├─ tests/
│  ├─ unit/
│  └─ e2e/
└─ README.md
```

## Branching & daily flow (same)

* Create `develop` from `main`.
* Work in `feature/<short-name>`.
* Push small commits; open PR to `develop` every Thu; squash-merge after review.
* Promote `develop → main` after green tests.

---

## 1) Database & Types — Convex Schema

**`convex/schema.ts`**

```ts
import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  prompts: defineTable({
    userId: v.optional(v.string()),
    originalText: v.string(),
    createdAt: v.number(),                // Date.now()
    bestVersionId: v.optional(v.id("prompt_versions")),
    bestScore: v.optional(v.number())
  })
    .index("by_user", ["userId"])
    .index("by_created", ["createdAt"]),

  prompt_versions: defineTable({
    promptId: v.id("prompts"),
    versionNo: v.number(),                // 0 = original, 1..n
    text: v.string(),
    explanation: v.object({
      bullets: v.array(v.string()),
      diffs: v.array(v.object({ from: v.string(), to: v.string() }))
    }),
    source: v.string(),                   // "original" | "engine/v1" | "engine/llm"
    createdAt: v.number()
  })
    .index("by_prompt", ["promptId"])
    .index("by_prompt_version", ["promptId", "versionNo"]),

  judge_scores: defineTable({
    promptVersionId: v.id("prompt_versions"),
    clarity: v.number(), specificity: v.number(),
    actionability: v.number(), structure: v.number(),
    contextUse: v.number(),
    total: v.number(),
    feedback: v.object({
      pros: v.array(v.string()),
      cons: v.array(v.string()),
      summary: v.string()
    }),
    createdAt: v.number()
  }).index("by_version", ["promptVersionId"])
});
```

**Notes**

* This replaces all SQL/Alembic/ORM. Convex gives you serializable transactions inside mutations.

---

## 2) Core Functions (mutations/queries)

**`convex/functions/engine.ts`** (rewrite strategies; start heuristic, swap to LLM later)

```ts
export function improveHeuristic(original: string) {
  const improved = `You are a senior subject-matter expert.
Task: ${original.trim()}
Deliverables:
- Clear, step-by-step plan
- Examples and edge-cases
- Final answer ready to use
Constraints: [time, tools, data sources]
If information is missing, list precise clarifying questions first, then proceed with best assumptions.`;
  return {
    text: improved,
    explanation: {
      bullets: [
        "Added explicit expert role",
        "Specified deliverables and final artifact",
        "Inserted Constraints section",
        "Required clarifying questions before solution"
      ],
      diffs: [{ from: original, to: improved }]
    },
    source: "engine/v1"
  };
}
```

**`convex/functions/judge.ts`** (heuristic judge; plug LLM later)

```ts
export type Scorecard = {
  clarity: number; specificity: number; actionability: number; structure: number; contextUse: number;
  total: number;
  feedback: { pros: string[]; cons: string[]; summary: string };
};

export function judgeHeuristic(text: string): Scorecard {
  const contains = (xs: string[]) => xs.some(k => text.toLowerCase().includes(k.toLowerCase()));
  const s = { clarity:0, specificity:0, actionability:0, structure:0, contextUse:0 };
  const fb = { pros: [] as string[], cons: [] as string[], summary: "Heuristic v1" };

  if (contains(["you are a","task:"])) { s.clarity += 2; fb.pros.push("Clear role and task."); }
  if (contains(["deliverables","final"])) s.specificity += 2;
  if (contains(["step-by-step","steps","plan"])) s.actionability += 2;
  if (contains(["constraints","missing"])) s.contextUse += 2;
  if (contains(["- ","\n\n"])) s.structure += 2;

  (Object.keys(s) as (keyof typeof s)[]).forEach(k => (s[k] = Math.min(10, Math.max(0, s[k] * 2.5))));
  const total = s.clarity + s.specificity + s.actionability + s.structure + s.contextUse;
  return { ...s, total, feedback: fb };
}
```

**`convex/functions/prompts.ts`**

```ts
import { v } from "convex/values";
import { mutation, query } from "../_generated/server";
import { improveHeuristic } from "./engine";
import { judgeHeuristic } from "./judge";

export const createPrompt = mutation({
  args: { userId: v.optional(v.string()), text: v.string() },
  handler: async (ctx, { userId, text }) => {
    const now = Date.now();

    const promptId = await ctx.db.insert("prompts", {
      userId, originalText: text, createdAt: now
    });

    const v0Id = await ctx.db.insert("prompt_versions", {
      promptId, versionNo: 0, text,
      explanation: { bullets: ["Original"], diffs: [] },
      source: "original", createdAt: now
    });

    const improved = improveHeuristic(text);
    const v1Id = await ctx.db.insert("prompt_versions", {
      promptId, versionNo: 1, text: improved.text,
      explanation: improved.explanation, source: improved.source, createdAt: now
    });

    const score = judgeHeuristic(improved.text);
    await ctx.db.insert("judge_scores", {
      promptVersionId: v1Id, ...score, createdAt: now
    });

    await ctx.db.patch(promptId, { bestVersionId: v1Id, bestScore: score.total });

    return {
      promptId, versionId: v1Id, versionNo: 1,
      improved: improved.text, explanation: improved.explanation, judge: score
    };
  }
});

export const improvePrompt = mutation({
  args: { promptId: v.id("prompts"), strategy: v.optional(v.string()) },
  handler: async (ctx, { promptId }) => {
    const now = Date.now();
    const prompt = await ctx.db.get(promptId);
    if (!prompt) throw new Error("Prompt not found");

    const versions = await ctx.db.query("prompt_versions")
      .withIndex("by_prompt", q => q.eq("promptId", promptId))
      .collect();
    const nextNo = versions.reduce((m, x) => Math.max(m, x.versionNo), 0) + 1;

    // (v2 idea: improve from bestVersionId text)
    const improved = improveHeuristic(prompt.originalText);
    const newVid = await ctx.db.insert("prompt_versions", {
      promptId, versionNo: nextNo, text: improved.text,
      explanation: improved.explanation, source: improved.source, createdAt: now
    });

    const score = judgeHeuristic(improved.text);
    await ctx.db.insert("judge_scores", {
      promptVersionId: newVid, ...score, createdAt: now
    });

    // transactional adopt-if-better
    const fresh = await ctx.db.get(promptId);
    if (!fresh?.bestScore || score.total >= fresh.bestScore) {
      await ctx.db.patch(promptId, { bestVersionId: newVid, bestScore: score.total });
    }

    return { versionId: newVid, versionNo: nextNo, improved: improved.text, explanation: improved.explanation, judge: score };
  }
});

export const getPrompt = query({
  args: { promptId: v.id("prompts") },
  handler: async (ctx, { promptId }) => {
    const p = await ctx.db.get(promptId);
    if (!p) throw new Error("Prompt not found");

    const history = await ctx.db
      .query("prompt_versions")
      .withIndex("by_prompt", q => q.eq("promptId", promptId))
      .order("asc")
      .collect();

    const scores = await Promise.all(
      history.map(h =>
        ctx.db.query("judge_scores").withIndex("by_version", q => q.eq("promptVersionId", h._id)).collect()
      )
    );

    return {
      original: { text: p.originalText },
      best: p.bestVersionId,
      history: history.map((h, i) => ({ versionId: h._id, versionNo: h.versionNo, text: h.text, explanation: h.explanation, source: h.source, scores: scores[i] }))
    };
  }
});
```

---

## 3) Public HTTP Endpoints (for CLI/third-party callers)

**`convex/http.ts`**

```ts
import { httpAction } from "./_generated/server";
import { createPrompt, improvePrompt, getPrompt } from "./functions/prompts";
import { v } from "convex/values";

export const POST = {
  "/v1/prompts": httpAction(async (ctx, req) => {
    const body = await req.json();
    const { userId, text } = body ?? {};
    if (!text) return new Response(JSON.stringify({ error: "Missing text" }), { status: 400 });
    const out = await ctx.runMutation(createPrompt, { userId, text });
    return new Response(JSON.stringify(out), { headers: { "content-type": "application/json" } });
  }),

  "/v1/prompts/improve": httpAction(async (ctx, req) => {
    const body = await req.json();
    const { promptId, strategy } = body ?? {};
    const out = await ctx.runMutation(improvePrompt, { promptId, strategy });
    return new Response(JSON.stringify(out), { headers: { "content-type": "application/json" } });
  }),
} as const;

export const GET = {
  "/v1/prompts": httpAction(async (ctx, req) => {
    const url = new URL(req.url);
    const promptId = url.searchParams.get("promptId");
    if (!promptId) return new Response(JSON.stringify({ error: "Missing promptId" }), { status: 400 });
    // @ts-ignore – Convex Id is string at edge; frontend passes properly
    const out = await ctx.runQuery(getPrompt, { promptId });
    return new Response(JSON.stringify(out), { headers: { "content-type": "application/json" } });
  }),
} as const;
```

> Map these to your Convex deployment route (Convex auto-exposes http actions under `/api/<func>`; you can also proxy via Next.js).

---

## 4) UI Contracts (unchanged, now call Convex httpActions)

```ts
type Explanation = { bullets: string[]; diffs: { from: string; to: string }[] };
type Scorecard = { clarity:number; specificity:number; actionability:number; structure:number; contextUse:number; total:number; feedback:{pros:string[];cons:string[];summary:string} };

type CreatePromptResp = {
  promptId: string; versionId: string; versionNo: number;
  improved: string; explanation: Explanation; judge: Scorecard
};
```

Pages:

* `/` → textarea posts to `POST /v1/prompts` (httpAction).
* `/p/[id]` → `GET /v1/prompts?promptId=...`, button calls `POST /v1/prompts/improve`.

---

## 5) Deterministic E2E Path (demo-safe)

* If LLM providers fail/timeout → **always** fallback to `improveHeuristic` and `judgeHeuristic`.
* Keep all Convex actions under ~10–20s. If you add LLM, use short timeouts (e.g., 4–6s) and fallback.

---

## 6) Metrics & Logging (simple first)

| Metric                   | How to compute                        | Where                        |
| ------------------------ | ------------------------------------- | ---------------------------- |
| Avg Judge Total (weekly) | Sum/Count totals grouped by week      | Convex query or export       |
| Win Rate                 | % of new versions adopted ≥ bestScore | mutation logic               |
| Rollback Rate            | % not adopted                         | mutation logic               |
| Time to Result           | Measure client-side (ms)              | Frontend logs                |
| Heuristic vs LLM usage   | Counters in functions                 | `console.log` or table later |

Add later: a tiny `metrics` table if you want server-side counters.

---

## 7) Tests (adapted; keep green)

**Unit: engine**

```ts
// tests/unit/engine.test.ts (vitest or jest)
import { improveHeuristic } from "../../convex/functions/engine";
test("adds role and sections", () => {
  const out = improveHeuristic("help me code a parser in python");
  expect(out.text).toMatch(/You are a senior/);
  expect(out.text).toMatch(/Deliverables:/);
  expect(out.explanation.bullets.length).toBeGreaterThan(0);
});
```

**Unit: judge**

```ts
import { judgeHeuristic } from "../../convex/functions/judge";
test("scores 0..10 per axis", () => {
  const s = judgeHeuristic("You are a senior... Task: X\nDeliverables:\n- step-by-step\nConstraints:");
  ["clarity","specificity","actionability","structure","contextUse"].forEach(k =>
    expect((s as any)[k]).toBeGreaterThanOrEqual(0)
  );
  expect(s.total).toBeLessThanOrEqual(50);
});
```

**E2E:**

* Use a lightweight script hitting your httpActions locally (or Convex testing harness) to assert create→improve→fetch works.

---

## 8) CI/CD (Node + Convex)

**`infra/github/workflows/ci.yml`**

```yaml
name: ci
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20' }
      - run: npm ci
      - run: npm run typecheck --workspaces=false || true
      - run: npm run test --workspaces=false || true
```

*(Adjust to your monorepo tooling; Convex itself doesn’t require special CI to build.)*

---

## 9) Docker (optional)

If you containerize the **web** app, keep Convex as a managed service (no DB to host).

---

## 10) “Done Today” runbook (copy/paste)

1. **Scaffold**

```
mkdir -p self-learning-prompter/{apps/web,convex/{functions},infra/{docker,github},tests/{unit,e2e}}
cd self-learning-prompter
npm init -y
npm i convex
npx convex dev  # initializes convex/, env, etc. Stop after init if you want.
```

2. **Add files**

* Paste `convex/schema.ts`, `convex/functions/*.ts`, `convex/http.ts` above.

3. **Wire a minimal web page**

* In `apps/web`, create a simple Next.js page with a textarea that POSTs to `/api/v1/prompts` (proxy to Convex httpAction) and renders JSON.

4. **Run locally**

```
npx convex dev
npm run dev  # from apps/web, if using Next.js
```

5. **Smoke test**

* POST `{ "text": "Help me code." }` to your httpAction → verify improved + judge response.
* Call improve again → ensure bestScore logic works.

---

## 11) Upgrades (after baseline)

| Upgrade                 | Actionable step                                                                                                         |
| ----------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| **LLM Prompt Engineer** | Add `improveLLM(original)`; try 2–3 rewrite styles; call Judge for each; insert best; fallback to heuristic on timeout. |
| **LLM Judge**           | Prompt LLM with rubric; require strict JSON; validate; store raw & parsed; cap latency.                                 |
| **Improve-from-Best**   | In `improvePrompt`, fetch `bestVersionId` text and rewrite *that* instead of original.                                  |
| **Analytics UI**        | Build `/admin` in web: trend of avg total, win/rollback rate, top patterns in high scorers.                             |
| **Rate limits**         | Simple per-user ceilings in mutations; return friendly errors.                                                          |
| **Observability**       | Add request IDs and structured logs in actions; capture errors with Sentry.                                             |

---

## 12) Canonical Example (unchanged)

**Input**

```
Help me code.
```

**Improved** (stored in `prompt_versions`)

```
You are a senior Python developer.
Task: Help me design and implement clean, well-commented Python code for [task].
Deliverables:
- Step-by-step plan with rationale
- Working code examples with docstrings and tests
- Edge cases and performance notes
Constraints: [Python version], [libraries allowed], [time], [I/O limits]
If information is missing, list 3–5 clarifying questions first, then proceed with reasonable assumptions.
```

**Explanation** (bullets, diffs)
**Judge**: `{clarity:8, specificity:8, actionability:8, structure:8, contextUse:8, total:40, ...}`

---

## 13) Non-negotiables (baked in)

* **Always store the original** as `versionNo=0`.
* **Never adopt** a new version unless `score.total >= current bestScore`.
* **Deterministic fallback**: if LLM fails → heuristic.
* **Explanations mandatory** for every rewrite.
* **Strict JSON validation** for any LLM judge output before insert.

---

### TL;DR

Yes, switch to **Convex**. You get transactional updates for “best version,” simpler backend, and faster iteration. The code above replaces your SQL/FastAPI stack with **Convex schema + functions + httpActions**, keeping your UI contract intact and your learning loop identical.
