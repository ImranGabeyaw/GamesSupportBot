# TODO IMPLEMENT POCKET ITEM RECOGNITION
import sys
sys.path.append('OCR/.virtualenvs/ocr_server-EItdhW8L/Lib/site-packages')
try:
    from PIL import Image, ImageEnhance
except ImportError:
    import Image, ImageEnhance
import pytesseract

class BadImageError(ValueError):
    pass

single = [[8,16,24,32,40,48,56], [9,18,27,36,45,54,63], [11,12,33,44,55,66,77]]
double = [[4,8,12,16,20,24,28], [5,10,15,20,25,30,35], [6,12,18,24,30,36,42]]

def ocr_core(filename):
    """
    This function will handle the core OCR processing of images.
    """
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    img = Image.open(filename)
    enhanced = ImageEnhance.Color(img).enhance(0.0)
    enhanced = ImageEnhance.Sharpness(enhanced).enhance(2.0)
    enhanced = enhanced.resize([int(2 * s) for s in enhanced.size])
    # enhanced.save('result.png')
    text = pytesseract.image_to_string(enhanced)  # We'll use Pillow's Image class to open the image and pytesseract to detect the string in the image
    return text

#parses text to build a flame profile for the item and returns a flame based off that profile
def parse(text):
    level = 0
    strength = 0
    dex = 0
    intel = 0
    luk = 0
    attack = 0
    magicattack = 0
    allstat = 0
    advantaged = True
    text = text.replace(" ", "")
    text = text.upper()
    pocket = False
    if "POCKET" in text:
        pocket = True
    for item in text.split("\n"):
        if "REQLE" in item and "(" not in item:
            start = item.find(":")+1
            end =  len(item)
            level = int(item[start:end])
        if "REQLE" in item and "(" in item:
            start = item.find(":")+1
            end = item.find("(")
            level = item[start:end] 
            start = item.find("-")+1
            end = item.find(")")
            level = int(level) + int(item[start:end])  
        if "GOLLUX" in item or "TATTOO" in item:
            advantaged = False
        if "STR" in item and "%" not in item and "(" in item:
            start = item.find("(")+1
            end = item.find(")")
            item = item[start:end]
            item = item.split("+")
            if len(item) >= 3 or item[0] == '0':
                strength = int(item[1])
            if pocket and len(item) >= 2 or item[0] == '0':
                strength = int(item[1])
        elif "DEX" in item and "%" not in item and "(" in item:
            start = item.find("(")+1
            end = item.find(")")
            item = item[start:end]
            item = item.split("+")
            if len(item) >= 3 or item[0] == '0':
                dex = int(item[1])
            if pocket and len(item) >= 2 or item[0] == '0':
                dex = int(item[1])
        elif "INT" in item and "%" not in item and "(" in item:
            start = item.find("(")+1
            end = item.find(")")
            item = item[start:end]
            item = item.split("+")
            if len(item) >= 3 or item[0] == '0':
                intel = int(item[1])
            if pocket and len(item) >= 2 or item[0] == '0':
                intel = int(item[1])
        elif "LUK" in item and "%" not in item and "(" in item:
            start = item.find("(")+1
            end = item.find(")")
            item = item[start:end]
            item = item.split("+")
            if len(item) >= 3 or item[0] == '0':
                luk = int(item[1])
            if pocket and len(item) >= 2 or item[0] == '0':
                luk = int(item[1])
        elif "ATTACKPOWER" in item and "%" not in item and "(" in item:
            start = item.find("(")+1
            end = item.find(")")
            item = item[start:end]
            item = item.split("+")
            if len(item) >= 3:
                attack = int(item[1])
            if pocket and len(item) >= 2:
                attack = int(item[1])
        elif "MAGICATTACK" in item and "%" not in item and "(" in item:
            start = item.find("(")+1
            end = item.find(")")
            item = item[start:end]
            item = item.split("+")
            if len(item) >= 3:
                magicattack = int(item[1])
            if pocket and len(item) >= 2:
                magicattack = int(item[1])
        elif "ALLSTATS" in item and "(" in item:
            start = item.find("(")+1
            end = item.find(")")
            item = item[start:end]
            item = item.split("+")
            if len(item) >= 2:
                allstat = int(item[1][0])
            if pocket and len(item) >= 2:
                allstat = int(item[1][0])
    flame = Flame(level, strength, dex, intel, luk, attack, magicattack, allstat, advantaged)
    return flame


def is_valid_image(flame):
    return flame.flame_stats() != ""

def is_Image(attachment):
    url = attachment.url
    return url.find("png", len(url) - len("png")) != -1 or url.find("jpeg", len(url) - len("jpeg")) != -1


class Flame:
    def __init__(self, level=0, strength=0, dex=0, intel=0, luk=0, attack=0, magicattack=0, allstat=0, advantaged=True):
        self._level = level
        self._strength = strength
        self._dex = dex
        self._intel = intel
        self._luk = luk
        self._attack = attack
        self._magicattack = magicattack
        self._allstat = allstat
        self._advantaged = advantaged
        #firstpos level 150 items, secondpos 160 items, thirdpos 200 items
        self._early_settle = [85, 100, 115]
        self._early_cost = [0.4, 0.7, 0.7]
        self._midgame_settle = [105, 115, 130]
        self._midgame_cost = [2.4, 2.4, 2.3]
        self._endgame_settle = [120, 130, 150]
        self._endgame_cost = [18.1, 14.2, 17.4]
        #firstpos early game, secondpos mid game, thirdpos late game
        self._nonadvantaged_settle = [27, 45, 60]
        self._nonadvantaged_cost = [0.1, 1.5, 10.8]

    # Returns a string of the flame's stats to be printed
    def flame_stats(self):
        text = ""
        if self._strength != 0:
            text += "STR: " + str(self._strength) + ", "
        if self._dex != 0:
            text += "DEX: " + str(self._dex) + ", "
        if self._intel != 0:
            text += "INT: " + str(self._intel) + ", "
        if self._luk != 0:
            text += "LUK: " + str(self._luk) + ", "
        if self._attack != 0:
            text += "ATTACK: " + str(self._attack) + ", "
        if self._magicattack != 0:
            text += "MATTACK: " + str(self._magicattack) + ", "
        if self._allstat != 0:
            text += "ALLSTAT: " + str(self._allstat) + "%, "
        text = text[0:len(text)-2]
        if text == "":
            raise BadImageError("The image is either poorly cropped or not an image of a Maplestory item. The flame stats were not properly parsed.")
        return text

    # Returns the flamescore of a flame using the highest value stat as
    # the assumed stat for the class.
    # 1 as% = 9 flat stat
    # 1 attack = 2 main stat
    # 1 main stat = 11 secondary stat
    def flame_score(self):
        mainstat = max(self._strength, self._dex, self._intel, self._luk)
        if mainstat == self._strength:
            return str("{:.2f}".format(self._strength + self._secondary_stat(self._dex) + self._attack_equiv(self._attack) + self._attack_equiv(self._attack) + self._all_stat(self._allstat))) + "** Str**"
        elif mainstat == self._dex:
            return str("{:.2f}".format(self._dex + self._secondary_stat(self._strength) + self._attack_equiv(self._attack) + self._attack_equiv(self._attack) + self._all_stat(self._allstat))) + "** Dex**"
        elif mainstat == self._intel:
            return str("{:.2f}".format(self._intel + self._secondary_stat(self._luk) + self._attack_equiv(self._attack) + self._attack_equiv(self._attack) + self._all_stat(self._allstat))) + "** Int**"
        elif mainstat == self._luk:
            return str("{:.2f}".format(self._luk + self._secondary_stat(self._dex) + self._attack_equiv(self._attack) + self._attack_equiv(self._attack) + self._all_stat(self._allstat))) + "** Luk**"
        raise BadImageError("The image is either poorly cropped or not an image of a Maplestory item. The flame stats were not properly parsed.")

    def flame_recommendation(self):
        score = int(float(self.flame_score()[0:5]))
        if self._advantaged:
            if self._level == 150:
                if score in range(0, self._early_settle[0]):
                    return "This flame is very easy to reroll. Consider rerolling if you are willing to spend **" + str(self._early_cost[0]) + "B**"
                if score in range(self._early_settle[0], self._midgame_settle[0]):
                    return "Early-game flame. Consider rerolling if you are willing to spend **" + str(self._midgame_cost[0]) + "B**"
                if score in range(self._midgame_settle[0], self._endgame_settle[0]):
                    return "Mid-game flame. Consider rerolling if you are willing to spend **" + str(self._endgame_cost[0]) + "B**"
                if score >= self._endgame_settle[0]:
                    return "End-game flame. Come to your own conclusion on whether to reroll"
            if self._level == 160:
                if score in range(0, self._early_settle[1]):
                    return "This flame is very easy to reroll. Consider rerolling if you are willing to spend **" + str(self._early_cost[1]) + "B**"
                if score in range(self._early_settle[1], self._midgame_settle[1]):
                    return "Early-game flame. Consider rerolling if you are willing to spend **" + str(self._midgame_cost[1]) + "B**"
                if score in range(self._midgame_settle[1], self._endgame_settle[1]):
                    return "Mid-game flame. Consider rerolling if you are willing to spend **" + str(self._endgame_cost[1]) + "B**"
                if score >= self._endgame_settle[1]:
                    return "End-game flame. Come to your own conclusion on whether to reroll"
            if self._level == 200:
                if score in range(0, self._early_settle[2]):
                    return "This flame is very easy to reroll. Consider rerolling if you are willing to spend **" + str(self._early_cost[2]) + "B**"
                if score in range(self._early_settle[2], self._midgame_settle[2]):
                    return "Early-game flame. Consider rerolling if you are willing to spend **" + str(self._midgame_cost[2]) + "B**"
                if score in range(self._midgame_settle[2], self._endgame_settle[2]):
                    return "Mid-game flame. Consider rerolling if you are willing to spend **" + str(self._endgame_cost[2]) + "B**"
                if score >= self._endgame_settle[2]:
                    return "End-game flame. Come to your own conclusion on whether to reroll"
        else:
            if score in range(0, self._nonadvantaged_settle[0]):
                return "**Gollux Item;** This flame is very easy to reroll. Consider rerolling if you are willing to spend **" + str(self._nonadvantaged_cost[0]) + "B**"
            if score in range(self._nonadvantaged_settle[0], self._nonadvantaged_settle[1]):
                return "**Gollux Item;** Early-game flame. Consider rerolling if you are willing to spend **" + str(self._nonadvantaged_cost[1]) + "B**"
            if score in range(self._nonadvantaged_settle[1], self._nonadvantaged_settle[2]):
                return "**Gollux Item;** Mid-game flame. Consider rerolling if you are willing to spend **" + str(self._nonadvantaged_cost[2]) + "B**"
            if score >= self._nonadvantaged_settle[2]:
                return "**Gollux Item;** End-game flame. Come to your own conclusion on whether to reroll"
        raise BadImageError("The image is poorly cropped. The item level was not properly parsed.")

    def item_level(self):
        return self._level

    def _secondary_stat(self, value):
        return value / 11

    def _attack_equiv(self, value):
        return value * 3

    def _all_stat(self, value):
        return value * 9