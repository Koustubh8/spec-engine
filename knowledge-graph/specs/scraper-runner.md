---
title: Scraper Runner
kind: specs
created: 2026-05-09
updated: 2026-05-09
tags: [execution, monitoring, jobs]
---

# Scraper Runner
|rel:spec_of| [[tools/scraper-runner-module]]
|rel:depends_on| [[specs/prefect-backend]]
|rel:depends_on| [[specs/instagram-spiders]]
|rel:depends_on| [[specs/data-pipeline]]
|rel:depended_upon_by| [[specs/ui-frontend]]
|rel:contains| [[requirements/job-execution]]
|rel:contains| [[requirements/job-monitoring]]
|rel:contains| [[requirements/result-viewer]]
|rel:contains| [[requirements/retry-failed]]
|rel:contains| [[requirements/rate-limit-guard]]
|rel:depends_on| [[tools/prefect]]
|rel:exposes| [[references/post-run-job]]
|rel:exposes| [[references/get-job-status]]
|rel:constrained_by| [[concepts/sync-job-blocking]]
