import u6


d = u6.U6()

#Get starting reference temp of LabJack
def get_ref_temp():
    Tref = d.getTemperature() - 273.15

    c0 = -1.7600413686 * 10**-2
    c1 = 3.8921204975 * 10**-2
    c2 = 1.8558770032 * 10**-5
    c3 = -9.9457592874 * 10**-8
    c4 = 3.1840945719 * 10**-10
    c5 = -5.6072844889 * 10**-13
    c6 = 5.6075059059 * 10**-16
    c7 = -3.2020720003 * 10**-19
    c8 = 9.7151147152 * 10**-23
    c9 = -1.2104721275 * 10**-26

    voltage_reference = c0 + \
                        c1*Tref + \
                        c2*Tref**2 + \
                        c3*Tref**3 + \
                        c4*Tref**4 + \
                        c5*Tref**5 + \
                        c6*Tref**6 + \
                        c7*Tref**7 + \
                        c8*Tref**8 + \
                        c9*Tref**9
    return voltage_reference

#Function to turn thermocouple voltages to kelvin
def v_to_K(voltage, ref_voltage = 0):
    voltage_actual = voltage + ref_voltage
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
    
    voltage_actual = voltage_actual*1000

    tempC = C0 + \
            C1*voltage_actual + \
            C2*voltage_actual**2 + \
            C3*voltage_actual**3 + \
            C4*voltage_actual**4 + \
            C5*voltage_actual**5 + \
            C6*voltage_actual**6 + \
            C7*voltage_actual**7 + \
            C8*voltage_actual**8 + \
            C9*voltage_actual**9
   
    return (tempC + 273.15)