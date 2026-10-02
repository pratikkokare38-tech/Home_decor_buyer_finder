# Categories mapping for US Home Decor Buyers
BUYER_CATEGORIES = {
    'furniture': {
        'label': 'Furniture Stores & Showrooms',
        'geoapify_categories': ['commercial.houseware_and_furniture', 'commercial.furniture'],
        'osm_tags': ['shop=furniture', 'shop=interior_decoration', 'shop=bed'],
    },
    'interior_decoration': {
        'label': 'Interior Decor & Design Boutiques',
        'geoapify_categories': ['commercial.interior_decoration', 'commercial.antiques'],
        'osm_tags': ['shop=interior_decoration', 'shop=antiques', 'shop=curtain', 'shop=lighting'],
    },
    'gift_and_souvenir': {
        'label': 'Gift & Artisan Specialty Shops',
        'geoapify_categories': ['commercial.gift_and_souvenir', 'commercial.craft'],
        'osm_tags': ['shop=gift', 'shop=craft', 'shop=art', 'shop=boutique'],
    },
    'houseware': {
        'label': 'Houseware & Home Accessories Stores',
        'geoapify_categories': ['commercial.houseware_and_furniture', 'commercial.hardware'],
        'osm_tags': ['shop=houseware', 'shop=kitchen', 'shop=pottery', 'shop=tableware'],
    },
    'all': {
        'label': 'All US Home Decor Buyers',
        'geoapify_categories': [
            'commercial.houseware_and_furniture',
            'commercial.furniture',
            'commercial.interior_decoration',
            'commercial.gift_and_souvenir',
            'commercial.antiques'
        ],
        'osm_tags': ['shop=furniture', 'shop=interior_decoration', 'shop=gift', 'shop=antiques', 'shop=houseware', 'shop=craft', 'shop=lighting'],
    }
}

# Standard 50 US States + DC
US_STATES = {
    'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas', 'CA': 'California',
    'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware', 'FL': 'Florida', 'GA': 'Georgia',
    'HI': 'Hawaii', 'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa',
    'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
    'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi', 'MO': 'Missouri',
    'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada', 'NH': 'New Hampshire', 'NJ': 'New Jersey',
    'NM': 'New Mexico', 'NY': 'New York', 'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio',
    'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina',
    'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah', 'VT': 'Vermont',
    'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia', 'WI': 'Wisconsin', 'WY': 'Wyoming',
    'DC': 'District of Columbia'
}

# Quota Limits
GEOAPIFY_DAILY_LIMIT = 3000
HUNTER_MONTHLY_LIMIT = 50
BREVO_DAILY_LIMIT = 300
