class Languages:
    English = 'english'
    Spanish = 'spanish'


CurrentLanguage = Languages.Spanish


def set_language(lang):
    global CurrentLanguage
    CurrentLanguage = lang


EnglishDictionary = {
    'Cancel': 'Cancel',
    'Cancelled!': 'Cancelled!',
    'Choose Input File..': 'Choose Input File..',
    'Choose Weather File..': 'Choose Weather File..',
    'Close': 'Close',
    'E+ Version': 'E+ Version',
    'EnergyPlus Failed': 'EnergyPlus Failed',
    'EnergyPlus Failed!': 'EnergyPlus Failed!',
    'EnergyPlus Launch Light': 'EnergyPlus Launch Light',
    'EnergyPlus Simulation Output:': 'EnergyPlus Simulation Output:',
    'EPW files': 'EPW files',
    'Error file is the best place to start.  Would you like to open the Run Folder?':
        'Error file is the best place to start.  Would you like to open the Run Folder?',
    'IDF files': 'IDF files',
    'Input and/or Weather file paths are invalid': 'Input and/or Weather file paths are invalid',
    'Message': 'Message',
    'Open Run Directory': 'Open Run Directory',
    'Ready for launch': 'Ready for launch',
    'Restart the app to make the language change take effect':
        'Restart the app to make the language change take effect',
    'Select input file': 'Select input file',
    'Select weather file': 'Select weather file',
    'Simulate': 'Simulate',
    'Simulation Output': 'Simulation Output',
    'Simulation completed': 'Simulation completed',
    'Simulation failed': 'Simulation failed',
    'Simulation started': 'Simulation started',
    'Switch language': 'Switch language'
}

SpanishDictionary = {
    'Cancel': 'Cancelar',
    'Cancelled!': 'Cancelado!',
    'Choose Input File..': 'Elija el archivo de entrada..',
    'Choose Weather File..': 'Elija Tiempo Archivo..',
    'Close': 'Cerca',
    'E+ Version': 'E+ Version',
    'EnergyPlus Failed': 'EnergyPlus fallado',
    'EnergyPlus Failed!': 'EnergyPlus fallado!',
    'EnergyPlus Launch Light': 'EnergyPlus Launch Light',
    'EnergyPlus Simulation Output:': 'EnergyPlus salida de la simulacion:',
    'EPW files': 'EPW archivos',
    'Error file is the best place to start.  Would you like to open the Run Folder?':
        'Archivo de errores es el mejor lugar para empezar. Le gustaria abrir la carpeta Run?',
    'IDF files': 'IDF archivos',
    'Input and/or Weather file paths are invalid': 'Las rutas de entrada y/o archivos de tiempo no son validos',
    'Message': 'Mensaje',
    'Open Run Directory': 'Directorio de ejecucion abierta',
    'Ready for launch': 'Listo para su lanzamiento',
    'Restart the app to make the language change take effect':
        'Reiniciar la aplicacion para que el cambio de idioma surtiran efecto',
    'Select input file': 'Seleccionar archivo de entrada',
    'Select weather file': 'Seleccionar archivo de tiempo',
    'Simulate': 'Simular',
    'Simulation Output': 'Salida de la simulacion',
    'Simulation completed': 'Simulacion completado',
    'Simulation failed': 'Simulacion fallo',
    'Simulation started': 'Simulacion comenzo',
    'Switch language': 'Cambiar de idioma'
}


def report_missing_keys():
    base_keys = EnglishDictionary.keys()
    for dict_name, dictionary in {'Spanish': SpanishDictionary}.iteritems():  # add more here
        print("Processing missing keys from dictionary: " + dict_name)
        for key in base_keys:
            if key not in dictionary:
                print("Could not find key: \"%s\"" % key)


def translate(key):

    # if for some reason blank, just return blank
    if key is None or key == "":
        return ""

    # if English, just return the original key without looking anything up
    if CurrentLanguage == Languages.English:
        return key

    # otherwise, start with English, but swtich based on language
    dictionary = EnglishDictionary
    if CurrentLanguage == Languages.Spanish:
        dictionary = SpanishDictionary

    # if the key is there, return it, otherwise return a big flashy problematic statement
    if key in dictionary:
        return dictionary[key]
    else:
        print("Could not find this key in the dictionary: \"%s\"" % key)
        return "TRANSLATION MISSING"
