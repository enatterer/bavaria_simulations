import numpy as np

"""
This stage provides some data provided in the MiD 2017 report for Bayern and also from MiD 2017 report for the city of Munich.
"""

def configure(context):
    pass

def execute(context):
    data = {}

    # Updated to match the screenshot:
    data["car_availability_constraints"] = [
        { "zone": "stadt",     "target": 0.85 },  #städtische landkreis MiD Bavaria 2017
        { "zone": "landkreis", "target": 0.89 },  #landlicher kreis mit verdichtungsansätzen MiD Bavaria 2017
        { "zone": "external",  "target": 0.82 }, #Bavaria Value MiD Bavaria 2017
    ]

    data["bicycle_availability_constraints"] = [
        { "zone": "stadt",     "target": 0.82 },  # städtische kreis MiD Bavaria 2017
        { "zone": "landkreis", "target": 0.81 },  # landlicher kreis mit verdichtungsansätzen MiD Bavaria 2017
        { "zone": "external",  "target": 0.80 },  # bayern value  MiD Bavaria 2017
        
        #stadt
        { "zone": "stadt", "sex": "male",   "target": 0.83 },  
        { "zone": "stadt", "sex": "female", "target": 0.78 },  

        { "zone": "stadt", "age": (-np.inf, 17),   "target": 0.92 },  
        { "zone": "stadt", "age": (18, 29),        "target": 0.79 },  
        { "zone": "stadt", "age": (30, 49),        "target": 0.87 },  
        { "zone": "stadt", "age": (50, 64),        "target": 0.84 },  
        { "zone": "stadt", "age": (65, 74),        "target": 0.78 },  
        { "zone": "stadt", "age": (75, np.inf),    "target": 0.59 },

        #landkreis
        { "zone": "landkreis", "sex": "male",   "target": 0.83 },  
        { "zone": "landkreis", "sex": "female", "target": 0.78 },  

        { "zone": "landkreis", "age": (-np.inf, 17),   "target": 0.92 },  
        { "zone": "landkreis", "age": (18, 29),        "target": 0.79 },  
        { "zone": "landkreis", "age": (30, 49),        "target": 0.87 },  
        { "zone": "landkreis", "age": (50, 64),        "target": 0.84 },  
        { "zone": "landkreis", "age": (65, 74),        "target": 0.78 },  
        { "zone": "landkreis", "age": (75, np.inf),    "target": 0.59 },  
    ]

    data["pt_subscription_constraints"] = [
        { "zone": "stadt",    "target": 0.15 }, #städtische kreis MiD Bavaria 2017
        { "zone": "landkreis", "target": 0.08 }, #landlicher kreise mit verdichtungsansätzen MiD Bavaria 2017
        { "zone": "external", "target": 0.17 },  # Bavaria value

        { "zone": "stadt", "sex": "male",   "target": 0.23 }, #münchner umland MiD Munich 2017
        { "zone": "stadt", "sex": "female", "target": 0.21 }, #münchner umland MiD Munich 2017

        { "zone": "stadt", "age": (-np.inf, 17),   "target": 0.41 },
        { "zone": "stadt", "age": (18, 29),        "target": 0.39 },
        { "zone": "stadt", "age": (30, 49),        "target": 0.22 },
        { "zone": "stadt", "age": (50, 64),        "target": 0.20},
        { "zone": "stadt", "age": (65, 74),        "target": 0.11 },
        { "zone": "stadt", "age": (75, np.inf),    "target": 0.11 },

        # Umland
        { "zone": "landkreis", "sex": "male",   "target": 0.23 }, #münchner umland MiD Munich 2017
        { "zone": "landkreis", "sex": "female", "target": 0.21 }, #münchner umland MiD Munich 2017
        
        { "zone": "landkreis", "age": (-np.inf, 17),   "target": 0.41 },
        { "zone": "landkreis", "age": (18, 29),        "target": 0.39 },
        { "zone": "landkreis", "age": (30, 49),        "target": 0.22 },
        { "zone": "landkreis", "age": (50, 64),        "target": 0.20},
        { "zone": "landkreis", "age": (65, 74),        "target": 0.11 },
        { "zone": "landkreis", "age": (75, np.inf),    "target": 0.11 },
    ]

    return data
