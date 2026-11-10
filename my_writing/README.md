# My own writing (criterion 1)

Criterion 1 is tested on ten pieces of human writing, at least four of them
plain (short sentences, everyday words). The `plain_*` files are the plain
ones.

I wrote all ten pieces myself. To pick topics, I started from short drafts an
AI wrote (a Sunday dinner, a commute, a first job, and so on), then rewrote
each one in my own words. The pieces follow the same topics and order of ideas
as those drafts; the sentences are mine.

`scenarios.py` refuses to run if any file still starts with the AI draft's
`DRAFT` line, so a draft can't be tested by mistake.

Keep each piece over 40 words, or it is always labelled "unsure" and tests
nothing.
