function initializeCommentEventHandlers(container) {
    console.log("Réinitialisation des gestionnaires d'événements pour le popup.");
    const photoButton = container.querySelector("#add-photo");
    const photoInput = container.querySelector("#photo-input");
    const photoPreview = container.querySelector("#photo-preview");

    // Ouvrir le sélecteur de fichiers lorsqu'on clique sur le bouton "📷"
    photoButton.addEventListener("click", () => {
        photoInput.click();
    });

    const removePhotoButton = container.querySelector("#remove-photo");
    // Afficher un aperçu de la photo sélectionnée
    photoInput.addEventListener("change", (event) => {
        const file = event.target.files[0];
        if (file) {
            console.log("Fichier sélectionné :", file.name);
            const reader = new FileReader();
            reader.onload = (e) => {
                // Créer un conteneur pour l'image et le bouton
                const imageContainer = document.createElement("div");
                imageContainer.className = "image-container";

                // Créer une nouvelle image
                const img = document.createElement("img");
                img.src = e.target.result;
                img.alt = "Photo sélectionnée";
                img.className = "selected-photo";

                // Créer le bouton de suppression (image)
                // removePhotoButton = document.createElement("img");
                //removePhotoButton.src = "{{ url_for('static', filename='images/icons/remove-icon.png') }}";
                //removePhotoButton.alt = "Supprimer la photo";
                //removePhotoButton.className = "remove-photo";
                removePhotoButton.style.display = "block"; // Afficher le bouton de suppression

                // Ajouter un événement pour supprimer l'image
                removePhotoButton.addEventListener("click", () => {
                    photoPreview.innerHTML = ""; // Vider l'aperçu
                    photoInput.value = ""; // Réinitialiser l'input file
                });

                // Ajouter l'image et le bouton au conteneur
                imageContainer.appendChild(img);
                imageContainer.appendChild(removePhotoButton);

                // Vider uniquement les anciennes images
                photoPreview.innerHTML = ""; // Supprime tout le contenu précédent
                photoPreview.appendChild(imageContainer); // Ajouter le conteneur au preview
            };
            reader.readAsDataURL(file);
        } else {
            console.log("Aucun fichier sélectionné.");
            // Si aucun fichier n'est sélectionné, vider l'aperçu
            photoPreview.innerHTML = "";
        }
    });

    // Supprimer l'image sélectionnée
    removePhotoButton.addEventListener("click", () => {
        photoPreview.innerHTML = ""; // Vider l'aperçu
        photoInput.value = ""; // Réinitialiser l'input file
        removePhotoButton.style.display = "none"; // Cacher le bouton de suppression
    });

    const textarea = container.querySelector("textarea[name='contenu']");
    const formButtons = container.querySelector(".form-buttons");


    if (!textarea || !formButtons) {
        console.error("Les éléments textarea ou form-buttons sont introuvables.");
        return;
    }
    console.log("Textarea et form-buttons trouvés.");
    console.log("Textarea :", textarea);
    console.log("Form-buttons :", formButtons);
    // Afficher les boutons lorsque le textarea est cliqué
    textarea.addEventListener("focus", () => {
        console.log("Textarea focus event triggered.");
        //formButtons.classList.remove("hidden");
        formButtons.style.display = "flex"; // Afficher la div
    });

}


document.addEventListener("DOMContentLoaded", () => {
    initializeCommentEventHandlers(document);
});

