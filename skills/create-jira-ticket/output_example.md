Every value in this file is invented: the notes, the projects, the keys, the people, the paths,
the field names and the links. It shows the shape of the messages in SKILL.md "Output
contract". The skill has two modes, one ticket (any type, an epic included) and a story batch.
This file holds one example of each mode, plus a Bug and a Task in the single-ticket mode, so
the text rules of every type show on a real preview. It is not a list of allowed wordings,
counts or flags: a real preview has as many criteria, stories, fields, flags and questions as
its notes and its Jira project produce.

# Example 1 — a Story, with the agent and the related-issue search, created on "yes"

The notes (invented): "library members can't see which loans are due soon, they find out only
from the fine. add a due soon list on the account page. sam can take it"

The preview:

    ---
    Summary: Member sees which loans are due soon

    **User story**
    As a library member, I want to see which of my loans are due soon, so that I can return
    them before I get a fine.

    **Problem**
    A library member learns that a loan was due only when the fine arrives. Their current
    loans on the account page show no due dates (`web/account/loans.tsx:27`).

    **Acceptance criteria**
    - The account page lists the loans that are due soon, apart from the other loans.
    - Each loan in the due-soon list shows its due date.
    ---

    Fields:
    1. Project: LIB (from the repository)
    2. Type: Story (the notes ask for something a member will be able to see)
    3. Priority: Medium (Jira default)
    4. Assignee: not set — question 11
    5. Component: Member account (matches the component description)
    6. Labels: not set
    7. Parent: not set
    8. Fix version: not set
    9. Branch (required): not set — question 10

    Questions:
    10. The project requires the field Branch. Jira lists: Central, North, East.
    11. "sam" matches two people: Sam Ortiz (sam.ortiz@example.com) and Sam Lee (sam.lee@example.com). Which one?

    Flags: the notes do not say how many days count as "due soon", so the criteria leave the number open.
    Context: 1 agent read the repository: the account page lists loans without due dates; related-issue search: running in the background

    Reply yes to create it, or answer or change any line by its number (for example '10 Central', '3 High'). Lines you leave as they are stay.

The related-issues message (the background search returned while the user read the preview):

    1. LIB-310 — Show due dates on the loans list — To Do — related — the same account page, due dates only
    Say which to link (for example 'link 1'), or ignore this.

The user's reply (invented): "10 Central, 11 Sam Lee, link 1"

The full preview is shown again. The ticket between the rules is unchanged; outside it,
`4. Assignee: Sam Lee (your reply)`, `9. Branch (required): Central (your reply)`, a new line
`10. Links: this ticket relates to LIB-310 (your reply)` and `Questions: none`. It is not
printed twice here.

The user's reply (invented): "yes"

The result line:

    Created LIB-482: https://example.atlassian.net/browse/LIB-482 · linked: LIB-310 (Relates)

# Example 2 — a story batch: a new epic and its stories, created on "yes"

The notes (invented): "epic: library members pay fines online. now they can pay only at the desk: they
queue, and desk staff lose time on cash. done when a member pays from the account page and the
desk sees it as paid. and let's add stories: pay by card on the account page so there is no
queue; an email receipt with the fine and the amount, as proof of payment; a desk list of fines
paid online, so the desk does not charge twice"

The preview:

    ---
    Summary: Members pay fines online

    **Problem**
    Members can pay a fine only at the library desk, so they queue to pay. At the desk, staff
    lose time handling cash.

    **Outcome**
    Members pay fines online instead of queueing at the desk. At the desk, staff see those
    fines as paid without handling cash.

    **Done when**
    - A member can pay an open fine from the account page.
    - The desk sees a fine paid online as paid.

    Stories (3):
    S1. [Story] Member pays a fine by card on the account page
    S2. [Story] Member gets an email receipt for a paid fine
    S3. [Story] Desk staff see which fines were paid online

    **S1. Member pays a fine by card on the account page**

    **User story**
    As a library member, I want to pay a fine by card, so that I do not have to queue at the
    desk.

    **Acceptance criteria**
    - The account page offers card payment for each open fine.
    - A fine paid by card shows as paid.

    **S2. Member gets an email receipt for a paid fine**

    **User story**
    As a library member, I want an email receipt for a paid fine, so that I have proof of
    payment.

    **Acceptance criteria**
    - A member gets a receipt by email after each online payment.
    - The receipt names the fine and the amount.

    **S3. Desk staff see which fines were paid online**

    **User story**
    As a desk staff member, I want to see which fines were paid online, so that the desk does
    not charge a member twice.

    **Acceptance criteria**
    - The desk's list shows each fine paid online.
    - A fine paid online shows as paid at the desk.
    ---

    Fields:
    1. Project: PAY (from the repository)
    2. Type: Epic (your word)
    3. Priority: Medium (Jira default)
    4. Assignee: Alex Kim (current user)
    5. Component: Member account (matches the component description)
    6. Labels: not set
    7. Parent: not set
    8. Fix version: not set
    9. Stories: parent the new epic; each inherits Priority Medium, Assignee Alex Kim, Component Member account (from the epic)

    Questions: none
    Flags: none
    Empty sections: Scope, Out of scope (the notes do not mention them); Stories (created as this batch)
    Context: no agent: the notes were enough; related-issue search: running in the background

    Reply yes to create the epic and its 3 stories, or answer or change any line by its number or story id (for example '3 High', 'S2 drop'). Lines you leave as they are stay.

The related-issue search returned `none`, so no message follows.

The user's reply (invented): "yes"

The result line:

    Created PAY-40: https://example.atlassian.net/browse/PAY-40 · stories: PAY-41, PAY-42, PAY-43

# Example 3 — a Bug, with a required field from its Jira default, created on "yes"

The notes (invented): "bug: after a member renews a loan on the account page, the loan still
shows the old due date until they log out and back in. no error. members think the renewal
failed and call the desk. started after 3.2 went out. urgent. fix in 3.2.1. also the renew
button is grey on mobile"

The preview:

    ---
    Summary: Renewed loan shows the old due date until the member logs out

    **Problem**
    A member who renews a loan on the account page still sees the old due date there, so they
    call the desk about a renewal they think failed. The old date has shown since release 3.2.

    **Steps to reproduce**
    1. Renew a loan on the account page.
    2. Look at that loan's due date on the same page.

    **Expected result**
    The loan shows its new due date.

    **Actual result**
    The loan still shows its old due date, with no error message, until the member logs out
    and back in.
    ---

    Fields:
    1. Project: LIB (from the repository)
    2. Type: Bug (a renewal that exists and shows the wrong due date)
    3. Priority: High (from the notes: "urgent")
    4. Assignee: Jo Park (current user)
    5. Component: Member account (matches the component description)
    6. Labels: not set
    7. Parent: not set
    8. Fix version: 3.2.1 (from the notes)
    9. Branch (required): Central (Jira default)

    Questions: none
    Flags: the notes also say the Renew button is grey on mobile; that looks like a separate bug, so it stays out of this one.
    Context: no agent: the notes were enough; related-issue search: running in the background

    Reply yes to create it, or answer or change any line by its number (for example '9 North', '3 Medium'). Lines you leave as they are stay.

The related-issue search returned `none`, so no message follows.

The user's reply (invented): "yes"

The result line:

    Created LIB-497: https://example.atlassian.net/browse/LIB-497

# Example 4 — a Task, with the agent and an assignee question, created after one answer

The notes (invented): "task: upgrade the payment library to v5, v4 gets no security fixes
after 1 march. the payment tests must still pass, and members must pay by card the same way as
now. high priority, fix version 3.3.0, label security. dana will do it"

The preview:

    ---
    Summary: Upgrade the payment library to v5

    **Problem**
    The payment library is pinned to v4, which gets no security fixes after 1 March
    (`services/payment/pyproject.toml:14`).

    **Acceptance criteria**
    - The payment service runs on payment library v5.
    - The payment tests pass on payment library v5.
    - A member pays by card the same way as on payment library v4.
    ---

    Fields:
    1. Project: PAY (from the repository)
    2. Type: Task (an upgrade with no result a member sees)
    3. Priority: High (from the notes)
    4. Assignee: not set — question 9
    5. Component: Payments (matches the component description)
    6. Labels: security (from the notes)
    7. Parent: not set
    8. Fix version: 3.3.0 (from the notes)

    Questions:
    9. "dana" matches no Jira account. Who should take it? Reply with the full name, or '9 none' to leave it unassigned.

    Flags: none
    Context: 1 agent read the repository: the payment service pins payment library 4.8; related-issue search: running in the background

    Reply yes to create it, or answer or change any line by its number (for example '9 Dana Reyes', '3 Medium'). Lines you leave as they are stay.

The related-issue search returned `none`, so no message follows.

The user's reply (invented): "9 Dana Reyes"

"Dana Reyes" is looked up in Jira and matches one account. The full preview is shown again: the
ticket between the rules is unchanged; outside it, `4. Assignee: Dana Reyes (your reply)` and
`Questions: none`. It is not printed twice here.

The user's reply (invented): "yes"

The result line:

    Created PAY-57: https://example.atlassian.net/browse/PAY-57

---

Commentary on the examples, never part of a message:

- Four examples: Example 1 (a Story) and Example 2 (a story batch) are the two modes; Examples
  3 (a Bug) and 4 (a Task) are the single-ticket mode again, so the title and body rules of
  every type show on a real preview. An epic alone is the single-ticket mode with the Epic body
  and the `Empty sections` line.
- The two rules hold the drafts and nothing else. Fields, questions, flags, empty sections and
  the context line sit after the second rule, outside the drafts.
- Each Summary names what the ticket delivers: an activity for a Story, what goes wrong and
  under what condition for a Bug, the action for a Task, the outcome for an Epic.
- In a single Story the user story comes first, then the Problem, then the criteria. Every
  Problem opens with the Summary's actor or thing (a member, the payment library) and what
  happens to them today, and it never repeats the story's goal in negative form.
- The Bug's title and Actual result state what a person sees, never the cause; its Problem
  says since when only because the notes do. Expected and Actual may use "no longer" and
  similar forms; elsewhere the ticket says what is true ("shows as paid").
- In a batch the story titles come first, as one list, so the user reads what each story
  delivers before any body. Each title follows its type's rule (who does what for a Story, the
  action for a Task) and differs from the others by the result.
- A batch Story carries no Problem: the epic's Problem gives the reason. The stories inherit
  the epic's fields, so the `Fields` list is the epic's list plus one `Stories` line and any
  required field of a story's type that the inherited values leave empty (Example 2's project
  has none).
- The questions continue the numbers of the fields, so "10 Central" and "3 High" each point at
  one line; story ids (`S1`–`S3`) point at the stories. With no questions (Example 3), the
  closing line's examples point at field lines. After a correction the numbers are given again
  from 1.
- Examples 1 and 4 carry a file path because the agent returned one; the path ends its
  sentence.
- Example 3 flags the second failure in its notes instead of folding it into the Bug (step 4,
  check 1), and fills its required field from the Jira default. Example 4 shows a named person
  with no Jira match: the question asks for the name, and the reply's name is looked up before
  the next preview.
- A batch story has two criteria because its short shape asks for two and the notes support
  two. Example 1's story has two criteria, Example 4's task three, and Example 2's epic two
  `Done when` signals, because their notes hold that much; the count follows the notes, inside
  the limits SKILL.md sets.
- Every phrase in a draft has its source in the notes or in the agent's facts: the reason in
  each "so that" comes from the notes, and each criterion states a condition the notes or the
  agent's facts give.
- The labels (`Fields`, `Questions`, `Flags`, `Empty sections`, `Context`) and the closing line
  follow the user's language. The Summary and the bodies stay English.
