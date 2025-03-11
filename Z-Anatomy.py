# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
# Informations sur l'add-on
bl_info = {
    "name": "Z-Anatomy",  # Nom de l'add-on
    "author": "Marcin Zieliński, Justin Müller",  # Auteurs de l'add-on
    "description": "Shows all objects that contain 'always_front' front faced and 'always_show' are never hidden in viewport. Makes hiding objects inheritable.",  # Description de l'add-on
    "blender": (2, 80, 0),  # Version de Blender compatible
    "version": (0, 0, 1),  # Version de l'add-on
    "location": "",  # Emplacement dans l'interface de Blender
    "warning": "",  # Avertissements
    "category": "Interface"  # Catégorie de l'add-on
}

from typing import NewType
import bpy
from mathutils import Vector
import mathutils
import requests, json
import urllib.parse
import os.path
from pathlib import Path
from bpy_extras.object_utils import object_data_add
from bpy.app.handlers import persistent
import re

# Ensemble des éléments de label
label_elements = {"-txt", ".t", "-line"}

def family_all(object):
    ''' Object + Grand children without ancestors '''
    # Initialisation de la famille avec l'objet et ses enfants directs
    family = [object.children[:] + (object,)]

    # Fonction récursive pour ajouter tous les enfants et petits-enfants
    def rec(object, family):
        family[0] += object.children
        for ob in object.children:
            rec(ob, family)

    # Appel récursif pour chaque enfant de l'objet
    for ob in object.children:
        rec(ob, family)

    # Retourne la famille complète
    return family.pop()

def family(object):
    ''' Object + Grand children without ancestors (labels only) '''
    # Fonction interne pour filtrer les enfants qui sont des labels
    def inner_elements(children):
        return tuple(ob for ob in children if any(x in ob.name for x in label_elements))
        # return [ob for ob in children if any(x in ob.name for x in label_elements)]

    # Initialisation des labels avec les enfants directs de l'objet
    labels = inner_elements(object.children)
    family = [labels + (object,)]

    # Fonction récursive pour ajouter tous les labels enfants
    def rec(object, family):
        labels = inner_elements(object.children)
        family[0] += labels
        for ob in labels:
            rec(ob, family)

    # Appel récursif pour chaque enfant de l'objet
    for ob in object.children:
        rec(ob, family)

    # Retourne la famille complète
    return family.pop()


import bpy

class OBJECT_OT_hide_wrapper(bpy.types.Operator):
    """Hide"""
    bl_idname = "object.hide_wrapper"  # Identifiant unique de l'opérateur
    bl_label = "Hide"  # Nom de l'opérateur
    bl_options = {'REGISTER', 'UNDO'}  # Options de l'opérateur (enregistrement et annulation)

    # Propriétés de l'opérateur
    unselected: bpy.props.BoolProperty(default=False, name="Hide unselected")  # Masquer les objets non sélectionnés
    unselected_in_layer: bpy.props.BoolProperty(default=False, name="From active layer")  # Masquer les objets non sélectionnés dans la couche active
    follow_parent: bpy.props.BoolProperty(default=True, name="Follow parent's visibility")  # Suivre la visibilité du parent

    @classmethod
    def poll(cls, context):
        # Vérifie si l'opérateur peut être exécuté
        return context.mode == 'OBJECT' and context.object is not None

    def execute(self, context):
        # Fonction pour trouver la racine d'un objet
        def findRoot(ob):
            while ob and ob.parent:
                if ob in objects_to:
                    objects_to.remove(ob)
                # if '%' in ob.parent.name:
                if not any(x in ob.name for x in label_elements):
                    return ob
                if not ob.parent.parent and not self.unselected:
                    return ob
                ob = ob.parent
            return ob

        roots = []  # Liste pour stocker les racines des objets
        objects_to = set(context.selected_objects)  # Ensemble des objets sélectionnés

        # Trouver les racines des objets sélectionnés
        while objects_to:
            ob = objects_to.pop()
            roots.append(findRoot(ob))

        if self.unselected and not self.unselected_in_layer:
            # Masquer les objets non sélectionnés dans la scène
            all_visible_objects = set(context.visible_objects)
            lights = {l for l in context.view_layer.objects if l.type == 'LIGHT'}

            family_obs = (ob for r in roots for ob in family(r))
            for ob in all_visible_objects - lights - set(family_obs):
                ob.hide_set(True)
        elif self.unselected and self.unselected_in_layer:
            # Masquer les objets non sélectionnés dans la couche active
            all_layer_objects = set()
            for c in context.scene.collection.children:
                if context.object.name in c.all_objects:
                    all_layer_objects = set(c.all_objects)
                    break
            lights = {l for l in context.view_layer.objects if l.type == 'LIGHT'}

            family_obs = (ob for r in roots for ob in family(r))
            for ob in all_layer_objects - set(family_obs) - lights:
                ob.hide_set(True)
        else:
            # Masquer les objets de la famille
            if self.follow_parent:
                family_obs = (ob for r in roots for ob in family_all(r))
            else:
                family_obs = (ob for r in roots for ob in family(r))

            for ob in family_obs:
                ob.hide_set(True)

        return {'FINISHED'}


import bpy

class OBJECT_OT_hide_view_clear_wrapper(bpy.types.Operator):
    """Show Hidden Objects"""
    bl_idname = "object.hide_view_clear_wrapper"  # Identifiant unique de l'opérateur
    bl_label = "Show Hidden Objects"  # Nom de l'opérateur
    bl_options = {'REGISTER', 'UNDO'}  # Options de l'opérateur (enregistrement et annulation)

    # Propriétés de l'opérateur
    select: bpy.props.BoolProperty()  # Propriété pour sélectionner les objets
    active_layer: bpy.props.BoolProperty(default=False, name="Affect only active layer")  # Propriété pour affecter uniquement la couche active

    @classmethod
    def poll(cls, context):
        # Vérifie si l'opérateur peut être exécuté en mode objet
        return context.mode == 'OBJECT'

    def execute(self, context):
        if self.active_layer:
            # Si active_layer est vrai, affecter uniquement la couche active
            for col in context.scene.collection.children:
                if context.object.name in col.all_objects:
                    break

            # Rendre tous les objets de la couche active visibles
            for ob in col.all_objects:
                ob.hide_set(False)
        else:
            # Sinon, utiliser l'opérateur intégré pour rendre tous les objets visibles
            bpy.ops.object.hide_view_clear(select=self.select)

        # Masquer les objets avec ".t" dans leur nom, sauf l'objet actif
        for ob in (o for o in bpy.context.visible_objects if ".t" in o.name and o != context.object):
            if not ob.parent == context.object:
                ob.hide_set(True)
                for child in ob.children:
                    child.hide_set(True)

        # Si l'option enable_group_labels n'est pas activée, mettre à jour la case à cocher du groupe de labels
        if not context.scene.zanatomy.enable_group_labels:
            label_group_checkbox_update()

        return {'FINISHED'}

def get_user_keymap_item(keymap_name, keymap_item_idname, multiple_entries=False):
    """
    Récupère un élément de keymap utilisateur.

    :param keymap_name: Nom du keymap
    :param keymap_item_idname: Identifiant de l'élément de keymap
    :param multiple_entries: Indique si plusieurs entrées doivent être retournées
    :return: Keymap et éléments de keymap correspondants
    """
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.user

    km = kc.keymaps.get(keymap_name)
    if multiple_entries:
        return km, [i[1] for i in km.keymap_items.items() if i[0] == keymap_item_idname]
    else:
        return km, km.keymap_items.get(keymap_item_idname)

def register_keymaps():
    """
    Enregistre les keymaps pour l'add-on.
    """
    kc = bpy.context.window_manager.keyconfigs
    areas = ['Window', 'Text', 'Object Mode', '3D View']

    # Vérifie si tous les keymaps nécessaires sont actifs
    if not all(i in kc.active.keymaps for i in areas):
        bpy.app.timers.register(register_keymaps, first_interval=0.1)
    else:
        # Peut maintenant procéder à la vérification des kmis par défaut
        wm = bpy.context.window_manager
        addon_km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')
import bpy

def register_keymaps():
    """
    Enregistre les keymaps pour l'add-on.
    """
    kc = bpy.context.window_manager.keyconfigs
    areas = ['Window', 'Text', 'Object Mode', '3D View']

    # Vérifie si tous les keymaps nécessaires sont actifs
    if not all(i in kc.active.keymaps for i in areas):
        bpy.app.timers.register(register_keymaps, first_interval=0.1)
    else:
        # Peut maintenant procéder à la vérification des kmis par défaut
        wm = bpy.context.window_manager
        addon_km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')

        ###########
        # H / SHIFT+H / CTRL+SHIFT+H
        ###########
        try:
            # Récupère les éléments de keymap pour 'object.hide_view_set'
            km, kmis = get_user_keymap_item('Object Mode', 'object.hide_view_set', multiple_entries=True)
            for default_kmi in kmis:
                # Crée un nouvel élément de keymap pour l'add-on
                addon_kmi = addon_km.keymap_items.new(OBJECT_OT_hide_wrapper.bl_idname, default_kmi.type, default_kmi.value)
                addon_kmi.map_type = default_kmi.map_type
                if hasattr(addon_kmi, 'repeat'):
                    addon_kmi.repeat = default_kmi.repeat
                addon_kmi.any = default_kmi.any
                addon_kmi.shift = default_kmi.shift
                addon_kmi.ctrl = default_kmi.ctrl
                addon_kmi.alt = default_kmi.alt
                addon_kmi.oskey = default_kmi.oskey
                addon_kmi.key_modifier = default_kmi.key_modifier

                # Copie les propriétés de l'élément de keymap par défaut
                for prop in default_kmi.properties.__dir__():
                    if not (prop.startswith('_') or prop in {'bl_rna', 'rna_type'}):
                        setattr(addon_kmi.properties, prop, getattr(default_kmi.properties, prop))

                addon_kmi.properties.unselected_in_layer = False

                addon_keymaps.append((addon_km, addon_kmi))

            # CTRL+SHIFT+H pour masquer les objets non sélectionnés de la couche active (collection principale)
            addon_kmi = addon_km.keymap_items.new(OBJECT_OT_hide_wrapper.bl_idname, kmis[0].type, kmis[0].value)
            addon_kmi.map_type = "KEYBOARD"
            if hasattr(addon_kmi, 'repeat'):
                addon_kmi.repeat = False
            addon_kmi.any = False
            addon_kmi.shift = True
            addon_kmi.ctrl = True
            addon_kmi.alt = False
            addon_kmi.oskey = False
            addon_kmi.key_modifier = "NONE"
            addon_kmi.properties.unselected = True
            addon_kmi.properties.unselected_in_layer = True
            addon_keymaps.append((addon_km, addon_kmi))

            ###########
            # ALT+H
            ###########

            # Récupère les éléments de keymap pour 'object.hide_view_clear'
            km, kmis = get_user_keymap_item('Object Mode', 'object.hide_view_clear', multiple_entries=True)
            for default_kmi in kmis:
                # Crée un nouvel élément de keymap pour l'add-on
                addon_kmi = addon_km.keymap_items.new(OBJECT_OT_hide_view_clear_wrapper.bl_idname, default_kmi.type, default_kmi.value)
                addon_kmi.map_type = default_kmi.map_type
                if hasattr(addon_kmi, 'repeat'):
                    addon_kmi.repeat = default_kmi.repeat
                addon_kmi.any = default_kmi.any
                addon_kmi.shift = default_kmi.shift
                addon_kmi.ctrl = default_kmi.ctrl
                addon_kmi.alt = default_kmi.alt
                addon_kmi.oskey = default_kmi.oskey
                addon_kmi.key_modifier = default_kmi.key_modifier

                # Copie les propriétés de l'élément de keymap par défaut
                for prop in default_kmi.properties.__dir__():
                    if not (prop.startswith('_') or prop in {'bl_rna', 'rna_type'}):
                        setattr(addon_kmi.properties, prop, getattr(default_kmi.properties, prop))

                addon_kmi.properties.active_layer = False

                addon_keymaps.append((addon_km, addon_kmi))

            ###########
            # CTRL+SHIFT+ALT+H
            ###########
            addon_kmi = addon_km.keymap_items.new(OBJECT_OT_hide_view_clear_wrapper.bl_idname, default_kmi.type, default_kmi.value)
            addon_kmi.map_type = "KEYBOARD"
            if hasattr(addon_kmi, 'repeat'):
                addon_kmi.repeat = False
            addon_kmi.any = False
            addon_kmi.shift = True
            addon_kmi.ctrl = False
            addon_kmi.alt = True
            addon_kmi.oskey = False
            addon_kmi.key_modifier = "NONE"
            addon_kmi.properties.active_layer = True
            addon_keymaps.append((addon_km, addon_kmi))

            ###########
            # Local view with lights
            ###########
            km, kmis = get_user_keymap_item('3D View', 'view3d.localview', multiple_entries=True)
            for default_kmi in kmis:
                # Crée un nouvel élément de keymap pour l'add-on
                addon_kmi = addon_km.keymap_items.new(OBJECT_OT_local_view_wrapper.bl_idname, default_kmi.type, default_kmi.value)
                addon_kmi.map_type = default_kmi.map_type
                addon_kmi.repeat = default_kmi.repeat
                addon_kmi.any = default_kmi.any
                addon_kmi.shift = default_kmi.shift
                addon_kmi.ctrl = default_kmi.ctrl
                addon_kmi.alt = default_kmi.alt
                addon_kmi.oskey = default_kmi.oskey
                addon_kmi.key_modifier = default_kmi.key_modifier

                # Copie les propriétés de l'élément de keymap par défaut
                for prop in default_kmi.properties.__dir__():
                    if not (prop.startswith('_') or prop in {'bl_rna', 'rna_type'}):
                        setattr(addon_kmi.properties, prop, getattr(default_kmi.properties, prop))

                addon_keymaps.append((addon_km, addon_kmi))
        except Exception as e:
            print(f"Error registering keymaps: {e}")

# Liste pour stocker les keymaps de l'add-on
addon_keymaps = []

# Fonction pour récupérer un élément de keymap utilisateur
def get_user_keymap_item(keymap_name, keymap_item_idname, multiple_entries=False):
    """
    Récupère un élément de keymap utilisateur.

    :param keymap_name: Nom du keymap
    :param keymap_item_idname: Identifiant de l'élément de keymap
    :param multiple_entries: Indique si plusieurs entrées doivent être retournées
    :return: Keymap et éléments de keymap correspondants
    """
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.user

    km = kc.keymaps.get(keymap_name)
    if multiple_entries:
        return km, [i[1] for i in km.keymap_items.items() if i[0] == keymap_item_idname]
    else:
        return km, km.keymap_items.get(keymap_item_idname)


import bpy

addon_keymaps = []

def add_shortkeys():
    """
    Ajoute les raccourcis clavier pour l'add-on.
    """
    register_keymaps()

def remove_shortkeys():
    """
    Supprime les raccourcis clavier pour l'add-on.
    """
    wm = bpy.context.window_manager
    for km, kmi in addon_keymaps:
        try:
            km.keymap_items.remove(kmi)
        except:
            # Je ne comprends pas cette erreur mais elle ne semble pas importante.
            pass

    addon_keymaps.clear()

def register_keymaps():
    """
    Enregistre les keymaps pour l'add-on.
    """
    wm = bpy.context.window_manager

    try:
        ###########
        # Add Label
        ###########
        # Crée un nouveau keymap pour le mode objet
        addon_km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')
        # Ajoute un nouvel élément de keymap pour ajouter un label
        kmi = addon_km.keymap_items.new(OBJECT_OT_make_label.bl_idname, 'FIVE', 'PRESS', shift=True, ctrl=True, alt=False)
        kmi.active = True
        addon_keymaps.append((addon_km, kmi))

        # Crée un nouveau keymap pour le mode mesh
        addon_km = wm.keyconfigs.addon.keymaps.new(name='Mesh', space_type='EMPTY')
        # Ajoute un nouvel élément de keymap pour ajouter un label
        kmi = addon_km.keymap_items.new(OBJECT_OT_make_label.bl_idname, 'FIVE', 'PRESS', shift=True, ctrl=True, alt=False)
        kmi.active = True
        addon_keymaps.append((addon_km, kmi))

        ###########
        # Label transform to delta
        ###########
        # Crée un nouveau keymap pour le mode objet
        addon_km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')
        # Ajoute un nouvel élément de keymap pour convertir les transformations de label en delta
        kmi = addon_km.keymap_items.new(OBJECT_OT_label_delta.bl_idname, 'FIVE', 'PRESS', shift=True, ctrl=True, alt=True)
        kmi.active = True
        addon_keymaps.append((addon_km, kmi))

        ###########
        # Change Label
        ###########
        # Crée un nouveau keymap pour le mode objet
        addon_km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')
        # Ajoute un nouvel élément de keymap pour changer le label
        kmi = addon_km.keymap_items.new(OBJECT_OT_change_label_wrapper.bl_idname, 'F2', 'PRESS', shift=False, ctrl=False, alt=False)
        kmi.active = True
        addon_keymaps.append((addon_km, kmi))

        ###########
        # Download Wiki Texts
        ###########
        # Ajoute un nouvel élément de keymap pour télécharger les textes du wiki
        kmi = addon_km.keymap_items.new(TEXT_OT_wiki_download.bl_idname, 'ZERO', 'PRESS', shift=True, ctrl=True, alt=False)
        kmi.active = True
        addon_keymaps.append((addon_km, kmi))

        ###########
        # Muscle Key Color
        ###########
        # Ajoute un nouvel élément de keymap pour changer la couleur de la clé de muscle
        kmi = addon_km.keymap_items.new(OBJECT_OT_muscle_key_color.bl_idname, 'Z', 'PRESS', shift=True, ctrl=False, alt=True)
        kmi.active = True
        addon_keymaps.append((addon_km, kmi))

        ###########
        # Select Hierarchy
        ###########
        # Ajoute un nouvel élément de keymap pour sélectionner la hiérarchie
        kmi = addon_km.keymap_items.new(OBJECT_OT_select_parent_children.bl_idname, 'DOWN_ARROW', 'PRESS', shift=False, ctrl=False, alt=False)
        kmi.active = True
        addon_keymaps.append((addon_km, kmi))
    except Exception as e:
        print("Exception during keystroke registering... Trying again.", e)
        bpy.app.timers.register(register_keymaps, first_interval=0.1)

class OBJECT_OT_label_delta(bpy.types.Operator):
    """Convert label transforms to delta"""
    bl_idname = "object.label_transforms_delta"
    bl_label = "Label's transforms to delta"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        # Vérifie si l'opérateur peut être exécuté
        return context.mode == 'OBJECT' and context.object is not None and context.object.name.endswith('.t')

    def execute(self, context):
        # Convertit les transformations de label en delta
        label = context.object
        label.delta_location = label.delta_location + label.location
        label.delta_scale = label.delta_scale * label.scale
        label.location = (0,0,0)
        label.scale = (1,1,1)

        line = label.children[0]
        line.scale = (1,1,1)

        return {"FINISHED"}

class OBJECT_OT_select_parent_children(bpy.types.Operator):
    """Select parent and all grand children"""
    bl_idname = "object.select_parent_children"
    bl_label = "Select Hierarchy"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        # Vérifie si l'opérateur peut être exécuté
        return context.mode == 'OBJECT' and context.object is not None

    def execute(self, context):
        # Sélectionne le parent et tous les enfants récursivement
        bpy.ops.object.select_grouped('INVOKE_DEFAULT', type='PARENT')
        bpy.ops.object.select_grouped('INVOKE_DEFAULT', type='CHILDREN_RECURSIVE')
        return {"FINISHED"}

class OBJECT_OT_sync_visibility(bpy.types.Operator):
    """Sync render and viewport visibility"""
    bl_idname = "object.sync_visibility"
    bl_label = "Sync Visibility"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        # Vérifie si l'opérateur peut être exécuté
        return context.mode == 'OBJECT'

    def execute(self, context):
        # Synchronise la visibilité de rendu et de la vue 3D
        for o in context.scene.objects:
            if o.hide_render == o.visible_get():
                o.hide_render = not o.visible_get()
        return {"FINISHED"}
import bpy

class OBJECT_OT_change_label_wrapper(bpy.types.Operator):
    """Change label\n 1.Select label"""
    bl_idname = "object.change_label"  # Identifiant unique de l'opérateur
    bl_label = "Change Label"  # Nom de l'opérateur
    bl_options = {'REGISTER', 'UNDO'}  # Options de l'opérateur (enregistrement et annulation)

    custom_label: bpy.props.StringProperty(default="Custom Label", name="New Label")  # Propriété pour le nouveau label

    @classmethod
    def poll(cls, context):
        # Vérifie si l'opérateur peut être exécuté en mode objet et si l'objet sélectionné est un label
        return context.mode == 'OBJECT' and context.object is not None and ".t" in context.object.name

    def execute(self, context):
        # Change le label de l'objet sélectionné
        font_object = context.object
        line_object = context.object.children[0]

        # Met à jour le nom et le contenu du texte de l'objet de police
        font_object.name = font_object.data.name = f"{self.custom_label}.t"
        font_object.data.body = self.custom_label.upper()

        # Met à jour le nom de l'objet de ligne
        line_object.name = line_object.data.name = f"{self.custom_label}-line"

        return {"FINISHED"}

    def invoke(self, context, event):
        # Affiche une boîte de dialogue pour entrer le nouveau label
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

class OBJECT_OT_local_view_wrapper(bpy.types.Operator):
    """Local view (with lights)"""
    bl_idname = "view3d.localview_lights"  # Identifiant unique de l'opérateur
    bl_label = "Local View (w/ lights)"  # Nom de l'opérateur
    # bl_options = {'REGISTER', 'UNDO'}

    frame_selected: bpy.props.BoolProperty(default=True, name="Frame Selected")  # Propriété pour encadrer les objets sélectionnés

    @classmethod
    def poll(cls, context):
        # Vérifie si l'opérateur peut être exécuté en mode objet et si un objet est sélectionné
        return context.mode == 'OBJECT' and context.object is not None

    def execute(self, context):
        def findRoot(ob):
            # Trouve la racine d'un objet en remontant la hiérarchie des parents
            while ob and ob.parent:
                if ob in objects_to:
                    objects_to.remove(ob)
                if not any(x in ob.name for x in label_elements):
                    return ob
                if not ob.parent.parent:
                    return ob
                ob = ob.parent
            return ob

        roots = []  # Liste pour stocker les racines des objets
        objects_to = set(context.selected_objects)  # Ensemble des objets sélectionnés
        selected_objects = list(objects_to)  # Liste des objets sélectionnés
        while objects_to:
            ob = objects_to.pop()
            roots.append(findRoot(ob))

        lights = [o for o in context.visible_objects if o.type == 'LIGHT']  # Liste des lumières visibles
        hide_selects = []  # Liste des objets avec hide_select activé
        hidden = []  # Liste des objets masqués
        obj_family = []  # Liste des objets de la famille
        for obj in roots:
            obj_family += list(family(obj))
        obj_family += lights
        print(obj_family)

        # Rendre tous les objets de la famille visibles et sélectionnables
        for ob in obj_family:
            if ob.hide_get():
                ob.hide_set(False)
                hidden.append(ob)
            if ob.hide_select:
                ob.hide_select = False
                hide_selects.append(ob)
            ob.select_set(True)

        # Activer la vue locale
        bpy.ops.view3d.localview('INVOKE_DEFAULT', frame_selected=self.frame_selected)

        # Restaurer l'état des objets
        for ob in obj_family:
            ob.select_set(False)
        obj.select_set(True)
        for ob in hide_selects:
            ob.hide_select = True
        for ob in hidden:
            ob.hide_set(True)

        # Sélectionner les objets d'origine
        for ob in selected_objects:
            ob.select_set(True)
        bpy.ops.view3d.view_selected()

        return {"FINISHED"}
import bpy

# Fonction pour nettoyer les noms en enlevant les suffixes spécifiques
def clean_name(name):
    for ending in ('.r', '.l', '.t', '.st', '.r.t', '.l.t', '.r-line', '.l-line', '.g', '-line', '.o', '.e', ''):
        if ending == '':
            return name, ending
        elif name.endswith(ending):
            clean_name = name[:-len(ending)]
            return clean_name, ending

# Dictionnaire des polices pour différentes langues
fonts = {
    'English': 'Bfont',
    'Latin': 'Bfont',
    'Français': 'Bfont',
    'Español': 'Bfont',
    'Portugues': 'Bfont',
    'Nederlands': 'Bfont',
    'Deutsch': 'Bfont',
    'Polski': 'Bfont',
    '中國人': 'YuMincho-Regular',
}

# Fonction pour obtenir les n premiers octets d'une chaîne de caractères
def first_n_bytes(string, n=63):
    byte_length = 0
    out = ''
    for char in string:
        byte_length += len(char.encode())
        if byte_length <= n:
            out += char
        else:
            return out
    return out

class OBJECT_OT_translate_atlas(bpy.types.Operator):
    """Translate atlas"""
    bl_idname = "object.translate_atlas"  # Identifiant unique de l'opérateur
    bl_label = "Translate"  # Nom de l'opérateur
    bl_options = {'REGISTER', 'UNDO'}  # Options de l'opérateur (enregistrement et annulation)

    lang: bpy.props.EnumProperty(items=[
        ('ID', 'ID', '', 0),
        ('English', 'English', '', 1),
        ],
        default='ID',
        name="Language")  # Propriété pour sélectionner la langue

    def execute(self, context):
        if self.lang == "ID":
            # Si la langue est "ID", réinitialiser les noms en anglais
            for ob in bpy.data.objects[:]:
                if ob.type in {"MESH", "CURVE"}:
                    _, ending = clean_name(ob.name)
                    eng_name, _ = clean_name(ob.data.name)
                    ob.name = eng_name + ending
                elif ob.type == "FONT":
                    ob.name = ob.data.name
                    ob.data.body = clean_name(ob.data.name)[0].upper()
                    ob.data.font = bpy.data.fonts['Bfont']
                    if not ob.name.endswith('.st'):
                        ob.data.size = 0.003

            for col in bpy.data.collections[:]:
                if 'ID' in col.keys():
                    col.name = col['English']
            return {"FINISHED"}

        # Charger les traductions depuis un texte Blender
        translations = bpy.data.texts['Translations'].as_string().splitlines()
        languages = translations[0].split(';')
        trans_dict = dict()
        for langs in translations[1:]:
            langs = list(zip(languages, langs.split(';')))
            translated_phrase = trans_dict[langs[0][1]] = dict()
            for lang in langs[1:]:
                translated_phrase[lang[0]] = lang[1]

        # Traduire les noms des objets et des collections
        for ob in bpy.data.objects[:]:
            if ob.type in {"MESH", "CURVE"}:
                _, ending = clean_name(ob.name)
                eng_name, _ = clean_name(ob.data.name)
                if eng_name in trans_dict:
                    new_name = trans_dict[eng_name][self.lang]
                    new_name = first_n_bytes(new_name)
                    ob.name = new_name + ending
            elif ob.type == "FONT":
                _, ending = clean_name(ob.name)
                eng_name, _ = clean_name(ob.data.name)
                if eng_name in trans_dict:
                    new_name = trans_dict[eng_name][self.lang]
                    ob.data.body = new_name.upper()

                    new_name = first_n_bytes(new_name)
                    ob.name = new_name + ending

                    try:
                        ob.data.font = bpy.data.fonts[fonts[self.lang]]
                    except:
                        self.report(type={"WARNING"}, message=f"Font {fonts[self.lang]} not found. Add it manually.")

                    if not ob.name.endswith('.st'):
                        if self.lang == '中國人':
                            ob.data.size = 0.006
                        else:
                            ob.data.size = 0.003

        for col in bpy.data.collections[:]:
            if 'ID' in col.keys():
                eng_name = col['English']
                if eng_name.endswith("'"):
                    eng_name = eng_name[:-1]
                    if eng_name in trans_dict:
                        col.name = trans_dict[eng_name][self.lang] + "'"
                elif eng_name in trans_dict:
                    col.name = trans_dict[eng_name][self.lang]

        return {"FINISHED"}

    
import bpy
from mathutils import Vector
import mathutils
from bpy_extras.object_utils import object_data_add

class OBJECT_OT_make_label(bpy.types.Operator):
    """Make label\n 1.Select vertex in Edit Mode\n 2. Open text in Text Editor"""
    bl_idname = "object.make_label"  # Identifiant unique de l'opérateur
    bl_label = "Make Label"  # Nom de l'opérateur
    bl_options = {'REGISTER', 'UNDO'}  # Options de l'opérateur (enregistrement et annulation)

    use_custom_label: bpy.props.BoolProperty(default=False, name="Use custom property")  # Propriété pour utiliser un label personnalisé
    custom_label: bpy.props.StringProperty(default="Custom Label")  # Propriété pour le label personnalisé

    @classmethod
    def poll(cls, context):
        # Vérifie si l'opérateur peut être exécuté en mode édition de maillage ou en mode objet et si un objet est sélectionné
        return context.mode in {'EDIT_MESH', 'OBJECT'} and context.object is not None

    def invoke(self, context, event):
        # Affiche une boîte de dialogue pour entrer le label personnalisé
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):
        # Options pour le label
        font_radius = 0.003  # Taille de la police
        font_x_align = 'CENTER'  # Alignement horizontal du texte
        line_offset = 0.0015  # Distance entre le label et la ligne

        # Passer en mode objet
        bpy.ops.object.mode_set(mode='OBJECT')

        # Vérifier qu'un seul vertex est sélectionné
        selected_verts = [v for v in context.object.data.vertices if v.select]
        if len(selected_verts) != 1:
            self.report(type={"ERROR"}, message="Select one vertex.")
            return {"CANCELLED"}

        active_object = context.object

        # Coordonnées du vertex sélectionné
        vert_co = active_object.matrix_world @ Vector(selected_verts[0].co)
        text_co = vert_co.copy()
        text_co.z += 0.05

        line_end_co = vert_co.copy()

        # Nom du texte
        text_name = self.custom_label
        if not self.use_custom_label:
            for area in bpy.context.screen.areas:
                if area.type == 'TEXT_EDITOR':
                    for space in area.spaces:
                        if space.type == 'TEXT_EDITOR':
                            text_name = space.text.name

        # Ajouter un objet texte
        bpy.ops.object.text_add(radius=font_radius, enter_editmode=False, align='WORLD', location=text_co, rotation=(1.5708, 0, 0), scale=(1, 1, 1))
        font_object = context.object
        font_object.name = f"{text_name}.t"
        font_object.data.name = font_object.name
        font_object.data.body = text_name.upper()
        font_object.data.align_x = font_x_align
        try:
            font_object.data.font = bpy.data.fonts["DejaVuSansCondensed"]
        except:
            self.report(type={"WARNING"}, message="Font DejaVuSansCondensed not found. Add it manually.")

        # Obtenir ou créer un matériau pour le texte
        mat = bpy.data.materials.get("Text")
        if mat is None:
            mat = bpy.data.materials.new(name="Text")

        # Assigner le matériau à l'objet texte
        font_object.data.materials.append(mat)

        # Délier l'objet texte de la collection active
        context.collection.objects.unlink(font_object)
        try:
            for col in active_object.users_collection:
                col.objects.link(font_object)
        except:
            pass

        # Créer un maillage pour la ligne
        verts = [text_co - Vector((0, 0, line_offset)), line_end_co]
        edges = [[0, 1]]
        faces = []
        mesh = bpy.data.meshes.new(name=f"{text_name}-line")
        mesh.from_pydata(verts, edges, faces)

        # Sauvegarder la position du curseur
        old_cursor_loc = context.scene.cursor.location.copy()
        context.scene.cursor.location = (0, 0, 0)
        line_object = object_data_add(context, mesh)
        context.scene.cursor.location = old_cursor_loc
        line_object.hide_select = True
        line_object.show_wire = True

        # Délier l'objet ligne de la collection active
        context.collection.objects.unlink(line_object)
        try:
            for col in active_object.users_collection:
                col.objects.link(line_object)
        except:
            pass

        # Transformer l'origine de la ligne
        line_object.data.transform(mathutils.Matrix.Translation(-text_co))
        line_object.matrix_world.translation += text_co

        # Définir l'inverse de la matrice parente (ligne <- font)
        line_object.parent = font_object
        line_object.matrix_parent_inverse = font_object.matrix_world.inverted()

        # Définir l'inverse de la matrice parente (font <- element)
        font_object.parent = active_object
        font_object.matrix_parent_inverse = active_object.matrix_world.inverted()

        font_object.delta_location = font_object.delta_location + font_object.location
        font_object.location = (0, 0, 0)

        # Ajouter un modificateur Hook
        hm = line_object.modifiers.new(name="Hook", type='HOOK')
        hm.object = active_object
        hm.vertex_indices_set([1])

        # Activer l'objet texte et le sélectionner
        context.view_layer.objects.active = font_object
        font_object.select_set(True)
        font_object.hide_set(False)

        return {"FINISHED"}
class TEXT_OT_wiki_download(bpy.types.Operator):
    """Wiki download"""
    bl_idname = "text.wiki_download"  # Identifiant unique de l'opérateur
    bl_label = "Download Texts From Wiki"  # Nom de l'opérateur
    bl_options = {'REGISTER'}  # Options de l'opérateur (enregistrement)

    def execute(self, context):
        # 0. Préparer la liste des phrases
        if "Wiki Phrases" not in bpy.data.texts:
            self.report(type={"ERROR"}, message="Create 'Wiki Phrases' text file.")
            return {"CANCELLED"}

        phrases = bpy.data.texts["Wiki Phrases"].as_string().splitlines()
        not_matched = []
        partial_matches = []
        full_matches = []

        for i, possible_title in enumerate(phrases):
            print(f"Extract {i+1}/{len(phrases)}, " + possible_title)

            # 1. Recherche
            search_url = f"https://en.wikipedia.org/w/api.php?action=query&format=json&prop=&list=search&continue=-%7C%7Clanglinks&srsearch={urllib.parse.quote_plus(possible_title)}&srnamespace=0&srlimit=1&srinfo=&srprop="
            resp = requests.get(search_url).json()

            # 2. Comparer les titres
            try:
                if len(resp['query']['search']) == 0:
                    print(' ##### Object not matched:', possible_title)
                    not_matched.append(possible_title)
                    continue
                title = resp['query']['search'][0]['title']
            except Exception as e:
                print(e)
                print(json.dumps(resp, indent=2))
                continue

            diff = len(set(title.lower()) ^ set(possible_title.lower()))

            if diff > 3:
                print(' ##### Object not matched:', possible_title)
                not_matched.append(possible_title)
                continue
            elif title.lower() != possible_title.lower():
                print(f' +++++ Object partial match ({diff}):', possible_title)
                partial_matches.append(possible_title)

            # 3. Obtenir l'extrait
            extract_url = f"https://en.wikipedia.org/w/api.php?action=query&format=json&titles={urllib.parse.quote_plus(title)}&prop=extracts|info&explaintext&inprop=url"
            resp = requests.get(extract_url).json()
            wiki_page = resp['query']['pages'].popitem()[1]
            extract = wiki_page['extract']
            wiki_url = wiki_page['canonicalurl']

            if extract.startswith(f"{title} may refer to:"):
                print(' ????? Object not matched (multi-results page):', possible_title)
                not_matched.append(possible_title)
                continue
            full_matches.append(possible_title)

            # Créer ou mettre à jour le texte dans Blender
            if title in bpy.data.texts:
                text_edit = bpy.data.texts[title]
                text_edit.clear()
            else:
                text_edit = bpy.data.texts.new(title)

            # Supprimer le contenu indésirable
            extract += '\n'*3
            for paragraph in ("== Additional images ==", "== See also ==", "== References ==", "== External links =="):
                extract = re.sub(rf'{paragraph}\n+.*?\n\n\n', '', extract, flags=re.MULTILINE|re.DOTALL)

            extract = re.sub(r'( ==\n)(.?)', r'\1\n\2', extract, flags=re.MULTILINE)
            extract = re.sub(r'( ===\n)(.?)', r'\1\n\2', extract, flags=re.MULTILINE)
            extract = re.sub(r'  ', r' ', extract)
            extract = re.sub(r'(\. )([A-Z])', r'\1\n\n\2', extract)
            extract = re.sub(r' \[Fig\. \d+\]', r'', extract)

            body = "\n"*2 + title.upper() + "\n"*3 + extract + "\n" + wiki_url
            text_edit.write(body)
            text_edit.cursor_set(0)

        # Créer ou mettre à jour le rapport de résultats
        if 'Wiki Results' in bpy.data.texts:
            wiki_results = bpy.data.texts['Wiki Results']
            wiki_results.clear()
        else:
            wiki_results = bpy.data.texts.new('Wiki Results')

        body = "===== Wiki download report =====\n"
        body += " ## Partial matches (check manually) ##\n"
        body += "\n".join(partial_matches) + "\n"*5
        body += " ## Not matched ##\n"
        body += "\n".join(not_matched) + "\n"*5
        body += " ## Fully matched ##\n"
        body += "\n".join(full_matches) + "\n"*5
        wiki_results.write(body)
        wiki_results.cursor_set(0)

        return {"FINISHED"}


# Fonction persistante pour suivre la vue 3D
@persistent
def z_anatomy_load_post(scene=None):
    def refresh():
        # Parcourir toutes les zones de l'écran pour trouver les zones de vue 3D
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                area3D = area
                viewport_orientation = area3D.spaces[0].region_3d.view_rotation

                # Parcourir tous les objets visibles
                for obj in bpy.context.visible_objects:
                    # Vérifier si l'objet a un suffixe spécifique ou se termine par '...'
                    if '.t' in obj.name or obj.name.endswith('...'):
                        # Si la rotation de l'objet ne correspond pas à l'orientation de la vue, la mettre à jour
                        if obj.rotation_quaternion != viewport_orientation:
                            if obj.rotation_mode != 'QUATERNION':
                                obj.rotation_mode = 'QUATERNION'
                            obj.rotation_quaternion = viewport_orientation

                    # Si l'objet a 'always_show' dans son nom et est masqué, le rendre visible
                    if 'always_show' in obj.name and obj.hide_get():
                        obj.hide_set(False)
                        obj.hide_viewport = False
        return 0.0165

    # Enregistrer la fonction de rafraîchissement pour qu'elle soit appelée périodiquement
    bpy.app.timers.register(refresh, first_interval=0.01)

    # S'abonner aux messages RNA pour les changements d'objets actifs et d'espaces de travail
    bpy.msgbus.subscribe_rna(
        key=subscribe_to,
        owner=owner,
        args=(),
        notify=msgbus_callback,
    )

    bpy.msgbus.subscribe_rna(
        key=(bpy.types.Window, "workspace"),
        owner=owner,
        args=(),
        notify=msgbus_callback_workspace,
    )

    # Utiliser un timer pour obtenir le contexte correct après l'enregistrement
    bpy.app.timers.register(only_once, first_interval=0.01)

layer_collections = []
def only_once():
    # Initialiser les vues stockées si disponible
    if bpy.ops.view3d.stored_views_initialize.poll():
        bpy.ops.view3d.stored_views_initialize()

    # Définir la couleur des muscles pour tous les objets de type MESH
    for ob in [c for col in bpy.data.collections for c in col.all_objects if c.type == 'MESH']:
        ob['muscle_color'] = bpy.context.scene.zanatomy.muscle_color

    # Layers pour la version lite
    blend_path = bpy.data.filepath
    blend_name = bpy.path.basename(blend_path)
    main_blend = os.path.join(os.path.dirname(blend_path), 'Z-Anatomy.blend')
    global layer_collections
    if blend_name == 'Z-Anatomy-lite.blend':
        layer_collections = ['Skeletal system', 'Muscular insertions', 'Joints', 'Muscular system', 'Cardiovascular system', 'Nervous system & Sense organs', 'Visceral systems', 'Regions of human body', 'Reference lines, planes & movements']
        with bpy.data.libraries.load(main_blend) as (data_from, data_to):
            files = [{'name': txt_name} for txt_name in data_from.texts if txt_name != "z-anatomy.py"]
        bpy.ops.wm.append(directory=main_blend+"/Text/", files=files, do_reuse_local_id=True, link=True)

# Fonction pour synchroniser la sélection avec l'éditeur de texte
def msgbus_callback_workspace(*args):
    workspace = bpy.context.workspace
    if workspace.name == "Biomechanics":
        bpy.context.window.view_layer = bpy.data.scenes['Scene'].view_layers["Biomechanics"]
        bpy.context.view_layer.objects.active = bpy.data.objects['Armature']
        bpy.ops.object.mode_set(mode='POSE')
    elif workspace.name == "Anatomy":
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.window.view_layer = bpy.data.scenes['Scene'].view_layers["Anatomy"]

# Fonction pour mettre à jour la visibilité des labels de groupe
def label_group_checkbox_update(*args):
    active_object = bpy.context.active_object

    if not bpy.context.scene.zanatomy.enable_group_labels:
        for ob in (c for c in bpy.context.scene.objects if c.name.endswith('.g') or (c.name.endswith('-line') and c.parent and c.parent.name.endswith('.g'))):
            ob.hide_set(True)
    else:
        for ob in (o for o in set(bpy.context.scene.objects) - set(active_object.users_collection[0].all_objects) if o.name.endswith('.g')):
            ob.hide_set(True)

            for child in (c for c in bpy.context.scene.objects if c.parent == ob and c.name.endswith('-line')):
                child.hide_set(True)

        for ob in (o for o in active_object.users_collection[0].all_objects if not o.visible_get() and o.name.endswith('.g')):
            ob.hide_set(False)

            for child in (c for c in bpy.context.scene.objects if c.parent == ob and not c.visible_get() and c.name.endswith('-line')):
                child.hide_set(False)

# Fonction pour synchroniser la sélection avec l'éditeur de texte
def msgbus_callback(*args):
    active_object = bpy.context.active_object
    if not active_object or not active_object.data: return

    basename, _ = clean_name(active_object.data.name)
    text_editor_area = None
    for area in bpy.context.screen.areas:
        if area.type == "TEXT_EDITOR":
            text_editor_area = area
            break

    if text_editor_area and basename in bpy.data.texts:
        text_editor_area.spaces[0].text = bpy.data.texts[basename]
        text_editor_area.spaces[0].top = 0
        text_editor_area.spaces[0].text.select_set(0, 0, 0, 0)

    # Seulement le label de l'objet visible doit être visible
    if ".t" in active_object.name or ".st" in active_object.name:
        return

    for child in family(active_object):
        child.hide_set(False)

    if not bpy.context.scene.zanatomy.enable_group_labels or active_object.users_collection[0] is bpy.context.view_layer.layer_collection.collection:
        for ob in (c for c in bpy.context.visible_objects if c.name.endswith('.g') or (c.name.endswith('-line') and c.parent and c.parent.name.endswith('.g'))):
            ob.hide_set(True)
    else:
        for ob in (o for o in set(bpy.context.visible_objects) - set(active_object.users_collection[0].all_objects) if o.name.endswith('.g')):
            ob.hide_set(True)

            for child in (c for c in bpy.context.visible_objects if c.parent == ob and c.name.endswith('-line')):
                child.hide_set(True)

        for ob in (o for o in active_object.users_collection[0].all_objects if not o.visible_get() and o.name.endswith('.g')):
            ob.hide_set(False)

            for child in (c for c in bpy.context.scene.objects if c.parent == ob and not c.visible_get() and c.name.endswith('-line')):
                child.hide_set(False)

    for ob in (o for o in bpy.context.visible_objects if ".t" in o.name):
        if not ob.parent == active_object:
            ob.hide_set(True)
            for child in ob.children:
                child.hide_set(True)

    for ob in (o for o in bpy.context.visible_objects if o.name.endswith('...')):
        if ob == active_object:
            for child in ob.children:
                child.hide_set(False)
        else:
            for child in ob.children:
                child.hide_set(True)

    if active_object.name.endswith('.g'):
        bpy.ops.object.select_grouped('INVOKE_DEFAULT', type='CHILDREN_RECURSIVE')
        active_object.select_set(True)

subscribe_to = bpy.types.LayerObjects, "active"
owner = object()

# Panneau pour sélectionner la langue
class ZANATOMY_PT_languages(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = 'Languages'
    bl_context = 'objectmode'
    bl_category = 'Z-Anatomy'

    def draw(self, context):
        layout = self.layout
        layout.operator("object.translate_atlas")

# Panneau pour activer ou désactiver les labels de groupe
class ZANATOMY_PT_labels(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = 'Labels'
    bl_context = 'objectmode'
    bl_category = 'Z-Anatomy'

    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene.zanatomy, "enable_group_labels")

# Panneau pour activer ou désactiver les sections transversales
class ZANATOMY_PT_Xsection(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = 'Cross section'
    bl_context = 'objectmode'
    bl_category = 'Z-Anatomy'

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.label(text="Active:")

        obj = context.object
        if obj and 'Cross-section-X' in obj:
            box = col.box()
            sub = box.grid_flow(row_major=True, columns=3, align=True)
            emboss, depress = (True, True) if obj['Cross-section-X'] else (True, False)
            op = sub.operator("object.cross_section", emboss=emboss, depress=depress, text='X')
            op.axis = 'X'
            op.enable = not obj['Cross-section-X']

            emboss, depress = (True, True) if obj['Cross-section-Y'] else (True, False)
            op = sub.operator("object.cross_section", emboss=emboss, depress=depress, text='Y')
            op.axis = 'Y'
            op.enable = not obj['Cross-section-Y']

            emboss, depress = (True, True) if obj['Cross-section-Z'] else (True, False)
            op = sub.operator("object.cross_section", emboss=emboss, depress=depress, text='Z')
            op.axis = 'Z'
            op.enable = not obj['Cross-section-Z']

            emboss, depress = (True, True) if obj['Cross-section-X-inverse'] else (True, False)
            op = sub.operator("object.cross_section", emboss=emboss, depress=depress, text='', icon='ARROW_LEFTRIGHT')
            op.axis = 'X'
            op.enable = obj['Cross-section-X']
            op.invert = not obj['Cross-section-X-inverse']

            emboss, depress = (True, True) if obj['Cross-section-Y-inverse'] else (True, False)
            op = sub.operator("object.cross_section", emboss=emboss, depress=depress, text='', icon='ARROW_LEFTRIGHT')
            op.axis = 'Y'
            op.enable = obj['Cross-section-Y']
            op.invert = not obj['Cross-section-Y-inverse']

            emboss, depress = (True, True) if obj['Cross-section-Z-inverse'] else (True, False)
            op = sub.operator("object.cross_section", emboss=emboss, depress=depress, text='', icon='ARROW_LEFTRIGHT')
            op.axis = 'Z'
            op.enable = obj['Cross-section-Z']
            op.invert = not obj['Cross-section-Z-inverse']

        col = layout.column(align=True)
        col.label(text="Layers:")
        for collection in (c for c in bpy.data.collections if 'Cross-section-X' in c):
            row = col.split(factor=0.5, align=True)
            row.label(text=collection.name)
            box = row.box()

            sub = box.grid_flow(row_major=True, columns=3, align=True)
            emboss, depress = (True, True) if collection['Cross-section-X'] else (True, False)
            op = sub.operator("collection.cross_section", emboss=emboss, depress=depress, text='X')
            op.collection_name = collection.name
            op.axis = 'X'
            op.enable = not collection['Cross-section-X']

            emboss, depress = (True, True) if collection['Cross-section-Y'] else (True, False)
            op = sub.operator("collection.cross_section", emboss=emboss, depress=depress, text='Y')
            op.collection_name = collection.name
            op.axis = 'Y'
            op.enable = not collection['Cross-section-Y']

            emboss, depress = (True, True) if collection['Cross-section-Z'] else (True, False)
            op = sub.operator("collection.cross_section", emboss=emboss, depress=depress, text='Z')
            op.collection_name = collection.name
            op.axis = 'Z'
            op.enable = not collection['Cross-section-Z']

            emboss, depress = (True, True) if collection['Cross-section-X-inverse'] else (True, False)
            op = sub.operator("collection.cross_section", emboss=emboss, depress=depress, text='', icon='ARROW_LEFTRIGHT')
            op.collection_name = collection.name
            op.axis = 'X'
            op.enable = collection['Cross-section-X']
            op.invert = not collection['Cross-section-X-inverse']

            emboss, depress = (True, True) if collection['Cross-section-Y-inverse'] else (True, False)
            op = sub.operator("collection.cross_section", emboss=emboss, depress=depress, text='', icon='ARROW_LEFTRIGHT')
            op.collection_name = collection.name
            op.axis = 'Y'
            op.enable = collection['Cross-section-Y']
            op.invert = not collection['Cross-section-Y-inverse']

            emboss, depress = (True, True) if collection['Cross-section-Z-inverse'] else (True, False)
            op = sub.operator("collection.cross_section", emboss=emboss, depress=depress, text='', icon='ARROW_LEFTRIGHT')
            op.collection_name = collection.name
            op.axis = 'Z'
            op.enable = collection['Cross-section-Z']
            op.invert = not collection['Cross-section-Z-inverse']

# Panneau pour activer ou désactiver la couleur clé des muscles
class ZANATOMY_PT_Muscle_Color(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = 'Muscular system'
    bl_context = 'objectmode'
    bl_category = 'Z-Anatomy'

    def draw(self, context):
        layout = self.layout

        if '4:Muscular system' in bpy.data.collections:
            layout.prop(context.scene.zanatomy, "muscle_color")

import os
# Panneau pour gérer la visibilité des couches
class ZANATOMY_PT_Visibility(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = 'Visibility'
    bl_context = 'objectmode'
    bl_category = 'Z-Anatomy'

    def draw(self, context):
        layout = self.layout
        layout.operator(OBJECT_OT_sync_visibility.bl_idname)

        global layer_collections
        layout.separator()
        col = layout.column(align=True)
        for collection in layer_collections:
            if collection not in context.scene.collection.children:
                col.operator('layer.append_layer', text=collection).collection = collection
            else:
                col.operator('layer.remove_layer', text=collection, depress=True).collection = collection

# Fonction pour développer ou réduire les éléments dans l'outliner
def toggle_expand(context, state):
    area = next(a for a in context.screen.areas if a.type == 'OUTLINER')
    bpy.ops.outliner.show_hierarchy({'area': area}, 'INVOKE_DEFAULT')
    for i in range(state):
        bpy.ops.outliner.expanded_toggle({'area': area})
    area.tag_redraw()

# Opérateur pour ajouter une couche d'anatomie
class LAYERS_OT_add_layer(bpy.types.Operator):
    """Append anatomy layer"""
    bl_idname = "layer.append_layer"
    bl_label = "Append Layer"
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    collection: bpy.props.StringProperty()

    def execute(self, context):
        main_blend = os.path.join(os.path.dirname(bpy.data.filepath), 'Z-Anatomy.blend')

        with bpy.data.libraries.load(main_blend, link=False) as (data_from, data_to):
            data_to.collections = [self.collection]

        for collection in data_to.collections:
            if collection is not None:
                context.scene.collection.children.link(collection)

        context.view_layer.objects.active = collection.objects[0]
        msgbus_callback()

        # Relink cross section planes
        for tex_coord_node in [node for n in bpy.data.node_groups if n.name.startswith('CrossSectionControllerGroup') for node in n.nodes if node.type == 'TEX_COORD']:
            if tex_coord_node.object and re.match(r'.+\.\d\d\d', tex_coord_node.object.name):
                tex_coord_node.object = bpy.data.objects[re.split(r'\.\d\d\d', tex_coord_node.object.name)[0]]

        toggle_expand(context, 2)
        return {"FINISHED"}

# Opérateur pour supprimer une couche d'anatomie
class LAYERS_OT_remove_layer(bpy.types.Operator):
    """Remove anatomy layer"""
    bl_idname = "layer.remove_layer"
    bl_label = "Remove Layer"
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    collection: bpy.props.StringProperty()

    def execute(self, context):
        collection = bpy.data.collections.get(self.collection)

        for obj in collection.all_objects[:]:
            bpy.data.objects.remove(obj, do_unlink=True)

        bpy.data.collections.remove(collection)
        return {"FINISHED"}

# Opérateur pour activer ou désactiver les sections transversales pour une collection
class OBJECT_OT_collection_x_section(bpy.types.Operator):
    """Cross Section for Collection"""
    bl_idname = "collection.cross_section"
    bl_label = "Collection Cross Section"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    collection_name: bpy.props.StringProperty()
    enable: bpy.props.BoolProperty()
    axis: bpy.props.EnumProperty(items=[
        ('X', 'X', '', 0),
        ('Y', 'Y', '', 1),
        ('Z', 'Z', '', 2),
        ],
        default='X',
        name="Axis")
    invert: bpy.props.BoolProperty()

    def execute(self, context):
        collection = bpy.data.collections[self.collection_name]
        collection[f'Cross-section-{self.axis}'] = self.enable
        collection[f'Cross-section-{self.axis}-inverse'] = self.invert
        for ob in collection.all_objects:
            ob[f'Cross-section-{self.axis}'] = self.enable
            ob[f'Cross-section-{self.axis}-inverse'] = self.invert
            ob.update_tag(refresh={'OBJECT'})
        context.area.tag_redraw()

        return {"FINISHED"}

# Opérateur pour activer ou désactiver les sections transversales pour l'objet actif
class OBJECT_OT_object_x_section(bpy.types.Operator):
    """Cross Section for Active Object"""
    bl_idname = "object.cross_section"
    bl_label = "Object Cross Section"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    enable: bpy.props.BoolProperty()
    axis: bpy.props.EnumProperty(items=[
        ('X', 'X', '', 0),
        ('Y', 'Y', '', 1),
        ('Z', 'Z', '', 2),
        ],
        default='X',
        name="Axis")
    invert: bpy.props.BoolProperty()

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT' and context.object is not None and 'Cross-section-X' in context.object

    def execute(self, context):
        for obj in context.selected_objects:
            obj[f'Cross-section-{self.axis}'] = self.enable
            obj[f'Cross-section-{self.axis}-inverse'] = self.invert
            obj.update_tag(refresh={'OBJECT'})
        context.area.tag_redraw()
        return {"FINISHED"}

# Opérateur pour basculer la couleur clé des muscles
class OBJECT_OT_muscle_key_color(bpy.types.Operator):
    """Muscle Key Color"""
    bl_idname = "object.muscle_key_color"
    bl_label = "Muscle Key Color"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def execute(self, context):
        context.scene.zanatomy.muscle_color = not context.scene.zanatomy.muscle_color
        return {"FINISHED"}

# Groupe de propriétés pour l'add-on Z-Anatomy
class ZAnatomyProps(bpy.types.PropertyGroup):
    enable_group_labels: bpy.props.BoolProperty(default=True, name="Enable Group Labels", update=lambda self, context: label_group_checkbox_update())

    def muscle_color_func(self, context):
        if '4:Muscular system' in bpy.data.collections:
            var = self.muscle_color
            for ob in [c for col in bpy.data.collections for c in col.all_objects if c.type == 'MESH' and 'muscle_color' in c]:
                ob['muscle_color'] = var
                ob.update_tag(refresh={'OBJECT'})
        context.area.tag_redraw()

    muscle_color: bpy.props.BoolProperty(default=False, name="Key Color", update=muscle_color_func)

# Liste des classes à enregistrer
classes = (
    OBJECT_OT_hide_wrapper,
    OBJECT_OT_hide_view_clear_wrapper,
    TEXT_OT_wiki_download,
    OBJECT_OT_make_label,
    OBJECT_OT_label_delta,
    OBJECT_OT_change_label_wrapper,
    OBJECT_OT_translate_atlas,
    ZANATOMY_PT_languages,
    OBJECT_OT_local_view_wrapper,
    ZANATOMY_PT_Xsection,
    OBJECT_OT_collection_x_section,
    OBJECT_OT_object_x_section,
    OBJECT_OT_muscle_key_color,
    ZAnatomyProps,
    ZANATOMY_PT_labels,
    OBJECT_OT_select_parent_children,
    ZANATOMY_PT_Muscle_Color,
    OBJECT_OT_sync_visibility,
    ZANATOMY_PT_Visibility,
    LAYERS_OT_add_layer,
    LAYERS_OT_remove_layer
)

font_info = {
    "handler": None,
}

# Fonction de rappel pour dessiner le nom de l'objet actif dans la vue 3D
def draw_callback_px(self, context):
    context = bpy.context
    if not hasattr(context, 'area') or not context.object: return

    font_size = 24
    blf.color(0, 255, 255, 255, 255)
    blf.size(0, font_size, 72)
    blf.position(0, 55, context.area.height-70 - font_size, 0)
    blf.draw(0, f'{clean_name(context.object.name)[0]}')

# Fonction pour enregistrer les classes et les propriétés de l'add-on
def register():
    z_anatomy_load_post()
    bpy.app.handlers.load_post.append(z_anatomy_load_post)
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.Scene.zanatomy = bpy.props.PointerProperty(type=ZAnatomyProps)

    add_shortkeys()

    font_info["handler"] = bpy.types.SpaceView3D.draw_handler_add(
        draw_callback_px, (None, None), 'WINDOW', 'POST_PIXEL')

# Fonction pour désenregistrer les classes et les propriétés de l'add-on
def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)
    remove_shortkeys()

    bpy.app.handlers.load_post.remove(z_anatomy_load_post)

    bpy.msgbus.clear_by_owner(owner)

    bpy.types.SpaceView3D.draw_handler_remove(font_info["handler"], 'WINDOW')

if __name__ == "__main__":
    register()