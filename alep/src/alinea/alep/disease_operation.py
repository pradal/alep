""" Disease operation utilities

The aim of this module is to provide all the tools needed to manipulate
fungal objects on the MTG.

"""

import random as rd
from alinea.adel.mtg_interpreter import *
from openalea.plantgl.all import *

from alinea.alep.protocol import *
from alinea.alep.inoculation import RandomInoculation
from openalea.vpltk import plugin

def generate_stock_du(nb_du, disease):
    """ Generate a stock of dispersal units.
    
    Parameters
    ----------
    nb_du: int
        Number of dispersal units to create in the stock
    disease: model
        Implementation for a model of fungal disease
        
    Returns
    -------
    dus: list of objects
        List of dispersal units of the given disease
    """
    DU = disease.dispersal_unit()
    return [DU(nb_spores=rd.randint(1,100), status='emitted')
                        for i in range(nb_du)]
                        
def generate_stock_lesion(nb_lesions, disease):
    """ Generate a stock of lesions.
    
    Parameters
    ----------
    nb_lesions: int
        Number of dispersal units to create in the stock
    disease: model
        Implementation for a model of fungal disease
        
    Returns
    -------
    lesions: list of objects
        List of lesions of the given disease
    """
    lesion = disease.lesion()
    return [lesion(nb_spores=rd.randint(1,100)) for i in range(nb_lesions)]

def distribute_disease(g,
                       fungal_object='lesion', 
                       nb_objects=1, 
                       disease_model='powdery_mildew',
                       initiation_model=RandomInoculation()):
    """ Distribute dispersal units on the MTG.
    
    Parameters
    ----------
    g: MTG
        MTG representing the canopy
    fungal_object: str
        Type of fungal object. Choose between : 'dispersal_unit' or 'lesion'
    nb_objects: int
        Number of dispersal units or lesions to distribute on the MTG
    disease_model: model
        Type of model to compute disease lesion development
    initiation_model: model
        Model that sets the position of each DU/lesion in stock on g
        Requires a method named 'allocate' (see doc)
        
    Returns
    -------
    g: MTG
        Updated MTG with dispersal units or lesions
    """
    # Create a pool of dispersal units (DU)
    diseases=plugin.discover('alep.disease')
    disease = diseases[disease_model].load()
    if fungal_object=='dispersal_unit':
        objects = generate_stock_du(nb_du=nb_objects, disease=disease)
    elif fungal_object=='lesion':
        objects = generate_stock_lesion(nb_lesions=nb_objects, disease=disease)
    else:
        raise Exception('fungal object is not valid: choose between ''du'' or ''lesion')
    # Distribute the DU 
    initiate(g, objects, initiation_model)
    return g

def count_lesions(g):
    """ Count lesions of the mtg.
    
    Parameters
    ----------
    g: MTG
        MTG representing the canopy
        
    Returns
    -------
    nb_lesions: int
        Number of lesions on the MTG
    """
    lesions = g.property('lesions')
    return sum(len(l) for l in lesions.itervalues())
    
def count_lesions_by_leaf(g, label='LeafElement'):
    """ Count lesions on each part of the MTG given by the label.
    
    Parameters
    ----------
    g: MTG
        MTG representing the canopy
    label: str
        Label of the part of the MTG concerned by the calculation
        
    Returns
    -------
    nb_lesions_by_leaf: dict([id:nb_lesions])
        Number of lesions on each part of the MTG given by the label
    """
    lesions = g.property('lesions')
    return {k:len(v) for k,v in lesions.iteritems()}

def count_lesion_surfaces_by_leaf(g, label='LeafElement'):
    """ Count the surface of lesions on each part of the MTG given by the label.
    
    Parameters
    ----------
    g: MTG
        MTG representing the canopy
    label: str
        Label of the part of the MTG concerned by the calculation
        
    Returns
    -------
    surface_lesions_by_leaf: dict([id:nb_lesions])
        Number of lesions on each part of the MTG given by the label
    """
    lesions = g.property('lesions')
    return {k:sum(l.surface for l in v) for k,v in lesions.iteritems()}
    
def count_dispersal_units(g):
    """ Count dispersal units of the mtg.
    
    Parameters
    ----------
    g: MTG
        MTG representing the canopy
        
    Returns
    -------
    nb_dispersal_units: int
        Number of dispersal units on the MTG
    """
    dispersal_units = g.property('dispersal_units')
    return sum(len(l) for l in dispersal_units.itervalues())
    
def count_dispersal_units_by_leaf(g, label='LeafElement'):
    """ Count dispersal units on each part of the MTG given by the label.
    
    Parameters
    ----------
    g: MTG
        MTG representing the canopy
    label: str
        Label of the part of the MTG concerned by the calculation
        
    Returns
    -------
    nb_dispersal_units_by_leaf: dict([id:nb_dispersal_units])
        Number of dispersal units on each part of the MTG given by the label
    """
    dispersal_units = g.property('dispersal_units')
    return {k:len(v) for k,v in dispersal_units.iteritems()}
    
def plot_lesions(g):
    """ plot the plant with infected elements in red """
    green = (0,180,0)
    red = (180, 0, 0)
    for v in g.vertices(scale=g.max_scale()) : 
        n = g.node(v)
        if 'lesions' in n.properties():
            n.color = red
        else : 
            n.color = green
    
    scene = plot3d(g)
    Viewer.display(scene)