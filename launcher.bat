@echo off
setlocal

:: === Configurazione ===
:: Nome della cartella del gioco nella directory Home dell'utente
set "GAME_FOLDER_NAME=slime_souls"
:: Percorso della directory Home dell'utente (variabile di sistema di Windows)
set "HOME_DIR=%USERPROFILE%"
:: Percorso completo dove si troverà il gioco installato
set "GAME_PATH=%HOME_DIR%\%GAME_FOLDER_NAME%"
:: Nome del file eseguibile del gioco
set "EXE_NAME=menu.exe"
:: Nome del file ZIP da scaricare
set "ZIP_NAME=bloop.zip"
:: URL COMPLETO del tuo file ZIP su GitHub (o qualsiasi altra fonte diretta)
:: --- *** IMPORTANTE: DEVI SOSTITUIRE QUESTO URL CON QUELLO REALE DEL TUO FILE ZIP *** ---
:: Puoi trovare questo URL se hai caricato il file ZIP come "Release Asset" o direttamente nel tuo repository.
set "GITHUB_ZIP_URL=https://github.com/Dutch1cat/cuphead/raw/refs/heads/main/slime_souls.zip"

:: === Inizio Script ===
echo Controllo la presenza di "%GAME_FOLDER_NAME%" in "%HOME_DIR%"...

:: Verifica se il gioco è già installato (controllando se l'eseguibile esiste nella cartella)
if exist "%GAME_PATH%\%EXE_NAME%" (
    echo "%GAME_FOLDER_NAME%" trovato. Avvio di "%EXE_NAME%"...
    :: Avvia l'eseguibile. Le virgolette vuote dopo 'start' servono per il titolo della finestra.
    start "" "%GAME_PATH%\%EXE_NAME%"
) else (
    echo "%GAME_FOLDER_NAME%" non trovato. Download ed estrazione in corso...

    :: === Download del file ZIP ===
    echo Download di "%ZIP_NAME%" da GitHub...
    :: Utilizza PowerShell per scaricare il file. %TEMP% è una cartella temporanea di Windows.
    powershell -Command "(New-Object System.Net.WebClient).DownloadFile('%GITHUB_ZIP_URL%', '%TEMP%\%ZIP_NAME%')"
    :: Controlla se il download ha avuto successo
    if errorlevel 1 (
        echo Errore: Impossibile scaricare "%ZIP_NAME%". Controlla la tua connessione internet o l'URL.
        pause
        exit /b 1
    )
    echo Download completato.

    :: === Creazione della directory di destinazione ===
    :: Crea la cartella del gioco se non esiste
    if not exist "%GAME_PATH%" (
        echo Creazione della directory "%GAME_PATH%"...
        mkdir "%GAME_PATH%"
    )

    :: === Estrazione del file ZIP ===
    echo Estrazione di "%ZIP_NAME%" in "%GAME_PATH%"...
    :: Utilizza PowerShell per decomprimere il file.
    :: Poiché la tua GitHub Action carica i *contenuti* della cartella 'menu' nel ZIP,
    :: l'estrazione diretta in %GAME_PATH% posizionerà correttamente i file (es. menu.exe, images/).
    powershell -Command "Expand-Archive -Path '%TEMP%\%ZIP_NAME%' -DestinationPath '%GAME_PATH%' -Force"
    :: Controlla se l'estrazione ha avuto successo
    if errorlevel 1 (
        echo Errore: Impossibile estrarre "%ZIP_NAME%".
        pause
        exit /b 1
    )
    echo Estrazione completata.

    :: === Pulizia ===
    echo Eliminazione del file ZIP temporaneo...
    del "%TEMP%\%ZIP_NAME%"
    echo Pulizia completata.

    :: === Avvio del gioco ===
    echo Avvio di "%EXE_NAME%"...
    start "" "%GAME_PATH%\%EXE_NAME%"
)

:: Mantiene la finestra del prompt dei comandi aperta alla fine, utile per vedere eventuali messaggi di errore.
pause
:: Ripristina lo stato iniziale delle variabili d'ambiente.
endlocal
