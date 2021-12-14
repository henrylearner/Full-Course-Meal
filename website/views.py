from flask import Flask, Blueprint, request, render_template, flash
from urllib.request import Request, urlopen
import urllib.parse, urllib.error, json

beerurl = "https://api.punkapi.com/v2/beers"
foodurl = "https://api.spoonacular.com/recipes/findByIngredients"
recipeurl = "https://api.spoonacular.com/recipes/"

apiKey = "a727ea74c5d346629cca5e66489316fc"
apiKey2 = "e5bf033e22654612b651f80b720af55b"


def get_beer_data(beer_food='steak'):
    if beer_food == 'steak':
        beer_dict = {"food": 'steak'}
    else:
        beer_dict = {"food": beer_food}
    param = urllib.parse.urlencode(beer_dict)
    url = beerurl + "?" + param
    data = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    beer_data = urllib.request.urlopen(data).read()
    return json.loads(beer_data)


def get_food_data(ingredients="steak"):
    if ingredients == "steak":
        food_dict = {"apiKey": apiKey2, "ingredients": "steak"}
    else:
        food_dict = {"apiKey": apiKey2, "ingredients": ingredients}
    param = urllib.parse.urlencode(food_dict)
    url = foodurl + "?" + param
    data = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        food_data = urllib.request.urlopen(data).read()
        return json.loads(food_data)
    except urllib.error.HTTPError as e:
        return None


def get_recipe_data(id):
    url = recipeurl + str(id) + "/information?apiKey=e5bf033e22654612b651f80b720af55b"
    data = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        recipe_data = urllib.request.urlopen(data).read()
        return json.loads(recipe_data)
    except urllib.error.HTTPError as e:
        return None


def get_beer_data_safe(food_type='steak'):
    try:
        return get_beer_data(food_type)
    except urllib.error.URLError as e:
        return None


def get_beer(food_type='steak'):
    if get_beer_data_safe(food_type) is None:
        return None
    else:
        string = ("Beer that goes with " + food_type.upper() + ":")
        var = 0
        beer_dict = {}
        for beer in get_beer_data_safe(food_type):
            if "name" in beer:
                beer_dict[var] = "- " + beer["name"]
                var += 1
        return string, beer_dict


def get_food(food_type="steak"):
    if get_food_data(food_type) is None:
        return None
    else:
        var = 0
        string = ("Recipes that include " + food_type.upper() + ":")
        food_dict = {}
        for recipe in get_food_data(food_type):
            if "id" in recipe:
                recipe_layout = get_recipe_data(recipe["id"])
                food_dict[var] = (recipe_layout["title"], recipe_layout["spoonacularSourceUrl"])
                var += 1
        return string, food_dict


views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        data = request.form.get('food')
        if get_beer(data)[1] == {}:
            flash('Please change input, current input has no results', category='error')
            return render_template("home.html")
        elif get_food_data(data) is None:
            flash('Beer Results Returned, But You\'ve Ran Out of Recipe Searches for Today ', category='error')
            return render_template("home.html", beer_tag=get_beer(data)[0], beer_results=get_beer(data)[1].values())
        else:
            flash('Results Returned!', category='success')
            return render_template("home.html", beer_tag=get_beer(data)[0], beer_results=get_beer(data)[1].values(),
                                   food_tag=get_food(data)[0], food_results=get_food(data)[1].values())
    else:
        return render_template("home.html")
