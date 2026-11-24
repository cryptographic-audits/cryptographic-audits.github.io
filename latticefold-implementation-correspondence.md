---
title: "LatticeFold Implementation Correspondence — Protected Working Draft"
description: "Password-protected implementation notes for a forthcoming LatticeFold audit."
layout: page
permalink: /protected/latticefold-implementation-correspondence/
sitemap: false
robots: noindex, nofollow
math: true
---

> **Draft status.** This page currently contains only the implementation-to-attack code correspondence. No theorem statement or theorem analysis has been added or modified.
{: .prompt-info }

[Open LatticeFold on IACR ePrint](https://eprint.iacr.org/2024/257) · [Open the Nethermind implementation](https://github.com/NethermindEth/latticefold)

The working materials are encrypted in the browser. The password is never embedded in this repository, transmitted to the site, or stored after the page is reloaded. Decryption uses PBKDF2-SHA-256 and AES-256-GCM through the browser's Web Crypto API.

## Protected implementation correspondence

<link rel="stylesheet" href="/assets/css/latticefold-lock.css">

<section class="lf-lock"
  data-latticefold-lock
  data-payload="/assets/protected/latticefold/code-correspondence.lfenc"
  aria-labelledby="lf-lock-title">
  <div class="lf-lock__header">
    <div class="lf-lock__icon" aria-hidden="true">◆</div>
    <div>
      <h3 id="lf-lock-title">Encrypted code appendix</h3>
      <p>Unlocks the code map, control experiment, integrity data, and encrypted downloads.</p>
    </div>
  </div>
  <form class="lf-lock__form" autocomplete="off">
    <label class="visually-hidden" for="lf-password">Password</label>
    <input id="lf-password" type="password" inputmode="numeric" autocomplete="off" placeholder="Password" required>
    <button type="submit">Unlock locally</button>
  </form>
  <p class="lf-lock__status" data-lock-status aria-live="polite">Locked. No plaintext implementation material is present in the page source.</p>
  <div class="lf-lock__output" data-lock-output></div>
</section>

<script src="/assets/js/latticefold-lock.js" defer></script>

---

## License and Attribution

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

© 2026 cxcx52. This working note is licensed under the [Creative Commons Attribution 4.0 International License](https://creativecommons.org/licenses/by/4.0/). The bundled third-party implementation retains its MIT/Apache-2.0 licensing terms.
