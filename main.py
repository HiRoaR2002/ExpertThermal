import math
from flask import Flask, request, jsonify
import json

def calculate_thermal_metrics(params):
    # Constants and Material Properties
    k_al = 167  
    k_tim = 4   
    k_air = 0.0262  
    nu_air = 1.57e-05  
    pr = 0.71 

    # Input Parameters (Extracted from params or defaults from CSV)
    l_die = params.get('l_die')
    w_die = params.get('w_die')
     
    
    q_tdp = params.get('q_tdp') 
    t_ambient = params.get('t_ambient') 
    
    t_tim = params.get('t_tim')
    t_base = params.get('t_base') 
    
    w_sink = params.get('w_sink')
    l_sink = params.get('l_sink')
    n_fins = params.get('n_fins')
    t_fin = params.get('t_fin')
    h_fin = params.get('h_fin')
    v_air = params.get('v_air') 
    a_die = l_die * w_die
    # Step 3 & 4: Resistance calculations
    r_jc = 0.2  
    r_tim = t_tim / (k_tim * a_die) 
    
    # Step 5: Heat Sink Resistance (Conduction)
    r_cond = t_base / (k_al * a_die) 

    # Step 5: Convection Resistance
    # Fin Spacing Calculation
    s_f = (w_sink - (n_fins * t_fin)) / (n_fins - 1)
    
    # Reynolds Number (Characteristic length = Sf as per image text)
    re = (v_air * s_f) / nu_air 
    
    # Nusselt Number (Laminar Sieder-Tate)
    nu = 1.86 * (re * pr * (2 * s_f / l_sink))**(1/3)
    
    # Convective Heat Transfer Coefficient
    h_conv = (nu * k_air) / (2 * s_f) 
    
    # Total Area for Convection (Fins + Base)
    a_total = params.get('a_total', 0.27504) 
    r_conv = 1 / (h_conv * a_total) 

    # Total Resistance and Junction Temperature
    r_hs = r_cond + r_conv 
    r_total = r_jc + r_tim + r_hs 
    t_junction = t_ambient + (q_tdp * r_total) 

    return {
        "r_total": round(r_total, 6),
        "t_junction": round(t_junction, 6),
        "r_hs": round(r_hs, 6),
        "r_conv": round(r_conv, 6)
    }

app = Flask(__name__)

@app.route('/calculate', methods=['POST'])
def api_calculate():
    data = request.get_json()
    results = calculate_thermal_metrics(data)
    return jsonify(results)

if __name__ == '__main__':
    with open('test_data.json', 'r') as f:
        test_data = json.load(f)
    val = calculate_thermal_metrics(test_data)
    print(f"Validation Result: R_total={val['r_total']}, T_j={val['t_junction']}")
    
    app.run(port=5000)