# faker_food: food provider for Faker
An add-on provider for the Python Faker module to generate random and/or fake data for food-related categories.

## Description
`faker_maytok_food` provides food-related fake data for testing purposes.

## Installation
Install the `faker_maytok_food` library with your package management tool.
``` bash
pip install faker_maytok_food
```

## Usage
Add as a provider to your Faker instance:
``` python
>>> from faker import Faker
>>> from faker_food import FoodProvider
>>> fake = Faker()
>>> fake.add_provider(FoodProvider)
```

Now you can start to generate data:

```python
>>> fake.dish()
>>> fake.dish_description()
>>> fake.ethnic_category()
>>> fake.fruit()
>>> fake.ingredient()
>>> fake.measurement()
>>> fake.metric_measurement()
>>> fake.measurement_size()
>>> fake.spice()
>>> fake.sushi()
>>> fake.vegetable()
```
