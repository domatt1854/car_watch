RAM_MODELS = ['1500', '2500', '3500', 'ProMaster']
ROLLS_ROYCE_MODELS = ['Cullinan']
ASTON_MARTIN_MODELS = ['DBX', 'Vantage']
NISSAN_MODELS = ['Frontier', 'Titan']
TOYOTA_MODELS = ['Tacoma', 'Tundra', 'GR86']
GMC_MODELS = ['Canyon']
CHEVY_MODELS = ['Colorado']
VOLKSWAGEN_MODELS = ['ID.4', 'Taos']
FORD_MODELS = ['Ranger', 'Maverick', 'Transit']


# how the makes will be formatted when querying from the API
QUERY_MAKES = [
    "acura",
    "buick",
    "cadillac",
    "chevrolet",
    "chrysler",
    "gmc",
    "ford",
    "honda",
    "infiniti",
    "jeep",
    "kia",
    "mitsubishi",
    "nissan",
    "porsche",
    "ram",
    "subaru",
    "toyota",
    "volkswagen",
    "volvo",
    "alfa_romeo",
    "rolls_royce",
    "mini",
    "fiat",
    "aston_martin",
    "maserati",
    "bmw",
    "mercedes_benz"
]

# How the makes will be displayed in the drop down menu
DROP_DOWN_MENU_MAKES = [
    "Acura",
    "Buick",
    "Cadillac",
    "Chevrolet",
    "Chrysler",
    "GMC",
    "Ford",
    "Honda",
    "Infiniti",
    "Jeep",
    "Kia",
    "Mitsubishi",
    "Nissan",
    "Porsche",
    "Ram",
    "Subaru",
    "Toyota",
    "Volkswagen",
    "Volvo",
    "Alfa Romeo",
    "Rolls Royce",
    "Mini",
    "Fiat",
    "Aston Martin",
    "Maserati",
    "BMW",
    "Mercedes Benz"
]

# make names within the makes_models.csv
MAKES_JOIN_KEY = [
    'Acura',
    'Buick',
    'Cadillac',
    'Chevrolet',
    'Chrysler',
    'Gmc',
    'Ford',
    'Honda',
    'Infiniti',
    'Jeep',
    'Kia',
    'Mitsubishi',
    'Nissan',
    'Porsche',
    'Ram',
    'Subaru',
    'Toyota',
    'Volkswagen',
    'Volvo',
    'Alfa Romeo',
    'Rolls Royce',
    'Mini',
    'Fiat',
    'Aston Martin',
    'Maserati',
    'Bmw',
    'Mercedes Benz'
]

MAKES_DROPDOWN_TO_PARAMETER_QUERY = {k: v for k, v in zip(DROP_DOWN_MENU_MAKES, QUERY_MAKES)}
MAKES_DROPDOWN_TO_JOIN_KEY = {k: v for k, v in zip(QUERY_MAKES, MAKES_JOIN_KEY)}