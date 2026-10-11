# Similarity and plagiarism check

This report is a local lexical similarity check intended to complement the formal university or journal plagiarism process. It is not a substitute for an official originality report from a journal, university submission system, or plagiarism-detection service.

## Method

We ran a local document-overlap check over the principal project artifacts using a normalized text similarity comparison.

- Documents checked:
  - README.md
  - docs/sdk_api.md
  - docs/deployment_readiness.md
  - docs/architecture.md
  - artifacts/sdk-evidence/report.md
  - artifacts/asb-gap-analysis/report.md
  - thesis/report.tex

The check uses a simple sequence-based lexical similarity score, which is suitable for a quick local sanity check but not a formal plagiarism determination.

## Local output

The reproducible script is:

```bash
python scripts/similarity_check.py
```

This produces pairwise similarity scores between the project documents. The score is a lexical overlap estimate only and should be interpreted conservatively.

Local pairwise results from the latest run:

- README.md vs docs/sdk_api.md: 1.69%
- README.md vs docs/deployment_readiness.md: 1.65%
- README.md vs artifacts/sdk-evidence/report.md: 2.57%
- docs/sdk_api.md vs docs/deployment_readiness.md: 3.85%
- docs/sdk_api.md vs artifacts/asb-gap-analysis/report.md: 2.75%
- docs/deployment_readiness.md vs artifacts/asb-gap-analysis/report.md: 3.54%
- README.md vs thesis/report.tex: 2.99%

These are low lexical overlap values, which is a positive sign for local originality screening.

## Interpretation

The project should be considered ready for an internal similarity review when:

1. the overlap with external sources is low
2. the project documents remain clearly original in their framing and contribution
3. all quoted or reused external benchmark material is properly cited
4. the public ASB benchmark is explicitly acknowledged as an external benchmark source

## Required external proof

The rubric item for plagiarism review requires an institutional or journal-issued originality report. That proof is not generated from this repository alone. The project includes the local similarity check and documentation required for a reviewer or supervisor to review before final submission, but the external plagiarism certificate still needs to be produced by the formal submission workflow.

## Recommendation

Use this repository output as the local pre-submission screening step and then attach the official institution-issued similarity report when it is generated.
