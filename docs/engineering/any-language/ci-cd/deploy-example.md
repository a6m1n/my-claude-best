# Example: the deploy workflows of a Python and React monorepo on AWS

A worked example for [delivery.md](delivery.md). The monorepo of [ci-example.md](ci-example.md)
deploys its API image to Amazon ECS (Elastic Container Service) on Fargate (AWS runs the
machines) and its React bundle to S3 behind CloudFront. A
merge to `main` runs CI again, builds the image that ships once, takes the frontend bundle from
CI, and deploys them to staging; a version tag such as `v1.4.2`, created by the go or no-go
decider of [release.md](../project-management/release.md) section 3, deploys the same artifacts
to production. No cloud key is stored in GitHub: every AWS call uses OIDC.

What the example assumes exists, set up outside these files: an ECR (Elastic Container Registry)
repository with immutable tags ([images.md](../docker/images.md) section 8) and continuous
enhanced scanning, whose findings a named person reads, so the digest each environment runs is
scanned again when a vulnerability that affects it reaches Amazon Inspector's database
([pipeline-security.md](pipeline-security.md) section 7); one ECS cluster and service per environment,
with the deployment circuit breaker and CloudWatch deployment alarms turned on, both with rollback
([delivery.md](delivery.md) section 7); one S3 bucket for released bundles and one site bucket per
environment; no lifecycle rule on the ECR repository or the releases bucket that expires an image
or a bundle a `v*` release uses, or the way back to that release finds nothing to deploy; one
CloudFront distribution per environment, whose `/api/*` behaviour goes to the service's load
balancer with caching off, and whose default behaviour goes to the site bucket, with a minimum TTL
of 0 so `index.html` is never served stale ([delivery.md](delivery.md) sections 3 and 6). The
CloudFront and load balancer setup is not shown; section 5 gives the order of the first setup.
To keep these resources as code, with a plan on each pull request and an apply on `main`, see
[delivery.md](delivery.md) section 9. The end-to-end tests that run against staging after its
deploy ([delivery.md](delivery.md) section 7) are left out of this example.

Actions are pinned as in [ci-example.md](ci-example.md), to the commit `git ls-remote` printed on
2026-10-18 for the release in each comment, and on 2026-10-19 for `actions/setup-node`. Trivy's
`version:` in `publish-api` has no mover in Renovate's config: the pipeline owners move it by hand,
with the same pin in ci-example.md's `image` job, when Trivy's release notes name a security fix
and at each quarterly review. The same holds for two pins in `run:` steps, read on 2026-10-19: the
ZAP image digest in `dast-staging` and the CSP Evaluator tarball's checksum in `headers-staging`.

**Navigation**

- [1. deploy.yml: what a merge and a tag start](#1-deployyml-what-a-merge-and-a-tag-start)
- [2. What deploy.yml does](#2-what-deployyml-does)
- [3. deploy-to.yml: the same steps for every environment](#3-deploy-toyml-the-same-steps-for-every-environment)
- [4. What deploy-to.yml does](#4-what-deploy-toyml-does)
- [5. The GitHub settings](#5-the-github-settings)
- [6. The AWS side: roles and the task definition](#6-the-aws-side-roles-and-the-task-definition)
- [7. Sources](#7-sources)

## 1. deploy.yml: what a merge and a tag start

`.github/workflows/deploy.yml`

```yaml
name: deploy

on:
  push:
    branches: [main]  # staging
    tags: ["v*"]      # production
  # "Run workflow" on an earlier version's tag deploys that version again: the way back.
  # With staging chosen, it rehearses the way back there first (delivery.md section 7).
  workflow_dispatch:
    inputs:
      environment:
        type: choice
        options: [staging, production]
        default: staging  # a rehearsal, unless the person picks production
      migrate:
        description: Run the migration. Turn it on for a retry of the newest release or a run on main; leave it off to go back to an earlier tag.
        type: boolean
        default: false  # the way back: the database already holds the newer schema (delivery.md section 7)

permissions: {}  # nothing by default; each job asks for what it uses (pipeline-security.md section 3)

jobs:
  ci:
    # Every check again, the security jobs included, on the merged code, before anything is built
    # (pipeline.md section 5).
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    uses: ./.github/workflows/ci.yml
    secrets:
      DOCKERHUB_TOKEN: ${{ secrets.DOCKERHUB_TOKEN }}  # the one secret CI uses, by name; inherit would pass every secret
    permissions:
      # What the jobs of ci.yml and security.yml ask for; a called job cannot get more.
      contents: read
      pull-requests: read
      security-events: write
      actions: read

  publish-api:
    # A departure from images.md section 10, one job from lint to push: only the job on main holds
    # the AWS role. The cost: two builds per merge, and ci.yml's image tests ran on the first build.
    needs: ci
    runs-on: ubuntu-24.04  # a version label, never ubuntu-latest: the OS changes only when this line does (pipeline.md section 9)
    timeout-minutes: 20  # a hung job stops here, not at GitHub's 360 minutes (pipeline.md section 8)
    permissions:
      contents: read
      id-token: write  # OIDC login to AWS (delivery.md section 5)
    env:
      # Without the secret the login below is skipped, and the base image is pulled anonymously.
      DOCKERHUB_TOKEN: ${{ secrets.DOCKERHUB_TOKEN }}
    steps:
      # Every action by full commit SHA, the release in the comment: a tag can be moved (pipeline-security.md section 4).
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1  # v7.0.1
        with:
          persist-credentials: false  # the token is not left on the runner for the steps after this one (pipeline-security.md section 3)
      - uses: aws-actions/configure-aws-credentials@e1253824e5c10ff9df46874f81ed3ec929e19cfd  # v6.3.0
        with:
          role-to-assume: ${{ vars.AWS_PUBLISH_API_ROLE_ARN }}  # may push and tag images; nothing in S3, deploys nothing
          aws-region: ${{ vars.AWS_REGION }}
      - uses: aws-actions/amazon-ecr-login@03f1aad4c6c7ffd436567f42f9384779290529bd  # v2.1.7
      # The rebuild pulls the base image from Docker Hub; log in before it (images.md section 10).
      - uses: docker/login-action@dbcb813823bdd20940b903addbd779551569679f  # v4.6.0
        if: env.DOCKERHUB_TOKEN != ''  # if: may read env, never secrets
        with:
          username: ${{ vars.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}
      - uses: docker/setup-buildx-action@f87e5991a6d7451dcb8d9637bfbc97413f497069  # v4.4.1
      - id: meta
        uses: docker/metadata-action@dc802804100637a589fabce1cb79ff13a1411302  # v6.2.0
        with:
          images: ${{ vars.ECR_IMAGE }}  # for the OCI labels (images.md section 8); the push below names no tag
      # ci.yml's image job built, tested and scanned this image as a check; this rebuild from its
      # cache is the artifact that ships (delivery.md section 3).
      - id: build
        uses: docker/build-push-action@c3c9e263c25d99ce0380d002d59b67737d91b0dc  # v7.4.0
        with:
          context: backend
          # Pushed by digest with no tag: an image that fails the scan below has no name a deploy
          # finds, and a re-run pushes again without meeting an immutable tag (delivery.md section 3).
          outputs: type=image,name=${{ vars.ECR_IMAGE }},push-by-digest=true,name-canonical=true,push=true
          labels: ${{ steps.meta.outputs.labels }}
          # An SBOM and max-level provenance go with the image (images.md section 9).
          sbom: true
          provenance: mode=max
          cache-from: type=gha,scope=acme-api
      # Scan the pushed digest, so the bytes that ship are the bytes scanned (delivery.md section 3).
      # A finding fails this job before the tag below exists, so no deploy can find this image.
      - uses: aquasecurity/trivy-action@ed142fd0673e97e23eac54620cfb913e5ce36c25  # v0.36.0
        with:
          image-ref: ${{ vars.ECR_IMAGE }}@${{ steps.build.outputs.digest }}
          version: v0.76.0  # the Trivy release and the policy of ci.yml's image job
          severity: CRITICAL,HIGH
          ignore-unfixed: true
          exit-code: "1"
      # sha-<full commit> means "scanned": deploy-to.yml finds an image only by this tag.
      # A departure from images.md section 8, which also tags the version: the version lives on
      # the git tag, created after this build. The cost: the registry shows only commit tags.
      - name: Tag the scanned digest
        env:
          REPOSITORY: ${{ vars.ECR_REPOSITORY }}
          DIGEST: ${{ steps.build.outputs.digest }}
        run: |
          # ECR's retag: read the manifest and write it back under the new tag, with no pull or push.
          manifest=$(aws ecr batch-get-image --repository-name "$REPOSITORY" \
            --image-ids imageDigest="$DIGEST" --query 'images[0].imageManifest' --output text)
          media_type=$(aws ecr batch-get-image --repository-name "$REPOSITORY" \
            --image-ids imageDigest="$DIGEST" --query 'images[0].imageManifestMediaType' --output text)
          # --image-digest makes ECR refuse a manifest whose digest is not the one scanned.
          aws ecr put-image --repository-name "$REPOSITORY" --image-tag "sha-$GITHUB_SHA" \
            --image-manifest "$manifest" --image-manifest-media-type "$media_type" \
            --image-digest "$DIGEST" > /dev/null

  publish-web:
    needs: ci
    runs-on: ubuntu-24.04
    timeout-minutes: 10
    permissions:
      id-token: write
    steps:
      - uses: actions/download-artifact@9000827ccba6bdab643e8b6fd33ac0654aef8333  # v8.0.2
        with:
          name: web-dist  # the bundle ci.yml's frontend job built in this run
          path: dist
      - uses: aws-actions/configure-aws-credentials@e1253824e5c10ff9df46874f81ed3ec929e19cfd  # v6.3.0
        with:
          # A role of its own, one per artifact: it writes the releases bucket and nothing in ECR (delivery.md section 5).
          role-to-assume: ${{ vars.AWS_PUBLISH_WEB_ROLE_ARN }}
          aws-region: ${{ vars.AWS_REGION }}
      - name: Store the bundle under its commit
        env:
          RELEASES: ${{ vars.WEB_RELEASES_BUCKET }}
        run: |
          # Vite hashes the names in assets/ only, so only they may be kept for a year; index.html and
          # the files Vite copies from public/ keep their names and must be fetched again.
          aws s3 sync dist/assets "s3://$RELEASES/$GITHUB_SHA/assets/" --no-progress \
            --cache-control "public, max-age=31536000, immutable"
          aws s3 sync dist "s3://$RELEASES/$GITHUB_SHA/" --exclude "assets/*" --no-progress \
            --cache-control "no-cache"

  staging:
    needs: [publish-api, publish-web]
    # A merge deploys what it just published; "Run workflow" with staging redeploys the chosen version.
    if: ${{ !cancelled() && ((github.event_name == 'push' && needs.publish-api.result == 'success' && needs.publish-web.result == 'success') || (github.event_name == 'workflow_dispatch' && inputs.environment == 'staging')) }}
    uses: ./.github/workflows/deploy-to.yml
    with:
      environment: staging
      commit: ${{ github.sha }}
      migrate: ${{ github.event_name != 'workflow_dispatch' || inputs.migrate }}  # a manual run migrates only with migrate on
    permissions:
      contents: read
      id-token: write

  dast-staging:
    # A passive scan of the version staging now runs; it sends no attacks (pipeline-security.md section 7).
    # A job of its own, so the scanner never runs next to the deploy role.
    needs: staging
    # Whenever staging succeeded, also on a manual run, where the jobs before staging were skipped.
    if: ${{ !cancelled() && needs.staging.result == 'success' }}
    runs-on: ubuntu-24.04
    timeout-minutes: 15
    permissions:
      contents: read  # the rules file
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1  # v7.0.1
        with:
          persist-credentials: false
      - name: ZAP baseline scan
        env:
          TARGET: ${{ needs.staging.outputs.base-url }}
        run: |
          # ZAP runs as its own user and writes its report to /zap/wrk, so it gets a folder it can write.
          mkdir zap && cp .zap-rules.tsv zap/rules.tsv && chmod a+w zap
          # By digest: the stable tag is rebuilt every month (images.md section 4). This is 2.17.0.
          # -I: a WARN rule only reports; a rule set to FAIL in rules.tsv fails the job.
          docker run --rm -v "$PWD/zap:/zap/wrk/:rw" \
            ghcr.io/zaproxy/zaproxy@sha256:5ccfff9a411743ab2615136a2edd7416bec9ce41572fa94e935df38c14adb2b6 \
            zap-baseline.py -t "$TARGET" -c rules.tsv -I -r report.html
      - uses: actions/upload-artifact@cf430e030ddbb5b0abf93d22962f4752f3646cd9  # v7.0.2
        if: ${{ !cancelled() }}  # the report is wanted most when the scan failed
        with:
          name: zap-report
          path: zap/report.html
          retention-days: 14  # long enough to read a failed scan; every reader of the repository can download it

  headers-staging:
    # The header scans react/security/security.md section 14 asks for, on the version staging now runs.
    needs: staging
    if: ${{ !cancelled() && needs.staging.result == 'success' }}  # as in dast-staging
    runs-on: ubuntu-24.04
    timeout-minutes: 10
    permissions:
      contents: read  # frontend/.node-version
    env:
      BASE_URL: ${{ needs.staging.outputs.base-url }}
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1  # v7.0.1
        with:
          persist-credentials: false
      - uses: actions/setup-node@949feb2413d6458794dcd2491c4babbbce0c15c1  # v7.1.0
        with:
          node-version-file: frontend/.node-version  # the Node the application pins (pipeline.md section 9)
          package-manager-cache: false  # this job installs nothing
      - name: CSP Evaluator over the policy staging sends
        run: |
          # One tarball pinned by its checksum, as ci-example.md pins gitleaks: no package manager runs,
          # so no install script can run. A departure from security.md section 10, which installs from the
          # lockfile: the job only reads a header. The cost: Renovate does not move it; the pipeline owners do.
          curl -sSfL -o csp_evaluator.tgz https://registry.npmjs.org/csp_evaluator/-/csp_evaluator-1.1.8.tgz
          echo "2b4f2a30ed67a39908708c05ba559accbad0b5a6c0fa29f1761a641a342fd904  csp_evaluator.tgz" | sha256sum --check
          mkdir csp_evaluator && tar -xzf csp_evaluator.tgz -C csp_evaluator --strip-components=1
          POLICY=$(curl -sSfI "$BASE_URL/" | tr -d '\r' | sed -n 's/^content-security-policy: //Ip')
          export POLICY
          # Fails on a HIGH or SYNTAX finding, the two most severe levels; the others are printed only.
          node -e '
            const { CspParser } = require("./csp_evaluator/dist/parser.js");
            const { CspEvaluator } = require("./csp_evaluator/dist/evaluator.js");
            const { Severity } = require("./csp_evaluator/dist/finding.js");
            if (!process.env.POLICY) { console.error("No Content-Security-Policy header"); process.exit(1); }
            const findings = new CspEvaluator(new CspParser(process.env.POLICY).csp).evaluate();
            for (const f of findings) console.log(`${Severity[f.severity]} ${f.directive}: ${f.description}`);
            process.exit(findings.some((f) => f.severity <= Severity.SYNTAX) ? 1 : 0);
          '
      - name: HTTP Observatory over staging
        run: |
          host=${BASE_URL#https://}
          host=${host%%/*}
          # MDN's public API scans from outside, so staging must answer from the internet. It scans a
          # host once a minute; a second request inside that minute gets the earlier result.
          result=$(curl -sS --fail-with-body -X POST "https://observatory-api.mdn.mozilla.net/api/v2/scan?host=$host")
          echo "$result" | jq '{grade, score, tests_failed, details_url}'
          grade=$(echo "$result" | jq -r '.grade')
          # The bar this example sets; write down your own (pipeline-security.md section 7).
          case "$grade" in
            A+|A) ;;
            *) echo "::error::HTTP Observatory grade $grade is below A."; exit 1 ;;
          esac

  tag-is-on-main:
    # Proves only that the tagged commit is on main; that it ran in staging is the decider's check
    # (release.md section 3).
    if: github.ref_type == 'tag'
    runs-on: ubuntu-24.04
    timeout-minutes: 5
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1  # v7.0.1
        with:
          fetch-depth: 0  # main's history, for the check below
          persist-credentials: false
      - run: git merge-base --is-ancestor "$GITHUB_SHA" origin/main

  security:
    # A version tag runs the security jobs again on the tagged commit, so a new advisory against the
    # workflows or the lockfiles stops production; CodeQL only records its alerts here, and the image
    # is not scanned again (pipeline-security.md section 7). A redeploy skips them.
    if: github.event_name == 'push' && github.ref_type == 'tag'
    uses: ./.github/workflows/security.yml
    permissions:
      contents: read
      security-events: write  # CodeQL uploads its results
      actions: read  # the workflows job of security.yml asks for it

  production:
    needs: [tag-is-on-main, security]
    # A tag push needs the security jobs; "Run workflow" with production, the way back, does not wait for them.
    if: ${{ !cancelled() && needs.tag-is-on-main.result == 'success' && ((github.event_name == 'push' && needs.security.result == 'success') || (github.event_name == 'workflow_dispatch' && inputs.environment == 'production')) }}
    uses: ./.github/workflows/deploy-to.yml
    with:
      environment: production
      commit: ${{ github.sha }}
      migrate: ${{ github.event_name != 'workflow_dispatch' || inputs.migrate }}  # a manual run migrates only with migrate on
    permissions:
      contents: read
      id-token: write

  production-needs-a-tag:
    # Without this job, "Run workflow" from a branch with production chosen skips every job and looks green.
    if: github.event_name == 'workflow_dispatch' && inputs.environment == 'production' && github.ref_type != 'tag'
    runs-on: ubuntu-24.04
    timeout-minutes: 5
    permissions: {}
    steps:
      - run: |
          echo "Run this workflow from the release tag: production takes only a version tag." >&2
          exit 1

  notify-failure:
    # The last job: tells the team's channel when a job of this run failed or was cancelled
    # (delivery.md section 7).
    # Not production-needs-a-tag: the person who started that run sees its error on the page they are on.
    needs: [ci, publish-api, publish-web, staging, dast-staging, headers-staging, tag-is-on-main, security, production]
    # A job that hits its timeout-minutes is cancelled, not failed, so failure() alone misses it;
    # always(), not !cancelled(), so a run a person cancels is reported too (pipeline.md section 10).
    if: ${{ always() && (contains(needs.*.result, 'failure') || contains(needs.*.result, 'cancelled')) }}
    runs-on: ubuntu-24.04
    timeout-minutes: 5
    permissions: {}
    steps:
      - name: Post to the team's channel
        env:
          WEBHOOK_URL: ${{ secrets.DEPLOY_ALERT_WEBHOOK_URL }}  # the URL itself is the credential
          REF: ${{ github.ref_name }}
          RUN_URL: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}
        run: |
          if [ -z "$WEBHOOK_URL" ]; then
            echo "::warning::The secret DEPLOY_ALERT_WEBHOOK_URL is not set, so no channel was told."
            exit 0
          fi
          # jq writes the JSON, so a ref name cannot break out of the text (pipeline-security.md section 5).
          jq -n --arg text "The deploy run for $REF failed: $RUN_URL" '{text: $text}' \
            | curl -sS --fail-with-body -X POST -H 'Content-type: application/json' --data @- "$WEBHOOK_URL"
```

## 2. What deploy.yml does

| Part | Why |
|---|---|
| `push` to `main`, `push` of `v*` tags, `workflow_dispatch` | a merge deploys to staging; a version tag deploys to production; a manual run on an earlier tag deploys that version again ([delivery.md](delivery.md) sections 2 and 7) |
| `workflow_dispatch` with the input `environment` | "Run workflow" on a tag redeploys that version where the person chooses: `staging` rehearses the way back, `production` takes it ([delivery.md](delivery.md) section 7). The run uses `deploy.yml` and `deploy-to.yml` as they were at that tag, so a later fix to the deploy steps does not reach it. Where `production` has no required reviewers, anyone with write access can start such a run and put any earlier version in production ([delivery.md](delivery.md) section 7) |
| `ci` with `uses: ./.github/workflows/ci.yml` | every check of [ci-example.md](ci-example.md) runs on the merged code, the security jobs included, and the jobs after it start only when all of it is green. `workflow_call` with `needs` keeps the order in one run, where `workflow_run` would start whatever the result ([delivery.md](delivery.md) section 14) |
| `secrets: DOCKERHUB_TOKEN` on the call | a called workflow gets only the secrets its caller passes [9]; passing the one secret CI uses by name, not `secrets: inherit`, keeps every other secret out of CI ([pipeline.md](pipeline.md) section 3) |
| the permissions on the call | a called workflow's jobs can keep or lower the caller's permissions, never raise them ([pipeline.md](pipeline.md) section 4), so the call grants what the jobs of `ci.yml` and `security.yml` ask for: `pull-requests: read` for `changes`, `security-events: write` and `actions: read` for the security jobs |
| `publish-api` | pushes the image to ECR by digest, with no tag, with an SBOM and provenance ([images.md](../docker/images.md) section 9), and tags that digest `sha-<commit>` only after the scan passes. A departure from [images.md](../docker/images.md) section 10, which puts lint, build, test, scan and push in one job: here `ci.yml`'s image job builds, tests and scans the image as a check, and this job builds it again from the same cache, pushes it, scans the pushed digest and then tags it, because only the job on `main` should hold the AWS role ([pipeline-security.md](pipeline-security.md) section 3). The cost: two builds per merge, and the image tests of `ci.yml` ran on the first build, not on the pushed bytes; [docker/ci-example.md](../docker/ci-example.md) says why the two builds differ. A second departure, from [images.md](../docker/images.md) section 8: the image gets no version tag, because the version lives on the git tag, created after this build; the cost is that the registry shows only commit tags. It logs in to Docker Hub before the build, as section 10 asks |
| `outputs:` with `push-by-digest=true`, and no `tags:` | the image goes to the registry under its digest alone [14]; why it gets its tag only later: [delivery.md](delivery.md) section 3 |
| the Trivy step after the push, with `id: build` on the build | scans `<ECR_IMAGE>@<digest>`, the digest the build pushed, with the pin, the policy and the root `.trivyignore` of `ci.yml`'s image job, so the digest staging and production run is the digest scanned. A finding fails this job before the digest has its `sha-` tag, so `deploy-to.yml`, which finds an image only by that tag, cannot deploy it, and `staging`, which needs this job, never runs. Trivy pulls the image from ECR with the role this job assumed [13], so the publish-api role also holds `ecr:GetDownloadUrlForLayer` (section 6). The scanner runs with that ECR push role in reach, as [images.md](../docker/images.md) section 10 accepts for a scanner in the image job. The cost: a compromised action in this job could push and tag an unscanned image itself; the SHA pins are what guard it ([pipeline-security.md](pipeline-security.md) section 4). The role writes nothing in S3 |
| `Tag the scanned digest`, after the scan | adds `sha-<commit>` to the scanned digest with ECR's retag: `batch-get-image` reads the manifest, `put-image` writes it back under the new tag, with no pull or push [15]. `--image-manifest-media-type` passes the media type `batch-get-image` reports for the manifest [17], and `--image-digest` makes ECR refuse a manifest whose digest does not match [16]. What the tag means: [delivery.md](delivery.md) section 3. The publish-api role already holds `ecr:BatchGetImage` and `ecr:PutImage` (section 6) |
| ECR, not GitHub's registry | ECS pulls from a registry outside AWS only with a username and password stored in Secrets Manager [1]; from ECR it pulls with its own role, and ECR offers the immutable tags [images.md](../docker/images.md) section 8 asks for |
| `publish-web` | copies the bundle `ci.yml` built in this run to `s3://<releases>/<commit>/`, where it stays for later deploys and rollbacks; GitHub deletes workflow artifacts after 90 days by default ([delivery.md](delivery.md) section 3) |
| the two cache headers | Vite puts a hash in the names of the files in `assets/`, so they are cached for a year; it copies the files of `public/` "as-is" [10], so they and `index.html` get `no-cache`. A deploy copies the objects with their headers ([delivery.md](delivery.md) section 6) |
| `staging` and `production` with `uses: ./.github/workflows/deploy-to.yml` | one set of deploy steps for every environment, called with different inputs ([delivery.md](delivery.md) section 6) |
| `migrate:` on the two calls, and the `migrate` input | a push migrates. "Run workflow" migrates only when the person turns `migrate` on: on for a retry of the newest release or a run on `main`, whose code may need a migration the database does not have yet; off for a redeploy of an earlier version, because the database already holds the newer schema, which the older code still reads ([delivery.md](delivery.md) section 7) |
| `dast-staging` and `headers-staging`, after `staging` | the scans that need a running site, on the version staging now runs ([delivery.md](delivery.md) section 7). Each is a job of its own with only `contents: read`, so no scanner runs next to the deploy role ([pipeline-security.md](pipeline-security.md) section 7). They run after every staging deploy, a rehearsal of the way back included, and only when it succeeded. A failure turns the run red and `notify-failure` tells the team; it does not undo the deploy, because production comes from a version tag in another run |
| `needs.staging.outputs.base-url` | the staging address is an output of `deploy-to.yml`, mapped from its job's output [9], so it is the value of the environment just deployed (section 4). The scans need no copy of the value and name no environment, because naming one creates a deployment record ([delivery.md](delivery.md) section 4) |
| `zap-baseline.py` with `-c rules.tsv -I` | ZAP's baseline scan spiders the site for a minute, "doesn't perform any actual 'attacks'", and is "intended to be ideal to run in a CI/CD environment, even against production sites" [25]. Every alert is a WARN unless the rules file sets it to FAIL or IGNORE; `-I` keeps a WARN from failing the job, and the exit code is 1 when a FAIL rule matches, 3 on any other failure [25]. The rules file sets to FAIL the passive rules for the headers [security.md](../../react/security/security.md) section 5 asks for [29], [30], [31], [32] |
| the ZAP image by digest, and `chmod a+w zap` | the `stable` tag "is also regenerated monthly" [26], so the digest is what keeps the scan the same between two runs ([images.md](../docker/images.md) section 4); `--rm` leaves no container behind. ZAP reads the rules file and writes the report in the folder mounted at `/zap/wrk` [26], and runs as its own user, so the folder must be writable for it; ZAP's own action does the same `chmod a+w` [28] |
| `upload-artifact` with `if: ${{ !cancelled() }}` and `retention-days: 14` | the report is kept when the scan failed, when it is read most; GitHub's docs advise `!cancelled()` over `always()` for a step that must run after a failure [37]. Artifacts are kept 90 days unless `retention-days` is shorter [40]; two weeks covers reading a failed scan. Anyone with read access can download the report, so it holds only what any visitor of staging can see ([pipeline-security.md](pipeline-security.md) section 9) |
| the CSP Evaluator step | runs Google's CSP Evaluator over the policy staging sends, as [security.md](../../react/security/security.md) section 14 asks; Google offers it "only for the convenience of developers" with "no guarantees" [34]. The policy of this example: a finding of the two most severe levels, `HIGH` and `SYNTAX`, fails the job, and a missing header fails it too. The SHA-256 in the step was computed on 2026-10-19 from the tarball whose sha512 matches the registry's `integrity` entry for 1.1.8 [35]. A departure from [security.md](../../react/security/security.md) section 10, which installs packages through the lockfile: one package with no dependencies and no install script, pinned by checksum, keeps the frontend's whole install out of a job that only reads a header. The cost: Renovate does not move it, so the pipeline owners do, by hand |
| `actions/setup-node` with `node-version-file` | the Node version comes from the file the application pins, as [pipeline.md](pipeline.md) section 9 asks; `package-manager-cache: false`, which the action's README recommends where caching is not needed [36] |
| the HTTP Observatory step | MDN's HTTP Observatory checks the headers the deployed site sends, through its JSON API "For integration in CI pipelines"; the API scans a host once a minute and returns the earlier result inside that minute [33]. It scans from MDN's side, so staging must answer from the internet; a staging site only your network reaches needs the scanner's command-line tool instead [33]. The bar, grade A or better, is this example's written policy ([pipeline-security.md](pipeline-security.md) section 7); `jq` comes with the runner image [41] |
| `tag-is-on-main` | a tag on a commit that is not on `main` fails here. The job proves only that; that the commit ran in staging is the decider's check ([release.md](../project-management/release.md) section 3) |
| `security` on a tag push | the security jobs run again on the tagged commit, and `production` needs them, so a new advisory against the workflows or the lockfiles stops the release; CodeQL's job stays green on an alert, so it records alerts here and stops nothing; the image itself was scanned when it was pushed, and is not scanned again here ([pipeline-security.md](pipeline-security.md) section 7). A redeploy of an earlier version skips them, so the way back is not held up by such an advisory |
| `github.sha` as `commit` | on a tag push and on a manual run from a tag, it is the tagged commit; `deploy-to.yml` finds that commit's image and bundle, so nothing is built for production |
| `production-needs-a-tag` | "Run workflow" from a branch with `production` chosen fails here with "Run this workflow from the release tag". Without it, every job of that run is skipped and the run looks green, so the person may think the rollback ran |
| `notify-failure`, the last job, with `always()` and the results of the jobs it needs | a job that reaches its `timeout-minutes` is one GitHub "automatically cancels" [18], and a job's result in the `needs` context is one of `success`, `failure`, `cancelled` or `skipped` [38], so the job runs when any job it needs ended `failure` or `cancelled`: `failure()`, which "returns true if any ancestor job fails" [37], would miss a deploy that timed out. `always()` keeps the default `success()` check from skipping the job [37]. One job at the end covers a red CI, a failed publish, a failed or timed-out deploy and a red scan ([delivery.md](delivery.md) section 7). It sits in this workflow, not in a `workflow_run` workflow, which would start whatever the result and with secrets ([delivery.md](delivery.md) section 7) |
| `DEPLOY_ALERT_WEBHOOK_URL` as a repository secret, read through `env:` | a chat's incoming webhook takes a JSON body with a `text` field, and Slack warns: "Your webhook URL contains a secret" [39]. The job names no environment, so the URL is a repository secret ([pipeline-security.md](pipeline-security.md) section 6). Without it the job writes a warning on the run and posts nothing, so a missing secret shows instead of failing in silence |
| `jq -n --arg` | the ref name and the run's address go into the JSON as data; pasted into the string, a tag name with a quote in it would break the body ([pipeline-security.md](pipeline-security.md) section 5) |

Which jobs run on which event:

| Event | Jobs that run | Jobs skipped |
|---|---|---|
| push to `main` | `ci` (the security jobs included), `publish-api`, `publish-web`, `staging`, `dast-staging`, `headers-staging` | `tag-is-on-main`, `security`, `production`, `production-needs-a-tag` |
| push of a `v*` tag | `tag-is-on-main`, `security`, `production` | `ci`, `publish-api`, `publish-web`, `staging`, `dast-staging`, `headers-staging`, `production-needs-a-tag` |
| "Run workflow" on a `v*` tag, `production` chosen | `tag-is-on-main`, `production`, which migrates only with `migrate` on | `ci`, `publish-api`, `publish-web`, `security`, `staging`, `dast-staging`, `headers-staging`, `production-needs-a-tag` |
| "Run workflow" on a `v*` tag, `staging` chosen | `tag-is-on-main`, `staging`, which migrates only with `migrate` on, then `dast-staging` and `headers-staging` | `ci`, `publish-api`, `publish-web`, `security`, `production`, `production-needs-a-tag` |
| "Run workflow" on `main`, `staging` chosen | `staging`, for `main`'s last commit, which migrates only with `migrate` on, then `dast-staging` and `headers-staging` | every other job |
| "Run workflow" on `main`, `production` chosen | `production-needs-a-tag`, which fails with "Run this workflow from the release tag": production takes only a version tag | every other job |

`notify-failure` is in none of the rows: on any event it runs only when a job it needs has failed
or was cancelled, and it is skipped otherwise.

`.zap-rules.tsv`, the rules file `dast-staging` reads, at the root next to `.trivyignore`, where
[file-structure.md](../file-structure/file-structure.md) section 9 puts a scanner's config. It
decides what fails the scan, so list it in `CODEOWNERS` with the other scanner files
([pipeline-security.md](pipeline-security.md) section 8). ZAP reads three fields per line,
separated by tabs, and refuses a line with fewer [27]; a rule the file does not name stays a WARN:

```text
# zap-baseline rules: FAIL fails the job; every rule not listed here stays a WARN.
# The headers react/security/security.md section 5 asks for. Fields are separated by tabs.
10020	FAIL	(Anti-clickjacking Header)
10021	FAIL	(X-Content-Type-Options Header Missing)
10035	FAIL	(Strict-Transport-Security Header)
10038	FAIL	(Content Security Policy (CSP) Header Not Set)
```

It is good because a missing header that the security practice asks for fails the scan by name,
while the other alerts stay visible as warnings and stop nothing.

It is good because production runs the image and the bundle published once from a commit on
`main`, found by that commit, and only an image whose pushed digest passed the scan
([delivery.md](delivery.md) section 3); no job holds a stored cloud key; and the person who
decides the release starts the production deploy by creating
the version tag that names it, after checking that the commit ran in staging
([release.md](../project-management/release.md) section 3). The scans after the staging deploy
check the version that runs, in jobs that hold no cloud role, and one last job tells the team's
channel when any part of the run fails or times out, so nobody has to watch the run to learn it.

## 3. deploy-to.yml: the same steps for every environment

`.github/workflows/deploy-to.yml`

```yaml
name: deploy-to

on:
  workflow_call:
    inputs:
      environment:
        type: string
        required: true
      commit:
        type: string
        required: true
      migrate:
        type: boolean
        default: true  # false for a manual run with migrate off, such as a redeploy of an earlier version (delivery.md section 7)
    outputs:
      base-url:
        description: The address the environment answers on, for the checks after the deploy
        value: ${{ jobs.deploy.outputs.base-url }}

permissions: {}  # nothing by default; each job asks for what it uses (pipeline-security.md section 3)

jobs:
  deploy:
    runs-on: ubuntu-24.04  # a version label, never ubuntu-latest: the OS changes only when this line does (pipeline.md section 9)
    timeout-minutes: 40  # the migration wait (about 10 minutes) and the service wait (15), with room for the other steps
    environment:
      name: ${{ inputs.environment }}
      url: ${{ vars.BASE_URL }}
    outputs:
      base-url: ${{ vars.BASE_URL }}  # the environment's own value, so the checks scan the environment just deployed
    concurrency:
      group: deploy-${{ inputs.environment }}
      cancel-in-progress: false  # a deploy cut off halfway leaves the service on two versions
    permissions:
      contents: read
      id-token: write  # the environment's role trusts only this environment (section 6)
    env:
      ENVIRONMENT: ${{ inputs.environment }}
      COMMIT: ${{ inputs.commit }}
      CLUSTER: ${{ vars.ECS_CLUSTER }}
    steps:
      # An unset variable reads as an empty string, and an empty ECS_SERVICE even lets the deploy
      # action skip the service and end green; name every missing one before anything changes.
      - name: Check the variables this job reads
        env:
          AWS_DEPLOY_ROLE_ARN: ${{ vars.AWS_DEPLOY_ROLE_ARN }}
          AWS_REGION: ${{ vars.AWS_REGION }}
          ECR_REPOSITORY: ${{ vars.ECR_REPOSITORY }}
          ECR_IMAGE: ${{ vars.ECR_IMAGE }}
          WEB_RELEASES_BUCKET: ${{ vars.WEB_RELEASES_BUCKET }}
          ECS_CLUSTER: ${{ vars.ECS_CLUSTER }}
          ECS_SERVICE: ${{ vars.ECS_SERVICE }}
          TASK_SUBNETS: ${{ vars.TASK_SUBNETS }}
          TASK_SECURITY_GROUPS: ${{ vars.TASK_SECURITY_GROUPS }}
          SITE_BUCKET: ${{ vars.SITE_BUCKET }}
          CLOUDFRONT_DISTRIBUTION_ID: ${{ vars.CLOUDFRONT_DISTRIBUTION_ID }}
          BASE_URL: ${{ vars.BASE_URL }}
        run: |
          missing=0
          for name in AWS_DEPLOY_ROLE_ARN AWS_REGION ECR_REPOSITORY ECR_IMAGE WEB_RELEASES_BUCKET \
            ECS_CLUSTER ECS_SERVICE TASK_SUBNETS TASK_SECURITY_GROUPS SITE_BUCKET \
            CLOUDFRONT_DISTRIBUTION_ID BASE_URL; do
            # ${!name} is bash for "the value of the variable named in name"; run: uses bash here.
            if [ -z "${!name}" ]; then
              echo "::error::The variable $name is empty: set it in the $ENVIRONMENT environment or the repository."
              missing=1
            fi
          done
          exit "$missing"

      # Every action by full commit SHA, the release in the comment: a tag can be moved (pipeline-security.md section 4).
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1  # v7.0.1
        with:
          ref: ${{ inputs.commit }}  # the task definition of the version being deployed
          persist-credentials: false  # the token is not left on the runner for the steps after this one (pipeline-security.md section 3)

      - uses: aws-actions/configure-aws-credentials@e1253824e5c10ff9df46874f81ed3ec929e19cfd  # v6.3.0
        with:
          role-to-assume: ${{ vars.AWS_DEPLOY_ROLE_ARN }}
          aws-region: ${{ vars.AWS_REGION }}

      - id: image
        name: Find the image and the bundle built from this commit
        env:
          REPOSITORY: ${{ vars.ECR_REPOSITORY }}
          IMAGE: ${{ vars.ECR_IMAGE }}
          RELEASES: ${{ vars.WEB_RELEASES_BUCKET }}
        run: |
          digest=$(aws ecr describe-images --repository-name "$REPOSITORY" \
            --image-ids imageTag="sha-$COMMIT" --query 'imageDetails[0].imageDigest' --output text)
          # Both artifacts must exist before the first change, or a missing bundle stops the deploy halfway.
          aws s3api head-object --bucket "$RELEASES" --key "$COMMIT/index.html" > /dev/null
          echo "ref=$IMAGE@$digest" >> "$GITHUB_OUTPUT"

      - id: task
        uses: aws-actions/amazon-ecs-render-task-definition@8d79160660ad39c402a16e5fc7cd2a32e8f7d6b7  # v1.9.1
        with:
          task-definition: backend/deploy/task-definition.${{ inputs.environment }}.json
          container-name: api
          image: ${{ steps.image.outputs.ref }}  # by digest, never by tag (images.md section 8)

      - id: register
        env:
          TASK_FILE: ${{ steps.task.outputs.task-definition }}
        run: |
          arn=$(aws ecs register-task-definition --cli-input-json "file://$TASK_FILE" \
            --query 'taskDefinition.taskDefinitionArn' --output text)
          echo "arn=$arn" >> "$GITHUB_OUTPUT"

      - id: migrate
        name: Migrate the database before the new code runs
        if: inputs.migrate
        env:
          TASK_DEFINITION: ${{ steps.register.outputs.arn }}
          SUBNETS: ${{ vars.TASK_SUBNETS }}
          SECURITY_GROUPS: ${{ vars.TASK_SECURITY_GROUPS }}
        run: |
          # No public IP: the task runs in private subnets, which reach ECR and Secrets Manager
          # through a NAT gateway or VPC endpoints.
          task=$(aws ecs run-task --cluster "$CLUSTER" --launch-type FARGATE \
            --task-definition "$TASK_DEFINITION" \
            --network-configuration "awsvpcConfiguration={subnets=[$SUBNETS],securityGroups=[$SECURITY_GROUPS],assignPublicIp=DISABLED}" \
            --overrides '{"containerOverrides":[{"name":"api","command":["alembic","upgrade","head"]}]}' \
            --query 'tasks[0].taskArn' --output text)
          # A task that cannot start comes back as None, with the reason in run-task's failures list.
          if [ "$task" = "None" ]; then
            echo "The migration task did not start; the service keeps its current version."
            exit 1
          fi
          echo "Migration task: $task"
          # The wait ends when the task stops, whatever its exit code, and gives up after about ten minutes.
          if ! aws ecs wait tasks-stopped --cluster "$CLUSTER" --tasks "$task"; then
            echo "The wait gave up and the migration task may still run. Do not re-run this job until"
            echo "aws ecs describe-tasks --cluster $CLUSTER --tasks $task shows the task STOPPED."
            exit 1
          fi
          code=$(aws ecs describe-tasks --cluster "$CLUSTER" --tasks "$task" \
            --query "tasks[0].containers[?name=='api'].exitCode|[0]" --output text)
          if [ "$code" != "0" ]; then
            reason=$(aws ecs describe-tasks --cluster "$CLUSTER" --tasks "$task" \
              --query 'tasks[0].stoppedReason' --output text)
            echo "The migration ended with exit code $code ($reason); the service keeps its current version."
            exit 1
          fi

      - id: service
        uses: aws-actions/amazon-ecs-deploy-task-definition@a00d4d57ac0de1a99b39fe469f3d898d38717c2b  # v2.6.4
        with:
          task-definition: ${{ steps.task.outputs.task-definition }}
          cluster: ${{ vars.ECS_CLUSTER }}
          service: ${{ vars.ECS_SERVICE }}
          wait-for-service-stability: true  # green only when the new tasks are healthy
          wait-for-minutes: 15  # set, so the job's timeout can sit above this wait and the migration's

      - id: bundle
        name: Publish the bundle built from this commit
        env:
          RELEASES: ${{ vars.WEB_RELEASES_BUCKET }}
          SITE: ${{ vars.SITE_BUCKET }}
          DISTRIBUTION: ${{ vars.CLOUDFRONT_DISTRIBUTION_ID }}
        run: |
          # The assets first, index.html last, so a page never points at a file that is not there yet.
          # Old hashed files stay: a browser holding the old index.html may still ask for them.
          # cp, not sync: an S3-to-S3 sync skips a same-size object whose source is older,
          # so a rollback would keep a newer file of the same size (section 4).
          aws s3 cp "s3://$RELEASES/$COMMIT/" "s3://$SITE/" --recursive --exclude index.html --no-progress
          aws s3 cp "s3://$RELEASES/$COMMIT/index.html" "s3://$SITE/index.html"
          aws cloudfront create-invalidation --distribution-id "$DISTRIBUTION" --paths /index.html

      - id: smoke
        name: Smoke test
        env:
          BASE_URL: ${{ vars.BASE_URL }}
          RELEASES: ${{ vars.WEB_RELEASES_BUCKET }}
        run: |
          # Bounded retries wait for the first requests through the CDN: a wait for readiness, not a
          # rerun of a failed check (pipeline.md section 3).
          curl --fail --silent --show-error --retry 5 --retry-all-errors "$BASE_URL/api/health"
          aws s3 cp "s3://$RELEASES/$COMMIT/index.html" release-index.html --no-progress
          # The page must be this version's index.html; the retries wait for the invalidation to reach CloudFront.
          for _ in 1 2 3 4 5 6; do
            if curl --fail --silent --show-error --output served-index.html "$BASE_URL/" \
              && cmp -s served-index.html release-index.html; then
              exit 0
            fi
            sleep 20
          done
          echo "$BASE_URL/ does not serve the index.html of $COMMIT."
          exit 1

      - name: Record the deploy
        env:
          IMAGE: ${{ steps.image.outputs.ref }}
        run: |
          echo "$ENVIRONMENT runs $COMMIT: $IMAGE" >> "$GITHUB_STEP_SUMMARY"

      # The on-call opens the failed run first: say which steps changed the environment.
      - name: Say what the failed deploy changed
        if: failure()
        env:
          MIGRATION: ${{ steps.migrate.outcome }}
          SERVICE: ${{ steps.service.outcome }}
          BUNDLE: ${{ steps.bundle.outcome }}
          SMOKE: ${{ steps.smoke.outcome }}
        run: |
          {
            echo "The $ENVIRONMENT deploy of $COMMIT failed. The steps that change the environment ended as:"
            echo "- migration: $MIGRATION"
            echo "- service update: $SERVICE"
            echo "- bundle published: $BUNDLE"
            echo "- smoke test: $SMOKE"
            echo "A skipped step changed nothing. Decide the way back with the release's rollback plan (rollback-plan.md section 6 says where it is kept)."
          } >> "$GITHUB_STEP_SUMMARY"
```

## 4. What deploy-to.yml does

| Part | Why |
|---|---|
| `environment: name: ${{ inputs.environment }}` | the job gets that environment's variables, passes its rules first, creates a deployment record, and its OIDC token carries `environment:<name>` in `sub` ([delivery.md](delivery.md) sections 4 and 5) |
| `concurrency` with `cancel-in-progress: false` | one deploy at a time per environment, and never one cut off halfway ([delivery.md](delivery.md) section 4). The group keeps GitHub's default: one run waits, and a newer request cancels the one that waits [18]. So while a rollback waits behind a running deploy, start no other run for that environment; [delivery.md](delivery.md) section 14 says why the job does not set `queue: max` |
| `outputs: base-url`, on the job and on `workflow_call` | a reusable workflow hands a value to its caller only through a job output it maps to a workflow output [9], and a job output may read `vars` [38]. The value is the environment's own `BASE_URL`, so `dast-staging` and `headers-staging` scan the environment this job deployed |
| `Check the variables this job reads`, the first step | a variable that is not set reads as an empty string [20], so a missing one would fail later with an error that does not name it, or not at all: with `ECS_SERVICE` empty, the deploy action registers the task definition, updates no service and ends green [19], and the API stays on the old version. The step prints each missing name as an error [21] and stops the job before anything changes. It checks every variable the job reads, so a manual run with `migrate` on cannot find `TASK_SUBNETS` empty later |
| `checkout` at `inputs.commit` | the task definition comes from the version being deployed, so a rollback also rolls back its settings |
| `describe-images` by `sha-<commit>`, then `head-object` on the bundle's `index.html` | finds the digest of the image built from that commit, which carries the tag only when its scan passed (section 2), and proves its bundle is stored; a commit with no scanned image or no bundle fails the job here, before anything changes |
| `amazon-ecs-render-task-definition` | writes the image, by digest, into the task definition file [2] |
| `register-task-definition`, then `run-task` with `alembic upgrade head` | the migration runs once, in the new task definition, before the service changes ([delivery.md](delivery.md) section 6). Alembic is this example's migration tool; use your own command |
| `migrate` input, `if: inputs.migrate` | `deploy.yml` passes `false` for a manual run unless the person turns `migrate` on. A redeploy of an earlier version leaves it off: that version's Alembic scripts do not know the newer revision the database holds, and the newer schema still serves the older code ([delivery.md](delivery.md) section 7) |
| `None` from `run-task`, the task's ARN, `stoppedReason` | a task that never starts fails the job at once, not after the wait; the log names the task, and a failed migration prints why ECS stopped it [3], [11] |
| `wait tasks-stopped`, then `exitCode` | the wait succeeds when the task stops, whatever its exit code, so the job reads the container's exit code and fails unless it is `0` [3], [4]. When the wait gives up, the task may still run, and the job says not to re-run until it has stopped: a second `alembic upgrade head` would run against the same database |
| `amazon-ecs-deploy-task-definition` with `wait-for-service-stability` and `wait-for-minutes: 15` | updates the service and waits until the new tasks are healthy, for at most 15 minutes [5]. It registers the task definition again, an identical revision. The action's README recommends an IAM user's access key; this example logs in with OIDC instead ([delivery.md](delivery.md) section 5) |
| `timeout-minutes: 40` | above the migration wait and the service wait together, so GitHub never cuts a deploy off halfway ([delivery.md](delivery.md) section 4) |
| `aws s3 cp --recursive`, assets first and `index.html` last | copies every object, so a rollback restores every file: an S3-to-S3 `sync` copies an object only when the sizes differ, the source is newer or the object is missing [24], so it would keep a newer file of the same size, such as one from `public/`. The objects keep the cache headers `publish-web` gave them; only `index.html` is invalidated ([delivery.md](delivery.md) section 6) |
| the smoke test | the health route of the API through CloudFront, and the page itself, compared with this version's `index.html` in the release store, so an old page served through the CDN fails the test ([delivery.md](delivery.md) section 7). The retries wait for the CDN, for about two minutes; they never rerun a failed check. `/api/health` stands for your service's health route |
| the last step, `if: failure()` | writes which steps that change the environment ran, failed or were skipped, and points to the rollback plan, so the on-call sees from the run page what state the environment is in |
| `ENVIRONMENT`, `COMMIT` through `env:` | inputs reach the scripts as data, never pasted into them ([pipeline-security.md](pipeline-security.md) section 5) |

It is good because staging and production run these steps and no others, with different inputs;
a failed migration stops the deploy before the service changes; and the job ends green only when
the new version is healthy and answers through the CDN.

What this example does not claim: it was not run when it was written. The migration waits at most
about ten minutes, the limit of `aws ecs wait tasks-stopped` [4]; a longer migration needs a loop
of its own.

## 5. The GitHub settings

Day 0, in this order, in GitHub and in AWS. Each step needs what the steps before it created.

1. Create the `staging` and `production` environments, with the rules of the table below. A run
   that names an environment that does not exist creates it with no rules, and an environment's
   rules are all that stand between a workflow on any branch and the role that trusts it, so no
   role may trust an environment before it exists ([delivery.md](delivery.md) section 5).
2. In IAM, add the OIDC provider for `token.actions.githubusercontent.com`, then create the roles
   of [section 6](#6-the-aws-side-roles-and-the-task-definition): the two deploy roles, which trust
   those environments, and the two publish roles, one for `publish-api` and one for
   `publish-web`, which trust `main`. AWS asks you to add GitHub's provider before you create a
   role for it [6]. Write every trust policy in the `sub` form your repository's tokens carry: the
   form with numeric IDs when the repository was created after 2026-07-15, renamed or transferred
   after that date, or opted in, and the short form otherwise [22] (section 6 shows both).
   `gh api repos/{owner}/{repo} --jq '.created_at, .owner.id, .id'` prints the creation date and
   the two IDs.
3. Create the AWS resources the opening of this file lists: the ECR repository with immutable tags
   and continuous scanning, the releases bucket and the site buckets, the CloudFront distributions,
   the ECS cluster, and one service per environment, started from a bootstrap task definition at desired count 0, so it runs
   no task before the first deploy. Also create the task role, the execution role and the secret
   that the task definition of section 6 names. The deploy action updates a service that exists
   and fails when it finds none [19]; it creates no service.
4. Set the environment variables of the table below and the repository variables after it, which
   name the role ARNs of step 2 and the resources of step 3; then the tag ruleset after them, and
   `ci-ok` as the required status check for `main` ([ci-example.md](ci-example.md) section 2).
5. Merge `deploy.yml` and `deploy-to.yml` to `main`.
6. That merge is the first run, and it deploys staging. The service keeps its count of 0, because
   `deploy-to.yml` sets no `desired-count` [19], so the smoke test fails: set the count with
   `aws ecs update-service --cluster <cluster> --service <service> --desired-count <n>` and choose
   "Re-run failed jobs". Production's first version tag needs the same. Before each later version
   tag, rehearse the way back in staging ([delivery.md](delivery.md) section 7); the first tag has
   no earlier version to go back to.

The environments, in the repository settings:

| Setting | `staging` | `production` |
|---|---|---|
| Deployment branches and tags | the branch `main`, and tags that match `v*`, so an earlier version can be redeployed there to rehearse the way back | tags that match `v*` |
| Required reviewers | none | two or three reviewers, the decider's backup among them, with "Prevent self-review" on, where the plan offers it: Enterprise, or a public repository ([delivery.md](delivery.md) section 4) |
| Variables | `AWS_DEPLOY_ROLE_ARN`, `ECS_CLUSTER`, `ECS_SERVICE`, `TASK_SUBNETS`, `TASK_SECURITY_GROUPS`, `SITE_BUCKET`, `CLOUDFRONT_DISTRIBUTION_ID`, `BASE_URL` | the same names, with production's values |
| Secrets | none | none |

Repository variables: `AWS_REGION`, `AWS_PUBLISH_API_ROLE_ARN`, `AWS_PUBLISH_WEB_ROLE_ARN`,
`ECR_REPOSITORY` (the repository's name), `ECR_IMAGE` (`<account>.dkr.ecr.<region>.amazonaws.com/<repository>`), `WEB_RELEASES_BUCKET`,
`DOCKERHUB_USERNAME` (the Docker Hub login in `publish-api` reads it; the login is skipped when the
`DOCKERHUB_TOKEN` secret is absent). None of them is a secret; a role ARN lets nobody in without
the trust policy of section 6.

Repository secret: `DEPLOY_ALERT_WEBHOOK_URL`, the incoming webhook of the channel the team reads,
which `notify-failure` posts to. Without it the job warns on the run and posts nothing.

The release tags are protected by a tag ruleset that lets only the go or no-go decider of
[release.md](../project-management/release.md) section 3 and their backup create a `v*` tag, and
nobody move or delete one ([ruleset-example.md](../git/ruleset-example.md),
"Release tags"). With it, creating a version tag is the go decision, recorded in git.

## 6. The AWS side: roles and the task definition

The trust policy of the production deploy role.
[readability.md](../readability/readability.md) section 4 asks for the reason at the line in code
that others copy; this JSON departs from that rule because JSON has no comments, so the reason for
each part is in the table after it. The cost: a copy of the JSON alone loses these reasons.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::123456789012:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
          "token.actions.githubusercontent.com:sub": "repo:acme-corp/shop:environment:production"
        }
      }
    }
  ]
}
```

| Part | Why |
|---|---|
| `StringEquals` on `sub`, with the full value | only a job of this repository in the `production` environment gets the role; AWS rejects a `sub` that is missing or only a wildcard [6] |
| `environment:production` | a job that names an environment gets that form of `sub` ([delivery.md](delivery.md) section 5); the staging role names `environment:staging`, and the two publish roles name `ref:refs/heads/main`, because their jobs name no environment |
| `aud` = `sts.amazonaws.com` | the audience `configure-aws-credentials` requests by default [6] |

The JSON shows the short form of `sub`. A repository created after 2026-07-15, or renamed or
transferred after that date, carries the form with the owner's and the repository's numeric IDs
instead, and an older one carries it once someone opts it in [22], [23]. A role whose condition
names the other form refuses the token, so write the form your repository carries, for every role
(section 5, step 2):

| Role | Short form | Form with numeric IDs |
|---|---|---|
| production deploy | `repo:acme-corp/shop:environment:production` | `repo:acme-corp@<owner id>/shop@<repository id>:environment:production` |
| staging deploy | `repo:acme-corp/shop:environment:staging` | `repo:acme-corp@<owner id>/shop@<repository id>:environment:staging` |
| publish-api, publish-web | `repo:acme-corp/shop:ref:refs/heads/main` | `repo:acme-corp@<owner id>/shop@<repository id>:ref:refs/heads/main` |

It is good because only a job of this one repository, running in its `production` environment,
can assume the role, and no stored key exists that could leak.

What each role may do:

| Role | Its permissions |
|---|---|
| publish-api | push to the one ECR repository: `ecr:GetAuthorizationToken` on `*`, and `ecr:BatchCheckLayerAvailability`, `ecr:InitiateLayerUpload`, `ecr:UploadLayerPart`, `ecr:CompleteLayerUpload`, `ecr:PutImage`, `ecr:BatchGetImage` on its ARN [7]; `ecr:GetDownloadUrlForLayer` on the same ARN, because the scan of the pushed digest pulls its layers [12]; nothing in S3 |
| publish-web | write to the releases bucket; nothing in ECR |
| staging deploy, production deploy | read the image's digest (`ecr:DescribeImages`); register task definitions and describe tasks; `ecs:RunTask` and `ecs:UpdateService` only on that environment's cluster and service, and `ecs:DescribeServices` on the same service, which the service step's wait polls [5]; `iam:PassRole` only on that environment's task role and execution role, with the condition `iam:PassedToService` = `ecs-tasks.amazonaws.com`, so the staging role cannot start a task with production's roles and secrets; read the releases bucket and write the environment's site bucket; invalidate the environment's distribution |

Put each environment in its own AWS account where you can: then a wrong permission in the staging
role still reaches nothing of production.

The production task definition, cut to the parts the deploy touches. It sits in `backend/deploy/`,
which [file-structure.md](../file-structure/file-structure.md) section 9 does not list: a departure
from that section, because these files are deploy config the pipeline reads, kept next to the
application they deploy so `CODEOWNERS` can give them one owner
([security-example.md](security-example.md) section 3). The cost: a reader who knows
file-structure.md does not expect the folder.

[readability.md](../readability/readability.md) section 4 asks for the reason at the line in code
that others copy; this JSON departs from that rule because JSON has no comments, so the reason for
each part is in the table after it. The cost: a copy of the JSON alone loses these reasons.

`backend/deploy/task-definition.production.json`

```json
{
  "family": "acme-api-production",
  "executionRoleArn": "arn:aws:iam::123456789012:role/acme-api-production-execution",
  "taskRoleArn": "arn:aws:iam::123456789012:role/acme-api-production-task",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "containerDefinitions": [
    {
      "name": "api",
      "image": "set-by-the-deploy-job",
      "essential": true,
      "portMappings": [{ "containerPort": 8000 }],
      "secrets": [
        {
          "name": "ACME_DATABASE_PASSWORD",
          "valueFrom": "arn:aws:secretsmanager:eu-west-1:123456789012:secret:acme-api/production/database-password-AbCdEf"
        }
      ]
    }
  ]
}
```

| Part | Why |
|---|---|
| `secrets` with `valueFrom` | ECS reads the value from Secrets Manager and puts it into the container's environment when the container starts [8]; the workflow and the repository hold only the secret's name ([delivery.md](delivery.md) section 5) |
| `executionRoleArn` | the role ECS uses to pull the image and read the secret; it needs `secretsmanager:GetSecretValue` on that secret [8] |
| `ACME_DATABASE_PASSWORD` | the setting the application's settings class reads ([python.md](../../python/language/python.md) section 5), the same name [compose-example.md](../docker/compose-example.md) uses locally |
| `"image": "set-by-the-deploy-job"` | the deploy job writes the digest here; the file never names a tag |

A changed secret reaches the tasks only with a new deployment [8].

It is good because the file names the image only through the deploy job, by digest, and names
the secret only by its ARN, so the repository holds no secret value and no tag decides what runs.

## 7. Sources

Checked 2026-10-18 unless a line ends with — checked <YYYY-MM-DD>.

- [1] AWS — Amazon ECS Developer Guide: Using non-AWS container images in Amazon ECS — https://docs.aws.amazon.com/AmazonECS/latest/developerguide/private-auth.html
- [2] AWS — amazon-ecs-render-task-definition, README, v1.9.1 — https://github.com/aws-actions/amazon-ecs-render-task-definition/blob/v1.9.1/README.md
- [3] AWS — AWS CLI Command Reference: ecs describe-tasks, version 2 — https://docs.aws.amazon.com/cli/latest/reference/ecs/describe-tasks.html
- [4] AWS — AWS CLI Command Reference: ecs wait tasks-stopped, version 2 — https://docs.aws.amazon.com/cli/latest/reference/ecs/wait/tasks-stopped.html
- [5] AWS — amazon-ecs-deploy-task-definition, README, v2.6.4 — https://github.com/aws-actions/amazon-ecs-deploy-task-definition/blob/v2.6.4/README.md
- [6] AWS — IAM User Guide: Create a role for OpenID Connect federation — https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_create_for-idp_oidc.html
- [7] AWS — Amazon ECR User Guide: IAM permissions for pushing an image — https://docs.aws.amazon.com/AmazonECR/latest/userguide/image-push-iam.html
- [8] AWS — Amazon ECS Developer Guide: Pass Secrets Manager secrets through environment variables — https://docs.aws.amazon.com/AmazonECS/latest/developerguide/secrets-envvar-secrets-manager.html
- [9] GitHub — Reuse workflows: passing inputs and secrets, using outputs — https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows — checked 2026-10-19
- [10] Vite — Static Asset Handling: the public directory, Vite 8 — https://vite.dev/guide/assets#the-public-directory
- [11] AWS — AWS CLI Command Reference: ecs run-task, version 2 — https://docs.aws.amazon.com/cli/latest/reference/ecs/run-task.html
- [12] AWS — Amazon ECR API Reference: GetDownloadUrlForLayer — https://docs.aws.amazon.com/AmazonECR/latest/APIReference/API_GetDownloadUrlForLayer.html
- [13] Aqua Security — Trivy documentation, Private registries: Amazon ECR, v0.76.0 — https://github.com/aquasecurity/trivy/blob/v0.76.0/docs/guide/advanced/private-registries/ecr.md
- [14] Docker — Image and registry exporters (`push-by-digest`, `name-canonical`) — https://docs.docker.com/build/exporters/image-registry/
- [15] AWS — Amazon ECR User Guide: Retagging an image in Amazon ECR — https://docs.aws.amazon.com/AmazonECR/latest/userguide/image-retag.html
- [16] AWS — Amazon ECR API Reference: PutImage — https://docs.aws.amazon.com/AmazonECR/latest/APIReference/API_PutImage.html
- [17] AWS — Amazon ECR API Reference: BatchGetImage — https://docs.aws.amazon.com/AmazonECR/latest/APIReference/API_BatchGetImage.html
- [18] GitHub — Workflow syntax for GitHub Actions: `concurrency` and `jobs.<job_id>.timeout-minutes` — https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax — checked 2026-10-19
- [19] AWS — amazon-ecs-deploy-task-definition, `index.js` (the service check, an empty `service`, `desired-count`), v2.6.4 — https://github.com/aws-actions/amazon-ecs-deploy-task-definition/blob/v2.6.4/index.js
- [20] GitHub — Store information in variables: an unset variable reads as an empty string — https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-variables
- [21] GitHub — Workflow commands for GitHub Actions: setting an error message — https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-commands
- [22] GitHub — Immutable subject claims for GitHub Actions OIDC tokens (changelog, 2026-04-23) — https://github.blog/changelog/2026-04-23-immutable-subject-claims-for-github-actions-oidc-tokens/
- [23] GitHub — OpenID Connect reference: the immutable subject claim format — https://docs.github.com/en/actions/reference/security/oidc
- [24] AWS — AWS CLI Command Reference: s3 sync, version 2 — https://docs.aws.amazon.com/cli/latest/reference/s3/sync.html
- [25] ZAP — ZAP - Baseline Scan (options, exit values, configuration file) — https://www.zaproxy.org/docs/docker/baseline-scan/ — checked 2026-10-19
- [26] ZAP — ZAP Docker User Guide (the stable image, mounting `/zap/wrk`) — https://www.zaproxy.org/docs/docker/about/ — checked 2026-10-19
- [27] ZAP — `docker/zap_common.py` (`load_config`: three tab-separated fields per line) — https://github.com/zaproxy/zaproxy/blob/main/docker/zap_common.py — checked 2026-10-19
- [28] ZAP — action-baseline, `index.js` (`chmod a+w` on the mounted folder) — https://github.com/zaproxy/action-baseline/blob/master/index.js — checked 2026-10-19
- [29] ZAP — Alert 10020, Anti-clickjacking Header (passive) — https://www.zaproxy.org/docs/alerts/10020/ — checked 2026-10-19
- [30] ZAP — Alert 10021, X-Content-Type-Options Header Missing (passive) — https://www.zaproxy.org/docs/alerts/10021/ — checked 2026-10-19
- [31] ZAP — Alert 10035, Strict-Transport-Security Header (passive) — https://www.zaproxy.org/docs/alerts/10035/ — checked 2026-10-19
- [32] ZAP — Alert 10038, Content Security Policy (CSP) Header Not Set (passive) — https://www.zaproxy.org/docs/alerts/10038/ — checked 2026-10-19
- [33] MDN — mdn-http-observatory, README (the command-line tool and the JSON API) — https://github.com/mdn/mdn-http-observatory/blob/main/README.md — checked 2026-10-19
- [34] Google — csp-evaluator, README — https://github.com/google/csp-evaluator — checked 2026-10-19
- [35] npm — registry entry of `csp_evaluator` (version 1.1.8, its tarball and `integrity`) — https://registry.npmjs.org/csp_evaluator — checked 2026-10-19
- [36] GitHub — actions/setup-node, README, v7.1.0 — https://github.com/actions/setup-node/blob/v7.1.0/README.md — checked 2026-10-19
- [37] GitHub — Evaluate expressions in workflows and actions: status check functions — https://docs.github.com/en/actions/reference/workflows-and-actions/expressions — checked 2026-10-19
- [38] GitHub — Contexts reference: context availability (`jobs.<job_id>.outputs`) and the `needs` context — https://docs.github.com/en/actions/reference/workflows-and-actions/contexts — checked 2026-10-19
- [39] Slack — Sending messages using incoming webhooks — https://docs.slack.dev/messaging/sending-messages-using-incoming-webhooks — checked 2026-10-19
- [40] GitHub — actions/upload-artifact, README, v7.0.2 — https://github.com/actions/upload-artifact/blob/v7.0.2/README.md — checked 2026-10-19
- [41] GitHub — actions/runner-images, Ubuntu 24.04 image readme (installed `jq`) — https://github.com/actions/runner-images/blob/main/images/ubuntu/Ubuntu2404-Readme.md — checked 2026-10-19
