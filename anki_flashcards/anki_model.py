import genanki


class LanguageNote(genanki.Note):

    @property
    def guid(self):
        return genanki.guid_for(self.fields[0])


LANGUAGE_MODEL = genanki.Model(
    1498237801,
    'Language Model',
    fields=[
        {'name': 'Id'},
        {'name': 'Question', 'font': 'Arial'},
        {'name': 'Answer', 'font': 'Arial'},
        {'name': 'Audio'},
    ],
    templates=[
        {
            'name': 'Card 1',
            'qfmt': '{{Question}}<br>{{#Audio}}<div class="optional-media">{{Audio}}</div>{{/Audio}}',
            'afmt': '{{FrontSide}}<hr id="answer">{{Answer}}',
        },
    ],
    css='.card {\n font-family: arial;\n font-size: 20px;\n text-align: center;\n color: black;\n background-color: white;\n}\n'
)
