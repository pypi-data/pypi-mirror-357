import math
import xml.etree.ElementTree as et
from typing import Literal
from importlib import resources

class Config:
    """
    A configuration object used to provide data to the DecayChain calculator.
    After creating a config object and adding chain information, it can be used
    to instantiate a DecayChain using ```chain = DecayChain(config)```.
    """
    _sources = {}
    _initial_quantities = {}
    decay_info = {}
    atom_numbers = {}
    sources = {}
    
    def add_nuclide_number(self, nuclide: str, number: float):
        """
        Adds a quantity of nuclide atoms.
        
        Parameters
        ----------
        nuclide : str
            The nuclide identifier. Ex. U238.
        number : float
            The initial number of atoms in the sample
        """
        self._initial_quantities[nuclide] = (number, "number")
    
    def add_nuclide_activity(self, nuclide: str, activity: float, units:
                             Literal["Bq", "Ci"] = "Bq"):
        """
        Adds an activity of nuclide.

        Parameters
        ----------
        nuclide : str
            The nuclide identifier. Ex. U238.
        activity : float
            The initial activity of the sample in either Bq or Ci.
        units: "Bq" or "Ci"
            The units of the supplied activity (default is Bq).
        """
        if (units == "Ci"):
            activity *= 37e9
        self._initial_quantities[nuclide] = (activity, "activity")

    def add_from_xml(self, input_file: str = "input.xml"):
        """
        Fills configuration with data from an xml input.

        Parameters
        ----------
        input_file : str
            The filename of the xml input.
        """
        # Parse the input file
        isotopes_xml = et.parse(input_file).getroot().findall('nuclide')
        for nuclide in isotopes_xml:
            info = nuclide.attrib
            self._initial_quantities[info['name']] = \
                ([float(info['N0'])], "number")
            self.sources[info['name']] = float(info['source'])

    def configure(self):
        """
        Performs calculations and conversions to prepare object for use in the
        decay calculator.
        """
        chain_file = resources.path("decay_chains", "chain_endfb71_pwr.xml")
        with chain_file as f:
            chain = et.parse(f).getroot().findall('nuclide')

        atom_numbers = {}
        for nuclide in chain:
            info = nuclide.attrib
            el = info['name']
            if el in self._initial_quantities.keys():
                print(f'Reading data for {el} from chain file')
                # Need error handling if nuclide is stable
                try:
                    self.decay_info[el] = \
                        {'half_life': float(info['half_life'])}
                    self.decay_info[el]['decay_const'] = \
                        math.log(2) / float(info['half_life'])
                except KeyError:
                    self.decay_info[el] = {'half_life': 0.}
                    # If stable, set lambda to 0 so there is no decay
                    self.decay_info[el]['decay_const'] = 0.
                    
                # Add initial atom number to dictionary
                atom_numbers[el] = self._initial_quantities[el][0]
                if (self._initial_quantities[el][1] == "activity"):
                    if (self.decay_info[el]['decay_const'] == 0. and
                        atom_numbers[el] != 0.):
                        
                        print(f"\nWARNING: {el} is stable! Ignoring activity "
                               "and setting number to zero.")
                        atom_numbers[el] = 0.
                    else:
                        atom_numbers[el] /= self.decay_info[el]['decay_const']
                # Find the decay targets
                self.decay_info[el]['targets'] = {}
                for mode in nuclide.findall('decay'):
                    m = mode.attrib
                    # Do not include spontaneous fission
                    if m['type'] == "sf":
                        print(f"\nWARNING: Ignoring spontaneous fission in {el} "
                              f"({float(m['branching_ratio']) * 100:.4e}%).\n")
                    else:
                        self.decay_info[el]['targets'][m['target']] = \
                            float(m['branching_ratio'])
                        
        # Order nuclides by place in the chain
        order = []
        for el, info in self.decay_info.items():
            if len(order) == 0:
                order.append(el)
                continue
            order_cp = order
            inserted = False
            for i, oel in enumerate(order_cp):
                if oel in info['targets'].keys() and not inserted:
                    order.insert(i, el)
                    inserted = True
            if inserted == False:
                order.insert(0, el)
        for el in order:
            self.atom_numbers[el] = [atom_numbers[el]]

        # If source was not set, set it to 0
        for el in self.decay_info.keys():
            if el not in self.sources.keys():
                self.sources[el] = 0.
