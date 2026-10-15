Every value in this file is invented: the project, the branch, the files, the ticket key, the
change and the model name. It shows the shape of one Step 6 output, not real content.

# Worked example — one draft (Step 6)

The setting (invented): a booking site for a chain of climbing gyms, written in TypeScript. The
branch is `feat/PROJ-417-class-waitlist`. The repository's binding lists `scratch/` as working
documents. The identity gate passed: the repo-local `user.name` and `user.email` are set, and
`git var` shows the same pair.

`git status --short` before the draft:

```
 M src/bookings/book-class.ts
?? scratch/
?? src/bookings/waitlist.test.ts
?? src/bookings/waitlist.ts
```

What the skill shows, then it stops and waits:

```
feat [PROJ-417]: Let members join a waitlist when a class is full

- Add a waitlist to each class, so a member who finds a class full can join the waitlist instead of checking again later for a free spot
- Offer a freed spot to the first member on the waitlist when someone cancels, and hold it for two hours before it moves to the next member
- Cover joining, the offer and the two-hour hold in the booking tests

Co-Authored-By: Claude Example 1.0 <noreply@anthropic.com>
```

Approval will stage and commit: `src/bookings/book-class.ts` `src/bookings/waitlist.ts` `src/bookings/waitlist.test.ts`

Why it looks like this: the branch carries the ticket key, so the title uses `type [PROJ-417]:`
(Step 2). The title says what changed for the gym's members, not which functions were added
(title rules). Each bullet says what was done and why, and none lists file names (body rules).
`scratch/` is a working-document folder that the binding lists, so the message does not describe
it and the list of files to commit leaves it out (Step 3). Nothing is staged until the user says
yes (Step 7).
