"""
    CcsCal/metabolism/Encoder.py
    Dylan H. Ross
    2018/05/23
        description:
            Utilities for encoding/decoding metabolite patterns.
"""


from CcsCal.metabolism.Metabolites import Metabolite


class MetabEncoder():
    """
MetabEncoder
    description:
        TODO
        
0 None ..?
1 Metabolite
2 Hydroxyl
3 HAOxidized
4 Desmethyl
5 Desethyl
6 Glucuronyl
7 Glutathionyl
8 Oxidized
9 Reduced
A Acetyl
B Hydrolyzed

Metabolite string is read in as a series of hexadecimal numbers reflecting the sequence of
subsequent metabolites in a depth-first order. 

-> M
    -> hydroxyl
        -> hydroxyl
            -> glucuronide
        -> glucuronide
    -> glucuronide

01 12 22 36 26 16

01 m = Metabolite(mass, 0)
    12 m.add_sub("Hydroxyl")
        22 m.sub["Hydroxyl"].add_sub("Hydroxyl")
            36 m.sub["Hydroxyl"].sub["Hydroxyl"].add_sub("Glucuronyl")
        26 m.sub["Hydroxyl"].add_sub("Glucuronyl")
    16 m.add_sub("Glucuronyl")



"""

    # dictionary mapping characters to metabolite types
    metab_types = {
        '0': "None",
        '1': "Metabolite",
        '2': "Hydroxyl",
        '3': "HAOxidized",
        '4': "Desmethyl",
        '5': "Desethyl",
        '6': "Glucuronyl",
        '7': "Glutathionyl",
        '8': "Oxidized",
        '9': "Reduced",
        'A': "Acetyl",
        'B': "Hydrolyzed",
    }
    
    def __init__(self):
        """
MetabEncoder.__init__
    description:
    parameters:
    returns:
"""
        # pass
        pass
    
    def tokenize(self, metab_seq):
        """
MetabEncoder.tokenize
    description:
        TODO
    parameters:
        metab_seq (str) -- encoded metabolic sequence
    yields:
        (tuple(char, char)) -- level, metabolite
"""
        # sequence must be an even length
        if len(metab_seq) % 2:
            raise ValueError("MetabEncoder: tokenize: encoded metabolite " +
                             "sequence must be even length")
        for i in range(int(len(metab_seq) / 2)):
            yield (metab_seq[2 * i], metab_seq[2 * i + 1])
            
    def decode(self, mass, metab_seq):
        """
MetabEncoder.decode
    description:
        Decodes an encoded metabolic sequence string and returns the corresponding
        Metabolite data structure.
    parameters:
        mass (float) -- parent mass
        metab_seq (str) -- encoded metabolic sequence
    returns:
        (Metabolite) -- Metabolite data structure representing metabolic sequence
"""
        metab = Metabolite(mass, 0)
        # main loop, traverse encoded metabolite sequence
        for level, mtype in self.tokenize(metab_seq):
            print("level", level, "metab_type", self.metab_types[mtype]) # DEBUG
            
        return metab
        
        
        



