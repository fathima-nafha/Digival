import pytesseract
import cv2
import re
from autocorrect import spell
import time

try:
    from PIL import Image
except ImportError:
    import Image


def recognize( filepath ):

    # val = pytesseract.image_to_string(Image.open(filepath), lang='LanguageTrain+eng')
    # return val
    try:
        img = cv2.imread(filepath)
        img = cv2.resize(img, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        val = pytesseract.image_to_string(Image.open(filepath), lang = 'LanguageTrain+eng')
        return val
    except:
        return -1


def evaluate_paper(results, db_answer):
    val = results.splitlines()
    print(val)

    final_str = list()
    for everyLine in val:
        cleanString = re.sub('\W+', '', everyLine)
        final_str.append(cleanString.lower())
    new_str = list()

    score = 0
    print(new_str)
    print(db_answer)
    for key, val in db_answer.items():
        val = val.lower()

    for key, val in db_answer.items():
        print(key, val)
        for item in final_str:
            if val.lower() in item:
                score+=1
            elif (item.startswith(key)) and (val in spell(item[1:])):
                print(spell(item[1:]))
                score += 1
            elif val in spell(item):
                print(spell(item))
                score += 1
            elif val in spell(item[1:]):
                score += 1
        print(score)
    return score


