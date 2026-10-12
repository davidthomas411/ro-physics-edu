"""The usage events the site can send, and the only ones it can send.
app.js reads EVENTS (through DATA) and drops any event or property that is not listed here, or whose value does not match its check.
The privacy text on the About page and docs/irb-data-description.md are generated from the same list, and tests/analytics.py compares all three."""
import re

BOOL = dict(kind="bool")
def ENUM(*v): return dict(kind="enum", values=list(v))
def PAT(rx, fmt=""): return dict(kind="pattern", re=rx, fmt=fmt)

ITEM_RE = r"^[a-z0-9-]{1,40}:\d{1,3}:[0-9a-f]{6}$"
CHOICE_RE = r"^([A-Z]{1,8}|-?\d+(\.\d+)?(e[+-]\d+)?|\d{1,3},\d{1,3})$"
SECS = ["lt5", "5-15", "15-30", "30-60", "gt60"]
SECS_TEXT = "under 5 s, 5 to 15 s, 15 to 30 s, 30 to 60 s, or over 60 s"

# Each property: name, check (how app.js validates the value), what (text for the privacy page and the IRB description), example.
# tokens, when present, give the word that stands for true and for false in the GoatCounter path.
EVENTS = [
    dict(name="view", what="A page of the site was opened.", props=[
        dict(name="route", check=PAT(r"^[a-z0-9/_-]{0,60}$", "page address, lower case letters, digits, / _ -"), what="The page address after the #, with card and slide numbers left out.", example="t/pdd/c")]),
    dict(name="ans", what="A question was answered.", props=[
        dict(name="item", check=PAT(ITEM_RE, "topic:number:hash, for example pdd:12:3fa9c1"), what="The question: the topic, the number of the question within the topic, and the first six characters of a hash of the question text. A question that is edited gets a new identifier.", example="pdd:12:3fa9c1"),
        dict(name="kind", check=ENUM("mc", "multi", "typed", "sort", "match", "rank", "fig"), what="The form of the question: multiple choice with one answer, select all that apply, typed number, sort or true or false, match, rank, or tap the figure.", example="mc"),
        dict(name="ok", check=BOOL, tokens=("c", "w"), what="Whether the answer was correct.", example=False),
        dict(name="attempt", check=ENUM(1, 2, 3), what="1 for the first answer to this question, 2 for the second, 3 for the third or later. Counted from the answers stored in this browser.", example=1),
        dict(name="choice", check=PAT(CHOICE_RE, "a letter or letters, a number, or two numbers from 0 to 100 separated by a comma"), what="What was chosen. Multiple choice: the letter. Select all that apply: the letters in alphabetical order. Typed number: the value rounded to 3 significant digits. Sort, match, rank, and true or false: a number whose binary digits mark the items that were placed correctly. Tap the figure: the position of the tap as a percentage of each axis, rounded to the nearest 2.", example="B"),
        dict(name="secs", check=ENUM(*SECS), what="How long the question was in view before it was answered, in a coarse range: " + SECS_TEXT + ".", example="15-30"),
        dict(name="help", check=BOOL, tokens=("1", "0"), what="Whether Explain further was opened for this question since the previous answer.", example=False)]),
    dict(name="more_q", what="Explain further was opened under a question.", props=[
        dict(name="item", check=PAT(ITEM_RE, "topic:number:hash, for example pdd:12:3fa9c1"), what="The question, identified as above.", example="pdd:12:3fa9c1"),
        dict(name="state", check=ENUM("before_answer", "after_wrong", "after_correct"), what="Whether the question had not been answered, had been answered wrongly, or had been answered correctly.", example="after_wrong")]),
    dict(name="more_s", what="Show more details was opened in a chapter.", props=[
        dict(name="topic", check=PAT(r"^[a-z0-9-]{1,40}$", "chapter identifier"), what="Chapter identifier.", example="pdd"),
        dict(name="section", check=PAT(r"^\d{1,2}$", "whole number"), what="Section number within that chapter.", example="3")]),
    dict(name="card", what="A flash card was shown.", props=[
        dict(name="card", check=PAT(r"^[a-z0-9-]{1,40}:\d{1,3}$", "topic:number"), what="The card: the topic and the number of the card.", example="pdd:4"),
        dict(name="action", check=ENUM("seen"), what="The action. A card counts as seen when it is shown.", example="seen")]),
    dict(name="mu", what="A monitor-unit practice case was used.", props=[
        dict(name="case", check=PAT(r"^(r|\d{1,3})$", "whole number, or r"), what="The case number, or r for a random case.", example="7"),
        dict(name="action", check=ENUM("tried", "solution"), what="Whether the answers were checked or the solution was shown.", example="tried")]),
    dict(name="about", what="The About page was opened.", props=[]),
]

NEVER = ["names", "email addresses", "accounts", "times or dates from the device", "cookies", "identifiers stored in the browser",
         "typed text of any kind other than the rounded number in the choice of a typed-number question"]

BY = {e["name"]: e for e in EVENTS}

def check_value(check, v):
    k = check["kind"]
    if k == "bool": return isinstance(v, bool)
    if k == "enum": return v in check["values"] and not isinstance(v, bool)
    if k == "pattern": return isinstance(v, str) and re.match(check["re"], v) is not None
    return False

def clean(event, props):
    """Python twin of track() in app.js: the event with only listed properties whose values pass their checks, or None."""
    e = BY.get(event)
    if not e: return None
    out = {}
    for p in e["props"]:
        if p["name"] in props and check_value(p["check"], props[p["name"]]): out[p["name"]] = props[p["name"]]
    return out if len(out) == len(e["props"]) else None

def token(prop, v):
    if isinstance(v, bool): return prop["tokens"][0 if v else 1]
    return re.sub(r"[^A-Za-z0-9._,:+/-]", "_", str(v))

def path(event, props):
    """The GoatCounter path for an event: ev/<event>/<value>/<value>... in the order the properties are listed."""
    e = BY[event]
    return "/".join(["ev", event] + [token(p, props[p["name"]]) for p in e["props"]])

def decode(pth):
    """Inverse of path(). Returns (event, props) or None. A route may contain slashes, so a view takes the rest of the path."""
    parts = pth.strip("/").split("/")
    if len(parts) < 2 or parts[0] != "ev" or parts[1] not in BY: return None
    e = BY[parts[1]]; vals = parts[2:]
    if e["name"] == "view": return "view", {"route": "/".join(vals)}
    if len(vals) != len(e["props"]): return None
    props = {}
    for p, t in zip(e["props"], vals):
        c = p["check"]
        if c["kind"] == "bool": props[p["name"]] = (t == p["tokens"][0])
        elif c["kind"] == "enum":
            m = [x for x in c["values"] if token(p, x) == t]
            if not m: return None
            props[p["name"]] = m[0]
        else: props[p["name"]] = t
    return e["name"], props

def values_text(check):
    k = check["kind"]
    if k == "bool": return "true or false"
    if k == "enum": return ", ".join(str(v) for v in check["values"])
    return check.get("fmt", "")

def example_props(name):
    return {p["name"]: p["example"] for p in BY[name]["props"]}

def js_schema():
    """What app.js needs: events, property names, checks, and path tokens."""
    return [dict(name=e["name"], props=[dict(name=p["name"], check=p["check"], **({"tokens": list(p["tokens"])} if "tokens" in p else {})) for p in e["props"]]) for e in EVENTS]
