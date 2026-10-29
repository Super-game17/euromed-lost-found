document.addEventListener("DOMContentLoaded", () => {
    document.addEventListener("submit", (event) => {
        const form = event.target;
        if (!(form instanceof HTMLFormElement) || !form.hasAttribute("data-confirm-action")) {
            return;
        }
        const action = form.querySelector('select[name="action"]')?.value;
        if (action === "reject" || action === "restitute") {
            const message = action === "reject"
                ? "Refuser cette réclamation ?"
                : "Confirmer que l’objet a bien été restitué ?";
            if (!window.confirm(message)) {
                event.preventDefault();
                event.stopImmediatePropagation();
            }
        }
    }, true);

    const intro = document.querySelector("[data-app-intro]");
    if (intro instanceof HTMLElement) {
        const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
        try {
            if (!reducedMotion && sessionStorage.getItem("uemfind-intro-seen") !== "true") {
                sessionStorage.setItem("uemfind-intro-seen", "true");
                document.body.classList.add("intro-active");
                intro.setAttribute("aria-hidden", "false");

                const finishIntro = () => {
                    document.body.classList.remove("intro-active");
                    intro.setAttribute("aria-hidden", "true");
                    window.setTimeout(() => { intro.hidden = true; }, 380);
                };

                intro.querySelector("[data-intro-skip]")?.addEventListener("click", finishIntro, { once: true });
                window.setTimeout(finishIntro, 1850);
            } else {
                intro.hidden = true;
            }
        } catch {
            intro.hidden = true;
        }
    }

    document.querySelectorAll("[data-password-toggle]").forEach((toggle) => {
        if (!(toggle instanceof HTMLButtonElement)) {
            return;
        }
        const field = toggle.closest(".auth-password-control")?.querySelector("input");
        if (!(field instanceof HTMLInputElement)) {
            return;
        }

        toggle.addEventListener("click", () => {
            const showing = field.type === "password";
            field.type = showing ? "text" : "password";
            toggle.textContent = showing ? "Masquer" : "Afficher";
            toggle.setAttribute("aria-label", showing ? "Masquer le mot de passe" : "Afficher le mot de passe");
            toggle.setAttribute("aria-pressed", String(showing));
        });
    });

    document.querySelectorAll("form[data-confirm-unsaved]").forEach((form) => {
        if (!(form instanceof HTMLFormElement)) {
            return;
        }
        let dirty = false;
        form.addEventListener("input", () => { dirty = true; });
        form.addEventListener("change", () => { dirty = true; });
        form.addEventListener("submit", () => { dirty = false; });
        window.addEventListener("beforeunload", (event) => {
            if (dirty && form.dataset.uploadConfirmed !== "true") {
                event.preventDefault();
                event.returnValue = "";
            }
        });
    });

    const photoInputs = Array.from(document.querySelectorAll("[data-photo-input]"))
        .filter((input) => input instanceof HTMLInputElement);
    const photoPreview = document.querySelector("[data-photo-preview]");
    const photoWrap = document.querySelector("[data-photo-wrap]");
    const uploadProgress = document.querySelector("[data-upload-progress]");
    const uploadStatus = document.querySelector("[data-upload-status]");
    let previewUrl = null;

    const clearPhotoPreview = () => {
        if (previewUrl) {
            URL.revokeObjectURL(previewUrl);
            previewUrl = null;
        }
        photoInputs.forEach((input) => { input.value = ""; });
        if (photoPreview instanceof HTMLImageElement) {
            photoPreview.removeAttribute("src");
        }
        if (photoWrap instanceof HTMLElement) {
            photoWrap.hidden = true;
        }
    };

    document.querySelector("[data-open-camera]")?.addEventListener("click", () => {
        document.querySelector("#photo-camera")?.click();
    });
    document.querySelector("[data-open-gallery]")?.addEventListener("click", () => {
        document.querySelector("#photo-gallery")?.click();
    });
    document.querySelector("[data-remove-photo]")?.addEventListener("click", clearPhotoPreview);

    photoInputs.forEach((input) => {
        input.addEventListener("change", () => {
            const [file] = input.files || [];
            if (!file) {
                return;
            }
            if (!["image/png", "image/jpeg", "image/webp"].includes(file.type)) {
                input.setCustomValidity("Choisissez une image PNG, JPG ou WebP.");
                input.reportValidity();
                clearPhotoPreview();
                input.setCustomValidity("");
                if (uploadStatus instanceof HTMLElement) {
                    uploadStatus.textContent = "Format non accepté. Choisissez une photo PNG, JPG ou WebP.";
                    uploadStatus.hidden = false;
                }
                return;
            }
            if (file.size > 4 * 1024 * 1024) {
                clearPhotoPreview();
                if (uploadStatus instanceof HTMLElement) {
                    uploadStatus.textContent = "La photo ne peut pas dépasser 4 Mo.";
                    uploadStatus.hidden = false;
                }
                return;
            }

            photoInputs.forEach((otherInput) => {
                if (otherInput !== input) {
                    otherInput.value = "";
                }
            });
            if (uploadStatus instanceof HTMLElement) {
                uploadStatus.hidden = true;
                uploadStatus.textContent = "";
            }
            if (previewUrl) {
                URL.revokeObjectURL(previewUrl);
            }
            if (photoPreview instanceof HTMLImageElement && photoWrap instanceof HTMLElement) {
                previewUrl = URL.createObjectURL(file);
                photoPreview.src = previewUrl;
                photoWrap.hidden = false;
            }
        });
    });

    document.querySelectorAll("form[data-submit-label]").forEach((form) => {
        if (!(form instanceof HTMLFormElement)) {
            return;
        }

        form.addEventListener("submit", () => {
            const submitButton = form.querySelector('button[type="submit"]');
            if (!(submitButton instanceof HTMLButtonElement)) {
                return;
            }

            if (form instanceof HTMLFormElement && form.hasAttribute("data-async-upload")) {
                return;
            }
            submitButton.disabled = true;
            submitButton.setAttribute("aria-busy", "true");
            submitButton.textContent = form.dataset.submitLabel || "Enregistrement…";
        });
    });

    document.querySelectorAll("form[data-async-upload]").forEach((form) => {
        if (!(form instanceof HTMLFormElement)) {
            return;
        }
        form.addEventListener("submit", (event) => {
            event.preventDefault();
            if (!form.reportValidity() || form.dataset.submitting === "true") {
                return;
            }
            const submitButton = form.querySelector('button[type="submit"]');
            if (!(submitButton instanceof HTMLButtonElement)) {
                return;
            }

            form.dataset.submitting = "true";
            submitButton.disabled = true;
            submitButton.setAttribute("aria-busy", "true");
            submitButton.textContent = form.dataset.submitLabel || "Enregistrement…";
            if (uploadProgress instanceof HTMLProgressElement) {
                uploadProgress.value = 0;
                uploadProgress.hidden = false;
            }
            if (uploadStatus instanceof HTMLElement) {
                uploadStatus.textContent = "Envoi de votre déclaration…";
                uploadStatus.hidden = false;
            }

            const xhr = new XMLHttpRequest();
            xhr.open(form.method.toUpperCase(), form.action || window.location.href);
            xhr.upload.addEventListener("progress", (progressEvent) => {
                if (progressEvent.lengthComputable && uploadProgress instanceof HTMLProgressElement) {
                    uploadProgress.value = Math.round((progressEvent.loaded / progressEvent.total) * 100);
                    if (uploadStatus instanceof HTMLElement) {
                        uploadStatus.textContent = `Envoi de la photo… ${uploadProgress.value}%`;
                    }
                }
            });
            xhr.addEventListener("load", () => {
                let sameOriginResponse = false;
                try {
                    sameOriginResponse = new URL(xhr.responseURL, window.location.href).origin === window.location.origin;
                } catch {
                    sameOriginResponse = false;
                }
                if (xhr.status >= 200 && xhr.status < 400 && sameOriginResponse) {
                    form.dataset.uploadConfirmed = "true";
                    window.setTimeout(() => {
                        document.open();
                        document.write(xhr.responseText);
                        document.close();
                    }, 120);
                    return;
                }
                form.dataset.submitting = "false";
                submitButton.disabled = false;
                submitButton.removeAttribute("aria-busy");
                submitButton.textContent = "Réessayer";
                if (uploadProgress instanceof HTMLProgressElement) {
                    uploadProgress.hidden = true;
                }
                if (uploadStatus instanceof HTMLElement) {
                    uploadStatus.textContent = xhr.status === 413
                        ? "La photo dépasse la taille maximale autorisée. Choisissez une photo de 4 Mo maximum."
                        : "La déclaration n’a pas pu être envoyée. Vérifiez votre connexion et réessayez.";
                    uploadStatus.hidden = false;
                }
            });
            xhr.addEventListener("error", () => {
                form.dataset.submitting = "false";
                submitButton.disabled = false;
                submitButton.removeAttribute("aria-busy");
                submitButton.textContent = "Réessayer";
                if (uploadProgress instanceof HTMLProgressElement) {
                    uploadProgress.hidden = true;
                }
                if (uploadStatus instanceof HTMLElement) {
                    uploadStatus.textContent = "Échec de l’envoi. Vérifiez votre connexion et réessayez.";
                    uploadStatus.hidden = false;
                }
            });
            xhr.send(new FormData(form));
        });
    });

    document.querySelectorAll("[data-back-link]").forEach((link) => {
        if (!(link instanceof HTMLAnchorElement)) {
            return;
        }
        link.addEventListener("click", (event) => {
            if (window.history.length < 2 || !document.referrer) {
                return;
            }
            try {
                if (new URL(document.referrer).origin === window.location.origin) {
                    event.preventDefault();
                    window.history.back();
                }
            } catch {
                return;
            }
        });
    });
});