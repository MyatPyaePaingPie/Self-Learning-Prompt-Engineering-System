# Self-Learning Prompt Engineering System

## Timeline

### Weeks 1–2 – Research & Exploration (Sept 11 – Sept 25)
**Goal:** build a shared foundation before coding.
- Hold a group discussion on prompt engineering techniques and project direction.
- Explore techniques in depth: role prompting, structured outputs, context preservation, chain-of-thought.
- Test variations across different LLMs.
- Build personal libraries of optimized prompts.
- Document findings.
- **No PRs due.**

### Week 3 – GitHub Setup & First Steps (Sept 26 – Oct 2)
**Goal:** get everyone comfortable with GitHub workflow.

**All –**
- Create and clone a shared repo, each create a personal branch (name-week3).
- Make a small change (e.g., add name to README.md), push, and open a PR.
- Write the README together. 
- Review and approve each other's PRs, practice merging. 

**Assignments:**
- **Paing** – Streamlit: add a simple form (text input + output box).
- **Atang** – File storage: add folders (prompts/, results/) and a script to save text.
- **Bellul** – FastAPI: add /improve route returning placeholder text.
- **Testing & Docs:** everyone writes a test (e.g., does /improve return text?) and documents how to run it.
- **PRs due:** Thurs, Oct 2.

### Week 4 – LLM Integration & First Flow (Oct 3 – Oct 9)
**Goal:** connect backend to LLM and show real improvements.

**All** – Draft first Prompt Engineer and Judge prompts.

**Assignments:**
- **Paing** – File storage: log input + improved prompt.
- **Atang** – FastAPI: connect /improve to LLM and return improved prompt + explanation.
- **Bellul** – Streamlit: send input to backend and display output.
- **Testing & Docs:** add one test each (API returns content, UI displays, file saves correctly). Document where files are stored and how flow works.
- **PRs due:** Thurs, Oct 9.

### Week 5 – Full Loop with Judge (Oct 10 – Oct 16)
**Goal:** run the complete system end-to-end.

**All** – Finalize Judge rubric (clarity, specificity, actionability, structure, context use).

**Assignments:**
- **Paing** – Streamlit: show Judge scores + feedback.
- **Atang** – File storage: save Judge scores alongside prompts.
- **Bellul** – FastAPI: add Judge scoring and return results.
- **Testing & Docs:** each person writes at least one test (Judge returns scores, scores save, UI shows scores). Document rubric clearly in repo.
- **PRs due:** Thurs, Oct 16.

### Week 6 – Self-Learning Basics (Oct 17 – Oct 23)
**Goal:** add simple memory + feedback loop.

**All** – Test prompts from library and observe improvements.

**Assignments:**
- **Paing** – File storage: save prompt versions with timestamps.
- **Atang** – Streamlit: add version history display.
- **Bellul** – FastAPI: implement keep/revert rules using average Judge scores.
- **Testing & Docs:** add tests (history saves correctly, scores tracked, rollback works). Document update rules for clarity.
- **PRs due:** Thurs, Oct 23.

### Week 7 – Integration & Reliability (Oct 24 – Oct 30)
**Goal:** strengthen and polish the system.

**All** – Run end-to-end tests; refine prompts and flow.

**Assignments:**
- **Paing** – FastAPI: add error handling for failed LLM calls.
- **Atang** – File storage: clean version history + organize files.
- **Bellul** – Streamlit: refine UI (clearer layout for results + history).
- **Testing & Docs:** add integration tests (input → output → Judge → history). Document how to run tests.
- **PRs due:** Thurs, Oct 30.

### Week 8 – Polish & Demo (Oct 31 – Nov 6)
**Goal:** prepare for presentation.

**All** – Final testing, full documentation, dry-run demo.

**Assignments:**
- **Paing** – File storage: document full data flow.
- **Atang** – Streamlit: polish demo interface.
- **Bellul** – FastAPI: ensure endpoints are clean, with inline comments.
- **Testing & Docs:** confirm demo runs without errors. Update README with final setup instructions.
- **PRs due:** Thurs, Nov 6.

### Weeks 9–13 – Flex & Wrap-Up (Nov 7 – Dec 9)
**Goal:** polish, catch-up, and extras.
- Add stretch goals and enhanced features if time allows.
- Keep documentation up to date and code well-commented.
- Prepare final demo and submission.
- **Final Submission:** Tues, Dec 9, 2025.
- **PRs due every Thursday** (Nov 13, Nov 20, Nov 27, Dec 4).

---

## Repository Structure

```
self-learning-prompter/
├─ apps/
│  └─ web/                    # Paing's Streamlit UI
│     ├─ streamlit_app.py     # Simple form (Week 3+)
│     ├─ requirements.txt     # Dependencies
│     └─ README.md           # How to run
├─ backend/                   # Bellul's FastAPI backend
│  ├─ api.py                 # API endpoints
│  ├─ requirements.txt       # Dependencies
│  └─ README.md             # How to run
├─ storage/                  # Atang's File storage
│  ├─ prompts/              # Saved prompts
│  ├─ results/              # Judge scores & history
│  ├─ save.py              # Save scripts
│  └─ README.md            # Data structure docs
├─ tests/                   # Testing & Documentation
│  ├─ unit/                # Individual component tests
│  ├─ integration/         # End-to-end tests
│  └─ README.md            # How to run tests
└─ README.md               # Project overview & setup
```

## Success Criteria

- Prompts are consistently rewritten into clearer, more useful versions with explanations.
- The Judge scores improvements fairly and consistently.
- The Prompt Engineer improves steadily over time by learning from stored results.
- Context from original inputs is always preserved and strengthened.
- The system runs reliably in demos without crashes.
- Code and documentation are clear enough that any team member can explain how the system works.
- Weekly PRs and reviews are completed so the whole team stays aligned.

## How it works:
1. A user enters a prompt.
2. The Prompt Engineer rewrites it to be clearer, more specific, and more useful.
3. The system shows the original, the improved version, and an explanation of the changes.
4. A Judge model scores the improvement on clarity, specificity, actionability, structure, and context.
5. The system saves every version and uses the Judge's scores to decide if the new version should replace the old one.
6. If the Judge says the new version is better, the system keeps it. If the Judge says it's worse, the system rolls back to the last best version. Over time, this memory of past attempts helps the system learn what works and what doesn't, so its improvements get stronger automatically.
```

