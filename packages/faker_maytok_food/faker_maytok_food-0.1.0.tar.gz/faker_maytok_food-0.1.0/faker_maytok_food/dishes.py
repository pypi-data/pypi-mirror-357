import random
from itertools import product

proteins = ["Chicken", "Beef", "Tofu", "Salmon", "Pork", "Shrimp", "Lamb", "Tuna", 
           "Eggplant", "Mushrooms", "Black Bean", "Quinoa", "Turkey", "Duck", "Tofu"]

vegetables = ["Spinach", "Zucchini", "Broccoli", "Asparagus", "Cauliflower", "Sweet Potato",
              "Portobello", "Avocado", "Artichoke", "Kale", "Brussels Sprouts", "Cabbage"]

starches = ["Rice", "Noodles", "Couscous", "Polenta", "Mashed Potatoes", "Buckwheat",
            "Barley", "Farro", "Sweet Potato Fries", "Crispy Potatoes", "Ratatouille"]

sauces = ["Alfredo", "Pesto", "Teriyaki", "Ginger", "Tomato", "Creamy Curry", "Sesame",
          "BBQ", "Lemon Butter", "Chipotle", "White Wine", "Soy Glaze"]

cooking_methods = ["Grilled", "Roasted", "Pan-Seared", "Stir-Fried", "Baked", "Crispy",
                   "Slow-Cooked", "Smoked", "Steamed", "Caramelized"]

cuisines = ["Mediterranean", "Thai", "Japanese", "Mexican", "Italian", "Indian", "Korean",
            "French", "Vietnamese", "Spanish", "Middle Eastern", "Peruvian"]

templates = [
    "{method} {protein} with {vegetable} and {starch} in {sauce}",
    "{cuisine} Style {protein} with {vegetable} and {starch}",
    "{method} {protein} served with {starch}, {vegetable}, and {sauce}",
    "{sauce} {protein} over {starch} with {vegetable}",
    "Spicy {cuisine} {protein} with {starch} and {vegetable}",
    "Creamy {sauce} {protein} paired with {vegetable} and {starch}",
    "{method} {vegetable} with {protein}, {starch}, and {sauce}",
    "{cuisine} Inspired {method} {protein} with {starch}"
]

def generate_dish():
    protein = random.choice(proteins)
    vegetable = random.choice(vegetables)
    starch = random.choice(starches)
    sauce = random.choice(sauces)
    method = random.choice(cooking_methods)
    cuisine = random.choice(cuisines)
    template = random.choice(templates)
    return template.format(**{
        "protein": protein,
        "vegetable": vegetable,
        "starch": starch,
        "sauce": sauce,
        "method": method,
        "cuisine": cuisine
    })
