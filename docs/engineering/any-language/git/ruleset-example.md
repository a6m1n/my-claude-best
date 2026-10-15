# Ruleset example

This file gives one GitHub ruleset for the default branch and for the branch `main`. The ruleset
applies the branch rules of [git.md](git.md) sections 5 and 6 to these two branches only. The
repository settings in section 5 are a separate step. The first two rules are the minimum for
every repository. The section "What to change for your repository" names the parts that a
repository can change.

The ruleset works in a public repository on all GitHub plans. It also works in a private
repository on GitHub Pro, Team or Enterprise Cloud. A private repository on GitHub Free has no
rulesets and no branch protection
([rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets),
[branch protection](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)).

## The ruleset

```json
{
  "name": "protect-main-and-default-branch",
  "target": "branch",
  "enforcement": "active",
  "bypass_actors": [],
  "conditions": {
    "ref_name": { "include": ["~DEFAULT_BRANCH", "refs/heads/main"], "exclude": [] }
  },
  "rules": [
    { "type": "deletion" },
    { "type": "non_fast_forward" },
    {
      "type": "pull_request",
      "parameters": {
        "required_approving_review_count": 0,
        "dismiss_stale_reviews_on_push": false,
        "require_code_owner_review": false,
        "require_last_push_approval": false,
        "required_review_thread_resolution": false,
        "allowed_merge_methods": ["merge"]
      }
    }
  ]
}
```

JSON has no comments. So the reason for each part is in the table below, not at the line, as
[readability.md](../readability/readability.md) section 4 asks for code that others copy. Keep a
link to this file next to a copy of the JSON. A copy of the JSON alone loses these reasons.

## What each part means

| Part | What it does | Why |
|---|---|---|
| `name` | GitHub shows this name in the list of rulesets. | The name tells a reader what the ruleset protects. |
| `"target": "branch"` | The rules apply to branches, not to tags. | Tags need a different ruleset. |
| `"enforcement": "active"` | GitHub applies the rules when you create the ruleset. | The value `disabled` keeps the ruleset but stops all of its rules. |
| `"bypass_actors": []` | No person and no app can skip the rules. This includes the repository admins. | Nobody pushes to `main` directly ([git.md](git.md) section 5). An agent can use the token of a person, so a bypass for that person is also a bypass for the agent. An admin can still turn the ruleset off or delete it, and so can an agent with an admin token. A token that cannot edit rulesets keeps an agent inside the rules. |
| `"include": ["~DEFAULT_BRANCH", "refs/heads/main"]` | The rules apply to the default branch, with any name, and to the branch `main`. | `~DEFAULT_BRANCH` follows the default branch. If an admin makes another branch the default, the rules move to it. `refs/heads/main` keeps the rules on `main` in that case too. In a repository with no `main` branch, the second pattern matches nothing. |
| `deletion` | Nobody can delete the branch. | Keep this rule in every repository. All other branches start from the history on the default branch. |
| `non_fast_forward` | Nobody can force push to the branch. | Keep this rule in every repository. A force push replaces history that other people already use ([git.md](git.md) section 6). |
| `pull_request` | Each change gets to the branch through a pull request. | [git.md](git.md) section 5 lets `main` change only through a merged pull request. |
| `"required_approving_review_count": 0` | A pull request can merge without an approval. | The author of a pull request cannot approve it ([GitHub Docs](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests/approving-a-pull-request-with-required-reviews)). With a value of 1, a repository with one person cannot merge. With 0, the ruleset does not stop an agent from merging its own pull request. [git.md](git.md) section 5 forbids that as a rule, not as a setting. |
| `dismiss_stale_reviews_on_push`, `require_code_owner_review`, `require_last_push_approval` | Each of these settings asks for an approval or removes an approval. | With no required approvals, all three stay `false`. |
| `"required_review_thread_resolution": false` | An open review comment does not stop a merge. | Set it to `true` when a team must resolve each comment before a merge. |
| `"allowed_merge_methods": ["merge"]` | The merge button makes a merge commit. Squash and rebase are not available. | [git.md](git.md) section 5 lands each pull request with a merge commit. |

## Apply it

You need admin access to the repository, or a custom role with the "edit repository rules"
permission. Run the commands in a clone of the repository. `gh` takes `{owner}` and `{repo}` from
`GH_REPO`. Without `GH_REPO`, `gh` takes them from a remote of the clone, and it takes the remote
`upstream` before `origin`.

1. Run `export GH_REPO=OWNER/REPO`. Use the owner and the name of the repository to protect.
2. Run `gh api repos/{owner}/{repo} --jq .allow_merge_commit`. If the output is `false`, turn on
   merge commits in the repository settings. The ruleset allows only merge commits.
3. If a branch protection rule on the default branch or on `main` has "Require linear history",
   turn that setting off. It allows no merge commits.
4. Save the JSON above as `ruleset.json` in the root of the clone.
5. Run `gh api --method POST repos/{owner}/{repo}/rulesets --input ruleset.json --jq .id`. Write
   down the number that it shows. This number is the ID of the ruleset. If `gh` shows an HTTP
   error, correct the cause that the message gives. Then do this step again.
6. Run `gh api repos/{owner}/{repo} --jq .default_branch` to get the name of the default branch.
7. Run `gh api repos/{owner}/{repo}/rules/branches/BRANCH --jq '.[] | "\(.type) \(.ruleset_id)"'`.
   Put the name from step 6 in place of `BRANCH`.
8. Make sure that the output shows `deletion`, `non_fast_forward` and `pull_request`, each with
   the ID from step 5. If a rule is missing, the ruleset does not protect the branch.
9. If the repository has a branch `main` that is not the default, do steps 7 and 8 again. Use
   `main` in place of `BRANCH`.

## What to change for your repository

- If your repository uses squash or rebase merges, change `allowed_merge_methods`. Read
  [README.md](README.md) § "The point to adapt" before you change it.
- When two or more people review, you can ask for approvals. Set
  `required_approving_review_count` to 1 or more.
- This ruleset protects the default branch and `main` only. For the other shared branches that
  [git.md](git.md) section 6 protects, add one more ruleset with only the `non_fast_forward` rule.

## Change it later

Step 5 of "Apply it" makes a new ruleset. It does not change the ruleset that you have. To change
that ruleset, use its ID.

First do step 1 of "Apply it".

1. Run `gh api repos/{owner}/{repo}/rulesets --jq '.[] | "\(.id) \(.name)"'` to find the ID.
2. Change `ruleset.json`.
3. Run `gh api --method PUT repos/{owner}/{repo}/rulesets/RULESET_ID --input ruleset.json`. Put
   the ID in place of `RULESET_ID`.
4. Do steps 6 to 9 of "Apply it" again. In step 8, use the ID from step 1 above.

To delete the ruleset, run `gh api --method DELETE repos/{owner}/{repo}/rulesets/RULESET_ID`. In
the web interface, the ruleset is in the repository settings, under Rulesets.

Turn the rules off for a short time in two cases only. For each case, set `enforcement` to
`disabled` with steps 1 to 3 above. Set it back to `active` right after the work. Then do step 4
above. While the ruleset is disabled, all three rules stop. Any person or app with write access
can then push to these branches. They can also delete `main` when it is not the default branch.

- A history rewrite in the exception path of [git.md](git.md) section 6. A person does the
  rewrite, never an agent.
- A rename of the default branch, or a change to another default branch. GitHub's rules page
  says that an admin cannot do either while force pushes are blocked and nobody can bypass the
  ruleset
  ([GitHub Docs](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets)).

---

This ruleset is good because each rule applies a rule of [git.md](git.md), and it adds no other
rule. The two rules that every repository keeps come first. The empty bypass list makes the rules
hold for every push, from admins and agents too. Only a token that can edit rulesets can turn the
rules off. The section "What to change for your repository" names each part that a copy can
change, so a team changes it on purpose.
