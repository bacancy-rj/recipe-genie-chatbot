"""
Builds data/recipes.json: a curated recipe knowledge base for the
Recipe Recommendation Chatbot.

Each recipe has: id, title, cuisine, diet tags, ingredients (normalized
list used for matching), raw ingredient lines (for display), steps,
ready_in_minutes, servings, difficulty.

Run: python3 data/build_dataset.py
"""
import json
import os

RECIPES = []


def add(title, cuisine, diet, ingredients, steps, minutes, servings, difficulty):
    RECIPES.append({
        "id": len(RECIPES) + 1,
        "title": title,
        "cuisine": cuisine,
        "diet": diet,  # list, e.g. ["vegetarian", "vegan", "gluten-free", "non-vegetarian"]
        "ingredients": ingredients,  # list of normalized ingredient names
        "steps": steps,
        "ready_in_minutes": minutes,
        "servings": servings,
        "difficulty": difficulty,
    })


# ---------------------------------------------------------------- Indian
add("Paneer Butter Masala", "Indian", ["vegetarian", "gluten-free"],
    ["paneer", "tomato", "butter", "cream", "onion", "garlic", "ginger", "garam masala", "cashew"],
    ["Saute onion, garlic and ginger until soft.",
     "Add tomato puree and cook until oil separates.",
     "Blend with cashews into a smooth gravy.",
     "Add butter, cream and garam masala, simmer.",
     "Add paneer cubes and cook 5 minutes. Serve hot."],
    35, 4, "medium")

add("Chana Masala", "Indian", ["vegetarian", "vegan"],
    ["chickpeas", "tomato", "onion", "garlic", "ginger", "cumin", "coriander powder", "garam masala"],
    ["Saute onion until golden, add garlic and ginger.",
     "Add tomato and spices, cook until thick.",
     "Add boiled chickpeas and simmer 15 minutes.",
     "Garnish with coriander leaves."],
    30, 4, "easy")

add("Chicken Biryani", "Indian", ["non-vegetarian"],
    ["chicken", "basmati rice", "yogurt", "onion", "garam masala", "saffron", "mint", "ginger", "garlic"],
    ["Marinate chicken in yogurt and spices for 1 hour.",
     "Fry onions until crisp and golden.",
     "Cook chicken until half done.",
     "Layer partially cooked rice over chicken with saffron milk and fried onions.",
     "Cover and cook on low heat (dum) for 20 minutes."],
    75, 6, "hard")

add("Masoor Dal Tadka", "Indian", ["vegetarian", "vegan", "gluten-free"],
    ["red lentils", "onion", "tomato", "garlic", "cumin seeds", "turmeric", "ghee"],
    ["Boil lentils with turmeric until soft.",
     "Prepare tempering with cumin, garlic and onion in ghee.",
     "Pour tempering over dal and simmer with tomato."],
    25, 4, "easy")

add("Aloo Gobi", "Indian", ["vegetarian", "vegan", "gluten-free"],
    ["potato", "cauliflower", "turmeric", "cumin seeds", "ginger", "coriander powder", "onion"],
    ["Heat oil, add cumin seeds and ginger.",
     "Add potato and cauliflower with turmeric and coriander powder.",
     "Cover and cook until vegetables are tender, stirring occasionally."],
    30, 4, "easy")

add("Palak Paneer", "Indian", ["vegetarian", "gluten-free"],
    ["spinach", "paneer", "onion", "tomato", "garlic", "ginger", "cream", "garam masala"],
    ["Blanch spinach and blend into a puree.",
     "Saute onion, garlic, ginger; add tomato and cook down.",
     "Add spinach puree and simmer.",
     "Add paneer cubes and cream, cook 5 minutes."],
    30, 4, "medium")

add("Vegetable Pulao", "Indian", ["vegetarian", "vegan", "gluten-free"],
    ["basmati rice", "mixed vegetables", "onion", "cumin seeds", "bay leaf", "garam masala"],
    ["Saute cumin seeds and bay leaf in ghee.",
     "Add onion and vegetables, cook briefly.",
     "Add soaked rice and water, cook until fluffy."],
    30, 4, "easy")

add("Egg Curry", "Indian", ["non-vegetarian", "gluten-free"],
    ["eggs", "onion", "tomato", "garlic", "ginger", "garam masala", "turmeric"],
    ["Boil and peel eggs, lightly fry them.",
     "Prepare a masala base with onion, tomato, garlic, ginger.",
     "Add eggs to the gravy and simmer 10 minutes."],
    30, 3, "easy")

add("Rajma", "Indian", ["vegetarian", "vegan", "gluten-free"],
    ["kidney beans", "onion", "tomato", "garlic", "ginger", "cumin", "garam masala"],
    ["Boil kidney beans until soft.",
     "Prepare a masala base and add beans with a little water.",
     "Simmer 20 minutes until thick, mash a few beans for texture."],
    45, 4, "easy")

add("Tandoori Chicken", "Indian", ["non-vegetarian", "gluten-free"],
    ["chicken", "yogurt", "ginger", "garlic", "lemon", "tandoori masala"],
    ["Marinate chicken in yogurt, ginger, garlic, lemon and spices for 4 hours.",
     "Grill or bake at high heat until charred and cooked through."],
    50, 4, "medium")

# ---------------------------------------------------------------- Italian
add("Margherita Pizza", "Italian", ["vegetarian"],
    ["pizza dough", "tomato", "mozzarella", "basil", "olive oil"],
    ["Spread tomato sauce on stretched dough.",
     "Top with mozzarella and bake at high heat until crust is golden.",
     "Finish with fresh basil and olive oil."],
    25, 2, "easy")

add("Spaghetti Aglio e Olio", "Italian", ["vegetarian", "vegan"],
    ["spaghetti", "garlic", "olive oil", "chili flakes", "parsley"],
    ["Cook spaghetti until al dente.",
     "Gently saute sliced garlic in olive oil until golden.",
     "Toss pasta with garlic oil, chili flakes and parsley."],
    20, 2, "easy")

add("Chicken Alfredo", "Italian", ["non-vegetarian"],
    ["chicken", "fettuccine", "cream", "parmesan", "garlic", "butter"],
    ["Cook fettuccine until al dente.",
     "Saute chicken until cooked, set aside.",
     "Make a cream sauce with butter, garlic and parmesan.",
     "Combine pasta, chicken and sauce."],
    30, 3, "medium")

add("Margarita Risotto (Mushroom Risotto)", "Italian", ["vegetarian", "gluten-free"],
    ["arborio rice", "mushroom", "onion", "white wine", "parmesan", "vegetable stock", "butter"],
    ["Saute onion and mushrooms until soft.",
     "Add rice and toast briefly, deglaze with wine.",
     "Add stock gradually, stirring, until creamy.",
     "Finish with butter and parmesan."],
    40, 4, "medium")

add("Caprese Salad", "Italian", ["vegetarian", "gluten-free"],
    ["tomato", "mozzarella", "basil", "olive oil", "balsamic vinegar"],
    ["Slice tomato and mozzarella.",
     "Arrange alternating slices with basil leaves.",
     "Drizzle with olive oil and balsamic vinegar."],
    10, 2, "easy")

add("Lasagna", "Italian", ["non-vegetarian"],
    ["lasagna sheets", "ground beef", "tomato", "mozzarella", "parmesan", "onion", "garlic"],
    ["Prepare a meat sauce with beef, onion, garlic and tomato.",
     "Make a bechamel sauce.",
     "Layer pasta sheets, meat sauce, bechamel and cheese.",
     "Bake until golden and bubbling."],
    70, 6, "hard")

add("Minestrone Soup", "Italian", ["vegetarian", "vegan"],
    ["carrot", "celery", "onion", "tomato", "beans", "pasta", "vegetable stock"],
    ["Saute carrot, celery and onion.",
     "Add tomato and stock, simmer.",
     "Add beans and pasta, cook until pasta is tender."],
    35, 4, "easy")

# ---------------------------------------------------------------- Mexican
add("Chicken Tacos", "Mexican", ["non-vegetarian"],
    ["chicken", "tortilla", "onion", "lime", "cilantro", "cumin", "chili powder"],
    ["Season and cook chicken with cumin and chili powder.",
     "Warm tortillas.",
     "Fill tortillas with chicken, onion, cilantro and lime juice."],
    25, 4, "easy")

add("Vegetable Quesadilla", "Mexican", ["vegetarian"],
    ["tortilla", "cheese", "bell pepper", "onion", "corn", "beans"],
    ["Saute bell pepper, onion and corn.",
     "Fill tortilla with cheese and vegetables, fold.",
     "Cook on a pan until cheese melts and tortilla is crisp."],
    20, 2, "easy")

add("Black Bean Burrito", "Mexican", ["vegetarian", "vegan"],
    ["tortilla", "black beans", "rice", "corn", "salsa", "avocado"],
    ["Warm beans and rice.",
     "Assemble tortilla with beans, rice, corn, salsa and avocado.",
     "Roll tightly into a burrito."],
    20, 2, "easy")

add("Beef Enchiladas", "Mexican", ["non-vegetarian"],
    ["ground beef", "tortilla", "cheese", "enchilada sauce", "onion"],
    ["Cook beef with onion and spices.",
     "Roll beef in tortillas, place in a dish.",
     "Cover with enchilada sauce and cheese, bake until bubbly."],
    45, 4, "medium")

add("Guacamole", "Mexican", ["vegetarian", "vegan", "gluten-free"],
    ["avocado", "onion", "tomato", "lime", "cilantro", "chili"],
    ["Mash avocado.",
     "Mix in finely chopped onion, tomato, chili and cilantro.",
     "Add lime juice and salt to taste."],
    10, 4, "easy")

# ---------------------------------------------------------------- Chinese
add("Vegetable Fried Rice", "Chinese", ["vegetarian", "vegan"],
    ["rice", "carrot", "peas", "bell pepper", "soy sauce", "spring onion", "garlic"],
    ["Saute garlic, carrot, peas and bell pepper.",
     "Add cold cooked rice and soy sauce, stir-fry on high heat.",
     "Garnish with spring onion."],
    20, 3, "easy")

add("Kung Pao Chicken", "Chinese", ["non-vegetarian"],
    ["chicken", "peanuts", "bell pepper", "soy sauce", "garlic", "chili", "spring onion"],
    ["Marinate and stir-fry chicken until cooked.",
     "Add bell pepper, garlic and dried chilies, stir-fry.",
     "Add sauce and peanuts, toss to coat."],
    30, 4, "medium")

add("Vegetable Hakka Noodles", "Chinese", ["vegetarian", "vegan"],
    ["noodles", "cabbage", "carrot", "bell pepper", "soy sauce", "garlic", "spring onion"],
    ["Boil noodles and set aside.",
     "Stir-fry garlic and vegetables on high heat.",
     "Add noodles and soy sauce, toss well."],
    20, 3, "easy")

add("Chilli Paneer", "Chinese", ["vegetarian"],
    ["paneer", "bell pepper", "onion", "soy sauce", "garlic", "cornstarch", "chili sauce"],
    ["Toss paneer in cornstarch and shallow fry until crisp.",
     "Stir-fry garlic, onion and bell pepper.",
     "Add sauces and paneer, toss well and serve."],
    30, 4, "medium")

add("Egg Fried Rice", "Chinese", ["non-vegetarian"],
    ["rice", "eggs", "carrot", "peas", "soy sauce", "spring onion"],
    ["Scramble eggs and set aside.",
     "Stir-fry carrot and peas.",
     "Add rice, soy sauce and eggs, toss together."],
    20, 3, "easy")

# ---------------------------------------------------------------- Thai
add("Thai Green Curry", "Thai", ["non-vegetarian", "gluten-free"],
    ["chicken", "coconut milk", "green curry paste", "bell pepper", "basil", "fish sauce"],
    ["Fry curry paste in a little coconut milk until fragrant.",
     "Add chicken and cook through.",
     "Add remaining coconut milk and bell pepper, simmer.",
     "Finish with basil and fish sauce."],
    35, 4, "medium")

add("Pad Thai", "Thai", ["non-vegetarian"],
    ["rice noodles", "shrimp", "eggs", "bean sprouts", "peanuts", "tamarind", "fish sauce"],
    ["Soak rice noodles until pliable.",
     "Stir-fry shrimp and eggs.",
     "Add noodles, tamarind sauce and fish sauce, toss.",
     "Top with bean sprouts and crushed peanuts."],
    30, 3, "medium")

add("Tofu Green Curry", "Thai", ["vegetarian", "vegan", "gluten-free"],
    ["tofu", "coconut milk", "green curry paste", "bell pepper", "basil"],
    ["Fry curry paste in coconut milk until fragrant.",
     "Add tofu and bell pepper, simmer in coconut milk.",
     "Finish with basil leaves."],
    30, 4, "medium")

# ---------------------------------------------------------------- Mediterranean / Middle Eastern
add("Falafel Wrap", "Mediterranean", ["vegetarian", "vegan"],
    ["chickpeas", "garlic", "parsley", "cumin", "tortilla", "tahini", "cucumber"],
    ["Blend chickpeas, garlic, parsley and cumin, form patties.",
     "Fry or bake falafel until golden.",
     "Wrap with tahini sauce and cucumber in flatbread."],
    35, 3, "medium")

add("Greek Salad", "Mediterranean", ["vegetarian", "gluten-free"],
    ["cucumber", "tomato", "feta cheese", "olives", "red onion", "olive oil"],
    ["Chop cucumber, tomato and onion.",
     "Toss with olives and feta.",
     "Drizzle with olive oil and oregano."],
    10, 2, "easy")

add("Hummus", "Mediterranean", ["vegetarian", "vegan", "gluten-free"],
    ["chickpeas", "tahini", "garlic", "lemon", "olive oil"],
    ["Blend chickpeas, tahini, garlic and lemon juice until smooth.",
     "Drizzle with olive oil before serving."],
    10, 4, "easy")

add("Chicken Shawarma", "Mediterranean", ["non-vegetarian"],
    ["chicken", "yogurt", "garlic", "lemon", "cumin", "flatbread", "cucumber"],
    ["Marinate chicken in yogurt, garlic, lemon and spices.",
     "Grill or pan-sear until charred and cooked.",
     "Serve in flatbread with garlic sauce and cucumber."],
    40, 4, "medium")

# ---------------------------------------------------------------- American / misc
add("Classic Beef Burger", "American", ["non-vegetarian"],
    ["ground beef", "burger bun", "cheese", "lettuce", "tomato", "onion"],
    ["Form and grill beef patties.",
     "Toast buns.",
     "Assemble with cheese, lettuce, tomato and onion."],
    20, 4, "easy")

add("Veggie Burger", "American", ["vegetarian"],
    ["black beans", "burger bun", "cheese", "lettuce", "tomato", "breadcrumbs"],
    ["Mash beans with breadcrumbs and spices, form patties.",
     "Pan-fry patties until golden.",
     "Assemble in buns with toppings."],
    25, 4, "easy")

add("Mac and Cheese", "American", ["vegetarian"],
    ["macaroni", "cheese", "butter", "milk", "flour"],
    ["Cook macaroni until al dente.",
     "Make a roux with butter and flour, whisk in milk.",
     "Add cheese to make a sauce, combine with macaroni."],
    25, 4, "easy")

add("Grilled Chicken Salad", "American", ["non-vegetarian", "gluten-free"],
    ["chicken", "lettuce", "tomato", "cucumber", "olive oil", "lemon"],
    ["Grill seasoned chicken and slice.",
     "Toss salad greens, tomato and cucumber.",
     "Top with chicken and dress with olive oil and lemon."],
    20, 2, "easy")

add("Pancakes", "American", ["vegetarian"],
    ["flour", "eggs", "milk", "butter", "sugar", "baking powder"],
    ["Whisk dry ingredients together.",
     "Add eggs, milk and melted butter, mix until just combined.",
     "Cook spoonfuls on a griddle until bubbles form, flip and cook through."],
    20, 3, "easy")

add("Vegetable Stir Fry", "Asian", ["vegetarian", "vegan", "gluten-free"],
    ["broccoli", "carrot", "bell pepper", "garlic", "soy sauce", "ginger"],
    ["Heat oil, add garlic and ginger.",
     "Add vegetables and stir-fry on high heat until crisp-tender.",
     "Toss with soy sauce."],
    15, 3, "easy")

add("Lentil Soup", "Mediterranean", ["vegetarian", "vegan", "gluten-free"],
    ["red lentils", "carrot", "onion", "celery", "cumin", "vegetable stock"],
    ["Saute onion, carrot and celery.",
     "Add lentils, stock and cumin, simmer until lentils are soft.",
     "Blend partially for a creamy texture, if desired."],
    35, 4, "easy")

add("Shrimp Scampi", "Italian", ["non-vegetarian"],
    ["shrimp", "spaghetti", "garlic", "butter", "lemon", "parsley", "white wine"],
    ["Cook spaghetti until al dente.",
     "Saute garlic in butter, add shrimp and cook through.",
     "Deglaze with wine and lemon, toss with pasta and parsley."],
    25, 3, "medium")

add("Butter Chicken", "Indian", ["non-vegetarian", "gluten-free"],
    ["chicken", "tomato", "butter", "cream", "garam masala", "ginger", "garlic"],
    ["Marinate and grill or pan-sear chicken pieces.",
     "Prepare a tomato-butter gravy with garam masala.",
     "Add cream and cooked chicken, simmer 10 minutes."],
    45, 4, "medium")

add("Vegetable Omelette", "American", ["vegetarian", "gluten-free"],
    ["eggs", "onion", "bell pepper", "tomato", "cheese"],
    ["Whisk eggs with salt and pepper.",
     "Saute vegetables briefly.",
     "Pour eggs over vegetables, cook until set, fold and add cheese."],
    10, 1, "easy")

add("Baingan Bharta", "Indian", ["vegetarian", "vegan", "gluten-free"],
    ["eggplant", "onion", "tomato", "garlic", "ginger", "cumin seeds"],
    ["Roast eggplant until charred and soft, then mash.",
     "Saute cumin seeds, onion, garlic and ginger.",
     "Add tomato and mashed eggplant, cook until combined."],
    35, 4, "easy")


def main():
    out_path = os.path.join(os.path.dirname(__file__), "recipes.json")
    with open(out_path, "w") as f:
        json.dump(RECIPES, f, indent=2)
    print(f"Wrote {len(RECIPES)} recipes to {out_path}")


if __name__ == "__main__":
    main()
