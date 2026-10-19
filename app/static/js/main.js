document.addEventListener("DOMContentLoaded", () => {
    const photoInput = document.querySelector("#photo");
    const photoPreview = document.querySelector("[data-photo-preview]");

    if (photoInput instanceof HTMLInputElement && photoPreview instanceof HTMLImageElement) {
        let previewUrl = null;

        photoInput.addEventListener("change", () => {
            if (previewUrl) {
                URL.revokeObjectURL(previewUrl);
                previewUrl = null;
            }

            const [file] = photoInput.files || [];
            if (!file) {
                photoPreview.removeAttribute("src");
                photoPreview.hidden = true;
                return;
            }

            if (!["image/png", "image/jpeg", "image/webp"].includes(file.type)) {
                photoInput.setCustomValidity("Choisissez une image PNG, JPG ou WebP.");
                photoInput.reportValidity();
                photoInput.value = "";
                photoPreview.removeAttribute("src");
                photoPreview.hidden = true;
                return;
            }

            photoInput.setCustomValidity("");
            previewUrl = URL.createObjectURL(file);
            photoPreview.src = previewUrl;
            photoPreview.hidden = false;
        });
    }

    document.querySelectorAll("form[data-submit-label]").forEach((form) => {
        if (!(form instanceof HTMLFormElement)) {
            return;
        }

        form.addEventListener("submit", () => {
            const submitButton = form.querySelector('button[type="submit"]');
            if (!(submitButton instanceof HTMLButtonElement)) {
                return;
            }

            submitButton.disabled = true;
            submitButton.setAttribute("aria-busy", "true");
            submitButton.textContent = form.dataset.submitLabel || "Enregistrement…";
        });
    });
});