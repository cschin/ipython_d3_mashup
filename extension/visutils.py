import json
from IPython.core.display import display_javascript
from collections import OrderedDict
from time import sleep


def run_js(js):
    display_javascript(js, raw=True)

def get_widget_by_name(name):
    return NotebookVisualWidget.get_widget_by_name(name)
    
def set_js_var(vis_name, js_var, py_obj):
    js  = """(function() { var vc = IPython.vis_utils.name_to_viscell["%s"];""" % vis_name
    js += """vc.data.%s=%s;})()""" % (js_var, json.dumps(py_obj))
    run_js(js)

def set_action(instance, action, func, argv_name=None, kwargv_name=None):
    import types
    instance.__setattr__(action, types.MethodType(func, instance))
    instance.on_action(action, (action, argv_name, kwargv_name))

class NotebookVisualDisplay(object):

    def __init__(self, container = None ):
        self.container = container # we should allow more than the standard out cell
        self.widgets = OrderedDict() 
        self.js_code = []
        self._displayed = False
        self.attach_widget(container)

    def attach_widget(self, widget):
        self.widgets[widget.name] = widget
        widget.set_vis(self)


    def attach_js_code(self, js):
        self.js_code.append(js)

    @property
    def js(self):
        js = []
        for n,w in self.widgets.items():
            js.append(w.js)
        for js_code in self.js_code:
            js.append(js_code)
        return "\n\n".join(js)

    def display(self):
        """
        send the javascript to the frontend to show the visulization
        """
        if self._displayed == False:
            self.container._create()
            self.container.set_all_js_vars()
            run_js(self.js)
            self._displayed = True

    def remove(self):
        run_js("$('#%s').remove()" % self.container.name)
        self._displayed = False
        
    def refresh(self):
        """
        clean everything up, and re-display all widget
        """
        self.remove()
        sleep(1)
        self.display()

    def show(self):
        run_js("""$("#%s").css("visibility","visible")""" % self.container.name)

    def hide(self):
        run_js("""$("#%s").css("visibility","hidden")""" % self.container.name)


    def delete_widget(self, widget):
        try:
            del self.widgets[widget.name]
            widget.remove()
        except:
            pass



class NotebookVisualWidget(object): #maybe this should be an ABC

    _name_widget_map = {}
    
    def __init__(self, name = None, parent= None, style={}, vis=None):
        self.name = name
        if name in NotebookVisualWidget._name_widget_map:
            del NotebookVisualWidget._name_widget_map[name]
        NotebookVisualWidget._name_widget_map[name] = self
        self.parent = parent
        self.style = style
        self._js = "" #non-jsonfied verions of the javascript 
        self._action = {}
        self._vis = vis 
        if vis != None:
            vis.attach_widget(self)
        self._create()
        self._js_vars = {}

    def _create(self):
        raise NotImplementedError

    def set_js_var(self, js_var, py_obj):
        self._js_vars[js_var] = py_obj;
        js  = """(function(){var vc = IPython.vis_utils.name_to_viscell["%s"];""" % self.name
        js += """vc.data.%s=%s;})()""" % (js_var, json.dumps(py_obj))
        run_js(js)

    def set_all_js_vars(self):
        for js_var, py_obj in self._js_vars.items():
            self.set_js_var(js_var, py_obj)
    
    @classmethod
    def get_widget_by_name(cls, name):
        return cls._name_widget_map[name]

    def on_action(self, action, func_argvs ):
        self._action[action] = func_argvs
        self._js += self._generate_action_js(action, func_argvs)

    def _get_css_settings(self):
        js_strs = []
        for k,v in self.style.items():
            js_strs.append( """ $("#%s").css("%s", "%s");""" % (self.name, k, v) )
        return js_strs
    
    def _generate_action_js(self, action, func_spec):
        func, argv, kwargv = func_spec

        py_code = self.get_py_code_for_widget
        if argv != None and kwargv != None:
            py_code += """_w.%s(*_w.%s,**_w.%s)""" % (func, argv, kwargv)
        elif argv != None:
            py_code += """_w.%s(*_w.%s)""" % (func, argv)
        elif kwargv != None:
            py_code += """_w.%s(**_w.%s)""" % (func, kwargv)
        else:
            py_code += """_w.%s()""" % (func)

        js_str  = """( function () {$("#%s")[0].%s= function() {"""  % ( self.name, action )
        js_str += """var vc = IPython.vis_utils.name_to_viscell["%s"]; """ % (self._vis.container.name)
        js_str += """var vis_code = "%s";""" % py_code
        js_str += """vc.execute_py(vis_code);} """  
        js_str += "} )();" 
        return js_str

    def set_vis(self, vis):
        self._vis = vis

    def remove(self):
        run_js("$('#%s').remove()" % self.name)

    @property
    def js(self):
        return self._js

    @property
    def get_py_code_for_widget(self):
        py_code  = """try:\\n"""
        py_code += """    _w = _vis.get_widget_by_name('%s')\\n""" % self.name 
        py_code += """except NameError:\\n"""
        py_code += """    import %s as _vis\\n""" % self.__module__
        py_code += """    _w = _vis.get_widget_by_name('%s')\\n""" % self.name
        return py_code


class VISCellWidget(NotebookVisualWidget):

    def _create(self):
        js_strs = [ """IPython.vis_utils.insert_vis_cell("%s"); """ % self.name ]
        js_strs.extend(self._get_css_settings())
        run_js("\n".join(js_strs))
        #self._js = "\n".join(js_strs)

    def execute_code_js(self, py_code):

        js_str  = """(function() { var vc = IPython.vis_utils.name_to_viscell["%s"];""" % (self.name)
        js_str += """var vis_code = "%s"; """ % py_code
        js_str += """vc.execute_py(vis_code)}) ) ()"""

        return js_str

    def execute_code(self, py_code):
        js_str = self.execute_code_js(py_code)
        run_js(js_str)


    def set_py_var(self, py_name, js_exp):
        js_str  = """(function () var vc = IPython.vis_utils.name_to_viscell["%s"];""" % (self.name)
        js_str += """var vis_code = "%s="+JSON.stringify(%s) ;""" % (py_name, js_exp)
        js_str += """vc.execute_py(vis_code) )()"""

        run_js(js_str)

class DIVWidget(NotebookVisualWidget):

    def _create(self):
        js_strs = ["""$("#%s").append("<div id='%s'></div>"); """ % (self.parent,
                                                                    self.name)]

        js_strs.extend(self._get_css_settings())
        self._js = "\n".join(js_strs)

class SVGWidget(NotebookVisualWidget):

    def _create(self):
        js_strs = ["""$("#%s").append("<svg id='%s'></svg>"); """ % (self.parent,
                                                                    self.name)]

        js_strs.extend(self._get_css_settings())

        self._js = "\n".join(js_strs)


class ButtonWidget(NotebookVisualWidget):

    def __init__(self, name = None, parent= None, style={}, text="Button", vis=None):
        self.text = text
        super(ButtonWidget, self).__init__(name = name, parent = parent, style = style, vis = vis)

    def _create(self):
        js_strs = ["""$("#%s").append("<button id='%s'>%s</button>"); """ % (self.parent,
                                                                            self.name,
                                                                            self.text)]
        js_strs.extend(self._get_css_settings())

        self._js = "\n".join(js_strs)

    def set_text(self, text):
        js = """$("#button_1")[0].innerHTML=%s; """ % json.dumps(text)
        run_js(js) 


class InputWidget(NotebookVisualWidget):

    def __init__(self, name = None, parent= None, style={}, value="Text", vis=None):
        self.value = value
        super(InputWidget, self).__init__(name = name, parent = parent, style = style, vis = vis)

    def _create(self):
        js_strs = ["""$("#%s").append("<input id='%s' value='%s'></input>"); """ % (self.parent,
                                                                                    self.name,
                                                                                    self.value)]
        js_strs.extend(self._get_css_settings())

        self._js = "\n".join(js_strs)

    @property
    def _get_value_js(self):
        container_name = self._vis.container.name
        py_code = self.get_py_code_for_widget
        js_str  = """(function() { var vc = IPython.vis_utils.name_to_viscell["%s"];""" % (container_name)
        js_str += """var vc = IPython.vis_utils.name_to_viscell["%s"];""" % (container_name)
        js_str += """var vis_code = "%s";""" % py_code
        js_str += """vc.execute_py(vis_code);""" 
        js_str += """vc.execute_py( "_w.value =" + JSON.stringify( $("#%s").attr("value") ) );""" % ( self.name) 
        js_str += "}  ) ();" 
        return js_str

    def update_value(self):
        run_js(self._get_value_js)


_loaded = False

def load_ipython_extension(ip):
    """Load the extension in IPython."""
    global _loaded
    if not _loaded:
        ip.user_ns["vis"] = __import__("visutils")
        _loaded = True
