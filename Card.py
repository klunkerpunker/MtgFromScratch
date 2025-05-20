class Face:
    def __init__(self, data:dict):
        self.name = data['name']
        self.mana_cost = data['mana_cost']
        self.type_line = data['type_line']
        self.oracle = data['oracle_text']
        self.colors = data['colors'] if 'colors' in data else None

        self.power = data['power'] if 'power' in data else None
        self.toughness = data['toughness'] if 'toughness' in data else None
        self.loyalty = data['loyalty'] if 'loyalty' in data else None
        self.defence = data['defence'] if 'defence' in data else None

    def to_dict(self):
        """Convert Face to a serializable dictionary"""
        return {
            'name': self.name,
            'mana_cost': self.mana_cost,
            'type_line': self.type_line,
            'oracle_text': self.oracle,
            'colors': self.colors,
            'power': self.power,
            'toughness': self.toughness,
            'loyalty': self.loyalty,
            'defence': self.defence
        }


class Card:
    def __init__(self,data:dict):
        self.name = data['name']
        self.layout = data['layout']
        self.cmc = data['cmc']
        self.colors = data['colors'] if 'colors' in data else None
        self.color_id = data['color_identity']

        self.faces = self.init_faces(data)

        self.abilities = []
        self.zone = None
        self.tapped = False
        self.counters = {}

    def init_faces(self, data:dict):
        """Initialize faces with proper dictionary structure"""
        faces = {}
        if 'card_faces' in data:
            for i, face_data in enumerate(data['card_faces'], 1):
                faces[f'Face{i}'] = Face(face_data)
        else:
            faces['Face1'] = Face(data)
        return faces

    def to_dict(self):
        """Convert Card to a serializable dictionary"""
        return {
            'name': self.name,
            'layout': self.layout,
            'cmc': self.cmc,
            'colors': self.colors,
            'color_identity': self.color_id,
            'faces': {name: face.to_dict() for name, face in self.faces.items()},
        }




