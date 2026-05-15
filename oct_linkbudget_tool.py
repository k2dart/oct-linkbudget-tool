import numpy as np
import pandas as pd
from datetime import datetime

def dbm_to_w(dbm):
    return 10 ** (dbm / 10) / 1000

def w_to_dbm(w):
    return 10 * np.log10(w * 1000)

def aperture_gain(D_mm, lambda_m=1.55e-6, eta=0.8):
    D = D_mm / 1000.0
    return 10 * np.log10(eta * (np.pi * D / lambda_m) ** 2)

def free_space_loss(R_km, lambda_m=1.55e-6):
    R = R_km * 1000
    return 20 * np.log10(4 * np.pi * R / lambda_m)

def calculate_linkbudget(scenario, D_mm, P_tx_dbm=30.0, other_loss_db=12.0):
    lambda_m = 1.55e-6
    eta = 0.8
    
    if scenario == "LEO-ERDE":
        R_km = 800
        atm_loss_db = 3.0
        title = "LEO → ERDE (Ground Station)"
    elif scenario == "LEO-GEO":
        R_km = 36000
        atm_loss_db = 0.0
        title = "LEO → GEO"
    elif scenario == "LEO-LEO":
        R_km = 1500
        atm_loss_db = 0.0
        title = "LEO → LEO (Intersatelliten)"
    else:
        raise ValueError("Unbekanntes Szenario")
    
    G_tx = aperture_gain(D_mm, lambda_m, eta)
    G_rx = aperture_gain(D_mm, lambda_m, eta)
    L_fsl = free_space_loss(R_km, lambda_m)
    total_loss = L_fsl + other_loss_db + atm_loss_db
    
    P_rx_dbm = P_tx_dbm + G_tx + G_rx - total_loss
    P_rx_w = dbm_to_w(P_rx_dbm)
    
    data = {
        "Parameter": ["Tx Power", "Tx Gain (dB)", "Rx Gain (dB)", "Free-Space Loss (dB)", 
                      "Other Losses (dB)", "Atmosph. Loss (dB)", "Rx Power (dBm)", "Rx Power (W)"],
        "Wert": [f"{P_tx_dbm:.1f} dBm ({dbm_to_w(P_tx_dbm):.3f} W)", 
                 f"{G_tx:.1f}", f"{G_rx:.1f}", f"{L_fsl:.1f}", 
                 f"{other_loss_db:.1f}", f"{atm_loss_db:.1f}", 
                 f"{P_rx_dbm:.2f} dBm", f"{P_rx_w:.2e} W"]
    }
    df = pd.DataFrame(data)
    return title, R_km, df, P_rx_dbm, P_rx_w

print("🚀 OCT Linkbudget-Tool für Satellitenpayloads (v1.0)")
print("   100Gbit Ethernet → E/O → Free-Space-Optic + Acquisition/Tracking\n")
print(f"   Erstellt am: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n")

print("Wählen Sie ein Szenario:")
print("1 = LEO-ERDE    2 = LEO-GEO    3 = LEO-LEO")
wahl = input("Ihre Wahl (1/2/3): ").strip()
scenarios = {"1":"LEO-ERDE", "2":"LEO-GEO", "3":"LEO-LEO"}
scenario = scenarios.get(wahl, "LEO-ERDE")

D_mm = float(input("Aperturgröße Tx/Rx in mm (30–200): "))
P_tx_dbm = float(input("Tx-Leistung in dBm (z. B. 30): "))

title, R_km, df, prx_dbm, prx_w = calculate_linkbudget(scenario, D_mm, P_tx_dbm)

print("\n" + "="*80)
print(f"📡 {title} – Apertur = {D_mm} mm – Distanz ≈ {R_km} km")
print("="*80)
print(df.to_string(index=False))
print("="*80)
print(f"✅ Rx-Leistung: {prx_dbm:.2f} dBm  =  {prx_w:.2e} W")
print("   (Link-Margin kann je nach Empfänger-Empfindlichkeit berechnet werden)")
print("\nTool fertig! Einfach erneut starten und andere Werte eingeben. 😊")