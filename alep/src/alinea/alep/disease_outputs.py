""" Utilities for computing outputs from the disease model.

The aim of this module is to provide all the tools needed to compute
the outputs of the disease models. 
"""


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
    return len(sum(g.property('lesions').values(), []))

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
    return len(sum(g.property('dispersal_units').values(), []))
    
def count_lesions_by_leaf(g):
    """ Count lesions on each leaf of the MTG.
    
    Parameters
    ----------
    g: MTG
        MTG representing the canopy
        
    Returns
    -------
    nb_lesions_by_leaf: dict([id:nb_lesions])
        Number of lesions on each part of the MTG given by the label
    """
    lesions = g.property('lesions')
    return {k:len(v) for k,v in lesions.iteritems()}

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
    from alinea.adel.mtg_interpreter import plot3d
    from openalea.plantgl.all import Viewer
    
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

def plot_dispersal_units(g):
    """ plot the plant with infected elements in red """
    from alinea.adel.mtg_interpreter import plot3d
    from openalea.plantgl.all import Viewer
    
    green = (0,180,0)
    red = (180, 0, 0)
    for v in g.vertices(scale=g.max_scale()) : 
        n = g.node(v)
        if 'dispersal_units' in n.properties():
            n.color = red
        else : 
            n.color = green
    
    scene = plot3d(g)
    Viewer.display(scene)
    
def compute_lesion_areas_by_leaf(g, label='LeafElement'):
    """ Compute lesion area on each part of the MTG given by the label.
    
    Parameters
    ----------
    g: MTG
        MTG representing the canopy
    label: str
        Label of the part of the MTG concerned by the calculation
        
    Returns
    -------
    lesion_surfaces_by_leaf: dict([id:surface_lesions])
        Surface of the lesions on each part of the MTG given by the label
    """
    from alinea.alep.architecture import get_leaves
    vids = get_leaves(g, label=label)
    lesions = g.property('lesions')
    return {vid:(sum(l.surface for l in lesions[vid])
            if vid in lesions.keys() else 0.) for vid in vids} 

def compute_green_lesion_areas_by_leaf(g, label='LeafElement'):
    """ Compute lesion areas on each green part of the MTG given by the label.
    
    Parameters
    ----------
    g: MTG
        MTG representing the canopy
    label: str
        Label of the part of the MTG concerned by the calculation
        
    Returns
    -------
    green_lesion_area_by_leaf: dict([id:lesion_area])
        Surface of the lesions on each green part of the MTG given by the label
    """
    from alinea.alep.architecture import get_leaves
    vids = get_leaves(g, label=label)
    lesions = g.property('lesions')
    areas = g.property('area')
    green_lengths = g.property('green_length')
    sen_lengths = g.property('senesced_length')
    
    gla = {}
    for vid in vids:
        if vid in lesions.keys():
            les_surf = sum(l.surface_alive for l in lesions[vid])
            ratio_sen = sen_lengths[vid]/(sen_lengths[vid]+green_lengths[vid]) if (sen_lengths[vid]+green_lengths[vid])>0. else 0.
            # /!\ TODO : Can be replaced by green_areas[vid]/senesced_areas[vid]
            if les_surf<=areas[vid]:
                gla[vid]=les_surf*(1-ratio_sen)
            else:
                gla[vid]=les_surf-(areas[vid]*ratio_sen)
        else:
            gla[vid]=0.
    return gla

def compute_healthy_area_by_leaf(g, label='LeafElement'):
    """ Compute healthy area on each part of the MTG given by the label.
    
    Healthy area is green area (without senescence) minus the surface of lesions.
    
    Parameters
    ----------
    g: MTG
        MTG representing the canopy
    label: str
        Label of the part of the MTG concerned by the calculation
        
    Returns
    -------
    healthy_by_leaf: dict([id:healthy_area])
        Healthy area on each part of the MTG given by the label
    """
    from alinea.alep.architecture import get_leaves
    vids = get_leaves(g, label=label)
    # green_areas = g.property('green_area')

    areas = g.property('area')
    labels = g.property('label')
    # positions_senescence = g.property('position_senescence')
    sen_lengths = g.property('senesced_length')
    green_lengths = g.property('green_length')
    senesced_areas = {k:v*(sen_lengths[k]/(sen_lengths[k]+green_lengths[k]) if (sen_lengths[k]+green_lengths[k])>0. else 0.) for k,v in areas.iteritems() if labels[k].startswith(label)}
    
    # if len(positions_senescence)>0:
        # senesced_areas = {k:v*(1-positions_senescence[k]) for k,v in areas.iteritems() if labels[k].startswith(label)}
    # else:
        # senesced_areas = {k:0. for k,v in areas.iteritems() if labels[k].startswith(label)}
    green_lesion_areas = compute_green_lesion_areas_by_leaf(g, label)
    
    # return {vid:(areas[vid] - (senesced_areas[vid] + green_lesion_areas[vid])
        # if round(areas[vid],10)>round((senesced_areas[vid] + green_lesion_areas[vid]),10) else 0.)
        # for vid in vids}
        
    return {vid:(areas[vid] - (senesced_areas[vid] + green_lesion_areas[vid])) for vid in vids}
    
def compute_severity_by_leaf(g, label='LeafElement'):
    """ Compute severity of the disease on each part of the MTG given by the label.
    
    Severity is the ratio between disease surface and total leaf area (in %).
    
    Parameters
    ----------
    g: MTG
        MTG representing the canopy
    label: str
        Label of the part of the MTG concerned by the calculation
        
    Returns
    -------
    severity_by_leaf: dict([id:severity])
        Severity on each part of the MTG given by the label
    """
    from alinea.alep.architecture import get_leaves
    leaves = get_leaves(g, label=label)
    total_areas = g.property('area')
    lesion_areas = compute_lesion_areas_by_leaf(g, label)
    
    # Calculate by blade
    blades = np.array_split(leaves,np.where(np.diff(leaves)!=1)[0]+1)
    sev={}
    for bl in blades:
        area_bl = np.array([total_areas[lf] for lf in bl])
        if any(area_bl==0.):
            for lf in bl[area_bl==0.]:
                sev[lf]=0.
            bl = np.delete(bl,np.where(area_bl==0.))
            area_bl = np.delete(area_bl,np.where(area_bl==0.))
        les_bl = np.array([lesion_areas[lf] for lf in bl])
        sev_bl = np.zeros(len(les_bl))
        diff = area_bl - les_bl
        if any(diff<0):
            for lf in bl[diff<0]:
                sev[lf]=100.
            to_share = abs(sum(diff[diff<0]))
            bl = np.delete(bl,np.where(diff<0))
            area_bl = np.delete(area_bl,np.where(diff<0))
            diff = np.delete(diff,np.where(diff<0))
            diff*=1-to_share/sum(diff)
        for ind in range(len(bl)):
            if diff[ind]>area_bl[ind]:
                import pdb
                pdb.set_trace()
            sev[bl[ind]] = max(0, min(100, 100.*(1-diff[ind]/area_bl[ind])))
    
    #return {vid:(100*lesion_areas[vid]/float(total_areas[vid]) if total_areas[vid]>0. else 0.) for vid in vids}
    return sev
    
def compute_senescence_by_leaf(g, label='LeafElement'):
    """ Compute senescence on parts of the MTG given by the label.
    
    Parameters
    ----------
    g: MTG
        MTG representing the canopy
    label: str
        Label of the part of the MTG concerned by the calculation
        
    Returns
    -------
    senescence_by_leaf: dict([id:senescence_area])
        Senescence on each part of the MTG given by the label    
    """
    labels = g.property('label')
    total_areas = {k:v for k,v in g.property('area').iteritems() if labels[k].startswith(label)}
    pos_sen = g.property('position_senescence')
    sen = {}
    for vid in total_areas.iterkeys():
        sen[vid] = total_areas[vid]*(1-pos_sen[vid])
    return sen
    
def compute_senescence_necrosis_by_leaf(g, label='LeafElement'):
    """ Compute senescence and lesion necrosis on green parts. 
    
    Parameters
    ----------
    g: MTG
        MTG representing the canopy
    label: str
        Label of the part of the MTG concerned by the calculation
        
    Returns
    -------
    necrosis_senescence_by_leaf: dict([id:necrosis_senescence_area])
        Senescence and lesion necrosis on each part of the MTG given by the label    
    """
    from alinea.alep.architecture import get_leaves
    vids = get_leaves(g, label=label)
    total_areas = g.property('area')
    healthy_areas = g.property('healthy_area')
    lesions = g.property('lesions')
    pos_sen = g.property('position_senescence')
    nec_sen = {}
    for vid in total_areas.iterkeys():
        if vid in lesions.keys():
            # Note G.Garin 16/12/13:
            # Little hack when senescence reaches leaf basis to account 
            # non localized lesion growth with available space. 
            nec_on_green = sum(lesion.necrotic_area for lesion in lesions[vid] if not lesion.is_senescent)
            les_on_green = sum(lesion.surface for lesion in lesions[vid] if not lesion.is_senescent)
            ratio_nec_on_green = nec_on_green/les_on_green if les_on_green>0. else 0.
            nec = min(nec_on_green, (total_areas[vid]*pos_sen[vid] - healthy_areas[vid])*ratio_nec_on_green)
            sen = total_areas[vid]*(1-pos_sen[vid])
            nec_sen[vid] = nec + sen
        else:
            nec_sen[vid] = 0.
    return nec_sen

def compute_necrosis_percentage_by_leaf(g, label='LeafElement'):
    """ Compute necrosis percentage on each part of the MTG given by the label.
    
    Necrosis percentage is the ratio between necrotic area and total leaf area.
    A tissue is necrotic if it is covered by a lesion in one of these states:
        - NECROTIC
        - SPORULATING
        - EMPTY
    
    Parameters
    ----------
    g: MTG
        MTG representing the canopy
    label: str
        Label of the part of the MTG concerned by the calculation
        
    Returns
    -------
    necrosis_by_leaf: dict([id:necrosis_percentage])
        Necrosis percentage on each part of the MTG given by the label
    """
    from alinea.alep.architecture import get_leaves
    leaves = get_leaves(g, label=label)
    total_areas = g.property('area')
    lesions = g.property('lesions')
    necrotic_areas = {}
    for vid in total_areas.iterkeys():
        if vid in lesions.keys():
            necrotic_areas[vid] = sum([lesion.necrotic_area for lesion in lesions[vid]])
        else:
            necrotic_areas[vid] = 0.
            
    # Calculate by blade
    blades = np.array_split(leaves,np.where(np.diff(leaves)!=1)[0]+1)
    necrosis_by_leaf={}
    for bl in blades:
        area_bl = np.array([total_areas[lf] for lf in bl])
        if any(area_bl==0.):
            for lf in bl[area_bl==0.]:
                necrosis_by_leaf[lf]=0.
            bl = np.delete(bl,np.where(area_bl==0.))
            area_bl = np.delete(area_bl,np.where(area_bl==0.))
        nec_bl = np.array([necrotic_areas[lf] for lf in bl])
        diff = area_bl - nec_bl
        if any(diff<0):
            for lf in bl[diff<0]:
                necrosis_by_leaf[lf]=100.
            to_share = abs(sum(diff[diff<0]))
            bl = np.delete(bl,np.where(diff<0))
            area_bl = np.delete(area_bl,np.where(diff<0))
            diff = np.delete(diff,np.where(diff<0))
            diff*=1-to_share/sum(diff)
        for ind in range(len(bl)):
            if diff[ind]>area_bl[ind]:
                import pdb
                pdb.set_trace()
            necrosis_by_leaf[bl[ind]] = 100.*(1-diff[ind]/area_bl[ind])
    
    #return {vid:(100*necrotic_areas[vid]/float(total_areas[vid]) if total_areas[vid]>0. else 0.) for vid in vids}
    return necrosis_by_leaf
    
def compute_necrotic_area_by_leaf(g, label='LeafElement'):
    """ Compute necrosis percentage on each part of the MTG given by the label.
    
    Necrosis percentage is the ratio between necrotic area and total leaf area.
    A tissue is necrotic if it is covered by a lesion in one of these states:
        - NECROTIC
        - SPORULATING
        - EMPTY
    
    Parameters
    ----------
    g: MTG
        MTG representing the canopy
    label: str
        Label of the part of the MTG concerned by the calculation
        
    Returns
    -------
    necrotic_area_by_leaf: dict([id:necrotic_area])
        Necrotic area on each part of the MTG given by the label
    """
    from alinea.alep.architecture import get_leaves
    vids = get_leaves(g, label=label)
    total_areas = g.property('area')
    lesions = g.property('lesions')
    necrotic_areas = {}
    for vid in total_areas.iterkeys():
        if vid in lesions.keys():
            necrotic_areas[vid] = sum(lesion.necrotic_area for lesion in lesions[vid])
        else:
            necrotic_areas[vid] = 0.
    return necrotic_areas
    
def compute_total_severity(g, label='LeafElement'):
    """ Compute disease severity on the whole plant.
    
    Severity is the ratio between disease surface and green leaf area (in %).
    
    Parameters
    ----------
    g: MTG
        MTG representing the canopy
    label: str
        Label of the part of the MTG concerned by the calculation
        
    Returns
    -------
    severity: float
        Ratio between disease surface and green leaf area (in %)
    """
    from numpy import mean
    severities = compute_severity_by_leaf(g, label=label)
    return mean(severities.values())
    
def compute_total_necrosis_percentage(g, label='LeafElement'):
    """ Compute necrosis percentage on the whole plant.
    
    Necrosis percentage ratio between necrotic (and sporulating) disease surface and total area of leaves.
    
    Parameters
    ----------
    g: MTG
        MTG representing the canopy
    label: str
        Label of the part of the MTG concerned by the calculation
        
    Returns
    -------
    necrosis_percentage: float
        Ratio between necrotic (and sporulating) disease area and total area of leaves (in %)
    """   
    from numpy import mean
    nec = compute_necrosis_percentage_by_leaf(g, label=label)
    return mean(nec.values())

def compute_total_necrotic_area(g, label='LeafElement'):
    """ Compute necrosis percentage on the whole plant.
    
    Necrosis percentage ratio between necrotic (and sporulating) disease surface and total area of leaves.
    
    Parameters
    ----------
    g: MTG
        MTG representing the canopy
    label: str
        Label of the part of the MTG concerned by the calculation
        
    Returns
    -------
    necrotic_area: float
        Total area of leaves covered by necrotic surfaces of lesions (in cm2)
    """
    from numpy import mean
    nec = compute_necrotic_area_by_leaf(g, label=label)
    return sum(nec.values())

def compute_normalised_audpc(necrosis, total_area):
    """ Compute the normalised AUDPC as in Robert et al. 2008
    
    "AUDPC is calculated as the area below the curve of pycnidia bearing
    necrotic leaf area. The latter is the leaf area that is or has been
    covered by sporulating lesions and thus represents the sporulation 
    potential of the leaf. The normalised AUDPC is obtained by dividing
    the AUDPC by a theoretical maximum value corresponding to the situation
    where the leaf is infected fully just after its emergence."
    
    Parameters
    ----------
    necrosis: list or array
        Historical values of necrosis percentage
    total_area: list or array
        Historical values of leaf area (same length than necrosis)
        
    Returns
    -------
    normalised_audpc: float
       AUDPC divided by a theoretical maximum value
    """
    import numpy as np
    from scipy.integrate import trapz
    full_necrosis = np.array([100. if total_area[k]>0. else 0. 
                              for k in range(len(total_area))])
    
    audpc = trapz(necrosis, dx=1)
    theo_audpc = trapz(full_necrosis, dx=1)
    return 100*audpc/theo_audpc if theo_audpc>0. else 0.
 
def plot3d_transparency(g, 
               leaf_material = None,
               stem_material = None,
               soil_material = None,
               colors = None,
               transparencies = None):
    """
    Returns a plantgl scene from an mtg.
    """
    from openalea.plantgl import all as pgl
    Material = pgl.Material
    Color3 = pgl.Color3
    Shape = pgl.Shape
    Scene = pgl.Scene
    
    if colors is None:
        if leaf_material is None:
            leaf_material = Material(Color3(0,180,0))
        if stem_material is None:
            stem_material = Material(Color3(0,130,0))
        if soil_material is None:
            soil_material = Material(Color3(170, 85,0))
        colors = g.property('color')

    transparencies = g.property('transparency')
    
    geometries = g.property('geometry')
    greeness = g.property('is_green')
    labels = g.property('label')
    scene = Scene()

    def geom2shape(vid, mesh, scene):
        shape = None
        if isinstance(mesh, list):
            for m in mesh:
                geom2shape(vid, m, scene)
            return
        if mesh is None:
            return
        if isinstance(mesh, Shape):
            shape = mesh
            mesh = mesh.geometry
        label = labels.get(vid)
        is_green = greeness.get(vid)
        if colors:
            if transparencies==None:
                shape = Shape(mesh, Material(Color3(* colors.get(vid, [0,0,0]) )))
            else:
                shape = Shape(mesh, Material(Color3(* colors.get(vid, [0,0,0]) ), transparency=transparencies.get(vid,0)))
        elif not greeness:
            if not shape:
                shape = Shape(mesh)
        elif label.startswith('Stem') and is_green:
            shape = Shape(mesh, stem_material)
        elif label.startswith('Leaf') and is_green:
            shape = Shape(mesh, leaf_material)
        elif not is_green:
            shape = Shape(mesh, soil_material)
        shape.id = vid
        scene.add(shape)

    for vid, mesh in geometries.iteritems():
        geom2shape(vid, mesh, scene)
    return scene

def plot_severity_by_leaf(g, senescence=True, transparency=None, label='LeafElement'):
    """ Display the MTG with colored leaves according to disease severity 
    
    Parameters
    ----------
    g: MTG
        MTG representing the canopy
    senescence: bool
        True if senescence must be displayed, False otherwise
    transparency: float[0:1]
        Transparency of the part of the MTG without lesion
    label: str
        Label of the part of the MTG concerned by the calculation
        
    Returns
    -------
    scene:
        Scene containing the MTG attacked by the disease
    
    """
    from alinea.alep.architecture import set_property_on_each_id, get_leaves
    from alinea.alep.disease_outputs import compute_severity_by_leaf
    from alinea.alep.alep_color import alep_colormap, green_yellow_red
    from alinea.adel.mtg_interpreter import plot3d
    from openalea.plantgl.all import Viewer
    # Compute severity by leaf
    severity_by_leaf = compute_severity_by_leaf(g, label=label)
    set_property_on_each_id(g, 'severity', severity_by_leaf, label=label)

    # Visualization
    g = alep_colormap(g, 'severity', cmap=green_yellow_red(levels=100),
                      lognorm=False, zero_to_one=False, vmax=100)

    if senescence==True:
        leaves = get_leaves(g, label=label)
        # pos_sen = g.property('position_senescence')
        sen_lengths = g.property('senesced_length')
        green_lengths = g.property('green_length')
        for leaf in leaves:
            if sen_lengths[leaf]>0. and round(green_lengths[leaf],15)==0.:
                g.node(leaf).color = (157, 72, 7)
    
    if transparency!=None:
        for id in g:
            if not id in severity_by_leaf:
                g.node(id).color = (255,255,255)
                g.node(id).transparency = 0.9
            elif severity_by_leaf[id]==0.:
                g.node(id).color = (255,255,255)
                g.node(id).transparency = transparency
            else:
                g.node(id).transparency = 0.
        
        scene = plot3d_transparency(g)
    else:
        scene = plot3d(g)
    Viewer.display(scene)
    return scene

def plot_severity_vine(g, trunk=True, transparency=None, label='lf'):
    from alinea.alep.architecture import set_property_on_each_id
    from alinea.alep.disease_outputs import compute_severity_by_leaf
    from alinea.alep.alep_color import alep_colormap, green_yellow_red
    from alinea.adel.mtg_interpreter import plot3d
    from openalea.plantgl.all import Viewer
    # Compute severity by leaf
    severity_by_leaf = compute_severity_by_leaf(g, label = label)
    set_property_on_each_id(g, 'severity', severity_by_leaf, label = label)
                       
    # Visualization
    g = alep_colormap(g, 'severity', cmap=green_yellow_red(levels=100),
                      lognorm=False, zero_to_one=False, vmax=100)
    brown = (100,70,30)
    if trunk==True:
        trunk_ids = [n for n in g if g.label(n).startswith('tronc')]
        for id in trunk_ids:
            trunk = g.node(id)
            trunk.color = brown
            
    if transparency!=None:
        for id in g:
            if not id in severity_by_leaf:
                g.node(id).color = (255,255,255)
                g.node(id).transparency = 0.9
            elif severity_by_leaf[id]==0.:
                g.node(id).color = (255,255,255)
                g.node(id).transparency = transparency
            else:
                g.node(id).transparency = 0.
        scene = plot3d_transparency(g)
    else:
        scene = plot3d(g)
    Viewer.display(scene)
    return scene
    
def save_image(scene, image_name='%s/img%04d.%s', directory='.', index=0, ext='png'):
    '''
    Save an image of a scene in a specific directory

    Parameters
    ----------

        - scene: a PlantGL scene
        - image_name: a string template 
            The format of the string is dir/img5.png
        - directory (optional: ".") the directory where the images are written
        - index: the index of the image
        - ext : the image format

    Example
    -------

        - Movie:
            convert *.png movie.mpeg
            convert *.png movie.gif
            mencoder "mf://*.png" -mf type=png:fps=25 -ovc lavc -o output.avi
            mencoder -mc 0 -noskip -skiplimit 0 -ovc lavc -lavcopts vcodec=msmpeg4v2:vhq "mf://*.png" -mf type=png:fps=18 -of avi  -o output.avi
            
    '''
    from openalea.plantgl.all import Viewer
    import os.path
    if not image_name:
        image_name='{directory}/img{index:0>4d}.{ext}'
    filename = image_name.format(directory=directory, index=index, ext=ext)
    Viewer.frameGL.saveImage(filename)
    return scene,
 
######################################################################
from numpy import mean
import numpy as np
from scipy.integrate import trapz

class VineLeafInspector:
    def __init__(self, leaf_id, label='lf'):
        self.leaf_id = leaf_id
        self.label = label
        # Initialize leaf properties to save
        self.leaf_area = []
        self.leaf_green_area = []  
        self.leaf_healthy_area = []
        self.leaf_disease_area = []
        # Initialize surfaces in state
        self.surface_latent = []
        self.surface_spo = []
        self.surface_empty = []
        # Initialize ratios (surfaces in state compared to leaf area)
        self.ratio_latent = []
        self.ratio_spo = []
        self.ratio_empty = []
        # Initialize total severity
        self.severity = []

    def update_data(self, g):
        leaf = g.node(self.leaf_id)
        area = leaf.area
        if area!=None:
            self.leaf_area.append(area)
            self.leaf_green_area.append(leaf.green_area)
            self.leaf_healthy_area.append(leaf.healthy_area)
            self.leaf_disease_area.append(area - leaf.healthy_area)
            
        else:
            area = 0.
            self.leaf_area.append(0.)
            self.leaf_green_area.append(0.)
            self.leaf_healthy_area.append(0.)
            self.leaf_disease_area.append(0.)
        
        self.severity.append(100.*(1.-leaf.healthy_area/area) if area>0. else 0.)
        
        try:
            lesions = leaf.lesions
        except:
            lesions = []
        surface_latent = 0.
        surface_spo = 0.
        surface_empty = 0.
        if len(lesions)>0.:
            latent_lesions = [l for l in lesions if l.is_latent()]
            if len(latent_lesions)>0.:
                surface_latent = sum([l.surface for l in latent_lesions])
            
            spo_lesions = [l for l in lesions if l.is_sporulating()]
            if len(spo_lesions)>0.:
                surface_spo = sum([l.surface for l in spo_lesions])
            
            empty_lesions = [l for l in lesions if l.is_empty()]
            if len(empty_lesions)>0.:
                surface_empty = sum([l.surface for l in empty_lesions])
                
        self.surface_latent.append(surface_latent)
        self.ratio_latent.append(100.*surface_latent/area if area>0. else 0.)
        self.surface_spo.append(surface_spo)
        self.ratio_spo.append(100.*surface_spo/area if area>0. else 0.)
        self.surface_empty.append(surface_empty)
        self.ratio_empty.append(100.*surface_empty/area if area>0. else 0.)
        
######################################################################
import numpy
import pandas
from scipy.integrate import trapz, simps
from alinea.astk.plantgl_utils import get_height
from alinea.adel.newmtg import adel_ids
from collections import Iterable
try:
    import cPickle as pickle
except:
    import pickle

class AdelSeptoRecorder:
    def __init__(self, vids=None, adel_labels = None, 
                 group_dus=True, date_sequence = None, fungus_name = 'septoria'):
        """ vids are ids of leaf sectors on the same blade. """
        self.fungus_name = fungus_name
        self.vids = vids
        self.adel_labels = adel_labels
        self.group_dus = group_dus
        self.data = pandas.DataFrame(index = date_sequence, columns = ['degree_days',
                                                                       'leaf_area', 
                                                                       'leaf_green_area',
                                                                       'leaf_length',
                                                                       'leaf_senesced_length',
                                                                       'nb_dispersal_units',
                                                                       'nb_dus_on_green',
                                                                       'nb_lesions',
                                                                       'nb_lesions_on_green',
                                                                       'surface_inc',
                                                                       'surface_chlo',
                                                                       'surface_nec',
                                                                       'surface_spo',
                                                                       'surface_spo_on_green',
                                                                       'surface_empty',
                                                                       'surface_empty_on_green',
                                                                       'surface_dead'])
        self.date_death = None

    def update_vids_with_labels(self, adel_ids):
        self.vids = [adel_ids[lb] for lb in self.adel_labels]
        
    def update_vids(self, vids=[]):
        self.vids = vids
    
    def record(self, g, date, degree_days=None):
        if self.date_death == None:
            geometries = g.property('geometry')
            areas = g.property('geometry')
            vids = [id for id in self.vids if geometries.get(id) is not None and areas.get(id) is not None]
        
            # Spot disappearing of leaf_element to stop recording               
            if 'leaf_area' in self.data and self.data.leaf_area.sum()>0 and len(vids)==0.:
                self.date_death = date
                return
        
            self.data['degree_days'][date] = degree_days

            # Update leaf properties
            self.data['leaf_area'][date] = sum([g.node(id).area for id in vids])
            self.data['leaf_green_area'][date] = sum([g.node(id).green_area for id in vids])
            self.data['leaf_length'][date] = sum([g.node(id).length for id in vids])
            self.data['leaf_senesced_length'][date] = sum([g.node(id).senesced_length for id in vids])
                
            # Update properties of dispersal units and lesions
            nb_dus = 0
            nb_dus_on_green = 0
            nb_lesions = 0
            nb_lesions_on_green = 0
            surface_inc = 0.
            surface_chlo = 0.
            surface_nec = 0.
            surface_spo = 0.
            surface_spo_on_green = 0.
            surface_empty = 0.
            surface_empty_on_green = 0.
            surface_dead = 0.
            
            for id in vids:
                leaf = g.node(id)
                if 'dispersal_units' in leaf.properties():
                    for du in leaf.dispersal_units:
                        if du.fungus.name == self.fungus_name:
                            if self.group_dus:
                                nb_dus += len(du.position)
                                nb_dus_on_green += len(filter(lambda x: x[0]>leaf.senesced_length, du.position))
                            else:
                                nb_dus += 1
                                if du.position[0][0]>leaf.senesced_length:
                                    nb_dus_on_green += 1
                                    
                if 'lesions' in leaf.properties():
                    for les in leaf.lesions:
                        if les.fungus.name == self.fungus_name:
                            if self.group_dus:
                                nb_les = len(les.position)
                                nb_les_on_green = len(filter(lambda x: x[0]>leaf.senesced_length, les.position))
                                nb_lesions += nb_les
                                nb_lesions_on_green += nb_les_on_green
                                surface_spo_on_green = les.surface_spo * nb_les_on_green/nb_les if nb_les>0. else 0.
                                surface_empty_on_green = les.surface_empty * nb_les_on_green/nb_les if nb_les>0. else 0.
                            else:
                                nb_lesions += 1
                                if les.position[0][0]>leaf.senesced_length:
                                    nb_lesions_on_green += 1
                                    surface_spo_on_green = les.surface_spo
                                    surface_empty_on_green = les.surface_empty
                            surface_inc += les.surface_inc
                            surface_chlo += les.surface_chlo
                            surface_nec += les.surface_nec
                            surface_spo += les.surface_spo
                            surface_empty += les.surface_empty
                            surface_dead += les.surface_dead

            self.data['nb_dispersal_units'][date] = nb_dus
            self.data['nb_dus_on_green'][date] = nb_dus_on_green
            self.data['nb_lesions'][date] = nb_lesions
            self.data['nb_lesions_on_green'][date] = nb_lesions_on_green
            self.data['surface_inc'][date] = surface_inc
            self.data['surface_chlo'][date] = surface_chlo
            self.data['surface_nec'][date] = surface_nec
            self.data['surface_spo'][date] = surface_spo
            self.data['surface_empty'][date] = surface_empty
            self.data['surface_dead'][date] = surface_dead
            self.data['surface_spo_on_green'][date] = surface_spo_on_green
            self.data['surface_empty_on_green'][date] = surface_empty_on_green
    
    def get_nan_index(self):
        return self.data.index[np.isnan(self.data.ix[:,'leaf_area'].astype(float))]
    
    def leaf_senesced_area(self):
        self.data['leaf_senesced_area'] = self.data['leaf_area'] - self.data['leaf_green_area']
    
    def leaf_disease_area(self):
        self.data['leaf_disease_area'] = self.data['surface_inc'] + self.data['surface_chlo'] + self.data['surface_nec'] + self.data['surface_spo'] + self.data['surface_empty'] + self.data['surface_dead']

    def leaf_lesion_area_on_green(self):
        if not 'leaf_disease_area' in self.data:
            self.leaf_disease_area()
        if not 'leaf_senesced_area' in self.data:
            self.leaf_senesced_area()
        self.data['leaf_lesion_area_on_green'] = [self.data['leaf_disease_area'][ind]*(1 - self.data['leaf_senesced_area'][ind]/self.data['leaf_area'][ind]) if self.data['leaf_area'][ind]>0. else 0. for ind in self.data.index]
        self.data['leaf_lesion_area_on_green'][self.get_nan_index()] = np.nan
    
    def leaf_necrotic_area_on_green(self):
        if not 'necrosis' in self.data:
            self.necrosis()
        if not 'leaf_senesced_area' in self.data:
            self.leaf_senesced_area()
        self.data['leaf_necrotic_area_on_green'] = [self.data['necrosis'][ind]*(1 - self.data['leaf_senesced_area'][ind]/self.data['leaf_area'][ind]) if self.data['leaf_area'][ind]>0. else 0. for ind in self.data.index]
        self.data['leaf_necrotic_area_on_green'][self.get_nan_index()] = np.nan
    
    def leaf_necrotic_senescent(self):
        if not 'leaf_necrotic_area_on_green' in self.data:
            self.leaf_necrotic_area_on_green()
        if not 'leaf_senesced_area' in self.data:
            self.leaf_senesced_area()
        self.data['leaf_necrotic_senescent'] = self.data['leaf_senesced_area'] + self.data['leaf_necrotic_area_on_green']
        
    def necrotic_senescent_percentage(self):
        if not 'leaf_necrotic_senescent' in self.data:
            self.leaf_necrotic_senescent()
        self.data['leaf_necrotic_senescent'] = [self.data['leaf_necrotic_senescent'][ind]/self.data['leaf_area'][ind] if self.data['leaf_area'][ind]>0. else 0. for ind in self.data.index]
        self.data['leaf_necrotic_senescent'][self.get_nan_index()] = np.nan
        
    def leaf_healthy_area(self):
        if not 'leaf_lesion_area_on_green' in self.data:
            self.leaf_lesion_area_on_green()
        self.data['leaf_healthy_area'] = self.data['leaf_green_area'] - self.data['leaf_lesion_area_on_green']
    
    def leaf_unhealthy_area(self):
        if not 'leaf_healthy_area' in self.data:
            self.leaf_healthy_area()
        self.data['leaf_unhealthy_area'] = self.data['leaf_area'] - self.data['leaf_healthy_area']

    def surface_alive(self):
        self.data['surface_alive'] = self.data['surface_inc'] + self.data['surface_chlo'] + self.data['surface_nec'] + self.data['surface_spo'] + self.data['surface_empty']

    def ratios(self):
        self.data['ratio_inc'] = [self.data['surface_inc'][ind]/self.data['leaf_area'][ind] if self.data['leaf_area'][ind]>0. else 0. for ind in self.data.index]
        self.data['ratio_chlo'] = [self.data['surface_chlo'][ind]/self.data['leaf_area'][ind] if self.data['leaf_area'][ind]>0. else 0. for ind in self.data.index]
        self.data['ratio_nec'] = [self.data['surface_nec'][ind]/self.data['leaf_area'][ind] if self.data['leaf_area'][ind]>0. else 0. for ind in self.data.index]
        self.data['ratio_spo'] = [self.data['surface_spo'][ind]/self.data['leaf_area'][ind] if self.data['leaf_area'][ind]>0. else 0. for ind in self.data.index]
        self.data['ratio_empty'] = [self.data['surface_empty'][ind]/self.data['leaf_area'][ind] if self.data['leaf_area'][ind]>0. else 0. for ind in self.data.index]
        self.data['ratio_spo_on_green'] = [self.data['surface_spo_on_green'][ind]/self.data['leaf_green_area'][ind] if self.data['leaf_green_area'][ind]>0. else 0. for ind in self.data.index]
        self.data['ratio_empty_on_green'] = [self.data['surface_empty_on_green'][ind]/self.data['leaf_green_area'][ind] if self.data['leaf_green_area'][ind]>0. else 0. for ind in self.data.index]

        nan_ind = self.get_nan_index()
        self.data['ratio_inc'][nan_ind] = np.nan        
        self.data['ratio_chlo'][nan_ind] = np.nan        
        self.data['ratio_nec'][nan_ind] = np.nan        
        self.data['ratio_spo'][nan_ind] = np.nan        
        self.data['ratio_empty'][nan_ind] = np.nan        
        self.data['ratio_spo_on_green'][nan_ind] = np.nan        
        self.data['ratio_empty_on_green'][nan_ind] = np.nan        
        
    def severity(self):
        if not 'leaf_disease_area' in self.data:
            self.leaf_disease_area()
        self.data['severity'] = [self.data['leaf_disease_area'][ind]/self.data['leaf_area'][ind] if self.data['leaf_area'][ind]>0. else 0. for ind in self.data.index]
        self.data['severity'][self.get_nan_index()] = np.nan
    
    def severity_on_green(self):
        if not 'severity' in self.data:
            self.severity()
        if not 'leaf_lesion_area_on_green' in self.data:
            self.leaf_lesion_area_on_green()
        self.data['severity_on_green'] = [self.data['leaf_lesion_area_on_green'][ind]/self.data['leaf_area'][ind] if self.data['leaf_area'][ind]>0. else 0. for ind in self.data.index]
        self.data['severity_on_green'][self.get_nan_index()] = np.nan

    def necrosis(self):
        self.data['necrosis'] = self.data['surface_nec'] + self.data['surface_spo'] + self.data['surface_empty']
    
    def necrosis_percentage(self):
        if not 'necrosis' in self.data:
            self.necrosis()
        self.data['necrosis_percentage'] = [self.data['necrosis'][ind]/self.data['leaf_area'][ind] if self.data['leaf_area'][ind]>0. else 0. for ind in self.data.index]
        self.data['necrosis_percentage'][self.get_nan_index()] = np.nan
        
    def pycnidia_coverage(self):
        if not 'ratio_spo' in self.data and not 'ratio_empty' in self.data:
            self.ratios()
        self.pycnidia_coverage = self.data['ratio_spo'] + self.data['ratio_empty']
        
    def pycnidia_coverage_on_green(self):
        if not 'ratio_spo_on_green' in self.data and not 'ratio_empty_on_green' in self.data:
            self.ratios()
        self.pycnidia_coverage_on_green = self.data['ratio_spo_on_green'] + self.data['ratio_empty_on_green']
    
    def get_audpc(self, variable='necrosis_percentage'):
        """ Variable can be 'severity' or 'necrosis_percentage'. """
        if not variable in self.data:
            exec('self.'+variable+'()')
        if self.date_death != None and len(self.data.leaf_green_area)==0:
            self.audpc = 'audpc not available: premature leaf death'
        elif self.data['leaf_green_area'][-1]==0.:
            ind = self.data.index[self.data['leaf_green_area']>0]
            data = self.data[variable][ind]
            ddays = self.data['degree_days'][ind]
            self.audpc = simps(data, ddays)
        else:
            self.audpc = 'audpc not available: leaf has not reached senescence'
            
        return self.audpc
        
    def get_normalized_audpc(self, variable='necrosis_percentage'):
        """ Variable can be 'severity' or 'necrosis_percentage'. """
        if not variable in self.data:
            exec('self.'+variable+'()')
        if self.date_death != None and len(self.data.leaf_green_area)==0:
            self.normalized_audpc = 'audpc not available: premature leaf death'
        elif self.data['leaf_green_area'][-1]==0.:
            ind = self.data.index[self.data['leaf_green_area']>0]
            data = self.data[variable][ind]
            ddays = self.data['degree_days'][ind]
            data_ref = numpy.ones(len(ind))
            audpc = simps(data, ddays)
            audpc_ref = simps(data_ref, ddays)
            self.normalized_audpc = audpc/audpc_ref if audpc_ref>0. else 0.
        else:
            self.normalized_audpc = 'audpc not available: leaf has not reached senescence'
        return self.normalized_audpc
                
    def get_complete_dataframe(self):
        self.leaf_senesced_area()
        self.leaf_disease_area()
        self.leaf_lesion_area_on_green()
        self.leaf_healthy_area()
        self.leaf_unhealthy_area()
        self.surface_alive()
        self.ratios()
        self.severity()
        self.severity_on_green()
        self.necrosis()
        self.necrosis_percentage()

    def record_only_leaf_data(self, g, date, degree_days=None):
        if self.date_death == None:
            geometries = g.property('geometry')
            areas = g.property('geometry')
            vids = [id for id in self.vids if geometries.get(id) is not None and areas.get(id) is not None]
        
            # Spot disappearing of leaf_element to stop recording
            if sum(self.leaf_area)>0 and len(vids)==0.:
                self.date_death = date
                return
                
            self.data['degree_days'][date] = degree_days
        
            # Update leaf properties
            self.data['leaf_area'][date] = sum([g.node(id).area for id in vids])
            self.data['leaf_green_area'][date] = sum([g.node(id).green_area for id in vids])
            self.data['leaf_length'][date] = sum([g.node(id).length for id in vids])
            self.data['leaf_senesced_length'][date] = sum([g.node(id).senesced_length for id in vids])
            heights = [numpy.mean(get_height({vid:g.node(vid).geometry}).values()) for vid in vids]
            
            self.data['senesced_area'][date] = sum([g.node(id).senesced_area for id in vids])
            self.data['leaf_green_length'][date] = sum([g.node(id).green_length for id in vids])
            self.data['leaf_min_height'][date] = min(heights) if len(heights)>0. else 0.
            self.data['leaf_max_height'][date] = max(heights) if len(heights)>0. else 0.
        
    def inactivate(self, date=None):
        labels = self.adel_labels
        if sum(self.leaf_green_area)==0:
            self.__init__()
        self.adel_labels = labels
        self.date_death = date
        
def initiate_all_adel_septo_recorders(g, nsect=5, date_sequence = None, fungus_name = 'septoria'):
    """ Used in the case of recording all blades of the main stem of each plant.
    
    Returns
    -------
    leaf_labels: dict('P1'=dict('F1'= recorder init with list of labels for leaf sectors,
                                ...,
                                'Fi'= recorder),
                      ...,
                      'Pn'=dict('F1' = recorder,
                                ...,
                                'Fi' = recorder))
    
    """
    vids = adel_ids(g)
    labels = g.property('label')
    stems = [id for id,lb in labels.iteritems() if lb.startswith('MS')]
    recorders = {}
    ind_plant = 0
    for st in stems:
        ind_plant += 1
        recorders['P%d' % ind_plant] = {}
        nff = int(g.node(st).properties()['nff'])
        ind_lf = nff+1
        for leaf in range(1, nff+1):
            ind_lf -= 1
            lf_labels = ['plant%d_MS_metamer%d_blade_LeafElement%d' % (ind_plant, leaf, sect) for sect in range(1, nsect+1)]
            recorders['P%d' % ind_plant]['F%d' % ind_lf] = AdelSeptoRecorder(adel_labels = lf_labels, 
                                                                             date_sequence = date_sequence,
                                                                             fungus_name = fungus_name)
            recorders['P%d' % ind_plant]['F%d' % ind_lf].update_vids_with_labels(vids)
    return recorders
        
def num_leaf_to_str(num_leaves=range(1,5)):
    return ['F%d' % lf for lf in num_leaves]
    
def get_recorder(*filenames):
    recorder = []
    for file in filenames:
        f_rec = open(file)
        recorder.append(pickle.load(f_rec))
        f_rec.close()
    return recorder if len(recorder)>1 else recorder[0]

def split_recorder_by_fnl(recorder):
    fnls = set(len(v) for v in recorder.itervalues())
    recorders = {}
    for fnl in fnls:
        recorders[fnl] = {k:v for k,v in recorder.iteritems() if len(v)==fnl}
    return recorders
    
def renumber_recorder_from_bottom(recorder):
    bottomed_reco = {}
    for k, v in recorder.iteritems():
        fnl = len(v)
        bottomed_reco[k] = {}
        for kk, vv in v.iteritems():
            num_lf_top = int(''.join(x for x in kk if x.isdigit()))
            num_lf_bottom = fnl - num_lf_top + 1
            bottomed_reco[k]['F%d' % num_lf_bottom] = vv
    return bottomed_reco
    
def mean_by_leaf(recorder, variable='necrosis_percentage', skipna = False):
    ddays = max(recorder.values()[0].values(), key= lambda x: len(x.data.degree_days)).data.degree_days
    leaves = ['F%d' % leaf for leaf in range(1, max(len(v) for v in recorder.itervalues())+1)]
    df_mean_by_leaf = pandas.DataFrame(data={lf:[numpy.nan for i in range(len(ddays))] for lf in leaves}, 
                                        index = ddays, columns = leaves)
    dfs = []
    for lf in leaves:
        df_leaf = pandas.concat([v[lf].data[variable] for v in recorder.itervalues() if lf in v], axis=1)
        dfs.append(df_leaf)
        df_mean_by_leaf[:ddays[len(df_leaf)-1]][lf] = df_leaf.mean(axis=1, skipna = skipna).values
    return df_mean_by_leaf

def mean_audpc_by_leaf(recorder, variable = 'necrosis_percentage', normalized=True):
    def try_get(x, lf):
        try:
            if normalized==True:
                try:
                    return float(recorder[x][lf].normalized_audpc)
                except:
                    return float(recorder[x][lf].get_normalized_audpc(variable = variable))
            else:
                try:
                    return float(recorder[x][lf].audpc)
                except:
                    return float(recorder[x][lf].get_audpc(variable = variable))
        except:
            return np.nan
            
    df_mean_by_leaf = pandas.DataFrame()
    plants = recorder.keys()
    for leaf in range(1, max(len(v) for v in recorder.itervalues())+1):
        lf = 'F%d' % leaf
        df_mean_by_leaf[lf] = map(lambda x: try_get(x, lf), plants)
    return df_mean_by_leaf.mean()
    
def glue_df_means(df_means, nb_rep=5):
    glued = pandas.concat(df_means, axis=1, keys=range(nb_rep))
    glued.swaplevel(0, 1, axis=1).sortlevel(axis=1)
    return glued.groupby(level=1, axis=1).mean()
    
def get_mean_by_leaf(variable='necrosis_percentage', *recorders):
    if len(recorders)==1:
        return mean_by_leaf(recorders[0], variable=variable)
    else:
        df_means = [mean_by_leaf(reco, variable=variable) for reco in recorders]
        return glue_df_means(df_means, len(recorders))