# Validatore e generatore dei metadati JSON per i gestori di identità

Il presente tool richiede un unico argomento obbligatorio, cioè il nome (con percorso) del file JSON pre-generato contenente l'elenco dei nuovi metadati dei SP (prestatori di servizi).

Lo strumento convalida la sintassi JSON e la correttezza semantica del file, convalidando anche (qualora esista nel medesimo percorso) il file JSON secondario con gli URL dei metadati relativi al [registro SPID](https://registry.spid.gov.it) (anzichè all'URL locale del SP).
Qualora tale file secondario non esiste (il cio nome è identico al nome originario con '_registry' appeso alla fine), il file stesso è generato automaticamente.

Alcune pubbliche amministrazioni centrali possono richiedere un'ulteriore modifica manuale dell'URL del metadata relativo al registro SPID.

I file così convalidati sono pronto per l'invio agli IdP (gestori di identità digitale) affinché modifichino le proprie basi di dati.
