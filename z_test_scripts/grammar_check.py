import sys
import string
from gingerit.gingerit import GingerIt

text = "a second season suggest things are going well yeah so when you put. when you and Alan page this and then what did you tell the people clicks. what we pay so we just said we want to do. at a show about me and kind of based on my observations of my stand up and if we didn't really telling too much and the show real involved because we had a long break."

parser = GingerIt()
print(parser.parse(text)['result'])