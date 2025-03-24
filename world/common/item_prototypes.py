# ITEMS "crafting_material"

APFEL = {
    "typeclass": "typeclasses.items.Item",
    "key": "Apfel",
    "plural": "Äpfel",
    # "gender": "m",
    "desc": "Ein ganz normaler Apfel.",
    "weight": 0.1,
    "tags": [("apfel", "crafting_material"), ("m", "gender")],
}

HOLZ = {
    "typeclass": "typeclasses.items.Item",
    "key": "Holz",
    # "plural": "Hölzer",
    # "gender": "n",
    "desc": "Ein Stück Holz.",
    "weight": 1,
    "fuel": 10 * 60,
    "tags": [("holz", "crafting_material")],
}

GRAS = {
    "typeclass": "typeclasses.items.Item",
    "key": "Gras",
    # "plural": "Gräser",
    # "gender": "n",
    "desc": "Ein Büschel Gras.",
    "weight": 0.1,
    "fuel": 2 * 60,
    "tags": [("gras", "crafting_material")],
}

STEIN = {
    "typeclass": "typeclasses.items.Item",
    "key": "Stein",
    "plural": "Steine",
    # "gender": "m",
    "desc": "Ein mittelgroßer Stein.",
    "weight": 4,
    "tags": [("stein", "crafting_material"), ("m", "gender")],
}

HARTHOLZ = {
    "typeclass": "typeclasses.items.Item",
    "key": "Hartholz",
    # "plural": "Harthölzer",
    # "gender": "n",
    "desc": "Diese seltene Art von Holz ist doppelt so hart wi gewöhnliches Holz und brennt länger.",
    "weight": 1.5,
    "fuel": 15 * 60,
    "tags": [("hartholz", "crafting_material")],
}

GETROCKNETES_GRAS = {
    "typeclass": "typeclasses.items.Item",
    "key": "Getrocknetes Gras",
    "desc": "Dieses Gras wurde einige Tage getrocknet.",
    "weight": 0.2,
    "fuel": 3 * 60,
    "tags": [("getrocknetes_gras", "crafting_material")],
}

REET = {
    "typeclass": "typeclasses.items.Item",
    "key": "Reet",
    "desc": "Hohes, trockenes Gras. Lässt sich gut als Dachbelag verwenden.",
    "weight": 0.2,
    "fuel": 2 * 60,
    "tags": [("reet", "crafting_material")],
}

LEHM = {
    "typeclass": "typeclasses.items.Item",
    # "gender": "m",
    "desc": "Ein weicher Klumpen Lehm. Aus ihm lassen sich viele verschiedene Dinge formen — also hauche ihm Leben ein!",
    "key": "Lehmklumpen",
    "aliases": ["Lehm"],
    "weight": 0.5,
    "tags": [("lehm", "crafting_material"), ("m", "gender")],
}

FEUERHOLZ = {
    "typeclass": "typeclasses.items.Item",
    "key": "Feuerholz",
    "desc": "Dieses (meistens gekaufte) Holz brennt lange und heiß.",
    "weight": 2,
    "fuel": 30 * 60,
    "tags": [("feuerholz", "crafting_material")],
}

KOHLE = {
    "typeclass": "typeclasses.items.Item",
    "key": "Kohle",
    # "gender": "f",
    "plural": "Kohlen",
    "desc": "Dieser schwarze Klumpen lässt ein entzündetes Feuer viel länger und heißer brennen",
    "weight": 3,
    "fuel": 60 * 60,
    "tags": [("kohle", "crafting_material"), ("f", "gender")],
}

LEDER = {
    "typeclass": "typeclasses.items.Item",
    "key": "Leder",
    "desc": "Das Leder fühlt sich zäh an. Es ist wertvoll und gut, um Kleidung daraus herzustellen.",
    "weight": 2,
    "tags": [("leder", "crafting_material")],
}

ROBUSTES_LEDER = {
    "typeclass": "typeclasses.items.Item",
    "key": "Robustes Leder",
    "desc": "Dieses Leder ist selten, sehr robust und wertvoll.",
    "weight": 3,
    "tags": [("robustes_leder", "crafting_material")],
}

FELL = {
    "typeclass": "typeclasses.items.Item",
    "key": "Fell",
    "plural": "Felle",
    "desc": "Es ist flauschig weich und sehr, sehr wertvoll. Eignet sich für schöne und gemütliche Kleidung.",
    "weight": 3.5,
    "tags": [("fell", "crafting_material")],
}

STOFF = {
    "typeclass": "typeclasses.items.Item",
    "key": "Stoff",
    "plural": "Stoffe",
    "desc": "Dieser Stoff fühlt sich rau an.",
    "weight": 0.5,
    "tags": [("stoff", "crafting_material"), ("m", "gender")],
}

WEICHER_STOFF = {
    "typeclass": "typeclasses.items.Item",
    "key": "weicher Stoff",
    "plural": "weiche Stoffe",
    "accusative": "weichen Stoff",
    # "gender": "m",
    "desc": "Dieser Stoff ist weich. Er ist gut für Kleidung.",
    "weight": 0.75,
    "tags": [("weicher_stoff", "crafting_material"), ("m", "gender")],
}

MAUERSTEIN = {
    "typeclass": "typeclasses.items.Item",
    "key": "Mauerstein",
    "plural": "Mauersteine",
    # "gender": "m",
    "desc": "Ein großer, runder Stein, der gut für Mauern ist",
    "weight": 9,
    "tags": [("mauerstein", "crafting_material"), ("m", "gender")],
}

ZIEGELSTEIN = {
    "typeclass": "typeclasses.items.Item",
    "key": "Ziegelstein",
    "plural": "Ziegelsteine",
    # "gender": "m",
    "desc": "Ein rechteckiger Stein. Gut für Mauern oder auch als Dachziegel nützlich.",
    "weight": 7,
    "tags": [("ziegelstein", "crafting_material"), ("m", "gender")],
}

TIEFENSTEIN = {
    "typeclass": "typeclasses.items.Item",
    "key": "Tiefenstein",
    # "gender": "m",
    "plural": "Tiefensteine",
    "desc": "Ein kleiner, aber schwerer schwarzer Stein.",
    "weight": 10,
    "tags": [("tiefenstein", "crafting_material"), ("m", "gender")],
}

EDELSTEIN = {
    "typeclass": "typeclasses.items.Item",
    "key": "Edelstein",
    # "gender": "m",
    "plural": "Edelsteine",
    "desc": "Dieser schöne Stein funkelt und glänzt im Licht. Er ist viel wert!",
    "weight": 7,
    "tags": [("edelstein", "crafting_material"), ("m", "gender")],
}

MAGIESTEIN = {
    "typeclass": "typeclasses.items.Item",
    "key": "Magiestein",
    # "gender": "m",
    "plural": "Magiesteine",
    "desc": "Dieser orangefarbene Edelstein leuchtet im Dunkeln. Bei Berührungen zittert er stark. Er ist bei Händlern sehr begehrt, ist aber auch als Werkstoff wertvoll.",
    "weight": 5,
    "tags": [("magiestein", "crafting_material"), ("m", "gender")],
}

MAGIESTEIN_2 = {
    "typeclass": "typeclasses.items.Item",
    "key": "Magiestein LV2",
    # "gender": "m",
    "plural": "Magiesteine LV2",
    "desc": "Dieser violettfarbene Edelstein leuchtet für Magier hell, zittert in deren Händen und sie können ihn durch Wände sehen. In ihm befindet sich konzentrierte Magie",
    "weight": 6,
    "tags": [("magiestein_2", "crafting_material"), ("m", "gender")],
}

DIAMANT = {
    "typeclass": "typeclasses.items.Item",
    "key": "Diamant",
    # "gender": "m",
    "plural": "Diamanten",
    "accusative": "Diamanten",
    "desc": "Dieser weiß-hellblaue Edelstein ist von unfassbarem Wert.",
    "weight": 10,
    "tags": [("diamant", "crafting_material"), ("m", "gender")],
}

# TOOLS "crafting_tool"

KESSEL = {
    "typeclass": "typeclasses.items.Item",
    "key": "Kessel",
    # "gender": "m",
    "desc": "In diesem Kessel lassen sich Suppen und ähnliches zubereiten. Er ist beim Kochen unentbehrlich.",
    "weight": 3,
    "tags": [("kessel", "crafting_tool"), ("m", "gender")],
}

FEUERSTEIN = {
    "typeclass": "typeclasses.items.Item",
    "key": "Feuerstein",
    # "gender": "m",
    "desc": "Dieser schwarze Stein eignet sich zum Feuermachen.",
    "weight": 1,
    "tags": [("feuerstein", "crafting_tool"), ("m", "gender")],
}

# CONTAINERS

TRUHE = {
    "typeclass": "typeclasses.containers.Container",
    "key": "Truhe",
    "desc": "Eine gewöhnliche Holztruhe",
    "weight": 100,
    "capacity": 10,
    "tags": [("f", "gender")],
}
