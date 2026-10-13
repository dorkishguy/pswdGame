from dataclasses import dataclass, replace, asdict
from captcha.image import ImageCaptcha
from typing import Optional
import random
import string
import datetime
import requests
import csv
import os
import dotenv
import re

dotenv.load_dotenv()

with open("elements.csv", newline="", encoding="utf-8") as f:
    ELEMENTS = {int(r["number"]): r["symbol"] for r in csv.DictReader(f)}
MONTHS = ("january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december")
ROMAN = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
SPONSORS = ("shell", "pepsi", "starbucks")
SYMBOLS = {s for s in ELEMENTS.values() if len(s) == 2}
COUNTRIES = ['aruba', 'afghanistan', 'angola', 'anguilla', 'åland islands', 'albania', 'andorra', 'united arab emirates', 'argentina', 'armenia', 'american samoa', 'antarctica', 'french southern territories', 'antigua and barbuda', 'australia', 'austria', 'azerbaijan', 'burundi', 'belgium', 'benin', 'bonaire, sint eustatius and saba', 'burkina faso', 'bangladesh', 'bulgaria', 'bahrain', 'bahamas', 'bosnia and herzegovina', 'saint barthélemy', 'belarus', 'belize', 'bermuda', 'bolivia, plurinational state of', 'brazil', 'barbados', 'brunei darussalam', 'bhutan', 'bouvet island', 'botswana', 'central african republic', 'canada', 'cocos (keeling) islands', 'switzerland', 'chile', 'china', "côte d'ivoire", 'cameroon', 'congo, the democratic republic of the', 'congo', 'cook islands', 'colombia', 'comoros', 'cabo verde', 'costa rica', 'cuba', 'curaçao', 'christmas island', 'cayman islands', 'cyprus', 'czechia', 'germany', 'djibouti', 'dominica', 'denmark', 'dominican republic', 'algeria', 'ecuador', 'egypt', 'eritrea', 'western sahara', 'spain', 'estonia', 'ethiopia', 'finland', 'fiji', 'falkland islands (malvinas)', 'france', 'faroe islands', 'micronesia, federated states of', 'gabon', 'united kingdom', 'georgia', 'guernsey', 'ghana', 'gibraltar', 'guinea', 'guadeloupe', 'gambia', 'guinea-bissau', 'equatorial guinea', 'greece', 'grenada', 'greenland', 'guatemala', 'french guiana', 'guam', 'guyana', 'hong kong', 'heard island and mcdonald islands', 'honduras', 'croatia', 'haiti', 'hungary', 'indonesia', 'isle of man', 'india', 'british indian ocean territory', 'ireland', 'iran, islamic republic of', 'iraq', 'iceland', 'israel', 'italy', 'jamaica', 'jersey', 'jordan', 'japan', 'kazakhstan', 'kenya', 'kyrgyzstan', 'cambodia', 'kiribati', 'saint kitts and nevis', 'korea, republic of', 'kuwait', "lao people's democratic republic", 'lebanon', 'liberia', 'libya', 'saint lucia', 'liechtenstein', 'sri lanka', 'lesotho', 'lithuania', 'luxembourg', 'latvia', 'macao', 'saint martin (french part)', 'morocco', 'monaco', 'moldova, republic of', 'madagascar', 'maldives', 'mexico', 'marshall islands', 'north macedonia', 'mali', 'malta', 'myanmar', 'montenegro', 'mongolia', 'northern mariana islands', 'mozambique', 'mauritania', 'montserrat', 'martinique', 'mauritius', 'malawi', 'malaysia', 'mayotte', 'namibia', 'new caledonia', 'niger', 'norfolk island', 'nigeria', 'nicaragua', 'niue', 'netherlands', 'norway', 'nepal', 'nauru', 'new zealand', 'oman', 'pakistan', 'panama', 'pitcairn', 'peru', 'philippines', 'palau', 'papua new guinea', 'poland', 'puerto rico', "korea, democratic people's republic of", 'portugal', 'paraguay', 'palestine, state of', 'french polynesia', 'qatar', 'réunion', 'romania', 'russian federation', 'rwanda', 'saudi arabia', 'sudan', 'senegal', 'singapore', 'south georgia and the south sandwich islands', 'saint helena, ascension and tristan da cunha', 'svalbard and jan mayen', 'solomon islands', 'sierra leone', 'el salvador', 'san marino', 'somalia', 'saint pierre and miquelon', 'serbia', 'south sudan', 'sao tome and principe', 'suriname', 'slovakia', 'slovenia', 'sweden', 'eswatini', 'sint maarten (dutch part)', 'seychelles', 'syrian arab republic', 'turks and caicos islands', 'chad', 'togo', 'thailand', 'tajikistan', 'tokelau', 'turkmenistan', 'timor-leste', 'tonga', 'trinidad and tobago', 'tunisia', 'türkiye', 'tuvalu', 'taiwan, province of china', 'tanzania, united republic of', 'uganda', 'ukraine', 'united states minor outlying islands', 'uruguay', 'united states', 'uzbekistan', 'holy see (vatican city state)', 'saint vincent and the grenadines', 'venezuela, bolivarian republic of', 'virgin islands, british', 'virgin islands, u.s.', 'viet nam', 'vanuatu', 'wallis and futuna', 'samoa', 'yemen', 'south africa', 'zambia', 'zimbabwe']
@dataclass(frozen=True)
class Ctx:
    captcha: str = ""
    wordle: str = ""
    moon: str = ""
    country: str = ""
    sender: str = ""
    sent_at: Optional[datetime.datetime] = None
    message_id: str = ""
    subject: str = ""


def rule1(x, ctx):
    return len(x) >= 5

def rule2(x, ctx):
    return any(char.isdecimal() for char in x)

def rule3(x, ctx):
    return any(char.isupper() for char in x)

def rule4(x, ctx):
    return any(not char.isalnum() and not char.isspace() for char in x)

def rule5(x, ctx):
    return sum(int(c) for c in x if c.isdecimal()) == 25

def rule6(x, ctx):
    return any(m in x.lower() for m in MONTHS)

def rule7(x, ctx):
    return any(r in x for r in ROMAN)

def rule8(x, ctx):
    return any(s in x.lower() for s in SPONSORS)

def rule9(x, ctx):
    product = 1
    i = 0
    while i < len(x):
        cur = ROMAN.get(x[i])
        if cur is None:
            i += 1
            continue
        nxt = ROMAN.get(x[i + 1]) if i + 1 < len(x) else None
        if nxt is not None and nxt > cur:
            product *= nxt - cur
            i += 2
        else: 
            product *= cur
            i += 1
    return product == 25

def genCaptcha():
    image = ImageCaptcha(fonts = ["./georgia.ttf"])
    chars = string.ascii_letters + string.digits
    txt = "".join(random.choices(chars, k=6))
    image.write(txt, "out.png")
    return txt

def rule10(x, ctx):
    return ctx.captcha in x

def todaysWordle(): 
    date = datetime.date.today()
    url = f"https://www.nytimes.com/svc/wordle/v2/{date:%Y-%m-%d}.json"
    response = requests.get(url).json()
    wordle = response['solution']
    return wordle

def rule11(x, ctx):
    return ctx.wordle in x

def rule12(x, ctx):
    return any(s in x for s in SYMBOLS)

def getMoon():
    return requests.get("https://api.apiverve.com/v1/moonphases?today=true", headers={"x-api-key": os.getenv("API-KEY")}).json()["data"]["phaseEmoji"]

def rule13(x, ctx):
    return ctx.moon in x

def randomCoutry():
    country = random.choice(COUNTRIES)
    return country

def rule14(x, ctx):
    return ctx.country in x.lower()

def isLeap(year):
    return (year % 4 == 0 and year % 100 != 0) or year % 400 == 0

def rule15(x, ctx):
    for n in re.findall(r"\d+", x):
        year = int(n)
        if year > 0 and isLeap(year):
            return True
    return False

def turn(rules):
    unlocked = 1 

    def submit(pswd, ctx):
        nonlocal unlocked
        while True:
            results = [(msg, hint, fn(pswd, ctx)) for fn, hint, msg in rules[:unlocked]]
            failed = not all(ok for _, _, ok in results)
            if failed or unlocked == len(rules):
                break
            unlocked += 1
        won = not failed and unlocked == len(rules)
        return results, unlocked, won       
    return submit

def main():
    base = Ctx(
    captcha = genCaptcha(),
    wordle = todaysWordle(),
    country = randomCoutry(),
    moon = getMoon()
    )

    rules = [
        (rule1,  None,                                  "Your password must be at least 5 characters."),
        (rule2,  None,                                  "Your password must include a number."),
        (rule3,  None,                                  "Your password must include an uppercase letter."),
        (rule4,  None,                                  "Your password must include a special character."),
        (rule5,  None,                                  "The digits in your password must add up to 25."),
        (rule6,  None,                                  "Your password must include a month of the year."),
        (rule7,  None,                                  "Your password must include a roman numeral."),
        (rule8,  None,                                  "Your password must include one of our sponsors(wish they actually sponsored me lol): (Pepsi, Starbucks, Shell)"),
        (rule9,  None,                                  "The roman numerals in your password should multiply to 25."),
        (rule10, "auto generated captcha(attached!)",   "Your password must include this CAPTCHA"),
        (rule11, "Today's wordle answer!",              "Your password must include today's Wordle answer."),
        (rule12, None,                                  "Your password must include a two letter symbol from the periodic table."),
        (rule13, "The current moon phase as an emoji!", "Your password must include the current phase of the moon as an emoji"),
        (rule14, "This random country \"{country}\"",   "Your password must include the name of this country. (randomly generated)"),
        (rule15, None,                                  "Your password must include a leap year.")
    ]

    game = turn(rules)
    print("Start!!!!")

    while True:
        try:
            pswd = input("Password: ")
        except KeyboardInterrupt:
            print("\nbaibaii!!")
            break
        if not pswd:
            continue

        ctx = replace(
                    base,
                    sender = "me@test",
                    sent_at = datetime.datetime.now(),
                    message_id = f"<{random.randrange(10**8)}@test>",
                    subject = "password"
                )

        results, unlocked, won = game(pswd, ctx)

        for msg, hint, ok in results:
            print("🟩" if ok else "🟥", msg)
            if hint:
                print(hint.format(**asdict(ctx)))
        print()

        if won:
            print("You won!!!!!")
            break

if __name__ == "__main__":
    main()