## In Game

### Bauen

#### Objekt erschaffen (create)

`create[/drop] <objname>[;alias;alias...][:typeclass]`

#### Raum bauen

`dig[/teleport] <raumname>[;alias;alias...] = <ausgang_nach_dort>[;alias] , <ausgang_von_dort_hierher>[;alias]`

Beispiel:

`dig Felsvorsprung = hochklettern;hoch, runterklettern;runter`

`dig Haus Nr. 21 = Haus Nr. 21;Nr. 21;21, Haustür;Tür`

#### Ausgang bauen

`open <neuer_ausgang>[;alias;alias..] ,<rückweg_ausgang>[;alias;..] = <zielraum>`

Beispiel:
(z.B. vom Felsvorsprung aus, angenommen es gibt einen Raum "Schlucht")

(`dig Schlucht`)

`open in die Schlucht abseilen;abseilen = Schlucht`

#### Prototypen spawnen

`spawn <prototype>`

Verfügbare Prototypen auflisten:

`spawn/list`

#### Objekte zerstören (destroy)

`destroy <obj1>, <obj2>, ...`

Beispiel:

`destroy stein`

`destroy #13`

#### Objekteigenschaften untersuchen (examine)

aktuellen Raum untersuchen:

`examine <obj>`

Objekt bzw. Objektattribut untersuchen:

`examine <obj>`

`examine <object>/<attrname>`

#### Objekte suchen

`find <obj_name>`

#### Teleportieren

Mich selbst teleportieren:

`tel <zielort>`

Objekt teleportieren:

`tel <obj> = <zielort>`

#### Objekt umbenennen

`name <obj> = <neuer_name>`

`name <obj> = <neuer_name>;<alias1>;<alias2>`

#### Pseudonyme (aliases)

Aliase anzeigen:

`alias <obj>`

Aliase hinzufügen:

`alias <obj> = <alias1>,<alias2>,...`

Alias entfernen:

`alias/delete <obj> = <alias>`

#### Beschreibung (description)

`@desc <obj> = <beschreibung>`

#### Attribute

Attribut setzen:

`@set <obj>/<attr>[:category] = wert`

Beispiel:

`@set apfel/plural = Äpfel`

`@set apfel/gender = m`

Attribut löschen:

`@set/delete <obj>/<attr>`
oder
`@wipe <object>[/<attr>]`

#### Tags

`tag <obj> = <tag>:<category>`

`tag/del <obj> = <tag>:<category>`

`tag/search <tag>:<category>`

Beispiel: Tag setzen

`tag holz = holz:crafting_material`

Beispiel: Objekte nach Tag suchen

`tag/search :crafting_material`

`tag/search holz:crafting_material`

Beispiel: Geschlecht (gender) ändern (z.B. zu weiblich: 'f'):

`tag/del <obj> = :gender`

`tag <obj> = f:gender`

#### Locks

`@lock <obj> = <lockstring>`

Beispiel: Nicht aufnehmbar (z.B. für "feste" Gegenstände):

`@lock brunnen = get:false()`

Beispiel: Versteckter Ausgang mittels Tag (z.B. "found_exit" aus Kategorie "hidden"):

`@lock notausgang = view:tag(found_exit, hidden) ; traverse:tag(found_exit, hidden)`

#### Handlung fernsteuern

`force <obj> = <kommando>`

Beispiel:
`force Spieler1 = nimm Stein`

### Manipupation durch py

#### Heilen/Schaden

`py c = me.search("testuser"); c.heal(10)`

`py c = me.search("testuser"); c.damage(10)`

#### Infoleiste eines Charakters anzeigen 

`py self.msg(self.search("#3").get_prompt())`

#### Infoleiste eines Charakters aktualisieren

`py self.search("#3").update_prompt()`
