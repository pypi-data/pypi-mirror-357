import random

proteins = ["chicken", "salmon", "eggs", "egg whites", "beef", "shrimp", "tofu", "pork", "lamb", "duck"]
cheeses = ["Emmental", "Roquefort", "feta", "mozzarella", "mascarpone", "cheddar", "gouda", "ricotta"]
vegetables = ["spinach", "mushrooms", "onions", "tomatoes", "avocados", "zucchini", "bell peppers", "kale"]
herbs_spices = ["cilantro", "chives", "rosemary", "thyme", "garlic", "shallots", "paprika", "cumin"]
grains = ["roasted potatoes", "quinoa", "rice", "couscous", "polenta", "bread", "croissant", "toast"]
sauces = ["Hollandaise", "pesto", "teriyaki", "BBQ", "cream cheese", "Dijon mustard", "soy glaze"]
preparations = ["fried", "poached", "scrambled", "grilled", "roasted", "baked", "stir-fried", "steamed"]
premium_details = ["28-day aged", "USDA Certified Prime", "Norwegian", "organic", "free-range", "wild-caught"]
sides = ["roasted potatoes", "mixed greens", "mashed sweet potatoes", "grilled vegetables", "candied yams"]

templates = [
    "{prep} {protein} with {cheese} cheese, {veg} and {herb}. With a side of {side}.",
    "{premium} {protein}, {prep} in {sauce}, served with {grain} and {side}.",
    "Fresh {protein} with {veg}, {herb}, and {cheese} in an {grain} crust. With {side}.",
    "{protein} {prep} with {sauce}, topped with {veg} and {cheese}. Served with {grain}.",
    "{grain}-crusted {protein} with {veg}, {herb}, and {sauce}. With {side}.",
    "Creamy {cheese} sauce over {prep} {protein}, {veg}, and {grain}. Topped with {herb}.",
    "{premium} {protein} brushed with {sauce}, {prep} to perfection. Served with {side} and {grain}.",
    "House-made {grain} filled with {protein}, {veg}, and {cheese}. Topped with {sauce}.",
    "{protein} sautéed with {herb}, {veg}, and {cheese}. Served over {grain} with {sauce}.",
    "{prep} {protein} layered with {veg}, {cheese}, and {sauce} in a {grain} crust. With {side}."
]

def generate_dish_descriptions():
    protein = random.choice(proteins)
    cheese = random.choice(cheeses)
    veg = ", ".join(random.sample(vegetables, random.randint(1, 3)))
    herb = random.choice(herbs_spices)
    grain = random.choice(grains)
    sauce = random.choice(sauces)
    prep = random.choice(preparations)
    premium = random.choice(premium_details)
    side = random.choice(sides)

       
    template = random.choice(templates)
    return template.format(**{
        "protein": protein,
        "cheese": cheese,
        "veg": veg,
        "herb": herb,
        "grain": grain,
        "sauce": sauce,
        "prep": prep,
        "premium": premium,
        "side": side
    })
