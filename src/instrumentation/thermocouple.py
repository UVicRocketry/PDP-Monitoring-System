# Get voltage of cold junction of LabJack
def get_ref_voltage(T_cold_junction_K):

    # T_cold_junction is in K from: d.getTemperature()

    # Coeffs expect Celsius 
    Tref = T_cold_junction_K - 273.15

    # For 0C to 1372C at reduced accuracy
    c0 = -1.7600413686 * 10**-2
    c1 =  3.8921204975 * 10**-2
    c2 =  1.8558770032 * 10**-5
    c3 = -9.9457592874 * 10**-8
    c4 =  3.1840945719 * 10**-10
    c5 = -5.6072844889 * 10**-13
    c6 =  5.6075059059 * 10**-16
    c7 = -3.2020720003 * 10**-19
    c8 =  9.7151147152 * 10**-23
    c9 = -1.2104721275 * 10**-26

    mV = c0 + \
         c1*Tref + \
         c2*Tref**2 + \
         c3*Tref**3 + \
         c4*Tref**4 + \
         c5*Tref**5 + \
         c6*Tref**6 + \
         c7*Tref**7 + \
         c8*Tref**8 + \
         c9*Tref**9

    # This computes the voltage in mV so convert to V
    return mV/1000

# Function to turn thermocouple voltages to kelvin
def V_to_K(tc_voltage, ref_voltage):

    voltage = (tc_voltage+ref_voltage)

    # Ranges based on volts and celsius
    if voltage > 0.020644 and voltage < 0.054886:
        C0 = -131.8058
        C1 = 48.30222
        C2 = -1.646031 
        C3 = 0.05464731
        C4 = -0.0009650715
        C5 = 0.000008802193
        C6 = -0.00000003110810
        C7 = 0
        C8 = 0
        C9 = 0
    elif voltage > -0.005891 and voltage < 0:
        C0 = 0
        C1 = 25.173462
        C2 = -1.1662878
        C3 = -1.0833638
        C4 = -0.89773540
        C5 = -0.37342377
        C6 = -0.086632643
        C7 = -0.010450598
        C8 = -0.00051920577
        C9 = 0
    elif voltage > 0 and voltage < 0.020644:
        C0 = 0
        C1 = 25.08355
        C2 = 0.07860106
        C3 = -0.2503131
        C4 = 0.08315270
        C5 = -0.01228034
        C6 = 0.0009804036
        C7 = -0.0000413030
        C8 = 0.000001057734
        C9 = -0.00000001052755
    else:
       return 0
    
    # Coeffs expect mV
    mV_voltage = voltage * 1000
    tempC = C0 + \
            C1*mV_voltage + \
            C2*mV_voltage**2 + \
            C3*mV_voltage**3 + \
            C4*mV_voltage**4 + \
            C5*mV_voltage**5 + \
            C6*mV_voltage**6 + \
            C7*mV_voltage**7 + \
            C8*mV_voltage**8 + \
            C9*mV_voltage**9
   
    return (tempC + 273.15)
