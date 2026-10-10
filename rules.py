from captcha.image import ImageCaptcha
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
COUNTRIES = ['Aruba', 'Afghanistan', 'Angola', 'Anguilla', 'Åland Islands', 'Albania', 'Andorra', 'United Arab Emirates', 'Argentina', 'Armenia', 'American Samoa', 'Antarctica', 'French Southern Territories', 'Antigua and Barbuda', 'Australia', 'Austria', 'Azerbaijan', 'Burundi', 'Belgium', 'Benin', 'Bonaire, Sint Eustatius and Saba', 'Burkina Faso', 'Bangladesh', 'Bulgaria', 'Bahrain', 'Bahamas', 'Bosnia and Herzegovina', 'Saint Barthélemy', 'Belarus', 'Belize', 'Bermuda', 'Bolivia, Plurinational State of', 'Brazil', 'Barbados', 'Brunei Darussalam', 'Bhutan', 'Bouvet Island', 'Botswana', 'Central African Republic', 'Canada', 'Cocos (Keeling) Islands', 'Switzerland', 'Chile', 'China', "Côte d'Ivoire", 'Cameroon', 'Congo, The Democratic Republic of the', 'Congo', 'Cook Islands', 'Colombia', 'Comoros', 'Cabo Verde', 'Costa Rica', 'Cuba', 'Curaçao', 'Christmas Island', 'Cayman Islands', 'Cyprus', 'Czechia', 'Germany', 'Djibouti', 'Dominica', 'Denmark', 'Dominican Republic', 'Algeria', 'Ecuador', 'Egypt', 'Eritrea', 'Western Sahara', 'Spain', 'Estonia', 'Ethiopia', 'Finland', 'Fiji', 'Falkland Islands (Malvinas)', 'France', 'Faroe Islands', 'Micronesia, Federated States of', 'Gabon', 'United Kingdom', 'Georgia', 'Guernsey', 'Ghana', 'Gibraltar', 'Guinea', 'Guadeloupe', 'Gambia', 'Guinea-Bissau', 'Equatorial Guinea', 'Greece', 'Grenada', 'Greenland', 'Guatemala', 'French Guiana', 'Guam', 'Guyana', 'Hong Kong', 'Heard Island and McDonald Islands', 'Honduras', 'Croatia', 'Haiti', 'Hungary', 'Indonesia', 'Isle of Man', 'India', 'British Indian Ocean Territory', 'Ireland', 'Iran, Islamic Republic of', 'Iraq', 'Iceland', 'Israel', 'Italy', 'Jamaica', 'Jersey', 'Jordan', 'Japan', 'Kazakhstan', 'Kenya', 'Kyrgyzstan', 'Cambodia', 'Kiribati', 'Saint Kitts and Nevis', 'Korea, Republic of', 'Kuwait', "Lao People's Democratic Republic", 'Lebanon', 'Liberia', 'Libya', 'Saint Lucia', 'Liechtenstein', 'Sri Lanka', 'Lesotho', 'Lithuania', 'Luxembourg', 'Latvia', 'Macao', 'Saint Martin (French part)', 'Morocco', 'Monaco', 'Moldova, Republic of', 'Madagascar', 'Maldives', 'Mexico', 'Marshall Islands', 'North Macedonia', 'Mali', 'Malta', 'Myanmar', 'Montenegro', 'Mongolia', 'Northern Mariana Islands', 'Mozambique', 'Mauritania', 'Montserrat', 'Martinique', 'Mauritius', 'Malawi', 'Malaysia', 'Mayotte', 'Namibia', 'New Caledonia', 'Niger', 'Norfolk Island', 'Nigeria', 'Nicaragua', 'Niue', 'Netherlands', 'Norway', 'Nepal', 'Nauru', 'New Zealand', 'Oman', 'Pakistan', 'Panama', 'Pitcairn', 'Peru', 'Philippines', 'Palau', 'Papua New Guinea', 'Poland', 'Puerto Rico', "Korea, Democratic People's Republic of", 'Portugal', 'Paraguay', 'Palestine, State of', 'French Polynesia', 'Qatar', 'Réunion', 'Romania', 'Russian Federation', 'Rwanda', 'Saudi Arabia', 'Sudan', 'Senegal', 'Singapore', 'South Georgia and the South Sandwich Islands', 'Saint Helena, Ascension and Tristan da Cunha', 'Svalbard and Jan Mayen', 'Solomon Islands', 'Sierra Leone', 'El Salvador', 'San Marino', 'Somalia', 'Saint Pierre and Miquelon', 'Serbia', 'South Sudan', 'Sao Tome and Principe', 'Suriname', 'Slovakia', 'Slovenia', 'Sweden', 'Eswatini', 'Sint Maarten (Dutch part)', 'Seychelles', 'Syrian Arab Republic', 'Turks and Caicos Islands', 'Chad', 'Togo', 'Thailand', 'Tajikistan', 'Tokelau', 'Turkmenistan', 'Timor-Leste', 'Tonga', 'Trinidad and Tobago', 'Tunisia', 'Türkiye', 'Tuvalu', 'Taiwan, Province of China', 'Tanzania, United Republic of', 'Uganda', 'Ukraine', 'United States Minor Outlying Islands', 'Uruguay', 'United States', 'Uzbekistan', 'Holy See (Vatican City State)', 'Saint Vincent and the Grenadines', 'Venezuela, Bolivarian Republic of', 'Virgin Islands, British', 'Virgin Islands, U.S.', 'Viet Nam', 'Vanuatu', 'Wallis and Futuna', 'Samoa', 'Yemen', 'South Africa', 'Zambia', 'Zimbabwe']

def rule1(x, ctx):
    if len(x) >= 5:
        return True
    else:
        return False

def rule2(x, ctx):
    return any(char.isnumeric() for char in x)

def rule3(x, ctx):
    return any(char.isupper() for char in x)

def rule4(x, ctx):
    return any(not char.isalnum() and not char.isspace() for char in x)

def rule5(x, ctx):
    digits = []
    for char in x:
        if rule2(char):
            digits.append(int(char))
    if sum(digits) == 25:
        return True
    else: return False

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

def rule10(x, txt):
    return txt in x

def todaysWordle(): 
    date = datetime.date.today()
    url = f"https://www.nytimes.com/svc/wordle/v2/{date:%Y-%m-%d}.json"
    response = requests.get(url).json()
    wordle = response['solution']
    return wordle

def rule11(x, wordle):
    return wordle in x

def rule12(x, ctx):
    return any(s in x for s in SYMBOLS)

def rule13(x, ctx):
    MOONPHASE = requests.get("https://api.apiverve.com/v1/moonphases?today=true", headers={"x-api-key": os.getenv("API-KEY")}).json()["data"]["phaseEmoji"]
    return MOONPHASE in x

def randomCoutry():
    country = random.choice(COUNTRIES)
    return country

def rule14(x, country):
    return country in x

def isLeap(year):
    return (year % 4 == 0 and year % 100 != 0) or year % 400 == 0

def rule15(x, ctx):
    for n in re.findall(r"\d+", x):
        year = int(n)
        if year > 0 and isLeap(year):
            return True
    return False

txt = "1234"

def turn():
    unlocked = 1

    captcha = genCaptcha()
    wordle = todaysWordle()
    country = randomCoutry()

    rules = [
        (rule1,  None,    "Your password must be at least 5 characters."),
        (rule2,  None,    "Your password must include a number."),
        (rule3,  None,    "Your password must include an uppercase letter."),
        (rule4,  None,    "Your password must include a special character."),
        (rule5,  None,    "The digits in your password must add up to 25."),
        (rule6,  None,    "Your password must include a month of the year."),
        (rule7,  None,    "Your password must include a roman numeral."),
        (rule8,  None,    "Your password must include one of our sponsors(wish they actually sponsored me lol): (Pepsi, Starbucks, Shell)"),
        (rule9,  None,    "The roman numerals in your password should multiply to 25."),
        (rule10, captcha, "Your password must include this CAPTCHA"),
        (rule11, wordle,  "Your password must include today’s Wordle answer."),
        (rule12, None,    "Your password must include a two letter symbol from the periodic table."),
        (rule13, None,    "Your password must include the current phase of the moon as an emoji"),
        (rule14, country, "Your password must include the name of this country. (randomly generated)"),
        (rule15, None,    "Your password must include a leap year.")
    ] 

    def submit(pswd):
        nonlocal unlocked
        while True:
            results = [(txt, fn(pswd, ctx)) for fn, ctx, txt in rules[:unlocked]]
            failed = any(not ok for _, ok in results)
            if failed or unlocked == len(rules):
                break
            unlocked += 1
            won = not failed and unlocked == len(rules)
        return results, unlocked, won
    return submit
if __name__ == "__main__":
    game = turn()
    print(game("hihih9I7i9"))