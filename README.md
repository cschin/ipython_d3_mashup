IPython Notebook and d3.js Mashup
=================================

Thanks the IPython team for their excellent work on 0.13 release. The new
re-factored javascript for IPython 0.13 notebook makes writing mashup using
d3.js + IPython simpler. I put two examples in ipython_13_vis_example/

The examples use the python extension mechanism to load the python and
javascript extension directly from github. They should work fine under the
official IPython 0.13 Notebook. However, I have only limited tests under
FireFox.

The GDP_CO2_Example.ipynb only uses the vis_extension.py. It shows how to make
a movable chart with IPython + d3.js.

The Word_Ladder_network_vis.ipynb is an experiment to show how to build
interacitve widget to show it is possible to use python code as callbacks for
some html elements.

Currently, I don't feel happy about the visutils.py code. It is quite ugly. If
time permits, I will think a better way to make the mapping between javascript
objects and python objects more transparent. It is quite tricky to debug if any
simple mistake is in the code.



