document.addEventListener('DOMContentLoaded', () => {
    
    const uploadForm = document.getElementById('uploadForm');
    const convertButton = document.getElementById('convertButton');
    const statusText = document.getElementById('statusText');
    const loadingSpinner = document.getElementById('loading');
    const downloadLink = document.getElementById('downloadLink');
    
    // Gestiamo l'invio del form
    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault(); // Impediamo l'invio tradizionale del form

        // 1. Raccogliamo i file
        const imageFile = document.getElementById('imageUpload').files[0];
        const audioFile = document.getElementById('audioUpload').files[0];

        if (!imageFile || !audioFile) {
            statusText.textContent = 'Errore: Seleziona entrambi i file.';
            return;
        }
        
        // 2. Prepariamo l'interfaccia per il caricamento
        statusText.textContent = 'Caricamento file al server...';
        loadingSpinner.classList.remove('hidden');
        convertButton.disabled = true;
        downloadLink.classList.add('hidden');

        // 3. Creiamo un oggetto FormData per inviare i file
        const formData = new FormData();
        formData.append('image', imageFile);
        formData.append('audio', audioFile);

        try {
            // 4. Inviamo i file al nostro backend Flask (/convert)
            statusText.textContent = 'Conversione in corso sul server... Attendi...';
            
            const response = await fetch('/convert', {
                method: 'POST',
                body: formData,
                // Non serve 'Content-Type', il browser la imposta
                // in automatico con FormData e boundary
            });

            // 5. Gestiamo la risposta del server
            const result = await response.json(); // Leggiamo la risposta JSON

            if (!response.ok) {
                // Se il server ha inviato un errore (es. 400 o 500)
                throw new Error(result.error || 'Errore sconosciuto dal server');
            }

            // 6. Successo! Mostriamo il link per il download
            statusText.textContent = 'Conversione completata!';
            downloadLink.href = result.downloadUrl; // Impostiamo l'URL ricevuto
            downloadLink.classList.remove('hidden');

        } catch (error) {
            console.error('Errore:', error);
            statusText.textContent = `Errore: ${error.message}`;
        } finally {
            // 7. Riattiviamo l'interfaccia
            loadingSpinner.classList.add('hidden');
            convertButton.disabled = false;
        }
    });
});
