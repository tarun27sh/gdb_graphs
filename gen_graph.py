# Description:
#       Generate dot graph from gdb backtracet data
# Author: 
#       Tarun Sharma (tarun27sh@gmail.com)
# Date:
#       2019-01-19

import os
from matplotlib import use as muse
from copy import deepcopy
muse('Agg')
import sys
import pydotplus
import argparse
import pdb
from pprint import pprint as pp
import logging

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

HTML_SEP = '&#10;&#13;'

# Make resulting SVG interactive
js_string='''
<script>
<![CDATA[

        class Node {
            constructor(name) {
                this.name = name;
                this.parents = [];
                this.children = [];
                this.visited = false;
            }
        };
        var graph = [];

        function showNeighboursFast(nodeId) {
            node = graph[nodeId];
            if (node) {
                console.log('FAST: #of P=' + node.parents.length + '#of Ch=' + node.children.length);
                for(var i = node.parents.length - 1; i >= 0; i--) {
                    var neighElement =  document.getElementById(node.parents[i]);
                    if (neighElement) {
                        var inner_polygon = neighElement.getElementsByTagName('polygon');
                        inner_polygon[0].setAttribute("style", "fill: orange");
                    }
                }
                for(var i = node.children.length - 1; i >= 0; i--) {
                    var neighElement =  document.getElementById(node.children[i]);
                    if (neighElement) {
                        var inner_polygon = neighElement.getElementsByTagName('polygon');
                        inner_polygon[0].setAttribute("style", "fill: cyan");
                    }
                }
            }
        }

        function showNeighboursInfluenceFast(nodeId, visitParents, visitChildren, level) {
            // recursively, find all parents, chidlren and highlight them
            //console.log('node = ' + nodeId + 'P?=' + visitParents + 'C?=' + visitChildren);
            var node = graph[nodeId];
            if (node && !node.visited) {
                node.visited = true;
                level++;
                console.log(level + 'node = ' + node.name + '#of P = ' + node.parents.length + '#of Ch = ' + node.children.length);
                

                if (visitParents && node.parents && node.parents.length > 0) {
                    for(var i = node.parents.length - 1; i >= 0; i--) {
                        var neighElement =  document.getElementById(node.parents[i]);
                        if (neighElement) {
                            var inner_polygon = neighElement.getElementsByTagName('polygon');
                            inner_polygon[0].setAttribute("style", "fill: orange");

                            var inner_text = neighElement.getElementsByTagName('text');
                            inner_text[0].setAttribute("style", "fill: black");
                            
                            showNeighboursInfluenceFast(node.parents[i], true, false, level);
                        }
                    }
                }

                if (visitChildren && node.children && node.children.length > 0) {
                    for(var i = node.children.length - 1; i >= 0; i--) {
                        var neighElement =  document.getElementById(node.children[i]);
                        if (neighElement) {
                            var inner_polygon = neighElement.getElementsByTagName('polygon');
                            inner_polygon[0].setAttribute("style", "fill: cyan");

                            var inner_text = neighElement.getElementsByTagName('text');
                            inner_text[0].setAttribute("style", "fill: black");


                            showNeighboursInfluenceFast(node.children[i], false, true, level);
                        }
                    }
                }
            }
            return;
        }

        function nodeClick(element) {
            //showNeighboursFast(element.id);
            showNeighboursInfluenceFast(element.id, true, true, 0);
            var inner_polygon = element.getElementsByTagName('polygon');
            var inner_text = element.getElementsByTagName('text');
            inner_polygon[0].setAttribute("style", "fill: yellow");
            inner_text[0].setAttribute("style", "fill: black");
        }

        function printGraphElements() {
            for (var key in graph) {
                console.log('key=' + key + '; value=' + graph[key]);
            }            
        }

        // graph[node] = [edge1, edg2 etc...]
        function constructGraph() {
            console.log('FAST: constructing graph');
            edges = document.getElementsByClassName("edge");
            for (var i=edges.length - 1; i>0; i--) {
                var node0, node1;
                nodes = edges[i].id.split('|')
                node0 = nodes[0];
                node1 = nodes[1];
                if (!graph[node0]) {
                    graph[node0] = new Node(node0);
                }
                graph[node0].children.push(node1);

                if (!graph[node1]) {
                    graph[node1] = new Node(node1);
                }
                graph[node1].parents.push(node0);
            }
            printGraphElements();
        }

        window.addEventListener('load',function(){
            console.log('Add onclick property to all nodes');
            nodes = document.getElementsByClassName("node");
            for(var i = nodes.length - 1; i >= 0; i--) {
                nodes[i].setAttribute("onclick", 'nodeClick(this)');
            }
            constructGraph();
        })
]]>
</script>
'''

# parses into node in graph
class GDBFrame():
    def __init__(self):
        self.frame_no = None
        self.fn_name = None
        self.file_name = None
        self.fn_args = {}
        self.nof_arg_data = 0
        self.callers = [] # parent nodes, list of GDBFrame objs
        self.callees = [] # child nodes, list of GDBFrame objs

    def __str__(self):
        format_str = '#{} fn={}, args={}, file={}'.format(self.frame_no, self.fn_name, self.fn_args, self.file_name)
        return format_str

    def parse_frame_line(self, frame_str):
        frame_list = frame_str.split()
        self.frame_no = int(frame_list[0].strip('#'))
        if frame_list[1].startswith('0x'):
            self.fn_name = frame_list[3]
        else:
            self.fn_name = frame_list[1]
        self.file_name = frame_list[-1]
        self.fn_args = frame_str.split('(')[1].split(')')[0]



# collection of nodes
class GenGraph:
    def __init__(self, file_in, input_format='gdb'):
        self.nof_frames = 0
        self.parsed_frame_dict = {}   # key=fn_name, val=GDBFrame()
        self.g = None
        # create graph obj
        self.g = pydotplus.Dot(graph_type='digraph', 
                          graph_name='Created by: Tarun Sharma (tarun27sh@gmail.com)', 
                          rankdir='LR', 
                          strict=True,
                         )
        if input_format==None or input_format=='gdb':
            self.parse_bt_file(file_in)
            self.add_nodes_edges()
        self.add_legend(len(self.g.get_edges()), len(self.g.get_nodes()))
        self.save_graph(file_in)

    def __str__(self):
        format_str = 'Len(frames) = {}, 1st frame={}'.format(len(self.parsed_frame_dict), self.parsed_frame_dict[list(self.parsed_frame_dict.keys())[0]])
        return format_str

    def fix_up_global_dict(self, new_bt):
        logger.debug('fix up, #ofFrames={}'.format(len(new_bt)))
        for frame in new_bt:
            if frame.fn_name in self.parsed_frame_dict:
                existing_frame = self.parsed_frame_dict[frame.fn_name]
                existing_frame.callees.extend(frame.callees)
                existing_frame.callers.extend(frame.callers)
                # limit arg data to 6 entries only
                if frame.fn_args and existing_frame.nof_arg_data < 5:
                    existing_frame.fn_args += '{}{}'.format(HTML_SEP, frame.fn_args) # provide HTML format '\n'
                    existing_frame.nof_arg_data += 1
            else:
                self.parsed_frame_dict[frame.fn_name] = frame

    def parse_bt_file(self, in_file):
        logger.info('[1] processing gdb bt data')
        current_frame_list = []
        old_frame = None
        with open(in_file) as f:
            for i,line in enumerate(f):
                if line.startswith('#'):
                    frame = GDBFrame()
                    frame.parse_frame_line(line)
                    # new bt
                    if frame.frame_no == 0:
                        # new bt
                        callee = None
                        if len(current_frame_list) > 0:
                            for i in range(len(current_frame_list) - 1):
                                if callee:
                                    current_frame_list[i].callees.append(callee)
                                current_frame_list[i].callers.append(current_frame_list[i+1])
                                callee = current_frame_list[i]
                            current_frame_list[-1].callees.append(callee)
                            self.fix_up_global_dict(current_frame_list)

                        # reset for next iteration
                        current_frame_list = []
                        current_frame_list.append(frame)
                    else:
                        # exising bt
                        current_frame_list.append(frame)


    def add_nodes_edges(self):
        i = 0
        edge_seen_dict = {} # key = edge1_edge2
        logger.info('[2] adding nodes, edges, #ofnodes={}'.format(len(self.parsed_frame_dict)))
        for fn in self.parsed_frame_dict:
            print('Frame# [{}]\r'.format(i), end='')
            i+= 1
            frame = self.parsed_frame_dict[fn]
            new_element_name = '\"{}\"'.format(frame.fn_name)
            tooltip_str = '{}{}{}{}'.format(frame.file_name, HTML_SEP,
                                            frame.fn_args, HTML_SEP)
            logger.debug('adding node={}'.format(new_element_name))
            self.g.add_node(pydotplus.Node(
                                      new_element_name, 
                                      id=new_element_name,
                                      penwidth=0,
                                      tooltip=tooltip_str,
                                      style="filled",
                                      fillcolor='cornflowerblue', 
                                      #bgcolor='cornflowerblue',
                                      shape='box', 
                                      margin=0,
                                      fontname="Consolas", 
                                      #fontname="Courier New", 
                                      fontsize=12.0,
                                      fontcolor='white'))
            for callee in frame.callees:
                if callee:
                    new_tuple = ('\"{}\"'.format(frame.fn_name),
                                 '\"{}\"'.format(callee.fn_name))
                    key = '{}_{}'.format(frame.fn_name, callee.fn_name)
                    if key not in edge_seen_dict:
                        logger.debug('adding edge={}'.format(new_tuple))
                        self.g.add_edge(pydotplus.Edge(new_tuple, 
                                                  id='\"{}|{}\"'.format(
                                                  new_tuple[0].strip('"'), 
                                                  new_tuple[1].strip('"')),
                                                  color='grey',
                                                  ))
                        edge_seen_dict[key] = True
            for caller in frame.callers:
                new_tuple = ('\"{}\"'.format(caller.fn_name),
                             '\"{}\"'.format(frame.fn_name))
                key = '{}_{}'.format(caller.fn_name, frame.fn_name)
                if key not in edge_seen_dict:
                    logger.debug('adding edge={}'.format(new_tuple))
                    self.g.add_edge(pydotplus.Edge(new_tuple, 
                                              id='\"{}|{}\"'.format(
                                              new_tuple[0].strip('"'), 
                                              new_tuple[1].strip('"')),
                                              color='grey',
                                              ))
                    edge_seen_dict[key] = True
    
    def save_graph(self, file_in):
        file_name = file_in.split('/')[-1]
        
        full_output_name="{}/{}.svg".format(os.getcwd(), file_name[:-4])
        self.g.write_svg(full_output_name, 
                    prog='dot')
        logger.info('[3] Embedding JS')
        search_string = 'graph0'
        new_lines = ''
        with open(full_output_name, 'r') as f:
            for line in f:
                if search_string in line:
                    new_lines += js_string
                new_lines += line
        logger.info('[4] saving graph to:')
        logger.info("      {}\n".format(full_output_name))
        with open(full_output_name, "w") as text_file:
            text_file.write(new_lines)
        logger.info('Finished')
    
    def add_legend(self,nedges, nnodes):
        logger.debug('adding legend')
        node = pydotplus.Node(
                                  label='Nodes = {}\n Edges = {}'.format(nnodes, nedges),
                                  penwidth=0,
                                  style="filled", 
                                  fillcolor='gold1', 
                                  shape='box', 
                                  fontname="Consolas", 
                                  fontsize=14.0)
        self.g.add_node(node)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='read gen_graph inputs')
    parser.add_argument('-i', '--input_file', 
                        help='input data file', 
                        required=True)
    parser.add_argument('-f', '--input_file_format', 
                        help='input data file format (default=gdb)', 
                        choices=['gdb', 'objdump'])
    args = parser.parse_args()

    if args.input_file is None:
        args.print_usage()
        sys.exit()
    GenGraph(args.input_file, args.input_file_format)

