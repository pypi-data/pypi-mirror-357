# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Dragulacontainer(Component):
    """A Dragulacontainer component.


Keyword arguments:

- children (a list of or a singular dash component, string or number; optional)

- id (string; optional)

- childrenOrder (list of strings; optional)

- droppedContainerId (string; optional)

- droppedElementId (string; optional)

- immovableIds (list of strings; optional)"""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dragulacontainer'
    _type = 'Dragulacontainer'
    @_explicitize_args
    def __init__(self, children=None, id=Component.UNDEFINED, childrenOrder=Component.UNDEFINED, immovableIds=Component.UNDEFINED, droppedContainerId=Component.UNDEFINED, droppedElementId=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'childrenOrder', 'droppedContainerId', 'droppedElementId', 'immovableIds']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'childrenOrder', 'droppedContainerId', 'droppedElementId', 'immovableIds']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        super(Dragulacontainer, self).__init__(children=children, **args)
