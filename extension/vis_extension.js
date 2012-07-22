//----------------------------------------------------------------------------
//  Copyright (C) 2008-2011  The IPython Development Team
//
//  Distributed under the terms of the BSD License.  The full license is in
//  the file COPYING, distributed as part of this software.
//----------------------------------------------------------------------------

//============================================================================
// OutputArea
//============================================================================

var IPython = (function (IPython) {
   "use strict";

    var OutputArea = IPython.OutputArea 

    OutputArea.prototype.scroll_area = function () {
        this.element.addClass('output_scroll');
        this.element.find("pre").css("white-space","pre")
        this.prompt_overlay.attr('title', 'click to unscroll output; double click to hide');
        this.scrolled = true;
    };


    OutputArea.prototype.unscroll_area = function () {
        this.element.removeClass('output_scroll');
        this.element.find("pre").css("white-space","pre-wrap")
        this.prompt_overlay.attr('title', 'click to scroll output; double click to hide');
        this.scrolled = false;
    };

    return IPython;

}(IPython));


var IPython = (function (IPython) {

    var VisUtils = function (notebook) {
        this.notebook = notebook;
        this.name_to_viscell = {};
        this.vis_cells = {};
    };

    VisUtils.prototype.insert_vis_cell = function (name) {
        var name = name;
        var cell = null;
        if (name in this.name_to_viscell) {
            $("#"+name+".vis_cell").remove();
            delete this.name_to_viscell[name];
        }
        cell = new IPython.VisCell(IPython.notebook, name);
        if (cell !== null) {
            var that = IPython.notebook;
            that.element.find('div.end_space').before(cell.element);
            cell.name = name;
            cell.element.attr("id", name);
            cell.render();
            this.name_to_viscell[name] = cell;
            this.vis_cells[cell.cell_id] = cell 
            $("#"+name)[0].vis_cell = cell;
            return cell;
        };
        
        return cell;
    };

    IPython.VisUtils = VisUtils;

    return IPython;

}(IPython));

IPython.vis_init = function () {
    if (IPython.vis_utils == undefined) {
        IPython.vis_utils = new IPython.VisUtils(IPython.notebook);
    }
}

var IPython = (function (IPython) {

    var utils = IPython.utils;

    var VisCell = function (notebook, name) {
        this.notebook = notebook;
        this.isVisCell = true;
        this.selected = false;
        this.element = null;
        this.create_element();
        if (this.element !== null) {
            this.element.data("cell", this);
            this.bind_events();
        }   
        this.cell_id = utils.uuid();
        this.name = name;
        this.data = {}
    };  


    //VisCell.prototype = new IPython.VisCell();

    VisCell.prototype.bind_events = function () {}; 
    VisCell.prototype.render = function () {}; 

    VisCell.prototype.create_element = function () {
        var cell =  $('<div></div>').addClass('vis_cell');
        cell.css("position","absolute");
        cell.css("top", "0px");
        cell.css("width", "500px");
        cell.css("left", "850px");
        cell.css("height", "530px");
        cell.css("border", "2px solid");
        cell.css("background", "white");
        this.element = cell;
    };  

    VisCell.prototype._handle_execute_reply = function (content) {
        this.element.removeClass("running");
    }

    VisCell.prototype.handle_output = function (msg_type, content) {
        if (msg_type == "display_data") {
            eval(content.data["application/javascript"])
        }
    };

    VisCell.prototype.execute_py = function (code, callbacks) {
        if (callbacks == undefined) {
            var callbacks = {
                'execute_reply': $.proxy(this._handle_execute_reply, this),
                'output': $.proxy(this.handle_output),
            };
        }
        var msg_id = this.notebook.kernel.execute(code, callbacks); //TODO: need to add callbacks
        return msg_id
    };  
    
    IPython.VisCell = VisCell;

    return IPython;

}(IPython));
