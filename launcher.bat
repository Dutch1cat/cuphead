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
set "GITHUB_ZIP_URL=https://github.com/YOUR_USERNAME/YOUR_REPO_NAME/releases/download/YOUR_TAG/bloop.zip"

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
    set "DOWNLOAD_PATH=%TEMP%\%ZIP_NAME%"
    powershell -Command "(New-Object System.Net.WebClient).DownloadFile('%GITHUB_ZIP_URL%', '%DOWNLOAD_PATH%')"
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

    :: === Estrazione del file ZIP in una cartella temporanea dedicata ===
    :: Questa cartella temporanea si userà SOLO per l'estrazione iniziale.
    set "EXTRACT_TEMP_DIR=%TEMP%\SlimeSoulsExtracted"
    echo Eliminazione di vecchi file temporanei di estrazione (se presenti)...
    if exist "%EXTRACT_TEMP_DIR%" rd /s /q "%EXTRACT_TEMP_DIR%" >nul 2>nul
    mkdir "%EXTRACT_TEMP_DIR%" >nul 2>nul

    echo Estrazione di "%ZIP_NAME%" in "%EXTRACT_TEMP_DIR%"...
    powershell -Command "Expand-Archive -Path '%DOWNLOAD_PATH%' -DestinationPath '%EXTRACT_TEMP_DIR%' -Force"
    if errorlevel 1 (
        echo Errore: Impossibile estrarre "%ZIP_NAME%" in "%EXTRACT_TEMP_DIR%".
        pause
        goto :cleanup_and_exit
    )
    echo Estrazione completata nella cartella temporanea.

    :: === Spostamento del contenuto estratto nella directory finale del gioco ===
    set "ACTUAL_GAME_ROOT_FOUND=false"
    set "SOURCE_DIR_FOR_MOVE="

    :: Cerca il file menu.exe all'interno della cartella temporanea di estrazione.
    :: Questo ci aiuta a trovare la vera "radice" del gioco all'interno del file zip.
    for /f "delims=" %%A in ('dir /s /b "%EXTRACT_TEMP_DIR%\%EXE_NAME%"') do (
        set "SOURCE_DIR_FOR_MOVE=%%~dpA"
        set "ACTUAL_GAME_ROOT_FOUND=true"
        goto :found_game_root
    )

    :found_game_root
    if "%ACTUAL_GAME_ROOT_FOUND%"=="true" (
        echo Spostamento del contenuto del gioco da "%SOURCE_DIR_FOR_MOVE%" a "%GAME_PATH%"...
        :: Sposta tutti i contenuti (file e sottocartelle) dalla radice del gioco estratto alla cartella finale
        move /y "%SOURCE_DIR_FOR_MOVE%\*" "%GAME_PATH%\" >nul
        if errorlevel 1 (
            echo Errore durante lo spostamento dei file.
            pause
            goto :cleanup_and_exit
        )
        :: Elimina la cartella radice del gioco estratto una volta svuotata
        if exist "%SOURCE_DIR_FOR_MOVE%" rd /s /q "%SOURCE_DIR_FOR_MOVE%" >nul 2>nul
    ) else (
        echo Errore: "%EXE_NAME%" non trovato nel file ZIP estratto. Assicurati che il file ZIP sia corretto.
        pause
        goto :cleanup_and_exit
    )

    :: === Pulizia della cartella di estrazione temporanea ===
    echo Pulizia della cartella di estrazione temporanea...
    if exist "%EXTRACT_TEMP_DIR%" rd /s /q "%EXTRACT_TEMP_DIR%" >nul 2>nul

    :: === Pulizia del file ZIP temporaneo ===
    :cleanup_and_exit
    echo Eliminazione del file ZIP temporaneo...
    if exist "%DOWNLOAD_PATH%" del "%DOWNLOAD_PATH%" >nul 2>nul
    echo Pulizia completata.

    :: === Avvio del gioco ===
    echo Avvio di "%EXE_NAME%"...
    start "" "%GAME_PATH%\%EXE_NAME%"
)

:: Mantiene la finestra del prompt dei comandi aperta alla fine, utile per vedere eventuali messaggi di errore.
pause
:: Ripristina lo stato iniziale delle variabili d'ambiente.
endlocal
