
class Body:
    def __init__(self):
        self.organs = {
            'mouth': Mouth(),
            'nose': Nose(),
            'ears': Ears(),
            'stomach': Stomach(),
        }

        self.lymph_system = {
            'thymus': Thymus(),
            'spleen': Spleen(),
            'pelvic node': PelvicNode(),
            'bone marrow': BoneMarrow(),
        }


class Organ:
    def __init__(self):
        self.present_antigens = []
        self.present_pathogens = []
        self.present_cells = []
        self.present_antibodies = []
        self.modifiers = []


class Mouth(Organ):
    pass

class Eyes(Organ):
    pass

class Nose(Organ):
    pass

class Ears(Organ):
    pass

class Throat(Organ):
    pass

class Heart(Organ):
    pass

class Thymus(Organ):
    pass

class PelvicNode(Organ):
    pass

class BoneMarrow(Organ):
    pass

class Lungs(Organ):
    pass

class Spleen(Organ):
    pass

class Stomach(Organ):
    pass

class Intestines(Organ):
    pass



