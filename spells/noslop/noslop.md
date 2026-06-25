---
cast_name: noslop
full_name: No Slop In My Grimoire
description: Strip machine-generated tells out of prose so the text reads as written by a person. Cast when drafting, editing, or auditing any deliverable.
---

# No Slop In My Grimoire

A cleaning pass that lifts the machine residue off a draft and hands back something a person could have written.

> Cast it with `!cast noslop`. Everything lives in this one file. The working vocabulary stays English even when the text under the knife is not, so the same words name the same fault in any language.

## How to read a draft

Two kinds of fault hide in machine text, and they do not earn the same trust.

- **The hard kind is countable.** Characters no hand types: a hidden zero-width codepoint, a long dash standing in for a comma, two quote styles in one file, a single Cyrillic letter wedged into a Latin word. A search turns them up, and when one shows up the text was almost certainly pasted together out of model output. Treat it as proof.
- **The soft kind is a habit of phrasing.** A throat-clearing run-up, the dodge from "is" into "serves as," lists that always arrive in threes, a trailing clause that rates the sentence it hangs off. Any one of these can come from a careful person. Several stacked in one paragraph is the signature. Treat it as a hint, and reread before you cut.

Sweep the hard faults with a tool. Weigh the soft ones by eye. The rest of this spell follows that split: the mechanical sweep first, then the read for habit.

## What kind of text is this

Decide the type before you start, because the soft layer bends with it while the hard layer never does.

- **Reference** - notes, exam answers, command and config docs, runbooks, API and spec pages. The cargo here is facts and steps, not a voice. Repeating a flag name or a port number word for word is accuracy, not a fault, so the rhythm and anti-repetition advice goes quiet. Keep every mechanical check live. Run the emptiness test, but judge it one step or one fact at a time; a bare line that lands a fact has earned its place. Leave numbered steps and short labels as they are - that is how a reference is meant to read.
- **Prose** - anything that narrates or persuades: a report, a post, a message, a page of copy. The whole spell applies.

The model cannot tell these apart on its own; it infers from the text and can guess wrong. State the type when you cast it. If you do not, and the text could go either way, ask before scoring.

## The mechanical sweep (proof)

Run this first, with a tool, and trust the result without a judgement call.

**Invisible characters.** A pass of its own, after any quote or Markdown tidy, because those passes miss it. The junk that rides in from a paste or a model dump:

- zero-width space, non-joiner, joiner: U+200B, U+200C, U+200D
- zero-width no-break space and byte-order mark: U+FEFF
- non-breaking space: U+00A0 (swap for an ordinary space)
- soft hyphen: U+00AD
- left-to-right and right-to-left marks: U+200E, U+200F

Run a regex over those codepoints as the closing step; nothing else catches them.

**Dashes and quotes.** One dash only, the plain hyphen. No long dash of either width. Where a clause break wants a mark, give it a comma or a stop. Hold one quote style across the whole file - straight marks unless a house style calls for the curly kind, and never both in one file.

**One script, one tongue.** A page in one language must not carry a loose word or line in another, and Latin text must not hide a stray Cyrillic or Greek glyph. That mix is the loudest sign the text was assembled from pieces generated apart. Go looking for it on purpose and put the stray fragment back into the page's own language.

**Leaked formatting.** Prose for one channel should not arrive wearing another channel's marks. Strip stray `#` headers, `*` emphasis, and `---` rules when the destination does not speak Markdown. Headings in sentence case, not capitalised at every word. Bold for real weight, not sprayed over every key term.

## The read for habit (judgement)

Phrasing reflexes a model leans on. None convicts alone; a cluster does. After each, the move.

**Run-ups and filler.** The sentence that clears its throat before it says anything, the prop begging you to feel the weight, the modifier carrying no load. Openers shaped like "here is the thing," "here is why," "the real point is," "let me be straight," "the truth is"; props like "make no mistake," "let that land," "this matters because"; and the hollow words - very, really, simply, truly, genuinely, basically, deeply - plus stock lead-ins like "at its core," "when it comes to," "in today's world." Keep an adverb only when it bends the fact ("ran nightly," "failed over the wire").
Move: open on the claim.

**The named doer is missing.** A model writes around the person and lets a thing act. An outage does not teach a lesson - someone wrote the postmortem. A config does not drift - someone changed it and logged nothing. A backlog does not balloon - the team stopped triaging. Same for the bare passive: "it was decided," "the database was migrated," "approvals were obtained" - name who. Leave a true past-perfect alone.
Move: put the actor at the front.

**The dressed-up copula.** "Is," "are," "has" are honest verbs. A model flees them into "serves as," "stands as," "functions as," "represents," and into "boasts," "features," "offers," "maintains" for plain "has."
Move: if "is" or "has" carries it, use "is" or "has."

**The set-piece sentence.** Shapes a model reaches for to fake depth: the flip ("the problem is not X, it is Y"), the strip-tease that lists what a thing is not before naming it, chopped fragments staged as gravity ("One word. That is all it takes."), the leading question answered in the same breath ("So what changed? Everything.").
Move: state the end of the thought and drop the run-up to it.

**The trailing gloss.** A fact, then a participle clause bolted on to rate its own weight - "..., marking a turning point," "..., underscoring the scale of it," "..., which speaks to a wider shift." Nothing else gives a draft away as fast. Stop at the fact. If the consequence earns a sentence, give it one with a real subject. Usually it just goes.
Move: end at the period after the fact.

**Inflation.** Small facts tied to grand arcs: "a testament to," "a defining moment," "part of a larger movement," "set the stage for," "left its mark on," "rooted deep in." And the praise-then-pivot-then-fortune-telling tail ("for all its success, X still faces hurdles... yet X keeps thriving... the road ahead lies in adapting"). "Shipped in March" beats "shipped in March, a milestone that reset the roadmap."
Move: keep the fact, bin the frame.

**Fog.** A line that announces weight without naming a thing - "the implications run deep," "the causes are structural," "the stakes could not be higher." And the sweeping extreme - every, always, never - claiming authority it has not earned.
Move: trade the abstraction for the specific.

**Apology and chatter.** None of it reaches a delivered draft. The hedge that confesses ignorance then guesses anyway ("details are thin, but it probably...") - cut the guess with the hedge. The hand-holding ("worth noting that," "bear in mind that"). The recap header on a short piece ("in closing," "to sum up"). The leftover assistant voice ("certainly," "great question," "hope this helps," "want me to go on?"). And borrowed authority - "experts say," "widely seen as," "reports suggest" with no one named, or one voice swollen into "many."
Move: delete it, or pin the claim to one named, cited fact.

**The model's pet words.** One is chance; three in a paragraph is a fingerprint. The familiar set: delve, tapestry, intricate, robust, meticulous, showcase, underscore, pivotal, leverage, foster, garner, vibrant, seamless, crucial, bolster, interplay, testament, and "additionally" heading a sentence. The brochure register rides with them - "nestled in," "boasts," "rich and vibrant," "renowned," "a diverse array of," "thoughtfully." So does stale office talk - deep dive, circle back, double down, move the needle, lean into, on the same page.
Move: pick the word you would say out loud.

**Thesaurus drift.** A fresh synonym swapped in every time a noun comes round again. It reads machine-shuffled and bleeds precision. Lock onto the right term and repeat it; change only when the sense changes.
Move: reuse the accurate word.

**Metronome rhythm.** Every list a triple, every paragraph closing on a punch, three sentences of one length in a row, a question answered before it can breathe.
Move: break the meter - a list of two, a long sentence among short ones, an ending that does not snap.

**The whole menu.** A report that narrates every option it did not take, explains behaviour that was never in doubt ("expected during install"), and repeats one excuse word for word. What reads as human is the friction of the real path: "the migration held a lock, so I dropped the connection and reran it."
Move: record what you did and why, once.

**Carried-over English.** On text translated into English, check the articles and the small prepositions, and rebuild any sentence still walking in another language's word order. Lead with the subject or verb, not with What / When / Which / Why; do not open a paragraph on "So" or a line on "Look,".
Move: rewrite it the way a native would say it.

**Empty paragraphs.** Lay a hand over each one. If removing it costs no fact, no claim, no step, remove it - do not smooth it. Fluent and empty is still empty.
Move: cut the whole paragraph.

## A last walk before delivery

Run down this once, fast:

- An opener that stalls, or a weightless intensifier? Gone.
- A thing doing a person's verb, or a hidden passive? Name who acted.
- "Serves as / boasts / represents" where "is / has" fits? Swap back.
- A flip, a strip-tease, or a question answered in its own breath? State the end of it.
- A participle clause rating the sentence it hangs off? Stop at the fact.
- A grand frame on a small fact, or a line that says "this is important" without saying what? Name the thing.
- A hedge wrapped round a guess, or stray assistant chatter? Delete both.
- Three pet words in one paragraph, or one noun under three synonyms? Thin it; settle on one.
- A run of equal-length sentences, every paragraph snapping shut, or any long dash? Break the pattern; use a comma or a stop.
- The whole menu narrated, or "normal" behaviour explained? Cut to what you did.
- A loose word or line in the wrong language or script? Put it back in the page's own.
- Hidden codepoints? Strip them in the dedicated sweep.
- A hand over each paragraph: does cutting it lose anything? If not, it goes.

## What a person sounds like - leave it

The aim is a living voice, not flat safe text. These read as human; keep them.

- Plain "is," "are," "has," "there is."
- The short verb over the stiff one: began over commenced, sent over dispatched, ran over executed, used over utilized.
- A superlative that is earned - the first, the only, the best one they shipped.
- Real hedging the writer means - "I think," "maybe," "tends to."
- The odd long-way-round phrase that sounds like a person and not a template.

If a change leaves the text flatter, safer, or more generic, do not make it.
