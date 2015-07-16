""" Gather different strategies for checking position of dispersal units on a MTG
    that could prevent them from infecting the leaves.

"""

# Imports #########################################################################
import random
from math import sqrt, pi
from alinea.alep.disease_outputs import compute_severity_by_leaf

# Random inoculation ##############################################################
class BiotrophDUProbaModel:
    """ Template class for checking position of dispersal units on a MTG that 
        complies with the guidelines of Alep.
    
    A class for a model of dispersal unit position checking must contain the 
    following method:
        - 'control': work at leaf scale.
        Affect the property 'can_infect_at_position' of the DUs.
        
    In this example, a dispersal unit can only infect an healthy tissue. 
    Its property 'position' in its interface does not need to be given.
    The probability for it to be on a healthy tissue is computed with 
    the ratio between leaf healthy and total areas.
    """
    def control(self, g, label='LeafElement'):
        """ Control if the dispersal units can infect at their current position.
        
        Call the method 'can_not_infect_at_position' of DU interface eventually
        
        Parameters
        ----------
        g: MTG
            MTG representing the canopy (and the soil)
            'dispersal_units' are stored in the MTG as a property
            'lesions' are stored in the MTG as a property
            'green_area' is the green area of leaf elements
            'area' is the total area of leaf elements
        label: str
            Label of the part of the MTG concerned by the calculation
            
        Returns
        -------
        g: MTG
            Updated MTG representing the canopy
        """
        labels = g.property('label')
        bids = (v for v,l in labels.iteritems() if l.startswith('blade'))
        DUs = g.property('dispersal_units')
        dispersal_units = {k:v for k,v in DUs.iteritems() if len(v)>0.}
        areas = g.property('area')
        green_areas = g.property('green_area')
        lesions = g.property('lesions')
        for blade in bids:
            leaf = [vid for vid in g.components(blade) if labels[vid].startswith(label)]
            leaf_lesions = sum([lesions[lf] for lf in leaf if lf in lesions], []) 
            les_surf = sum([les.surface for les in leaf_lesions])
            leaf_area = sum([areas[lf] for lf in leaf])
            leaf_green_area = sum([green_areas[lf] for lf in leaf])
            ratio_les_surface = min(1, round(les_surf,3)/round(leaf_area,3)) if round(leaf_area,3)>0. else 0.
            ratio_green = min(1, round(leaf_green_area,3)/round(leaf_area,3)) if round(leaf_area,3)>0. else 0.
            
            if round(ratio_green*(1-ratio_les_surface), 10) == 0.:
                for vid in set(leaf) & set(dispersal_units):
                    DUs[vid] = []
            else:
                for vid in set(leaf) & set(dispersal_units):
                    dus_to_keep = []
                    dus = []
                    for du in dispersal_units[vid]:
                        if du.is_active:
                            if du.status == 'deposited':
                                dus_to_keep.append(du)
                            elif du.status == 'emitted':
                                dus.append(du)
                                
                    if len(dus)>0.:
                        group_dus = dus[0].fungus.group_dus
                        if group_dus == True:
                            total_nb_dus = dus[0].nb_dispersal_units
                        else:
                            total_nb_dus = len(dus)
                        nb_on_healthy = int(total_nb_dus*ratio_green*(1-ratio_les_surface))
                        if nb_on_healthy > 0:
                            if group_dus == True:
                                dus[0].nb_dispersal_units = nb_on_healthy
                            else:
                                dus = [du for i, du in enumerate(dus) 
                                        if i <= nb_on_healthy]
                            for du in dus:
                                du.set_status(status = 'deposited')
                                DUs[vid] = dus_to_keep + dus
                        else:
                            DUs[vid] = dus_to_keep
