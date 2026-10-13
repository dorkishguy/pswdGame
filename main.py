from rules import *

import base64

from email.message import EmailMessage
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

captcha = genCaptcha()
wordle = todaysWordle()
country = randomCoutry()

rules = [
    (rule1,  None,    None,                                 "Your password must be at least 5 characters."),
    (rule2,  None,    None,                                 "Your password must include a number."),
    (rule3,  None,    None,                                 "Your password must include an uppercase letter."),
    (rule4,  None,    None,                                 "Your password must include a special character."),
    (rule5,  None,    None,                                 "The digits in your password must add up to 25."),
    (rule6,  None,    None,                                 "Your password must include a month of the year."),
    (rule7,  None,    None,                                 "Your password must include a roman numeral."),
    (rule8,  None,    None,                                 "Your password must include one of our sponsors(wish they actually sponsored me lol): (Pepsi, Starbucks, Shell)"),
    (rule9,  None,    None,                                 "The roman numerals in your password should multiply to 25."),
    (rule10, captcha, "auto generated captcha(attatched!)", "Your password must include this CAPTCHA"),
    (rule11, wordle,  "Today's wordle answer!",             "Your password must include today's Wordle answer."),
    (rule12, None,    None,                                 "Your password must include a two letter symbol from the periodic table."),
    (rule13, None,    None,                                 "Your password must include the current phase of the moon as an emoji"),
    (rule14, country, f"This random country \"{country}\"", "Your password must include the name of this country. (randomly generated)"),
    (rule15, None,    None,                                 "Your password must include a leap year.")
]

def msg(pswd, ctx):
    game = turn(rules)
    return game(pswd, ctx)

def mail(pswd, ctx):
    creds, _ = google.auth.default()

    try:
        service = build("gmail", "v1", credentials=creds)
        message = EmailMessage()

        message.set_content()