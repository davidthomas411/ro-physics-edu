# Releasing the site

The site is published on GitHub Pages by `.github/workflows/pages.yml`. A release is a tag that starts with `v`. The workflow runs the static tests, builds the page with `python build.py --release`, and deploys `dist/ro-physics.html` as `index.html`.

## Once, before the first release

1. **Repository.** GitHub Pages on the free plan needs a public repository. Read "Before the repository is public" below first.
2. **Owner values.** Fill `site_config.json`: authors with ORCID, contact email, Pages URL, physics reviewers with review dates, acknowledgments, IRB number, survey URL, and the usage-count settings. `python build.py --release` lists everything that is still missing.
3. **Third-party terms.** Read the terms of the OpenKBP data, the ICBM152 template, and the linac illustration. Write the terms into their rows in `THIRD_PARTY_NOTICES.md`, then set the matching entries of `third_party_confirmed` to `true`. The release build stops while one is `false`.
4. **Pages settings.** Settings > Pages > Source: GitHub Actions. Settings > Environments > github-pages > Deployment branches and tags: add the tag rule `v*` (and the branch `main` for manual runs). Without the tag rule the deploy job fails.
5. **Zenodo.** Sign in at zenodo.org with GitHub and switch on the repository under GitHub settings. Zenodo archives each GitHub release and mints a DOI. It reads `.zenodo.json` and `CITATION.cff`.
6. **Usage counts** (only if `analytics_mode` is `anonymous`). See "Usage counts" below, and give the IRB `docs/irb-data-description.md`.

## Every release

1. Add an entry at the top of `CHANGELOG.md`: `## 1.0.1 - 2026-11-02`, then one bullet per change. The newest entry sets the version.
2. Run `python tools/sync_release_files.py`. It rewrites `CITATION.cff`, `.zenodo.json`, the citation block in `README.md`, and `docs/irb-data-description.md`. Check the changes with `git diff`.
3. Run the static tests, then `OUT=/tmp/release.html python build.py --release` to see the list of anything missing.
4. Commit and push to `main`. Tag the commit and push the tag: `git tag v1.0.1 && git push origin v1.0.1`. The tag must equal `v` plus the newest `CHANGELOG.md` version, or the workflow stops.
5. Open the Actions tab and wait for the Pages workflow to finish. Open the site and check the About page: version, build date, commit, citation, and privacy text.
6. Create a GitHub release from the tag. Zenodo then mints the DOI. Copy the concept DOI (the one that always points to the newest version) into `doi` in `site_config.json`, run `python tools/sync_release_files.py`, commit, and start the Pages workflow by hand (Actions > Pages > Run workflow) so that the page shows the DOI.

## Usage counts

`analytics_mode: "anonymous"` turns on the events listed in `src/analytics_schema.py`, in release builds only. A local build and the tests never send anything. Linked analytics, with a participant code, is not built.

- **GoatCounter** (`analytics_backend: "goatcounter"`, the default). Create a site at goatcounter.com and put its code in `analytics_site_code`. Each event is one request with a path such as `ev/ans/<item>/c/1/B/15-30/0`. Events count as page views, and the free plan has a monthly limit, so check the current limit against the expected use: every question answered and every page opened is one request. After the first release, answer one question on the live site and confirm that the event appears in the dashboard.
- **Collector run by the study team** (`analytics_backend: "endpoint"`, for example a Cloudflare Worker with a D1 database). The page sends `POST` with a JSON body `{"event": ..., "props": {...}}` and no cookie. The collector should check each event against the schema, store the event and the time it received it, discard the IP address and the User-Agent header, and answer with status 204. `https://` is required, except for `127.0.0.1` in tests.
- **Reports.** `python tools/item_report.py EXPORT --out report.csv` reads a GoatCounter CSV or API export, or JSON lines from the collector, and writes one row per question. Add `--external` for anything shared outside the study team: it leaves out every question with fewer than 5 first answers.
- **IRB.** `docs/irb-data-description.md` is generated from the schema. It lists three points to confirm with the collector: the fields of its export, its retention and deletion options, and whether reports could identify one participant in a small cohort.

## Before the repository is public

Public means that anyone can read every file and the whole history. Check these first.

- **Third-party document in history.** `ROECSG physics study guide (1).pdf` was committed in `000d930` and is still in the history, although it is no longer in the tree. Zenodo archives only the tagged tree, but the history of a public repository stays readable. Either publish from a new repository that starts from the current tree, or remove the file from the history with `git filter-repo --path "ROECSG physics study guide (1).pdf" --invert-paths` and force-push. Both change the commit ids, so do this before anyone else clones the repository.
- **Warnings from the release build.** `tools/book_pipeline.py` and the files next to it read text from an e-book through screen recordings, and `docs/roecsg-audit*` is a working document about a third-party study guide. Decide whether they belong in a public repository. The release build prints a warning for each.
- **No third-party text.** No textbook text, OCR output, or slide content may be tracked. `python tools/check_overlap.py <folder of local OCR text>` flags any run of 8 words that the site shares with those files. Keep the OCR folder outside the repository.
- **Ownership.** Check the institution's policy on who owns teaching material and software before choosing the licenses in `LICENSE` and `LICENSE-CONTENT.md`. `LICENSE` names "the authors of this repository" as the copyright holder; replace it if the institution or a lab must be named.
- **Actions versions.** `pages.yml` pins major versions of the GitHub actions. Update them when GitHub announces a new major version.

## Preview

`.github/workflows/preview.yml` builds the development page (`python build.py`, placeholders for missing owner values, noindex, no usage data) and publishes it on GitHub Pages after every push to `main`. It needs the same Pages settings as a release, with the branch `main` allowed under Settings > Environments > github-pages. Until a release is made the preview is the only published version; it is not a release and carries no DOI.
