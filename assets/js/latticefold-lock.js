import sodium from "../third-party/libsodium/libsodium-wrappers-sumo.mjs";

await sodium.ready;

const decoder = new TextDecoder();
const MAGIC = [0x4c, 0x46, 0x41, 0x32]; // LFA2
const FIXED_HEADER_BYTES = 54;
const TAG_BYTES = 16;

function parseEnvelope(buffer) {
  const bytes = new Uint8Array(buffer);
  if (
    bytes.length < FIXED_HEADER_BYTES + TAG_BYTES ||
    !MAGIC.every((value, index) => bytes[index] === value)
  ) {
    throw new Error("Invalid encrypted asset format");
  }

  const view = new DataView(buffer);
  const contextLength = view.getUint16(52, false);
  const headerLength = FIXED_HEADER_BYTES + contextLength;
  if (bytes.length < headerLength + TAG_BYTES) {
    throw new Error("Truncated encrypted asset");
  }

  return {
    opsLimit: view.getUint32(4, false),
    memLimit: view.getUint32(8, false),
    salt: bytes.slice(12, 28),
    nonce: bytes.slice(28, 52),
    context: decoder.decode(bytes.slice(FIXED_HEADER_BYTES, headerLength)),
    header: bytes.slice(0, headerLength),
    ciphertext: bytes.slice(headerLength),
  };
}

async function fetchEnvelope(url) {
  const response = await fetch(url, { cache: "no-store", credentials: "same-origin" });
  if (!response.ok) {
    throw new Error(`Encrypted asset returned HTTP ${response.status}`);
  }
  return parseEnvelope(await response.arrayBuffer());
}

function expectedContext(url) {
  return new URL(url, window.location.origin).pathname;
}

function validateContext(envelope, url) {
  if (envelope.context !== expectedContext(url)) {
    throw new Error("Encrypted asset context mismatch");
  }
}

function deriveKey(password, envelope) {
  const passwordBytes = sodium.from_string(password);
  try {
    return sodium.crypto_pwhash(
      sodium.crypto_aead_xchacha20poly1305_ietf_KEYBYTES,
      passwordBytes,
      envelope.salt,
      envelope.opsLimit,
      envelope.memLimit,
      sodium.crypto_pwhash_ALG_ARGON2ID13,
      "uint8array",
    );
  } finally {
    sodium.memzero(passwordBytes);
  }
}

function sameKeyParameters(left, right) {
  return (
    left.opsLimit === right.opsLimit &&
    left.memLimit === right.memLimit &&
    sodium.memcmp(left.salt, right.salt)
  );
}

function decryptEnvelope(envelope, key) {
  return sodium.crypto_aead_xchacha20poly1305_ietf_decrypt(
    null,
    envelope.ciphertext,
    envelope.header,
    envelope.nonce,
    key,
    "uint8array",
  );
}

async function unlockPayload(url, password) {
  const envelope = await fetchEnvelope(url);
  validateContext(envelope, url);
  const key = deriveKey(password, envelope);
  try {
    const plaintext = decryptEnvelope(envelope, key);
    return {
      plaintext,
      session: {
        key,
        opsLimit: envelope.opsLimit,
        memLimit: envelope.memLimit,
        salt: envelope.salt,
      },
    };
  } catch (error) {
    sodium.memzero(key);
    throw error;
  }
}

async function decryptUrlWithSession(url, session) {
  const envelope = await fetchEnvelope(url);
  validateContext(envelope, url);
  if (!sameKeyParameters(envelope, session)) {
    throw new Error("Encrypted asset key parameters do not match");
  }
  return decryptEnvelope(envelope, session.key);
}

function setStatus(node, text, state) {
  node.textContent = text;
  node.dataset.state = state;
}

function attachDownloads(container, session) {
  container.querySelectorAll("[data-encrypted-download]").forEach((button) => {
    button.addEventListener("click", async () => {
      const original = button.textContent;
      button.disabled = true;
      button.textContent = "Decrypting…";

      try {
        const plaintext = await decryptUrlWithSession(button.dataset.encryptedDownload, session);
        const blob = new Blob([plaintext], {
          type: button.dataset.mimeType || "application/octet-stream",
        });
        sodium.memzero(plaintext);
        const href = URL.createObjectURL(blob);
        const anchor = document.createElement("a");
        anchor.href = href;
        anchor.download = button.dataset.outputName;
        document.body.appendChild(anchor);
        anchor.click();
        anchor.remove();
        URL.revokeObjectURL(href);
        button.textContent = "Downloaded";
      } catch (_error) {
        button.textContent = "Decryption failed";
      } finally {
        window.setTimeout(() => {
          button.disabled = false;
          button.textContent = original;
        }, 1800);
      }
    });
  });
}

document.querySelectorAll("[data-latticefold-lock]").forEach((root) => {
  const form = root.querySelector("form");
  const input = root.querySelector("input[type='password']");
  const button = root.querySelector("button[type='submit']");
  const status = root.querySelector("[data-lock-status]");
  const output = root.querySelector("[data-lock-output]");
  let activeSession = null;

  window.addEventListener("pagehide", () => {
    if (activeSession?.key) sodium.memzero(activeSession.key);
  });

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const password = input.value;
    input.value = "";
    if (!password) {
      setStatus(status, "Enter the password.", "error");
      return;
    }

    button.disabled = true;
    setStatus(status, "Running Argon2id and decrypting locally…", "working");

    try {
      const unlocked = await unlockPayload(root.dataset.payload, password);
      activeSession = unlocked.session;
      output.innerHTML = decoder.decode(unlocked.plaintext);
      sodium.memzero(unlocked.plaintext);
      attachDownloads(output, activeSession);
      if (window.MathJax?.typesetPromise) {
        window.MathJax.typesetPromise([output]).catch(() => {});
      }
      form.hidden = true;
      setStatus(status, "Unlocked for this browser tab.", "success");
      root.classList.add("is-unlocked");
    } catch (_error) {
      input.focus();
      setStatus(status, "Incorrect password or damaged encrypted data.", "error");
    } finally {
      button.disabled = false;
    }
  });
});
