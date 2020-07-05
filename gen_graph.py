# Author: 
#       Tarun Sharma (tarun27sh@gmail.com)
# Description:
#       1. reads gdb backtrace logs
#       2. generates a function call graphs
#       3. saves output in SVG format
# Usage:
#       ./gen_graphs.py <gdb_backtrace.log> 
# Date:
#       2019-01-19
import os
from matplotlib import use as muse
from copy import deepcopy
muse('Agg')
import sys
import pydotplus

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
start_color = {
                # format - style, fg, bg
                'info':'\x1b[6;0;32m', # style, fg, bg
                'dbg': '\x1b[6;23;40m',
                'err': '\x1b[6;0;31m', # style, fg, bg
              }
end_color='\x1b[0m'

def special_print(text, level):
    print('{}{}{}'.format(start_color[level], text, end_color))

# use master list to add nodes
# no duplicates
def add_nodes(g, l_unique_nodes):
    special_print('[2] adding nodes..', 'info')
    for elem in l_unique_nodes:
        if ',' not in elem:
            #print('adding {}'.format(elem.replace(":", "_")))
            new_element_name = '\"{}\"'.format(elem)
            #print('adding {}'.format(new_element_name))
            g.add_node(pydotplus.Node(
                                      new_element_name, 
                                      id=new_element_name,
                                      style="filled", 
                                      fillcolor='cornflowerblue', 
                                      shape='box', 
                                      fontname="Consolas", 
                                      fontsize=12.0,
                                      fontcolor='white'))
    print('\t# of nodes: {}'.format(len(l_unique_nodes)))

def add_edges(g, file_in):
    # get edges
    fn_file=open(file_in,'r')
    special_print('[3] adding edges..', 'info')
    curr_bt=[]
    edge_tuples=[]
    backtraces=[]
    for i,line in enumerate(fn_file):
        line=line.strip()
        if '#' in line:
            # head node of backtrace
            if '#0' in line:
                fn=line.split()[1]
                # previous backtrace complete, add it to master list
                if len(curr_bt) > 0 :
                    backtraces.append(curr_bt)
                    curr_bt = []
                # frame 0 fn-name always at index 1 of line.split()
                curr_bt.append(line.split()[1])
            else:
                if 'breakpoint' in line or '\\' in line:
                    pass #continue
                if line.split()[1].startswith('0x'):
                    fn = line.split()[3]
                else:
                    fn = line.split()[1]
                if fn and \
                   ('(' not in fn) and \
                   ('>' not in fn) and \
                   ('<' not in fn) and \
                   ('=' not in fn) and \
                   ('/' not in fn):
                    curr_bt.append(fn)
    # save the last backtrace
    backtraces.append(list(curr_bt))
    for bt in backtraces:
        fn_old = bt[0]
        for fn in bt[1:]:
            if (fn, fn_old) not in edge_tuples:
                #print('adding edge:  {} --> {}'.format(fn, fn_old))
                edge_tuples.append((fn, fn_old))
            fn_old=deepcopy(fn)

    l_unique_edges=[]
    file_out_data=file_in[:-4]+".data"
    thefile = open(file_out_data, 'w')
    for edge_tuple in edge_tuples:
        if edge_tuple not in l_unique_edges:
            new_tuple = ('\"{}\"'.format(edge_tuple[0]),
                         '\"{}\"'.format(edge_tuple[1]))
            g.add_edge(pydotplus.Edge(new_tuple, 
                                      id='\"{}|{}\"'.format(
                                            new_tuple[0].strip('"'), 
                                            new_tuple[1].strip('"'))))
            #print('added {}'.format(new_tuple))
            l_unique_edges.append(new_tuple)

    print('\t# of edges: {}'.format(len(l_unique_edges)))
    return len(l_unique_edges)

def parse_gdb_logs(file_in):
    l_unique_nodes=[]
    fn_file=open(file_in,'r')
    special_print('[1] parsing gdb logs..', 'info')
    for i,line in enumerate(fn_file):
        line=line.strip()
        t_temp=()
        if '#' in line and (len(line.split(' ')) >= 4):
            # new back trace
            if '#0' in line:
                # if list has previous frame, add it to master list
                if line.split()[1].startswith('0x'):
                    fn = line.split()[3]
                else:
                    fn = line.split()[1]
                if fn not in l_unique_nodes:
                    #print('Adding #0 {}'.format(fn))
                    l_unique_nodes.append(fn)
            else:
                # non f#0 frame
                if line.split()[1].startswith('0x'):
                    fn=line.split()[3]
                else:
                    fn=line.split()[1]
                if fn and \
                   fn not in l_unique_nodes and \
                   ('(' not in fn) and \
                   ('>' not in fn) and \
                   ('<' not in fn) and \
                   ('=' not in fn) and \
                   ('/' not in fn):
                    #print('Adding #!0 {}'.format(fn))
                    l_unique_nodes.append(fn)
    return l_unique_nodes

def save_graph(g, file_in):
    # use master list to add edges
    # no duplicates
    special_print('[4] saving graph to:', 'info')
    #g.write(file_in[:-4]+".dot")
    file_name = file_in.split('/')[-1]
    
    full_output_name="{}/{}.svg".format(os.getcwd(), file_name[:-4])
    print("\t{}\n".format(full_output_name))
    g.write_svg(full_output_name)
    search_string = 'graph0'
    new_lines = ''
    with open(full_output_name, 'r') as f:
        for line in f:
            if search_string in line:
                #print('found --> at line# {}'.format(line))
                new_lines += js_string
            new_lines += line
    with open(full_output_name, "w") as text_file:
        text_file.write(new_lines)

def add_legend(g, nedges, nnodes):
    node = pydotplus.Node(
                              label='Nodes = {}\n Edges = {}'.format(nedges, nnodes),
                              style="filled", 
                              fillcolor='gold1', 
                              shape='box', 
                              fontname="Consolas", 
                              fontsize=14.0)
    #node = pydotplus.Node('legend')
    g.add_node(node)

def process(file_in):
    # hold egdes in list of tuples
    l_unique_nodes=[]

    g = pydotplus.Dot(graph_type='digraph', 
                      graph_name='Created by: Tarun Sharma (tarun27sh@gmail.com)', 
                      rankdir='LR', 
                      simplify='True')
    #                  bgcolor='grey35')
    l_unique_nodes = parse_gdb_logs(file_in)
    add_nodes(g, l_unique_nodes)
    no_of_edges = add_edges(g, file_in)
    add_legend(g, no_of_edges, len(l_unique_nodes))
    save_graph(g, file_in)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        special_print('Usage:', 'err')
        special_print('./gen_graphs.py  <gdb_backtrace_logs>', 'err')
        sys.exit()
    else:
        file_in = sys.argv[1].rstrip()
        process(file_in)
