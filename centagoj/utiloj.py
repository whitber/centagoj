import random

def get_band_name():

    urboj = [
        "Tokio",
        "Meksik-urbo",
        "Novjorko",
        "Seulo",
        "Sao-Paŭlo",
        "Osako",
        "Mumbajo",
        "Delhio",
        "Los-Anĝeleso",
        "Ĝakarto",
        "Teherano",
        "Kairo",
        "Kalkato",
        "Bonaero",
        "Manilo",
        "Moskvo",
        "Karaĉio",
        "Ŝanhajo",
        "Rio-de-Ĵanejro",
        "Londono",
        "Istanbulo",
        "Dako",
        "Parizo",
        "Ĉikago",
        "Lagoso",
        "Pekino",
        "Nagojo",
        "Limo",
        "Vaŝingtono",
        "Bogoto",
        "Bankoko",
        "Santiago",
    ]
    dombestoj = ['hundo','kato','hamstro','kavio','furo','muso','kuniklo',
    'birdo','fiŝo', 'araneo', 'krokodilo', 'rato', 'serpento', 
    'simio', 'skorpiono']

    urbo = random.choice(urboj).capitalize()
    besto = random.choice(dombestoj).capitalize()

    return f"{urbo} {besto}"
