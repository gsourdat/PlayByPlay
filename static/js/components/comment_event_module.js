    import '/static/js/node_modules/emoji-picker-element/index.js';   

    const emojiButton = document.querySelector("#selection-emoji");
    const emojiPicker = document.createElement('emoji-picker');

    // Ajoutez le picker au DOM (par exemple, en tant qu'enfant du body)
    document.body.appendChild(emojiPicker);

    // Positionnement du picker
    emojiPicker.style.position = 'absolute';
    emojiPicker.style.display = 'none';

    // Afficher/Masquer le picker lors du clic sur le bouton
    emojiButton.addEventListener("click", (event) => {
        const rect = emojiButton.getBoundingClientRect();
        emojiPicker.style.top = `${rect.bottom + window.scrollY}px`;
        emojiPicker.style.left = `${rect.left + window.scrollX - emojiPicker.offsetWidth}px`; // Alignement par la droite
        emojiPicker.style.display = emojiPicker.style.display === 'none' ? 'block' : 'none';
    });


    // Gérer la sélection d'un emoji
    emojiPicker.addEventListener('emoji-click', (event) => {
        const emoji = event.detail.unicode;
        const textarea = document.querySelector("textarea[name='contenu']");

        // Insérer l'emoji à la position du curseur ou à la fin du texte
        if (textarea) {
            const start = textarea.selectionStart;
            const end = textarea.selectionEnd;
            const text = textarea.value;

            // Ajouter l'emoji à la position du curseur
            textarea.value = text.slice(0, start) + emoji + text.slice(end);
            textarea.selectionStart = textarea.selectionEnd = start + emoji.length;
            textarea.focus();
        }

        //emojiPicker.style.display = 'none';
    });

    // Cacher le picker si on clique ailleurs
    document.addEventListener("click", (event) => {
        if (!emojiPicker.contains(event.target) && event.target !== emojiButton) {
            emojiPicker.style.display = 'none';
        }
    });
