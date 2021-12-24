import pandas as pd
import numpy as np
import re                  # advanced text processing
import sys                 # to exit script

# ----- FUNCTION: SUBSTITUTE VALUE IN INFILE1 -----
first_iteration = True
def change_INFILE(apparatus,var_name,var_value):
  
    # importing INFILE1
    f = open('INFILE1', "r")
    filedata = f.read()
    f.close()
    #print(type(filedata))
    #print(filedata)
    
    first_iteration = True
    if first_iteration:                                     # finding apparatus and variable name index has only to be done once (as pattern definition)
        # find startpoint of data with given apparatus
        try:
            apparatus_index = filedata.index("APDATA\tNO="+apparatus)
        except:
            print("\n ERROR: This apparatus number does no exist in the used Cycle Tempo system")
            sys.exit()            
        try:
            apparatus_index_geo = filedata.index("GEODAT\tNO="+apparatus)
        except:
            pass
        print("Apparatus index: ",apparatus_index)
        # find startpoint and endpoint of data with given variable
        try:
            var_name_index_beg = filedata.index(var_name, apparatus_index)
        except:
            print("\n ERROR: This variable name is not defined in the used Cycle Tempo system")
            sys.exit()
        print("Var name index begin: ",var_name_index_beg)
        var_name_index_end = var_name_index_beg + len(var_name)
        print("Var name index end: ",var_name_index_end)
        # use next apparatus number to check whether this apparatus contains the entried parameter
        apparatus_index_next = filedata.index("APDATA\tNO="+str(int(apparatus)+1))
        
        
        if not apparatus_index <= var_name_index_beg <= apparatus_index_next:
            try:
                if apparatus_index_geo <= var_name_index_beg:
                    print("Geometric input was found at end of infile")
            except:   
                print("\n ERROR: The entried apparatus does not use the entried parameter")
                sys.exit()
            
            
        # define pattern
        pattern = re.compile('-?[0-9,.]{0,20}[0-9]')          # redex pattern
        first_iteration = False
    # find span of variable value                           # must be executed every iteration, since length of variable value can influence index
    m = pattern.search(filedata,var_name_index_end)         # find first number (including decimals) after finding variable
    var_value_span = m.span()                               # create span of replacement                      
    print('Match found in INFILE1 at: ',m)
    #print(var_value_span)
    #print(var_value_span[0])
    #print(m.group())
    
    # create new string consisting of slices of old string and substitute
    var_value = str(var_value)
    filedata_changed = filedata[:var_value_span[0]] + var_value + filedata[var_value_span[1]:]
    #print(filedata_changed)
    
    f = open('INFILE1','w')
    f.write(filedata_changed)
    f.close()
    
    return var_value_span

# ----- FUNCTION: RETRIEVE OUTPUT (EFFICIENCIES)
def extract_OUTFILE(output_choice):
    try:
        output = pd.read_csv('OUTFIL4', header=None, engine='python', sep='/n')
    except:
        print("\n ERROR: No OUTFIL4 was created while executing Cycle Tempo")
        sys.exit()
    output = output[0].str.split(',', expand=True)
    print(output)
    
    efficiencies = output.iloc[[-2,-1],0:4]
    efficiencies = efficiencies.rename(columns={0:'Gross efficiency',1:'Net efficiency',2:'Heat efficiency',3:'Total efficiency'},index={output.index[-1]:'Energy',output.index[-2]:'Exergy'})
    print(efficiencies, '\n')
    
    additional_output = ['0' , '0', '0', '0', '0', '0', '0']
    
    # algorthm to find SOFC data
    SOFC_power_index = 9                    # place of data in OUTFIL4 in row of SOFC
    SOFC_oxygen_utilisation_index = 16      # place of data in OUTFIL4 in row of SOFC
    SOFC_current_density_index = 20         # place of data in OUTFIL4 in row of SOFC
    air_comp_power_index = 9                # place of data in OUTFIL4 in row of air blower
    air_preh_transheat_index = 11           # place of data in OUTFIL4 in row of air pre heater (times 1000)
    sink_ST_transheat_index = 3              # place of data in OUTFIL4 in row of air blower
    sink_HW_transheat_index = 3              # place of data in OUTFIL4 in row of air blower
    
    
    if not all(x == 0 for x in output_choice):
        # Make mask of to be found of data of to be find equipment
        mask_SOFC = np.column_stack([output[col].str.contains("SOFC", na=False) for col in output])
        mask_air_comp = np.column_stack([output[col].str.contains("Air compress", na=False) for col in output])
        mask_air_preh = np.column_stack([output[col].str.contains("Air preh", na=False) for col in output])
        mask_sink_ST = np.column_stack([output[col].str.contains("Heat Sink ST", na=False) for col in output])
        mask_sink_HW = np.column_stack([output[col].str.contains("Heat Sink HW", na=False) for col in output])
        
        # algorthm to find SOFC power
        if output_choice[0] != '0':
            SOFC_ACpower = output.loc[mask_SOFC.any(axis=1)].iloc[0,SOFC_power_index]
            print("SOFC AC power [kW]: ", SOFC_ACpower)
            additional_output[0] = SOFC_ACpower     
        # algorthm to find SOFC oxygen utilisation
        if output_choice[1] != '0':
            SOFC_U_O = output.loc[mask_SOFC.any(axis=1)].iloc[0,SOFC_oxygen_utilisation_index]
            print("SOFC oxygen utilisation [%]: ", SOFC_U_O)
            additional_output[1] = SOFC_U_O
        # algorthm to find SOFC current density
        if output_choice[2] != '0':
            SOFC_i = output.loc[mask_SOFC.any(axis=1)].iloc[0,SOFC_current_density_index]
            print("SOFC current density [A/m^2]: ", SOFC_i)
            additional_output[2] = SOFC_i
        # algorthm to find SOFC current density
        if output_choice[3] != '0':
            Air_comp_P = output.loc[mask_air_comp.any(axis=1)].iloc[0,air_comp_power_index]
            print("Air compressor power [kW]: ", Air_comp_P)
            additional_output[3] = Air_comp_P
        # algorthm to find heat transmitted in air pre-heater
        if output_choice[4] != '0':
            Air_preh_Phi = output.loc[mask_air_preh.any(axis=1)].iloc[0,air_preh_transheat_index]
            print("Heat transmission in air pre-heater [kW]: ",  1000*float(Air_preh_Phi))
            additional_output[4] = 1000*float(Air_preh_Phi)   
        # algorthm to find regenerated heat for saturated steam net
        if output_choice[5] != '0':
            Sink_ST_Phi = output.loc[mask_sink_ST.any(axis=1)].iloc[0,sink_ST_transheat_index]
            print("Heat regnerated for saturated steam net [kW]: ", Sink_ST_Phi)
            additional_output[5] = Sink_ST_Phi   
        # algorthm to find regenerated heat for hot water net
        if output_choice[6] != '0':
            Sink_HW_Phi = output.loc[mask_sink_HW.any(axis=1)].iloc[0,sink_HW_transheat_index]
            print("Heat regnerated for hot water net [kW]: ", Sink_HW_Phi)
            additional_output[6] = Sink_HW_Phi   
    print(additional_output)
    
              
    return efficiencies, additional_output

