IPython Notebook and d3.js Mashup
=================================

Thanks the IPython team for their excellent work on 0.13 release. The new
re-factored javascript for IPython 0.13 notebook makes writing mashup using
d3.js + IPython simpler. I put two examples in ipython_13_vis_example/

The examples should work with my own IPython vis_0.13 branch.
(More specifically, I test them with this commit https://github.com/cschin/ipython/commit/87c2fdff548bd2f86bb7f8dba1e47f23242ed4e0)

In IPython 0.13, I do not need to patch IPython's official CodeCell and
Notebook javascript like in the previous hack. I add two extra files,
IPython/frontend/html/notebook/static/vis/vis_extension.js and
IPython/frontend/html/notebook/visutils.py, in the code tree to support
excuting javascript code from IPython and excute Python code from javascript.

The GDP_CO2_Example.ipynb only uses the vis_extension.py. It shows how to make
a movable chart with IPython + d3.js.

The Word_Ladder_network_vis.ipynb is an experiment to show how to build
interacitve widget to show it is possible to use python code as callbacks for
some html elements.

Currently, I don't feel happy about the visutils.py code. It is quite ugly. If
time permits, I will think a better way to make the mapping between javascript
objects and python objects more transparent. It is quite tricky to debug if any
simple mistake is in the code.

--Jason Chin, July 19, 2012
