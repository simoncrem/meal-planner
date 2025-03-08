from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from datetime import datetime, timedelta
import random
import enum

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-key-please-change-in-production'  # Change this in production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recipes.db'

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'simon.cremieux@gmail.com'
app.config['MAIL_PASSWORD'] = 'imwk bqvd brfy wlad'
app.config['MAIL_DEFAULT_SENDER'] = 'simon.cremieux@gmail.com'

db = SQLAlchemy(app)
mail = Mail(app)

class IngredientCategory(enum.Enum):
    PROTEIN = 'protein'
    VEGETABLE = 'vegetable'
    CARB = 'carb'

class Ingredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.Enum(IngredientCategory), nullable=False)
    variations = db.Column(db.Text)  # Store cooking variations/preparations
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Database Models
class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    ingredients = db.Column(db.Text, nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    protein = db.Column(db.Float)  # in grams
    carbs = db.Column(db.Float)    # in grams
    fats = db.Column(db.Float)     # in grams
    calories = db.Column(db.Integer)
    prep_time = db.Column(db.Integer)  # in minutes
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class MealPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    recipe = db.relationship('Recipe', backref=db.backref('meal_plans', lazy=True))

def create_sample_recipes():
    """Create sample balanced recipes."""
    sample_recipes = [
        {
            'name': 'Cod with Roasted Potatoes & Broccoli',
            'description': 'Simple and healthy fish dish with roasted vegetables',
            'ingredients': '''Cod fillets
Potatoes
Broccoli
Olive oil
Herbs''',
            'instructions': 'Basic cooking instructions',
            'protein': 30,
            'carbs': 40,
            'fats': 15,
            'calories': 400,
            'prep_time': 15
        },
        {
            'name': 'Salmon, Rice, and Green Bean Medley',
            'description': 'Fresh salmon with rice and vegetables',
            'ingredients': '''Salmon fillets
Rice
Green beans
Lemon
Spices''',
            'instructions': 'Basic cooking instructions',
            'protein': 30,
            'carbs': 40,
            'fats': 15,
            'calories': 400,
            'prep_time': 10
        },
        {
            'name': 'Tuna Pasta Primavera',
            'description': 'Light pasta dish with tuna and vegetables',
            'ingredients': '''Tuna (canned or fresh)
Pasta
Mixed vegetables
Olive oil''',
            'instructions': 'Basic cooking instructions',
            'protein': 25,
            'carbs': 45,
            'fats': 15,
            'calories': 400,
            'prep_time': 15
        },
        {
            'name': 'Sardines on Toasted Tomato Bread',
            'description': 'Quick and healthy open-faced sandwich',
            'ingredients': '''Sardines (canned)
Tomatoes
Bread
Olive oil
Garlic''',
            'instructions': 'Basic cooking instructions',
            'protein': 20,
            'carbs': 30,
            'fats': 15,
            'calories': 350,
            'prep_time': 5
        },
        {
            'name': 'Mediterranean Fish Stew with Couscous',
            'description': 'Flavorful fish stew with Mediterranean spices',
            'ingredients': '''Mixed fish
Tomatoes
Onions
Couscous
Broth''',
            'instructions': 'Basic cooking instructions',
            'protein': 30,
            'carbs': 40,
            'fats': 15,
            'calories': 400,
            'prep_time': 20
        },
        {
            'name': 'Chicken Curry with Fragrant Rice',
            'description': 'Aromatic curry with tender chicken',
            'ingredients': '''Chicken
Curry spices
Coconut milk
Rice''',
            'instructions': 'Basic cooking instructions',
            'protein': 35,
            'carbs': 45,
            'fats': 20,
            'calories': 450,
            'prep_time': 15
        },
        {
            'name': 'Roasted Chicken, Carrots, and Golden Potatoes',
            'description': 'Classic roasted chicken with vegetables',
            'ingredients': '''Chicken
Carrots
Potatoes
Herbs
Olive oil''',
            'instructions': 'Basic cooking instructions',
            'protein': 35,
            'carbs': 40,
            'fats': 20,
            'calories': 450,
            'prep_time': 10
        },
        {
            'name': 'Creamy Chicken Breast with Peas and Pasta',
            'description': 'Creamy pasta dish with chicken and vegetables',
            'ingredients': '''Chicken breast
Peas
Pasta
Cream
Parmesan''',
            'instructions': 'Basic cooking instructions',
            'protein': 35,
            'carbs': 50,
            'fats': 25,
            'calories': 500,
            'prep_time': 15
        },
        {
            'name': 'Chicken Salad Sandwich on Artisan Bread',
            'description': 'Classic chicken salad sandwich',
            'ingredients': '''Cooked chicken
Mayonnaise
Celery
Bread''',
            'instructions': 'Basic cooking instructions',
            'protein': 25,
            'carbs': 35,
            'fats': 20,
            'calories': 400,
            'prep_time': 10
        },
        {
            'name': 'Chicken with Bok Choi and Steamed Rice',
            'description': 'Asian-inspired chicken dish',
            'ingredients': '''Chicken
Bok choy
Rice
Soy sauce
Ginger''',
            'instructions': 'Basic cooking instructions',
            'protein': 30,
            'carbs': 40,
            'fats': 15,
            'calories': 400,
            'prep_time': 10
        },
        {
            'name': 'Beef Steak with Asparagus and Roasted Potatoes',
            'description': 'Classic steak dinner',
            'ingredients': '''Beef steak
Asparagus
Potatoes
Olive oil
Seasonings''',
            'instructions': 'Basic cooking instructions',
            'protein': 40,
            'carbs': 35,
            'fats': 25,
            'calories': 500,
            'prep_time': 10
        },
        {
            'name': 'Ground Beef with Zucchini and Pasta',
            'description': 'Hearty pasta dish with ground beef',
            'ingredients': '''Ground beef
Zucchini
Pasta
Tomato sauce
Herbs''',
            'instructions': 'Basic cooking instructions',
            'protein': 35,
            'carbs': 45,
            'fats': 20,
            'calories': 450,
            'prep_time': 15
        },
        {
            'name': 'Hearty Beef Stew with Crusty Bread',
            'description': 'Comforting beef stew',
            'ingredients': '''Beef stew meat
Carrots
Potatoes
Onions
Broth''',
            'instructions': 'Basic cooking instructions',
            'protein': 35,
            'carbs': 40,
            'fats': 20,
            'calories': 450,
            'prep_time': 20
        },
        {
            'name': 'Beef Patties with Fresh Salad and Corn',
            'description': 'Simple burger with fresh sides',
            'ingredients': '''Ground beef
Salad greens
Corn
Tomatoes''',
            'instructions': 'Basic cooking instructions',
            'protein': 30,
            'carbs': 35,
            'fats': 25,
            'calories': 450,
            'prep_time': 10
        },
        {
            'name': 'Beef with Aubergine and Pasta',
            'description': 'Mediterranean-style beef and pasta',
            'ingredients': '''Beef
Aubergine(eggplant)
Pasta
Tomato sauce''',
            'instructions': 'Basic cooking instructions',
            'protein': 35,
            'carbs': 45,
            'fats': 20,
            'calories': 450,
            'prep_time': 20
        },
        {
            'name': 'Pork Chops with Green Beans and Potatoes',
            'description': 'Classic pork chop dinner',
            'ingredients': '''Pork chops
Green beans
Potatoes
Seasonings''',
            'instructions': 'Basic cooking instructions',
            'protein': 35,
            'carbs': 35,
            'fats': 20,
            'calories': 450,
            'prep_time': 10
        },
        {
            'name': 'Roasted Ribs with Braised Cabbage and Bread',
            'description': 'Hearty pork rib dinner',
            'ingredients': '''Pork ribs
Cabbage
Bread
Spices''',
            'instructions': 'Basic cooking instructions',
            'protein': 40,
            'carbs': 30,
            'fats': 30,
            'calories': 500,
            'prep_time': 15
        },
        {
            'name': 'Sausages with Lentils and Country Bread',
            'description': 'Rustic sausage and lentil dish',
            'ingredients': '''Sausages
Lentils
Bread
Vegetables''',
            'instructions': 'Basic cooking instructions',
            'protein': 30,
            'carbs': 40,
            'fats': 25,
            'calories': 450,
            'prep_time': 10
        },
        {
            'name': 'Prosciutto with Tomato and Fresh Bread',
            'description': 'Light Italian-style meal',
            'ingredients': '''Prosciutto
Tomatoes
Bread
Olive oil''',
            'instructions': 'Basic cooking instructions',
            'protein': 20,
            'carbs': 30,
            'fats': 15,
            'calories': 350,
            'prep_time': 5
        },
        {
            'name': 'Mortadella Pasta Salad',
            'description': 'Italian cold pasta salad',
            'ingredients': '''Mortadella
Pasta
Mixed vegetables
Dressing''',
            'instructions': 'Basic cooking instructions',
            'protein': 25,
            'carbs': 45,
            'fats': 20,
            'calories': 400,
            'prep_time': 15
        },
        {
            'name': 'Turkey Dutch Oven with Rice and Broccoli',
            'description': 'One-pot turkey and rice dish',
            'ingredients': '''Ground turkey
Rice
Broccoli
Onions
Spices''',
            'instructions': 'Basic cooking instructions',
            'protein': 30,
            'carbs': 40,
            'fats': 15,
            'calories': 400,
            'prep_time': 15
        },
        {
            'name': 'Merguez with Couscous and Carrots',
            'description': 'North African-inspired sausage dish',
            'ingredients': '''Merguez sausages
Couscous
Carrots
Spices''',
            'instructions': 'Basic cooking instructions',
            'protein': 25,
            'carbs': 40,
            'fats': 20,
            'calories': 400,
            'prep_time': 10
        },
        {
            'name': 'Bratwurst with Potatoes and Cabbage',
            'description': 'German-style sausage dinner',
            'ingredients': '''Bratwurst
Potatoes
Cabbage
Mustard''',
            'instructions': 'Basic cooking instructions',
            'protein': 25,
            'carbs': 35,
            'fats': 25,
            'calories': 400,
            'prep_time': 10
        },
        {
            'name': 'Chipo with Caramelized Onions on Bread',
            'description': 'Sausage sandwich with caramelized onions',
            'ingredients': '''Chipo sausages
Onions
Bread
Oil''',
            'instructions': 'Basic cooking instructions',
            'protein': 20,
            'carbs': 35,
            'fats': 20,
            'calories': 350,
            'prep_time': 15
        },
        {
            'name': 'Ham with Endive and Potatoes',
            'description': 'Classic ham dinner with vegetables',
            'ingredients': '''Ham
Endive
Potatoes
Cream''',
            'instructions': 'Basic cooking instructions',
            'protein': 30,
            'carbs': 35,
            'fats': 20,
            'calories': 400,
            'prep_time': 10
        },
        {
            'name': 'Ham and Melon with Toasted Bread',
            'description': 'Light summer meal',
            'ingredients': '''Ham
Melon
Bread''',
            'instructions': 'Basic cooking instructions',
            'protein': 20,
            'carbs': 30,
            'fats': 10,
            'calories': 300,
            'prep_time': 5
        },
        {
            'name': 'Herb Omelette with Toasted Bread and Salad',
            'description': 'Light and fresh omelette',
            'ingredients': '''Eggs
Herbs
Bread
Salad greens''',
            'instructions': 'Basic cooking instructions',
            'protein': 20,
            'carbs': 25,
            'fats': 15,
            'calories': 350,
            'prep_time': 5
        },
        {
            'name': 'Shakshuka with Warm Naan',
            'description': 'Middle Eastern egg dish',
            'ingredients': '''Eggs
Tomatoes
Peppers
Naan bread''',
            'instructions': 'Basic cooking instructions',
            'protein': 20,
            'carbs': 30,
            'fats': 15,
            'calories': 350,
            'prep_time': 10
        },
        {
            'name': 'Egg Salad Sandwich on Rustic Bread',
            'description': 'Classic egg salad sandwich',
            'ingredients': '''Eggs
Mayonnaise
Bread''',
            'instructions': 'Basic cooking instructions',
            'protein': 15,
            'carbs': 30,
            'fats': 20,
            'calories': 350,
            'prep_time': 10
        },
        {
            'name': 'Quiche with Side Salad and Potatoes',
            'description': 'French-style quiche with sides',
            'ingredients': '''Eggs
Cheese
Vegetables
Potatoes''',
            'instructions': 'Basic cooking instructions',
            'protein': 20,
            'carbs': 35,
            'fats': 25,
            'calories': 400,
            'prep_time': 20
        },
        {
            'name': 'Chickpea Curry with Basmati Rice',
            'description': 'Vegetarian curry dish',
            'ingredients': '''Chickpeas
Curry spices
Rice''',
            'instructions': 'Basic cooking instructions',
            'protein': 15,
            'carbs': 45,
            'fats': 10,
            'calories': 350,
            'prep_time': 15
        },
        {
            'name': 'Lentil Salad with Tomato and Bread',
            'description': 'Light vegetarian salad',
            'ingredients': '''Lentils
Tomatoes
Bread
Dressing''',
            'instructions': 'Basic cooking instructions',
            'protein': 15,
            'carbs': 40,
            'fats': 10,
            'calories': 350,
            'prep_time': 10
        },
        {
            'name': 'White Bean Stew with Carrots and Crusty Bread',
            'description': 'Hearty vegetarian stew',
            'ingredients': '''White beans
Carrots
Bread
Broth''',
            'instructions': 'Basic cooking instructions',
            'protein': 15,
            'carbs': 45,
            'fats': 10,
            'calories': 350,
            'prep_time': 15
        },
        {
            'name': 'Rice Beans with Steamed Broccoli and Rice',
            'description': 'Simple rice and beans dish',
            'ingredients': '''Rice beans
Broccoli
Rice''',
            'instructions': 'Basic cooking instructions',
            'protein': 15,
            'carbs': 50,
            'fats': 5,
            'calories': 350,
            'prep_time': 10
        },
        {
            'name': 'Lamb Chops with Potatoes and Asparagus',
            'description': 'Elegant lamb dinner',
            'ingredients': '''Lamb chops
Potatoes
Asparagus''',
            'instructions': 'Basic cooking instructions',
            'protein': 35,
            'carbs': 35,
            'fats': 25,
            'calories': 450,
            'prep_time': 10
        },
        {
            'name': 'Roasted Lamb with Carrots and Artisan Bread',
            'description': 'Classic roasted lamb dinner',
            'ingredients': '''Lamb
Carrots
Bread''',
            'instructions': 'Basic cooking instructions',
            'protein': 35,
            'carbs': 35,
            'fats': 25,
            'calories': 450,
            'prep_time': 15
        },
        {
            'name': 'Hearty Daal with Fragrant Rice and Salad',
            'description': 'Indian-style lentil dish',
            'ingredients': '''Lentils
Spices
Rice
Salad''',
            'instructions': 'Basic cooking instructions',
            'protein': 15,
            'carbs': 45,
            'fats': 10,
            'calories': 350,
            'prep_time': 20
        },
        {
            'name': 'Orzo with Zucchini and Pan-Seared Chicken',
            'description': 'Mediterranean pasta dish with chicken',
            'ingredients': '''Orzo pasta
Zucchini
Chicken''',
            'instructions': 'Basic cooking instructions',
            'protein': 30,
            'carbs': 45,
            'fats': 15,
            'calories': 400,
            'prep_time': 15
        },
        {
            'name': 'Mediterranean Fish Stew with Potatoes and Carrots',
            'description': 'Hearty fish stew',
            'ingredients': '''Mixed fish
Potatoes
Carrots
Tomatoes''',
            'instructions': 'Basic cooking instructions',
            'protein': 30,
            'carbs': 40,
            'fats': 15,
            'calories': 400,
            'prep_time': 20
        },
        {
            'name': 'Salmon with Broccolini and Steamed Rice',
            'description': 'Light and healthy salmon dish',
            'ingredients': '''Salmon
Broccolini
Rice''',
            'instructions': 'Basic cooking instructions',
            'protein': 30,
            'carbs': 40,
            'fats': 20,
            'calories': 400,
            'prep_time': 10
        },
        {
            'name': 'Cod with Turnips and Golden Potatoes',
            'description': 'Classic fish dinner',
            'ingredients': '''Cod
Turnips
Potatoes''',
            'instructions': 'Basic cooking instructions',
            'protein': 25,
            'carbs': 40,
            'fats': 10,
            'calories': 350,
            'prep_time': 10
        },
        {
            'name': 'Beef and Aubergine Pasta',
            'description': 'Hearty pasta dish',
            'ingredients': '''Beef
Aubergine
Pasta''',
            'instructions': 'Basic cooking instructions',
            'protein': 35,
            'carbs': 45,
            'fats': 20,
            'calories': 450,
            'prep_time': 20
        },
        {
            'name': 'Pork with Zucchini and Rice',
            'description': 'Simple pork and rice dish',
            'ingredients': '''Pork
Zucchini
Rice''',
            'instructions': 'Basic cooking instructions',
            'protein': 30,
            'carbs': 40,
            'fats': 15,
            'calories': 400,
            'prep_time': 15
        },
        {
            'name': 'Turkey Lentils and Bread',
            'description': 'Healthy turkey and lentil dish',
            'ingredients': '''Turkey
Lentils
Bread''',
            'instructions': 'Basic cooking instructions',
            'protein': 35,
            'carbs': 40,
            'fats': 10,
            'calories': 400,
            'prep_time': 15
        },
        {
            'name': 'Egg and Tomato on Toast',
            'description': 'Simple breakfast for dinner',
            'ingredients': '''Eggs
Tomatoes
Bread''',
            'instructions': 'Basic cooking instructions',
            'protein': 15,
            'carbs': 25,
            'fats': 15,
            'calories': 300,
            'prep_time': 5
        },
        {
            'name': 'Beans with Corn and Bread',
            'description': 'Simple vegetarian dish',
            'ingredients': '''Beans
Corn
Bread''',
            'instructions': 'Basic cooking instructions',
            'protein': 15,
            'carbs': 45,
            'fats': 5,
            'calories': 350,
            'prep_time': 10
        },
        {
            'name': 'Lamb with Peas and Potatoes',
            'description': 'Classic lamb dinner',
            'ingredients': '''Lamb
Peas
Potatoes''',
            'instructions': 'Basic cooking instructions',
            'protein': 35,
            'carbs': 35,
            'fats': 25,
            'calories': 450,
            'prep_time': 15
        },
        {
            'name': 'Butternut and Chicken with Rice',
            'description': 'Autumn-inspired chicken dish',
            'ingredients': '''Butternut squash
Chicken
Rice''',
            'instructions': 'Basic cooking instructions',
            'protein': 30,
            'carbs': 45,
            'fats': 15,
            'calories': 400,
            'prep_time': 20
        },
        {
            'name': 'Couscous with Merguez and Carrots',
            'description': 'North African-inspired dish',
            'ingredients': '''Merguez
Couscous
Carrots''',
            'instructions': 'Basic cooking instructions',
            'protein': 25,
            'carbs': 40,
            'fats': 20,
            'calories': 400,
            'prep_time': 10
        }
    ]
    
    # Clear existing recipes
    Recipe.query.delete()
    
    # Add new recipes
    for recipe_data in sample_recipes:
        recipe = Recipe(**recipe_data)
        db.session.add(recipe)
    
    db.session.commit()

def create_personal_ingredients():
    """Create your personal ingredient list."""
    ingredients = [
        # Proteins
        {'name': 'Fish', 'category': IngredientCategory.PROTEIN, 
         'variations': 'Cod, Salmon, Sardines, Tuna, Saumon fumé, Blanquette de poissons'},
        {'name': 'Chicken', 'category': IngredientCategory.PROTEIN,
         'variations': 'Thighs, Roasted, Breasts with cream, Curry, Sandwich, En papillotte, Sauce champignons'},
        {'name': 'Beef', 'category': IngredientCategory.PROTEIN,
         'variations': 'Steaks, Patties, Ground beef, Stew pieces'},
        {'name': 'Pork', 'category': IngredientCategory.PROTEIN,
         'variations': 'Chops, Roasted ribs, Sausages'},
        {'name': 'Charcuterie', 'category': IngredientCategory.PROTEIN,
         'variations': 'Prosciutto, Mortadella'},
        {'name': 'Turkey', 'category': IngredientCategory.PROTEIN,
         'variations': 'Ground turkey with vegetables (Dutch oven)'},
        {'name': 'Sausages', 'category': IngredientCategory.PROTEIN,
         'variations': 'Chipolatas, Merguez, Bratwurst'},
        {'name': 'Ham', 'category': IngredientCategory.PROTEIN,
         'variations': 'With endives, With melon'},
        {'name': 'Eggs', 'category': IngredientCategory.PROTEIN,
         'variations': 'Omelette, Sunny side up, Sandwich, Boiled in salad, Shakshuka, Quiche'},
        {'name': 'Beans', 'category': IngredientCategory.PROTEIN,
         'variations': 'Rice and beans, White bean stew, Chickpea curry, Tacos, Hot lentils, Lentil salad, Daal, Chickpea salad with onion/tomato/cucumber/cumin'},
        {'name': 'Lamb', 'category': IngredientCategory.PROTEIN,
         'variations': 'Gigot, Carré, Lamb chops'},
        
        # Vegetables
        {'name': 'Steam Vegetables', 'category': IngredientCategory.VEGETABLE,
         'variations': 'Green beans, Peas, Broccoli, Asparagus, Cauliflower, Cabbage, Leeks, Carrots, Turnips, Zucchini, Broccolini, Bok choy'},
        {'name': 'Endives', 'category': IngredientCategory.VEGETABLE,
         'variations': 'Gratin, Braised with mushrooms, Raw'},
        {'name': 'Raw Vegetables', 'category': IngredientCategory.VEGETABLE,
         'variations': 'Salad, Tomatoes with mozzarella, Cucumber, Onion, Carrots, Avocado, Grapefruit'},
        {'name': 'Carrots', 'category': IngredientCategory.VEGETABLE,
         'variations': 'Purée, Roasted, Boiled, Cooked with fish'},
        {'name': 'Eggplant', 'category': IngredientCategory.VEGETABLE,
         'variations': 'Grilled, In pasta'},
        {'name': 'Butternut Squash', 'category': IngredientCategory.VEGETABLE,
         'variations': 'Roasted, Soup'},
        
        # Carbs
        {'name': 'Bread', 'category': IngredientCategory.CARB,
         'variations': 'Sourdough batard, Naan'},
        {'name': 'Pasta', 'category': IngredientCategory.CARB,
         'variations': 'Giovanni Rana, Hot, Alla norma (tomato/eggplant/cheese/basil)'},
        {'name': 'Potatoes', 'category': IngredientCategory.CARB,
         'variations': 'Small red, Big yellow, Purée, Boiled, Roasted'},
        {'name': 'Rice', 'category': IngredientCategory.CARB,
         'variations': 'In salad, With curry, Plain hot'},
        {'name': 'Couscous', 'category': IngredientCategory.CARB,
         'variations': 'Plain, With vegetables'},
        {'name': 'Corn', 'category': IngredientCategory.CARB,
         'variations': 'On the cob, In salad, Hot'}
    ]
    
    for ingredient_data in ingredients:
        existing = Ingredient.query.filter_by(name=ingredient_data['name']).first()
        if not existing:
            ingredient = Ingredient(**ingredient_data)
            db.session.add(ingredient)
    
    db.session.commit()

# Create database tables and sample data
with app.app_context():
    db.create_all()
    create_personal_ingredients()
    create_sample_recipes()

@app.route('/')
def index():
    """Home page showing current meal plan and recipes."""
    recipes = Recipe.query.all()
    today = datetime.now().date()
    week_meal_plans = MealPlan.query.filter(
        MealPlan.date >= today,
        MealPlan.date < today + timedelta(days=7)
    ).order_by(MealPlan.date).all()
    return render_template('index.html', recipes=recipes, meal_plans=week_meal_plans)

@app.route('/recipe/add', methods=['GET', 'POST'])
def add_recipe():
    """Add a new recipe to the database."""
    if request.method == 'POST':
        recipe = Recipe(
            name=request.form['name'],
            description=request.form.get('description', ''),
            ingredients=request.form['ingredients'],
            instructions=request.form['instructions'],
            protein=float(request.form['protein']),
            carbs=float(request.form['carbs']),
            fats=float(request.form['fats']),
            calories=int(request.form['calories']),
            prep_time=int(request.form['prep_time'])
        )
        db.session.add(recipe)
        db.session.commit()
        flash('Recipe added successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('add_recipe.html')

@app.route('/recipe/<int:recipe_id>')
def view_recipe(recipe_id):
    """View details of a specific recipe."""
    recipe = Recipe.query.get_or_404(recipe_id)
    return render_template('recipe_detail.html', recipe=recipe)

@app.route('/generate_meal_plan')
def generate_meal_plan():
    """Generate a balanced meal plan for the week."""
    # Clear existing meal plans for the upcoming week
    today = datetime.now().date()
    MealPlan.query.filter(
        MealPlan.date >= today,
        MealPlan.date < today + timedelta(days=7)
    ).delete()
    
    # Get all recipes
    recipes = Recipe.query.all()
    if not recipes:
        flash('Please add some recipes first!', 'warning')
        return redirect(url_for('index'))
    
    # Generate a balanced meal plan for 7 days
    used_recipes = set()  # Track used recipes to avoid repetition
    for i in range(7):
        date = today + timedelta(days=i)
        available_recipes = [r for r in recipes if r.id not in used_recipes]
        
        # If we've used all recipes, reset the used_recipes set
        if not available_recipes:
            available_recipes = recipes
            used_recipes.clear()
        
        recipe = random.choice(available_recipes)
        used_recipes.add(recipe.id)
        
        meal_plan = MealPlan(date=date, recipe_id=recipe.id)
        db.session.add(meal_plan)
    
    db.session.commit()
    flash('New meal plan generated!', 'success')
    return redirect(url_for('index'))

@app.route('/meal_plan/<int:plan_id>/change', methods=['POST'])
def change_meal(plan_id):
    """Change a specific meal in the plan to a random different recipe."""
    meal_plan = MealPlan.query.get_or_404(plan_id)
    current_recipe_id = meal_plan.recipe_id
    
    # Get all recipes except the current one
    available_recipes = Recipe.query.filter(Recipe.id != current_recipe_id).all()
    if available_recipes:
        new_recipe = random.choice(available_recipes)
        meal_plan.recipe_id = new_recipe.id
        db.session.commit()
        flash(f'Meal updated to: {new_recipe.name}', 'success')
    else:
        flash('No alternative recipes available', 'warning')
    
    return redirect(url_for('index'))

@app.route('/ingredients')
def view_ingredients():
    """View all ingredients organized by category."""
    proteins = Ingredient.query.filter_by(category=IngredientCategory.PROTEIN).all()
    vegetables = Ingredient.query.filter_by(category=IngredientCategory.VEGETABLE).all()
    carbs = Ingredient.query.filter_by(category=IngredientCategory.CARB).all()
    return render_template('ingredients.html', 
                         proteins=proteins, 
                         vegetables=vegetables, 
                         carbs=carbs)

def send_weekly_meal_plan():
    """Generate and send weekly meal plan via email."""
    # Generate new meal plan
    today = datetime.now().date()
    MealPlan.query.filter(
        MealPlan.date >= today,
        MealPlan.date < today + timedelta(days=7)
    ).delete()
    
    recipes = Recipe.query.all()
    if not recipes:
        return "No recipes available"
    
    used_recipes = set()
    meal_plan_text = "Your Meal Plan for the Week:\n\n"
    
    # Keep track of all ingredients needed
    all_ingredients = set()
    
    for i in range(7):
        date = today + timedelta(days=i)
        available_recipes = [r for r in recipes if r.id not in used_recipes]
        
        if not available_recipes:
            available_recipes = recipes
            used_recipes.clear()
        
        recipe = random.choice(available_recipes)
        used_recipes.add(recipe.id)
        
        meal_plan = MealPlan(date=date, recipe_id=recipe.id)
        db.session.add(meal_plan)
        
        meal_plan_text += f"{date.strftime('%A, %B %d')}:\n"
        meal_plan_text += f"Recipe: {recipe.name}\n"
        meal_plan_text += f"Prep Time: {recipe.prep_time} minutes\n\n"
        
        # Add ingredients to the shopping list
        recipe_ingredients = recipe.ingredients.split('\n')
        all_ingredients.update(recipe_ingredients)
    
    db.session.commit()
    
    # Add shopping list to the email
    meal_plan_text += "\nShopping List for the Week:\n"
    meal_plan_text += "------------------------\n"
    for ingredient in sorted(all_ingredients):
        meal_plan_text += f"□ {ingredient.strip()}\n"
    
    # Send email
    msg = Message(
        subject=f"Your Weekly Meal Plan - Week of {today.strftime('%B %d, %Y')}",
        recipients=['simon.cremieux@gmail.com'],
        body=meal_plan_text
    )
    mail.send(msg)
    return "Meal plan sent successfully"

@app.cli.command('send-meal-plan')
def send_meal_plan_command():
    """Flask CLI command to send meal plan."""
    send_weekly_meal_plan()
    print("Weekly meal plan sent!")

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=3000) 