Every value in this file is invented: the notes, the projects, the keys, the people, the paths,
the field names and the links. It shows the shape of the messages in SKILL.md "Output
contract". The skill has one mode, so this file holds one example. It is not a list of allowed
wordings, counts or flags: a real preview has as many criteria, fields, flags and questions as
its notes and its Jira project produce.

# Example 1 — a Story, with the agent and the related-issue search, created on "yes"

The notes (invented): "members can't see which loans are due soon, they find out only from the
fine. add a due soon list on the account page. sam can take it"

The preview:

    ---
    Summary: Member sees which loans are due soon

    **Problem**
    A library member cannot see which loans are close to their due date. The account page
    lists current loans without due dates (`web/account/loans.tsx:27`), so a member learns
    that a book was due only when the fine arrives.

    **User story**
    As a library member, I want to see which of my loans are due soon, so that I can return
    them before I get a fine.

    **Acceptance criteria**
    - The account page lists the loans that are due soon, apart from the other loans.
    - Each loan in that list shows its due date.
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

    1. LIB-310 — Show due dates on the loans list — Done — related — the same account page, due dates only
    Say which to link (for example 'link 1'), or ignore this.

The user's reply (invented): "10 Central, 11 Sam Lee, link 1"

The full preview is shown again. The ticket between the rules is unchanged; outside it,
`4. Assignee: Sam Lee (your reply)`, `9. Branch (required): Central (your reply)`, a new line
`10. Links: this ticket relates to LIB-310 (your reply)` and `Questions: none`. It is not
printed twice here.

The user's reply (invented): "yes"

The result line:

    Created LIB-482: https://example.atlassian.net/browse/LIB-482 · linked: LIB-310 (Relates)

---

Commentary on the example, never part of a message:

- One example only: the skill has one mode (a preview, shown in full again after each
  correction, then one result line). The Bug and Task bodies are in SKILL.md "Ticket shapes".
- The two rules hold the ticket and nothing else. Fields, questions, flags and the context
  line sit after the second rule, outside the ticket.
- The questions continue the numbers of the fields, so "10 Central" and "3 High" each point at
  one line. After a correction the numbers are given again from 1.
- Example 1 carries a file path because the agent returned one.
- Example 1 has two criteria because its notes hold that much. The count follows the notes,
  inside the limits SKILL.md sets.
- The labels (`Fields`, `Questions`, `Flags`, `Context`) and the closing line follow the
  user's language. The Summary and the Body stay English.
