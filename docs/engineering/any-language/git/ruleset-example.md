# Ruleset example

This file gives one GitHub ruleset for the default branch and for the branch `main`, the rules to
add when CI runs, and two tag rulesets for release tags. The branch ruleset
applies the branch rules of [git.md](git.md) sections 5 and 6 to these two branches only. The
repository settings in section 5 are a separate step. Section 5 uses a ruleset in a new
repository. A repository that already has branch protection can keep it instead. The first two
rules are the minimum for every repository. The section "What to change for your repository"
names the changes that most repositories make.

**Navigation**

- [The ruleset](#the-ruleset)
- [What each part means](#what-each-part-means)
- [Apply it](#apply-it)
- [What to change for your repository](#what-to-change-for-your-repository)
- [Release tags](#release-tags)
- [Change it later](#change-it-later)

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

[readability.md](../readability/readability.md) section 4 asks for the reason at the line in code
that others copy. This JSON departs from that rule, because JSON has no comments. The reason for
each part is in the table below. The cost: a copy of the JSON alone loses these reasons. Keep a
link to this file next to each copy.

## What each part means

| Part | What it does | Why |
|---|---|---|
| `name` | GitHub shows this name in the list of rulesets. | The name tells a reader what the ruleset protects. |
| `"target": "branch"` | The rules apply to branches, not to tags. | Tags need a different ruleset. |
| `"enforcement": "active"` | GitHub applies the rules when you create the ruleset. | The value `disabled` keeps the ruleset but stops all of its rules. |
| `"bypass_actors": []` | No person and no app can skip the rules. This includes the repository admins. | Nobody pushes to `main` directly ([git.md](git.md) section 5). An agent can use the token of a person, so a bypass for that person is also a bypass for the agent. An admin can still turn the ruleset off or delete it, and so can an agent with an admin token. A token that cannot edit rulesets keeps an agent inside the rules. |
| `"include": ["~DEFAULT_BRANCH", "refs/heads/main"]` | The rules apply to the default branch, with any name, and to the branch `main`. | `~DEFAULT_BRANCH` follows the default branch. If an admin makes another branch the default, the rules move to it. `refs/heads/main` keeps the rules on `main` in that case too. In a repository with no `main` branch, the second pattern matches nothing. |
| `deletion` | Nobody can delete the branch. | Keep this rule in every repository. Deleting a branch and pushing it again replaces its history ([git.md](git.md) section 6). |
| `non_fast_forward` | Nobody can force push to the branch. | Keep this rule in every repository. A force push replaces history that other people already use ([git.md](git.md) section 6). |
| `pull_request` | Each change gets to the branch through a pull request. | [git.md](git.md) section 5 lets `main` change only through a merged pull request. |
| `"required_approving_review_count": 0` | A pull request can merge without an approval. | The author of a pull request cannot approve it ([GitHub Docs](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests/approving-a-pull-request-with-required-reviews)). With a value of 1, a repository with one person cannot merge. With 0, the ruleset does not stop an agent from merging its own pull request. [git.md](git.md) section 5 forbids this merge as a rule, not as a setting. |
| `dismiss_stale_reviews_on_push`, `require_code_owner_review`, `require_last_push_approval` | Each of these settings asks for an approval or removes an approval. | With no required approvals, all three stay `false`. |
| `"required_review_thread_resolution": false` | An open review comment does not stop a merge. | Set it to `true` when a team must resolve each comment before a merge. |
| `"allowed_merge_methods": ["merge"]` | The merge button makes a merge commit. Squash and rebase are not available. | [git.md](git.md) section 5 lands each pull request with a merge commit. |

## Apply it

You need admin access to the repository, or a custom role with the "edit repository rules"
permission. Run the commands in a folder outside any clone of the repository. Then
`ruleset.json` never becomes a file of the repository. `gh` takes `{owner}` and `{repo}` from
`GH_REPO`, which step 1 sets.

1. Run `export GH_REPO=OWNER/REPO`. Use the owner and the name of the repository to protect.
2. Run `gh api repos/{owner}/{repo} --jq .allow_merge_commit`. If the output is `false`, turn on
   merge commits in the repository settings. The ruleset allows only merge commits.
3. If a branch protection rule on the default branch or on `main` has "Require linear history",
   turn that setting off. That setting allows no merge commits.
4. Save the JSON above as `ruleset.json` in that folder.
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
- When two or more people review, ask for approvals and for the code owners' review. Set
  `required_approving_review_count` to 1 or more, `require_code_owner_review` to `true` and
  `require_last_push_approval` to `true`, and give every person and team that `CODEOWNERS` names
  write access. A pull request that changes a file with a code owner then merges only after that
  owner approves it
  ([GitHub Docs](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets)),
  and a push after the approval needs a new approval from someone other than the person who
  pushed, so an author cannot change a workflow after it was approved. GitHub says that code owners
  "must have write permissions for the repository"
  ([GitHub Docs](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners)).
  [ci-cd/pipeline-security.md](../ci-cd/pipeline-security.md) section 8 says which files need
  their owners.
- This ruleset protects the default branch and `main` only. For the other shared branches that
  [git.md](git.md) section 6 protects, add one more ruleset with only the `non_fast_forward` rule.
- When CI runs on pull requests, add a rule that requires its gate job, the one required check of
  [ci-cd/pipeline.md](../ci-cd/pipeline.md) section 6, to the `rules` list. This JSON departs
  from [readability.md](../readability/readability.md) section 4, which asks for the reason at the
  line, because JSON has no comments; the reasons are in the paragraph after it. The cost: a copy
  of the JSON alone loses these reasons.

  ```json
  {
    "type": "required_status_checks",
    "parameters": {
      "strict_required_status_checks_policy": true,
      "required_status_checks": [{ "context": "ci-ok", "integration_id": 15368 }]
    }
  }
  ```

  `context` is the name of the gate job. `integration_id` 15368 is the GitHub Actions app
  (`gh api apps/github-actions --jq .id` prints it): without it, any person or app with write
  access can set the check's state, and the ruleset can name an app as the expected source
  ([GitHub Docs](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets)),
  so only a workflow run can turn `ci-ok` green. `strict_required_status_checks_policy: true` is
  "Require branches to be up to date before merging": the branch must be current with `main`, so
  the check ran on the code that lands, at the cost of more builds. The security jobs join the same
  gate ([ci-cd/security-example.md](../ci-cd/security-example.md)), so `ci-ok` stays the one
  required check.

  The rule is good because one required name, set only by GitHub Actions, guards `main`: a new job
  joins the gate in the workflow file, and nobody can mark the check green by hand.
- When the repository runs CodeQL, also add the ruleset's code scanning rule to the `rules` list.
  CodeQL's job stays green when it finds an alert, so this rule is what makes an alert block a
  merge; why, and the plan it needs on a private repository:
  [ci-cd/pipeline-security.md](../ci-cd/pipeline-security.md) section 7. This JSON departs from
  [readability.md](../readability/readability.md) section 4, which asks for the reason at the
  line, because JSON has no comments; the reasons are in the table after it. The cost: a copy of
  the JSON alone loses these reasons.

  ```json
  {
    "type": "code_scanning",
    "parameters": {
      "code_scanning_tools": [
        { "tool": "CodeQL", "alerts_threshold": "errors", "security_alerts_threshold": "high_or_higher" }
      ]
    }
  }
  ```

  | Part | What it does | Why |
  |---|---|---|
  | `"type": "code_scanning"` | A merge waits until each named tool has results for the pull request, and is blocked when a tool reports an alert at or above a threshold ([GitHub Docs](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets)). | It works apart from the required status checks ([GitHub Docs](https://docs.github.com/en/code-security/concepts/code-scanning/merge-protection)), so `ci-ok` being green does not stand in for it. |
  | `code_scanning_tools` | The tools that must report results; required ([GitHub Docs](https://docs.github.com/en/rest/repos/rules)). | One entry per tool the repository runs; here CodeQL is the only one. |
  | `"tool": "CodeQL"` | The tool's name as code scanning shows it ([GitHub Docs](https://docs.github.com/en/code-security/how-tos/find-and-fix-code-vulnerabilities/manage-your-configuration/set-merge-protection)). | It names the tool of the `code` job in [ci-cd/security-example.md](../ci-cd/security-example.md). |
  | `"alerts_threshold": "errors"` | A non-security alert of severity error blocks; warnings and notes do not. The values are `none`, `errors`, `errors_and_warnings` and `all` ([GitHub Docs](https://docs.github.com/en/rest/repos/rules)). | Set `none` when only security alerts should block. |
  | `"security_alerts_threshold": "high_or_higher"` | A critical or high security alert blocks; medium and low do not. The values are `none`, `critical`, `high_or_higher`, `medium_or_higher` and `all` ([GitHub Docs](https://docs.github.com/en/rest/repos/rules)). | It matches the written policy of the image scan, which fails on critical and high findings that have a fix ([docker/images.md](../docker/images.md) section 10). Set the level your own written policy names. |

  The rule has two limits: it does not apply to merge queue groups, and it blocks only when all
  the lines of an alert are in the pull request's diff
  ([GitHub Docs](https://docs.github.com/en/code-security/concepts/code-scanning/merge-protection)).
  An alert on a line the pull request did not change, or one CodeQL raises on `main`, blocks
  nothing.

  The rule is good because it is the one setting that lets a CodeQL alert block a merge, and it
  names the tool and both thresholds, so a reader sees which alerts block and which do not.

## Release tags

When a version tag starts the production deploy ([ci-cd/delivery.md](../ci-cd/delivery.md)
section 4), creating the tag is the release decision, so only the go or no-go decider of
[release.md](../project-management/release.md) section 3 and their backup may create one, and
nobody may move or delete one. That takes two tag rulesets, because a bypass actor of a ruleset
skips all of its rules, and the rules of several rulesets apply together.

The two JSON files below depart from [readability.md](../readability/readability.md) section 4,
which asks for the reason at the line, because JSON has no comments; the reasons are in the table
after them. The cost: a copy of the JSON alone loses these reasons.

The first lets only the go or no-go decider and their backup create a `v*` tag:

```json
{
  "name": "release-tags-create",
  "target": "tag",
  "enforcement": "active",
  "bypass_actors": [{ "actor_id": 0, "actor_type": "Team", "bypass_mode": "always" }],
  "conditions": { "ref_name": { "include": ["refs/tags/v*"], "exclude": [] } },
  "rules": [{ "type": "creation" }]
}
```

The second stops everyone, the decider included, from moving or deleting a `v*` tag:

```json
{
  "name": "release-tags-fixed",
  "target": "tag",
  "enforcement": "active",
  "bypass_actors": [],
  "conditions": { "ref_name": { "include": ["refs/tags/v*"], "exclude": [] } },
  "rules": [{ "type": "update" }, { "type": "deletion" }]
}
```

| Part | What it does | Why |
|---|---|---|
| `"target": "tag"` | the rules apply to tags | branch rulesets do not cover tags |
| `"include": ["refs/tags/v*"]` | the version tags only | other tags stay free |
| `creation` with the team as bypass actor | only members of that team can create a `v*` tag | creating the tag starts the production deploy; the team holds the go or no-go decider of [release.md](../project-management/release.md) section 3 and their backup, and for each release the named decider creates the tag. Put the team's ID in `actor_id`: `gh api orgs/{org}/teams/{team_slug} --jq .id` prints it |
| `update`, `deletion` with no bypass actor | nobody can move or delete a `v*` tag | a released version never changes ([release.md](../project-management/release.md) section 4), and the deploy finds the image by the tagged commit |

Apply each one as the section "Apply it" says, with its own file. Steps 7 to 9 of "Apply it" check
the branch ruleset only: GitHub's rules endpoint "Returns all active rules that apply to the
specified branch", and the same page lists no endpoint for the rules of a tag
([GitHub Docs](https://docs.github.com/en/rest/repos/rules)). To check the tag rulesets, run
`gh api repos/{owner}/{repo}/rulesets --jq '.[] | select(.target=="tag") | "\(.id) \(.name) \(.enforcement)"'`
and make sure the output shows `release-tags-create` and `release-tags-fixed`, each `active`. If
one is missing, a person with write access can create or move a `v*` tag.

These rulesets are good because creating a release tag stays with the person who decides the
release, and once created, no one, that person included, can point the tag at other code.

## Change it later

Step 5 of "Apply it" makes a new ruleset. It does not change the ruleset that you have. To change
that ruleset, use its ID.

First do step 1 of "Apply it", in the folder that holds `ruleset.json`.

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
can then push to these branches. The same people and apps can also delete `main` when it is not
the default branch.

- A history rewrite in the exception path of [git.md](git.md) section 6. A person does the
  rewrite, never an agent.
- A rename of the default branch, or a change to another default branch. GitHub's rules page
  says that an admin cannot do either while force pushes are blocked and nobody can bypass the
  ruleset
  ([GitHub Docs](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets)).

---

This ruleset is good because each of its three rules applies a [git.md](git.md) rule, and the
ruleset adds no rule that git.md does not have. The two rules that every repository keeps come
first. The empty bypass list makes the rules hold for every push, from admins and agents too.
Only a person or a token that can edit rulesets can turn the rules off. The section "What to
change for your repository" names the changes that most repositories make, so a team makes each
change on purpose.
