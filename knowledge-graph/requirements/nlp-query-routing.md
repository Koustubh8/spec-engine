---
title: Nlp Query Routing
kind: requirement
created: 2026-05-10
updated: 2026-05-10
tags: [chat]
strength: SHALL
---

# Nlp Query Routing

The chat interface SHALL route natural-language queries to the appropriate analytical module (MMM, CLV, Uplift, Segmentation, Creative) using a DSPy classifier. Unrecognized queries SHALL return 'I can help with marketing analytics questions about ROAS, customer value, campaign effectiveness, segments, and creative performance.'

|rel:portion_of| [[specs/consultant-interface-spec]]
