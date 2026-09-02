"""
Constants and Reference Master Data for Synthetic MPLADS Data Generator.
All master data uses synthetic demonstration entities adhering to synthetic data guidelines.
"""

from typing import Dict, List, Tuple, Any

# Mandatory metadata flag
SYNTHETIC_FLAG: bool = True

# Standard Categories for MPLADS peer-group analysis
CATEGORIES: List[str] = [
    "Drinking Water",
    "Education Infrastructure",
    "Health & Sanitation",
    "Roads, Pathways & Bridges",
    "Community Infrastructure & Halls",
    "Irrigation & Flood Control",
    "Renewable & Solar Energy",
    "Sports & Youth Development",
]

# Cost and timeline benchmarks per category (amounts in INR)
# (min_estimate, median_estimate, max_estimate, typical_duration_days)
CATEGORY_BENCHMARKS: Dict[str, Dict[str, Any]] = {
    "Drinking Water": {
        "min_cost": 150_000,
        "median_cost": 500_000,
        "max_cost": 2_500_000,
        "typical_duration_days": 120,
        "std_cost": 300_000,
    },
    "Education Infrastructure": {
        "min_cost": 400_000,
        "median_cost": 1_500_000,
        "max_cost": 6_000_000,
        "typical_duration_days": 210,
        "std_cost": 800_000,
    },
    "Health & Sanitation": {
        "min_cost": 300_000,
        "median_cost": 1_200_000,
        "max_cost": 5_000_000,
        "typical_duration_days": 180,
        "std_cost": 700_000,
    },
    "Roads, Pathways & Bridges": {
        "min_cost": 500_000,
        "median_cost": 2_500_000,
        "max_cost": 10_000_000,
        "typical_duration_days": 270,
        "std_cost": 1_500_000,
    },
    "Community Infrastructure & Halls": {
        "min_cost": 600_000,
        "median_cost": 2_000_000,
        "max_cost": 7_500_000,
        "typical_duration_days": 240,
        "std_cost": 1_200_000,
    },
    "Irrigation & Flood Control": {
        "min_cost": 450_000,
        "median_cost": 1_800_000,
        "max_cost": 8_000_000,
        "typical_duration_days": 240,
        "std_cost": 1_100_000,
    },
    "Renewable & Solar Energy": {
        "min_cost": 200_000,
        "median_cost": 800_000,
        "max_cost": 3_500_000,
        "typical_duration_days": 90,
        "std_cost": 450_000,
    },
    "Sports & Youth Development": {
        "min_cost": 350_000,
        "median_cost": 1_400_000,
        "max_cost": 5_500_000,
        "typical_duration_days": 180,
        "std_cost": 850_000,
    },
}

# Master List of States, Districts, Constituencies, and geographic centers (lat, lon, bounding radius in deg)
STATE_DISTRICT_MASTER: Dict[str, Dict[str, Dict[str, Any]]] = {
    "Maharashtra": {
        "Pune": {
            "constituency": "Pune Parliamentary Constituency",
            "lat": 18.5204,
            "lon": 73.8567,
            "sub_divisions": ["Haveli", "Khed", "Baramati", "Shirur", "Maval", "Ambegaon"],
        },
        "Nagpur": {
            "constituency": "Nagpur Parliamentary Constituency",
            "lat": 21.1458,
            "lon": 79.0882,
            "sub_divisions": ["Nagpur Urban", "Nagpur Rural", "Katol", "Saoner", "Ramtek", "Umred"],
        },
        "Nashik": {
            "constituency": "Nashik Parliamentary Constituency",
            "lat": 19.9975,
            "lon": 73.7898,
            "sub_divisions": ["Nashik Central", "Dindori", "Igatpuri", "Sinnar", "Niphad", "Malegaon"],
        },
        "Aurangabad": {
            "constituency": "Aurangabad Parliamentary Constituency",
            "lat": 19.8762,
            "lon": 75.3433,
            "sub_divisions": ["Aurangabad East", "Aurangabad West", "Paithan", "Gangapur", "Vaijapur", "Kannad"],
        },
        "Thane": {
            "constituency": "Thane Parliamentary Constituency",
            "lat": 19.2183,
            "lon": 72.9781,
            "sub_divisions": ["Thane City", "Kalyan", "Murbad", "Bhiwandi", "Shahapur"],
        },
    },
    "Tamil Nadu": {
        "Chennai": {
            "constituency": "Chennai Central Parliamentary Constituency",
            "lat": 13.0827,
            "lon": 80.2707,
            "sub_divisions": ["Tondiarpet", "Egmore", "Mylapore", "Guindy", "Velachery", "Royapuram"],
        },
        "Coimbatore": {
            "constituency": "Coimbatore Parliamentary Constituency",
            "lat": 11.0168,
            "lon": 76.9558,
            "sub_divisions": ["Coimbatore North", "Coimbatore South", "Pollachi", "Mettupalayam", "Sulur"],
        },
        "Madurai": {
            "constituency": "Madurai Parliamentary Constituency",
            "lat": 9.9252,
            "lon": 78.1198,
            "sub_divisions": ["Madurai North", "Madurai South", "Melur", "Thirumangalam", "Usilampatti"],
        },
        "Tiruchirappalli": {
            "constituency": "Tiruchirappalli Parliamentary Constituency",
            "lat": 10.7905,
            "lon": 78.7047,
            "sub_divisions": ["Tiruchirappalli East", "Tiruchirappalli West", "Srirangam", "Manapparai", "Lalgudi"],
        },
        "Salem": {
            "constituency": "Salem Parliamentary Constituency",
            "lat": 11.6643,
            "lon": 78.1460,
            "sub_divisions": ["Salem North", "Salem South", "Attur", "Omalur", "Mettur", "Sankari"],
        },
    },
    "Karnataka": {
        "Bengaluru Urban": {
            "constituency": "Bengaluru South Parliamentary Constituency",
            "lat": 12.9716,
            "lon": 77.5946,
            "sub_divisions": ["Bengaluru North", "Bengaluru South", "Bengaluru East", "Anekal", "Yelahanka"],
        },
        "Mysuru": {
            "constituency": "Mysore Parliamentary Constituency",
            "lat": 12.2958,
            "lon": 76.6394,
            "sub_divisions": ["Mysuru City", "Nanjangud", "Hunsur", "T. Narasipura", "K.R. Nagar"],
        },
        "Dharwad": {
            "constituency": "Dharwad Parliamentary Constituency",
            "lat": 15.4589,
            "lon": 75.0078,
            "sub_divisions": ["Hubballi Urban", "Dharwad Urban", "Kalghatgi", "Kundgol", "Navalgund"],
        },
        "Belagavi": {
            "constituency": "Belgaum Parliamentary Constituency",
            "lat": 15.8497,
            "lon": 74.4977,
            "sub_divisions": ["Belagavi Rural", "Chikkodi", "Gokak", "Bailhongal", "Athani", "Ramdurg"],
        },
        "Dakshina Kannada": {
            "constituency": "Dakshina Kannada Parliamentary Constituency",
            "lat": 12.9141,
            "lon": 74.8560,
            "sub_divisions": ["Mangaluru", "Bantwal", "Puttur", "Belthangady", "Sullia"],
        },
    },
    "Uttar Pradesh": {
        "Lucknow": {
            "constituency": "Lucknow Parliamentary Constituency",
            "lat": 26.8467,
            "lon": 80.9462,
            "sub_divisions": ["Lucknow Central", "Bakshi Ka Talab", "Malihabad", "Sarojini Nagar", "Mohanlalganj"],
        },
        "Varanasi": {
            "constituency": "Varanasi Parliamentary Constituency",
            "lat": 25.3176,
            "lon": 82.9739,
            "sub_divisions": ["Varanasi Cantt", "Varanasi North", "Varanasi South", "Rohaniya", "Sewapuri", "Pindra"],
        },
        "Kanpur Nagar": {
            "constituency": "Kanpur Parliamentary Constituency",
            "lat": 26.4499,
            "lon": 80.3319,
            "sub_divisions": ["Kanpur Central", "Kalyanpur", "Govind Nagar", "Bilhaur", "Ghatampur"],
        },
        "Agra": {
            "constituency": "Agra Parliamentary Constituency",
            "lat": 27.1767,
            "lon": 78.0081,
            "sub_divisions": ["Agra Cantt", "Agra North", "Agra South", "Fatehabad", "Etmadpur", "Kheragarh"],
        },
        "Prayagraj": {
            "constituency": "Allahabad Parliamentary Constituency",
            "lat": 25.4358,
            "lon": 81.8463,
            "sub_divisions": ["Allahabad North", "Allahabad South", "Phulpur", "Karchhana", "Handia", "Bara"],
        },
    },
    "Rajasthan": {
        "Jaipur": {
            "constituency": "Jaipur Parliamentary Constituency",
            "lat": 26.9124,
            "lon": 75.7873,
            "sub_divisions": ["Jaipur Urban", "Sanganer", "Amber", "Chaksu", "Jamwa Ramgarh", "Phulera"],
        },
        "Jodhpur": {
            "constituency": "Jodhpur Parliamentary Constituency",
            "lat": 26.2389,
            "lon": 73.0243,
            "sub_divisions": ["Jodhpur City", "Sardarpura", "Luni", "Bilara", "Shergarh", "Osian"],
        },
        "Udaipur": {
            "constituency": "Udaipur Parliamentary Constituency",
            "lat": 24.5854,
            "lon": 73.7125,
            "sub_divisions": ["Udaipur City", "Udaipur Rural", "Mavli", "Vallabhnagar", "Salumber", "Kherwara"],
        },
        "Kota": {
            "constituency": "Kota Parliamentary Constituency",
            "lat": 25.2138,
            "lon": 75.8648,
            "sub_divisions": ["Kota North", "Kota South", "Ladpura", "Sangod", "Ramganj Mandi", "Pipalda"],
        },
        "Ajmer": {
            "constituency": "Ajmer Parliamentary Constituency",
            "lat": 26.4499,
            "lon": 74.6399,
            "sub_divisions": ["Ajmer North", "Ajmer South", "Kishangarh", "Pushkar", "Nasirabad", "Beawar"],
        },
    },
    "Gujarat": {
        "Ahmedabad": {
            "constituency": "Ahmedabad East Parliamentary Constituency",
            "lat": 23.0225,
            "lon": 72.5714,
            "sub_divisions": ["Ahmedabad City", "Daskroi", "Sanand", "Dholka", "Viramgam", "Bavla"],
        },
        "Surat": {
            "constituency": "Surat Parliamentary Constituency",
            "lat": 21.1702,
            "lon": 72.8311,
            "sub_divisions": ["Surat City", "Choryasi", "Bardoli", "Olpad", "Kamrej", "Mahuva"],
        },
        "Vadodara": {
            "constituency": "Vadodara Parliamentary Constituency",
            "lat": 22.3072,
            "lon": 73.1812,
            "sub_divisions": ["Vadodara City", "Padra", "Karjan", "Savli", "Waghodia", "Dabhoi"],
        },
        "Rajkot": {
            "constituency": "Rajkot Parliamentary Constituency",
            "lat": 22.3039,
            "lon": 70.8022,
            "sub_divisions": ["Rajkot Urban", "Gondal", "Jetpur", "Dhoraji", "Jasdan", "Morbi"],
        },
    },
    "West Bengal": {
        "Kolkata": {
            "constituency": "Kolkata North Parliamentary Constituency",
            "lat": 22.5726,
            "lon": 88.3639,
            "sub_divisions": ["Shyampukur", "Maniktala", "Beliaghata", "Jorasanko", "Entally", "Bhowanipore"],
        },
        "North 24 Parganas": {
            "constituency": "Barasat Parliamentary Constituency",
            "lat": 22.7196,
            "lon": 88.4674,
            "sub_divisions": ["Barasat", "Barrackpore", "Bangaon", "Basirhat", "Bidhannagar"],
        },
        "Darjeeling": {
            "constituency": "Darjeeling Parliamentary Constituency",
            "lat": 27.0410,
            "lon": 88.2663,
            "sub_divisions": ["Darjeeling Sadar", "Kurseong", "Siliguri", "Mirik", "Matigara"],
        },
        "Purba Medinipur": {
            "constituency": "Tamluk Parliamentary Constituency",
            "lat": 21.9366,
            "lon": 87.7787,
            "sub_divisions": ["Tamluk", "Haldia", "Contai", "Egra", "Panskura"],
        },
    },
    "Kerala": {
        "Thiruvananthapuram": {
            "constituency": "Thiruvananthapuram Parliamentary Constituency",
            "lat": 8.5241,
            "lon": 76.9366,
            "sub_divisions": ["Thiruvananthapuram City", "Neyyattinkara", "Nedumangad", "Attingal", "Varkala"],
        },
        "Ernakulam": {
            "constituency": "Ernakulam Parliamentary Constituency",
            "lat": 9.9816,
            "lon": 76.2999,
            "sub_divisions": ["Kochi", "Aluva", "Paravur", "Kunnathunad", "Kanayannur", "Muvattupuzha"],
        },
        "Kozhikode": {
            "constituency": "Kozhikode Parliamentary Constituency",
            "lat": 11.2588,
            "lon": 75.7804,
            "sub_divisions": ["Kozhikode City", "Vadakara", "Koyilandy", "Thamarassery"],
        },
    },
    "Madhya Pradesh": {
        "Bhopal": {
            "constituency": "Bhopal Parliamentary Constituency",
            "lat": 23.2599,
            "lon": 77.4126,
            "sub_divisions": ["Bhopal City", "Huzur", "Berasia", "Kolar", "Govindpura"],
        },
        "Indore": {
            "constituency": "Indore Parliamentary Constituency",
            "lat": 22.7196,
            "lon": 75.8577,
            "sub_divisions": ["Indore City", "Sanwer", "Depalpur", "Mhow", "Rau"],
        },
        "Gwalior": {
            "constituency": "Gwalior Parliamentary Constituency",
            "lat": 26.2183,
            "lon": 78.1828,
            "sub_divisions": ["Gwalior City", "Gwalior Rural", "Dabra", "Bhitarwar"],
        },
    },
    "Bihar": {
        "Patna": {
            "constituency": "Patna Sahib Parliamentary Constituency",
            "lat": 25.5941,
            "lon": 85.1376,
            "sub_divisions": ["Patna Sadar", "Danapur", "Barh", "Masaurhi", "Paliganj", "Bakhtiarpur"],
        },
        "Gaya": {
            "constituency": "Gaya Parliamentary Constituency",
            "lat": 24.7914,
            "lon": 85.0002,
            "sub_divisions": ["Gaya Town", "Bodh Gaya", "Sherghati", "Tekari", "Wazirganj"],
        },
        "Muzaffarpur": {
            "constituency": "Muzaffarpur Parliamentary Constituency",
            "lat": 26.1209,
            "lon": 85.3647,
            "sub_divisions": ["Muzaffarpur East", "Muzaffarpur West", "Kanti", "Motipur", "Minapur"],
        },
    },
    "Telangana": {
        "Hyderabad": {
            "constituency": "Hyderabad Parliamentary Constituency",
            "lat": 17.3850,
            "lon": 78.4867,
            "sub_divisions": ["Charminar", "Secunderabad", "Khairatabad", "Musheerabad", "Malakpet", "Amberpet"],
        },
        "Warangal": {
            "constituency": "Warangal Parliamentary Constituency",
            "lat": 17.9689,
            "lon": 79.5941,
            "sub_divisions": ["Warangal East", "Warangal West", "Hanamkonda", "Wardhannapet", "Narsampet"],
        },
    },
    "Assam": {
        "Kamrup Metropolitan": {
            "constituency": "Gauhati Parliamentary Constituency",
            "lat": 26.1445,
            "lon": 91.7362,
            "sub_divisions": ["Guwahati", "Dispur", "Sonapur", "Chandrapur", "Azara"],
        },
        "Dibrugarh": {
            "constituency": "Dibrugarh Parliamentary Constituency",
            "lat": 27.4728,
            "lon": 94.9120,
            "sub_divisions": ["Dibrugarh East", "Dibrugarh West", "Chabua", "Tingkhong", "Naharkatia"],
        },
    },
    "Punjab": {
        "Amritsar": {
            "constituency": "Amritsar Parliamentary Constituency",
            "lat": 31.6340,
            "lon": 74.8723,
            "sub_divisions": ["Amritsar Central", "Amritsar North", "Amritsar South", "Ajnala", "Majitha", "Attari"],
        },
        "Ludhiana": {
            "constituency": "Ludhiana Parliamentary Constituency",
            "lat": 30.9010,
            "lon": 75.8573,
            "sub_divisions": ["Ludhiana East", "Ludhiana West", "Ludhiana Central", "Jagraon", "Khanna", "Sahnewal"],
        },
    },
    "Odisha": {
        "Khordha": {
            "constituency": "Bhubaneswar Parliamentary Constituency",
            "lat": 20.2961,
            "lon": 85.8245,
            "sub_divisions": ["Bhubaneswar Central", "Bhubaneswar North", "Jatni", "Khordha Town", "Begunia"],
        },
        "Cuttack": {
            "constituency": "Cuttack Parliamentary Constituency",
            "lat": 20.4625,
            "lon": 85.8828,
            "sub_divisions": ["Cuttack City", "Choudwar", "Banki", "Athagarh", "Salepur"],
        },
    },
    "Andhra Pradesh": {
        "Visakhapatnam": {
            "constituency": "Visakhapatnam Parliamentary Constituency",
            "lat": 17.6868,
            "lon": 83.2185,
            "sub_divisions": ["Visakhapatnam North", "Visakhapatnam South", "Gajuwaka", "Bheemunipatnam", "Anakapalli"],
        },
        "Krishna": {
            "constituency": "Machilipatnam Parliamentary Constituency",
            "lat": 16.1809,
            "lon": 81.1303,
            "sub_divisions": ["Machilipatnam", "Gudivada", "Pedana", "Kaikalur", "Pamarru"],
        },
    },
}

# Work title templates mapped to categories
TITLE_TEMPLATES: Dict[str, List[str]] = {
    "Drinking Water": [
        "Installation of RO Clean Drinking Water Plant at {location}",
        "Construction of Over-Head Water Storage Tank and Distribution Pipeline in {location}",
        "Provision of Deep Borewell with Solar Submersible Pump in {location}",
        "Laying of Potable Water Supply Pipeline Network connecting {loc_a} to {loc_b}",
        "Installation of Community Water Purification and Dispensing Unit at {location}",
        "Rejuvenation of Traditional Drinking Water Stepwell and Filter Beds at {location}",
    ],
    "Education Infrastructure": [
        "Construction of Additional Smart Classrooms for Govt Higher Secondary School at {location}",
        "Setting up of Digital STEM Learning and Computer Laboratory at Govt School in {location}",
        "Construction of Boundary Wall, Gates and Modern Toilets in Govt Primary School at {location}",
        "Provision of Composite Science Laboratory and Library Facility at {location}",
        "Construction of Multi-Purpose Auditorium Hall at Govt Degree College in {location}",
        "Installation of Rooftop Solar Energy System for Govt Educational Complex at {location}",
    ],
    "Health & Sanitation": [
        "Construction of Modern Primary Health Sub-Centre (PHC) Building at {location}",
        "Provision of Advanced Mobile Medical Diagnostic Van and Equipment for {location}",
        "Construction of Public Sanitation Complex and Bio-Toilet Block at {location}",
        "Upgradation of Pediatric & Maternal Care Ward at Community Health Centre in {location}",
        "Establishment of Solid Waste Management & Segregation Facility at {location}",
        "Procurement of Diagnostic Imaging & Ultrasound Unit for Sub-District Hospital at {location}",
    ],
    "Roads, Pathways & Bridges": [
        "Construction of Concrete Cement (CC) Road and RCC Drainage from {loc_a} to {loc_b}",
        "Widening and Bituminous Black-Topping of Rural Link Road connecting {loc_a} and {loc_b}",
        "Construction of High-Level RCC Box Culvert and Causeway across Stream near {location}",
        "Paving of Paver-Block Pedestrian Pathway and Street Lighting along {location}",
        "Construction of Bridge over Canal with Approach Roads at {location}",
        "Reconstruction of Damaged All-Weather Village Connectivity Road at {location}",
    ],
    "Community Infrastructure & Halls": [
        "Construction of Multi-Purpose Community Recreation and Welfare Hall at {location}",
        "Construction of Village Panchayat Sabha Bhawan and Citizen Service Centre at {location}",
        "Development of Senior Citizens Recreation Park and Open-Air Pavilion at {location}",
        "Construction of Modern Crematorium / Burial Ground Amenities with Shed at {location}",
        "Construction of Farmers Agro-Produce Storage and Community Shed at {location}",
        "Upgradation of Cultural Community Centre and Public Amphitheater at {location}",
    ],
    "Irrigation & Flood Control": [
        "Construction of Check Dam and Water Harvesting Percolation Structure across Nullah at {location}",
        "Desilting, Deepening and Concrete Lining of Agricultural Irrigation Canal from {loc_a} to {loc_b}",
        "Construction of Flood Protection Embankment and Stone Pitching Wall along River near {location}",
        "Installation of Community Lift Irrigation Scheme with Pipeline for Farmlands in {location}",
        "Rehabilitation of Traditional Irrigation Tank and Sluice Gate System at {location}",
        "Construction of Rainwater Harvesting Sump and Recharging Wells at {location}",
    ],
    "Renewable & Solar Energy": [
        "Installation of High-Mast Solar Street Lighting System across Public Squares in {location}",
        "Setting up of 25 kW Decentralized Solar Mini-Grid for Village Electrification at {location}",
        "Installation of Solar-Powered Cold Storage Unit for Agri-Farmers at {location}",
        "Deployment of Solar Powered LED Street Lights along Main Road connecting {loc_a} to {loc_b}",
        "Installation of Solar Water Pumping System for Community Agriculture at {location}",
        "Setting up of Rooftop Solar Power Plant with Battery Backup for PHC at {location}",
    ],
    "Sports & Youth Development": [
        "Development of Rural Sports Stadium with Running Track and Spectator Gallery at {location}",
        "Construction of Multi-Sport Outdoor Gymnasium and Fitness Arena at {location}",
        "Laying of Synthetic Volleyball and Badminton Courts at Youth Centre in {location}",
        "Construction of Youth Skill Development & Vocational Training Centre at {location}",
        "Development of Playground with Fencing and Floodlights at {location}",
        "Construction of Indoor Gymnasium and Physical Training Centre at {location}",
    ],
}

# Work Statuses
STATUS_RECOMMENDED = "Recommended"
STATUS_SANCTIONED = "Sanctioned"
STATUS_WORK_ORDER = "Work Order Issued"
STATUS_IN_PROGRESS = "In Progress"
STATUS_COMPLETED = "Completed"
STATUS_CANCELLED = "Cancelled"
STATUS_STALLED = "Stalled"

ALL_STATUSES: List[str] = [
    STATUS_RECOMMENDED,
    STATUS_SANCTIONED,
    STATUS_WORK_ORDER,
    STATUS_IN_PROGRESS,
    STATUS_COMPLETED,
    STATUS_CANCELLED,
    STATUS_STALLED,
]

# Inspector Designations for Inspection Records
INSPECTOR_DESIGNATIONS: List[str] = [
    "District Planning Officer (Demo)",
    "Executive Engineer - PWD (Demo)",
    "Assistant Executive Engineer - Rural Works (Demo)",
    "Technical Auditor - State Quality Monitor (Demo)",
    "Sub-Divisional Officer (Demo)",
    "Independent Quality Assessor (Demo)",
    "Junior Engineer - Zilla Parishad (Demo)",
]

# Inspection Rating Categories
INSPECTION_RATINGS: List[str] = [
    "Satisfactory",
    "Good",
    "Excellent",
    "Requires Rectification",
    "Non-Compliant",
]

# Standard geographical bounding box for India (for coordinate validation)
INDIA_GEO_BOUNDS = {
    "min_lat": 6.0,
    "max_lat": 38.0,
    "min_lon": 68.0,
    "max_lon": 98.0,
}
