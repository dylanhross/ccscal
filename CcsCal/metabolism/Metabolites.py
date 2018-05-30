"""
    CcsCal/metabolism/Metabolites.py
    Dylan H. Ross
    2018/05/23
        description:
            Data structures encapsulating various types of drug metabolites
            and their mass shifts from parent compounds.
"""


class Metabolite:
    """
Metabolite
    description:
        The base class for metabolic modifications.
"""

    def __init__(self, base_mass, depth):
        """
Metabolite.__init__
    description:
        Creates a new Metabolite instance.
    parameters:
        base_mass (float) -- mass of compound before metabolism
        depth (int) -- depth
    returns:
        (Metabolite) -- new Metabolite instance
"""
        # mass of the unmodified compound
        self.base_mass = base_mass
        self.depth = depth
        # dict of subsequent Metabolites
        self.sub = {}
        # this metabolite's mass defaults to base_mass
        self.mass_ = base_mass
        self.label_ = "M"
    
    def masses(self):
        """
Metabolite.masses
    description:
        Generator that calculates the metabolite mass for this modification 
        and all of the metabolite masses of subsequent metabolites in 
        self.sub and yields them.
    yields:
        (float) -- mass of metabolites
"""
        # yield this metabolite's mass
        if self.mass_: yield round(self.mass_, 5)
        # yield all of the subsequent metabolite masses
        for _, sub in self.sub.items():
            for mass in sub.masses():
                # all of the monoisotopic masses used in here are accurate 
                # to 5 decimal places so only report masses out to 5 decimal
                # places
                yield round(mass, 5)
        
    def labels(self):
        """
Metabolite.labels
    description:
        Generator that yields the label for this metabolite and all subsequent metabolites
    yields:
        (str) -- metabolite label
"""
        yield self.label_
        for _, sub in self.sub.items():
            for label in sub.labels():
                yield label
        
        
    def add_sub(self, metabolite, *args):
        """
Metabolite.add_sub
    description:
        Adds an instance of a Metabolite (or, more likely a child class) into
        this Metabolite's subsequent metabolites list. 
    parameters:
        metabolite (str) -- name of Metabolite or child class
"""
        # initialize the subsequent metabolite with this Metabolite's modified
        # mass and increase the depth by 1
        self.sub[metabolite] = self.meta_[metabolite](self.mass_, self.depth + 1, label=self.label_)
    
    
class Hydroxyl(Metabolite):
    """
Hydroxyl
    description:
        Metabolic modification representing R-H -> R-O-H
        [M + 15.99492]
"""

    def __init__(self, base_mass, depth, label=None):
        """
Hydroxyl.__init__
    description:
        Creates a new Hydroxyl instance.
    parameters:
        base_mass (float) -- mass of compound before metabolism
        level (int) -- depth
    returns:
        (Hydroxyl) -- new Hydroxyl instance
"""
        # use the base class' __init__ method
        super().__init__(base_mass, depth)
        # define this modification's characteristic mass shift
        self.mass_ = base_mass + 15.99492
        # add to the label if provided
        if label:
            self.label_ = label + "_+O"

        
class HAOxidized(Metabolite):
    """
HAOxidized
    description:
        Metabolic modification representing heteroatom oxidation
        R-S-R -> R-S=O-R sulfone
        R-S=O-R -> R-O=S=O-R sulfoxide
        R3-N -> R3-N->O N-oxide
        [M + 15.99492]
"""

    def __init__(self, base_mass, depth, label=None):
        """
HAOxidized.__init__
    description:
        Creates a new HAOxidized instance.
    parameters:
        base_mass (float) -- mass of compound before metabolism
        level (int) -- depth
    returns:
        (HAOxidized) -- new HAOxidized instance
"""
        # use the base class' __init__ method
        super().__init__(base_mass, depth)
        # define this modification's characteristic mass shift
        self.mass_ = base_mass + 15.99492
        # add to the label if provided
        if label:
            self.label_ = label + "_+O"
            
            
class Desmethyl(Metabolite):
    """
Desmethyl
    description:
        Metabolite modification representing (O/N)-CH3 -> (O/N)-H
        [M - 14.01564]
"""
    
    def __init__(self, base_mass, depth, label=None):
        """
Desmethyl.__init__
    description:
        Creates a new Desmethyl instance.
    parameters:
        base_mass (float) -- mass of compound before metabolism
        level (int) -- depth
    returns:
        (Desmethyl) -- new Desmethyl instance
"""
        # use the base class' __init__ method
        super().__init__(base_mass, depth)
        # define this modification's characteristic mass shift
        self.mass_ = base_mass - 14.01564
        # add to the label if provided
        if label:
            self.label_ = label + "_-Me"
        
        
class Desethyl(Metabolite):
    """
Desethyl
    description:
        Metabolite modification representing (O/N)-CH2CH3 -> (O/N)-H
        [M - 29.03910]
"""
    
    def __init__(self, base_mass, depth, label=None):
        """
Desethyl.__init__
    description:
        Creates a new Desethyl instance.
    parameters:
        base_mass (float) -- mass of compound before metabolism
        level (int) -- depth
    returns:
        (Desethyl) -- new Desethyl instance
"""
        # use the base class' __init__ method
        super().__init__(base_mass, depth)
        # define this modification's characteristic mass shift
        self.mass_ = base_mass - 29.03910
        # add to the label if provided
        if label:
            self.label_ = label + "_-Et"
        
        
class Glucuronyl(Metabolite):
    """
Glucuronyl
    description:
        Metabolite modification representing (O/N)-H -> (O/N)-Glc
        [M + 176.03208]
"""
    
    def __init__(self, base_mass, depth, label=None):
        """
Glucuronyl.__init__
    description:
        Creates a new Glucuronyl instance.
    parameters:
        base_mass (float) -- mass of compound before metabolism
        level (int) -- depth
    returns:
        (Glucuronyl) -- new Glucuronyl instance
"""
        # use the base class' __init__ method
        super().__init__(base_mass, depth)
        # define this modification's characteristic mass shift
        self.mass_ = base_mass + 176.03208
        # add to the label if provided
        if label:
            self.label_ = label + "_+Glc"


class Glutathionyl(Metabolite):
    """
Glutathionyl
    description:
        Metabolite modification representing 
        [M + 308.08374]
"""
    
    def __init__(self, base_mass, depth, label=None):
        """
Glutathionyl.__init__
    description:
        Creates a new Glutathionyl instance.
    parameters:
        base_mass (float) -- mass of compound before metabolism
        level (int) -- depth
    returns:
        (Glutathionyl) -- new Glutathionyl instance
"""
        # use the base class' __init__ method
        super().__init__(base_mass, depth)
        # define this modification's characteristic mass shift
        self.mass_ = base_mass + 307.08374
        # add to the label if provided
        if label:
            self.label_ = label + "_+GSH"
            
        
class Oxidized(Metabolite):
    """
Oxidized
    description:
        Metabolite modification representing RH-RH -> R=R
        [M - 2.01564]
"""
    
    def __init__(self, base_mass, depth, label=None):
        """
Oxidized.__init__
    description:
        Creates a new Oxidized instance.
    parameters:
        base_mass (float) -- mass of compound before metabolism
        level (int) -- depth
    returns:
        (Oxidized) -- new Oxidized instance
"""
        # use the base class' __init__ method
        super().__init__(base_mass, depth)
        # define this modification's characteristic mass shift
        self.mass_ = base_mass - 2.01564
        # add to the label if provided
        if label:
            self.label_ = label + "_-2H"
        
        
class Reduced(Metabolite):
    """
Reduced
    description:
        Metabolite modification representing R=R -> RH-RH
        [M + 2.01564]
"""
    
    def __init__(self, base_mass, depth, label=None):
        """
Reduced.__init__
    description:
        Creates a new Reduced instance.
    parameters:
        base_mass (float) -- mass of compound before metabolism
        level (int) -- depth
    returns:
        (Reduced) -- new Reduced instance
"""
        # use the base class' __init__ method
        super().__init__(base_mass, depth)
        # define this modification's characteristic mass shift
        self.mass_ = base_mass + 2.01564
        # add to the label if provided
        if label:
            self.label_ = label + "_+2H"

            
class Acetyl(Metabolite):
    """
Acetyl
    description:
        Metabolite modification representing R-NH2 -> R-NH-C=O-CH3
        [M + 42.01056]
"""
    
    def __init__(self, base_mass, depth, label=None):
        """
Acetyl.__init__
    description:
        Creates a new Acetyl instance.
    parameters:
        base_mass (float) -- mass of compound before metabolism
        level (int) -- depth
    returns:
        (Acetyl) -- new Acetyl instance
"""
        # use the base class' __init__ method
        super().__init__(base_mass, depth)
        # define this modification's characteristic mass shift
        self.mass_ = base_mass + 42.01056
        # add to the label if provided
        if label:
            self.label_ = label + "_+Ac"

            
class Hydrolyzed(Metabolite):
    """
Hydrolyzed
    description:
        Metabolite modification representing A-C=O-(O/N)-B -> A-C=O-OH + H-(C/N)-B
        The mass of the carbonyl half (A) is specified at initialization
        [M_A + 17.00274]
        [M_B + 1.00782]
"""
    
    def __init__(self, base_mass, depth, mass_A):
        """
Hydrolyzed.__init__
    description:
        Creates a new Hydrolyzed instance
    parameters:
        base_mass (float) -- mass of compound before metabolism
        level (int) -- depth
        mass_A (float) -- mass of one of the carbonyl half
    returns:
        (Hydrolyzed) -- new Hydrolyzed instance
"""
        # use the base class' __init__ method
        super().__init__(base_mass, depth)
        # define this modification's characteristic mass shift
        self.mass_A_ = mass_A + 17.00274
        self.mass_B_ = base_mass - mass_A + 1.00782
        
    def masses(self):
        """
Hydrolyzed.masses
    description:
        Generator that calculates the metabolite mass for this modification 
        and all of the metabolite masses of subsequent metabolites in 
        self.sub and yields them.
    yields:
        (float) -- mass of metabolites
"""
        yield round(self.mass_A_, 5)
        yield round(self.mass_B_, 5)
        # yield all of the subsequent metabolite masses
        for _, sub in self.sub.items():
            for mass in sub.masses():
                # all of the monoisotopic masses used in here are accurate 
                # to 5 decimal places so only report masses out to 5 decimal
                # places
                yield round(mass, 5)
        
    def add_sub(self, metabolite, *args):
        """
Hydrolyzed.add_sub
    description:
        Adds an instance of a Metabolite (or, more likely a child class) into
        this Metabolite's subsequent metabolites list. Adds subsequent metabolites
        for both mass_A and mass_B.
    parameters:
        metabolite (str) -- name of Metabolite or child class
"""
        # initialize the subsequent metabolite with this Metabolite's modified
        # mass and increase the depth by 1
        self.sub[metabolite + "_A"] = self.meta_[metabolite](self.mass_A_, self.depth + 1, *args)
        self.sub[metabolite + "_B"] = self.meta_[metabolite](self.mass_B_, self.depth + 1, *args)
        
        
# dictionary mapping strings to Metabolite child classes
Metabolite.meta_ = {
        "Metabolite": Metabolite,
        "Hydroxyl": Hydroxyl,
        "HAOxidized": HAOxidized,
        "Desmethyl": Desmethyl,
        "Desethyl": Desethyl,
        "Glucuronyl": Glucuronyl,
        "Glutathionyl": Glutathionyl,
        "Oxidized": Oxidized,
        "Reduced": Reduced,
        "Acetyl": Acetyl,
        "Hydrolyzed": Hydrolyzed
    }        
        
        
    