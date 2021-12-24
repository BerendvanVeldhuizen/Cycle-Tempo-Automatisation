import pandas as pd
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
        pattern = re.compile('[0-9,.]{0,20}[0-9]')          # redex pattern
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
def extract_OUTFILE():
    try:
        output = pd.read_csv('OUTFIL4', header=None, engine='python', sep='/n')
    except:
        print("\n ERROR: No OUTFIL4 was created while executing Cycle Tempo")
        sys.exit()
    output = output[0].str.split(',', expand=True)
    #print(output)
    
    efficiencies = output.iloc[[-2,-1],0:4]
    efficiencies = efficiencies.rename(columns={0:'Gross efficiency',1:'Net efficiency',2:'Heat efficiency',3:'Total efficiency'},index={output.index[-1]:'Energy',output.index[-2]:'Exergy'})
    print(efficiencies, '\n')
    
    
    return efficiencies

