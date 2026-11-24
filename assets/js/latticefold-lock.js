(() => {
  "use strict";

  const encoder = new TextEncoder();
  const decoder = new TextDecoder();
  const MAGIC = [0x4c, 0x46, 0x41, 0x31]; // LFA1

  function parseEnvelope(buffer) {
    const bytes = new Uint8Array(buffer);
    if (bytes.length < 53 || !MAGIC.every((value, index) => bytes[index] === value)) {
      throw new Error("Invalid encrypted asset format");
    }

    const view = new DataView(buffer);
    return {
      iterations: view.getUint32(4, false),
      salt: bytes.slice(8, 24),
      iv: bytes.slice(24, 36),
      ciphertext: bytes.slice(36),
    };
  }

  async function deriveKey(password, salt, iterations) {
    const material = await crypto.subtle.importKey(
      "raw",
      encoder.encode(password),
      "PBKDF2",
      false,
      ["deriveKey"]
    );

    return crypto.subtle.deriveKey(
      { name: "PBKDF2", hash: "SHA-256", salt, iterations },
      material,
      { name: "AES-GCM", length: 256 },
      false,
      ["decrypt"]
    );
  }

  async function decryptUrl(url, password) {
    const response = await fetch(url, { cache: "no-store" });
    if (!response.ok) {
      throw new Error(`Encrypted asset returned HTTP ${response.status}`);
    }

    const envelope = parseEnvelope(await response.arrayBuffer());
    const key = await deriveKey(password, envelope.salt, envelope.iterations);
    return crypto.subtle.decrypt(
      { name: "AES-GCM", iv: envelope.iv, tagLength: 128 },
      key,
      envelope.ciphertext
    );
  }

  function setStatus(node, text, state) {
    node.textContent = text;
    node.dataset.state = state;
  }

  function attachDownloads(container, password) {
    container.querySelectorAll("[data-encrypted-download]").forEach((button) => {
      button.addEventListener("click", async () => {
        const original = button.textContent;
        button.disabled = true;
        button.textContent = "Decrypting…";

        try {
          const plaintext = await decryptUrl(button.dataset.encryptedDownload, password);
          const blob = new Blob([plaintext], {
            type: button.dataset.mimeType || "application/octet-stream",
          });
          const href = URL.createObjectURL(blob);
          const anchor = document.createElement("a");
          anchor.href = href;
          anchor.download = button.dataset.outputName;
          document.body.appendChild(anchor);
          anchor.click();
          anchor.remove();
          URL.revokeObjectURL(href);
          button.textContent = "Downloaded";
        } catch (error) {
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

    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const password = input.value;
      if (!password) {
        setStatus(status, "Enter the password.", "error");
        return;
      }

      button.disabled = true;
      setStatus(status, "Deriving key and decrypting locally…", "working");

      try {
        const plaintext = await decryptUrl(root.dataset.payload, password);
        output.innerHTML = decoder.decode(plaintext);
        attachDownloads(output, password);
        form.hidden = true;
        setStatus(status, "Unlocked for this browser tab.", "success");
        root.classList.add("is-unlocked");
        input.value = "";
      } catch (error) {
        input.value = "";
        input.focus();
        setStatus(status, "Incorrect password or damaged encrypted data.", "error");
      } finally {
        button.disabled = false;
      }
    });
  });
})();
