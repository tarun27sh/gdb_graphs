from pprint import pprint as pp
from matplotlib import use as muse
from copy import deepcopy
muse('Agg')
from matplotlib import pyplot as plt
import networkx as nx

# dict: key=fn name(frame#0 string), val=stacktrace (string list of fns)
d_bt={}
# temp list to parse backtrace data. 
# Pushes output of loop to the hash table with key as 0th element. Lists are ordered, we want that to get edges
l=[]
# Edge List of tuples
el=[]
# dictonary to translate function names to integer index
d_fn_i={}
# dictonary to translate index to fn name string
d_i_fn={}

# list to store node colors
l_color=[]
count=0
# read bp fns from a file
# stored with:
# grep '^#' /auto/wwwPeople/tarusha2/logs2/rloc.gdb > $file
#fn_file=open('/auto/wwwPeople/tarusha2/logs2/rloc.gdb','r')
fn_file=open('/tmp/gdb_l2fib_2.txt','r')
pp('Reading fns from file')
dic={}
for i,line in enumerate(fn_file):
    line=line.strip()
    print('LLLINE = %s, len=%d'%(line, len(line.split(' '))))
    if '#' in line and (len(line.split(' ')) > 5):
        print('222LLLINE = %s'%(line))
        if '#0' in line:
            fn=line.split(' ')[2]
            print('FFFunction = %s'%(fn))
            print('SSSunction = %s'%(line))
            if fn:
                if l:
                    #pp(l)
                    l = filter(None, l)
                    if l[0] not in d_bt:
                        d_bt[l[0]]=l
                    l=[]
                print('Adding 1st element %s'%(fn))
                if fn not in d_fn_i:
                    d_fn_i[fn]=count
                    count+=1
                l.append(line.split(' ')[1])
        else:
            #print('Non #0 frame: %s'%(line))
            #pp(line.split(' '))
            frame_num, fn = line.split(' ')[0], line.split(' ')[4]
            #pp(frame_num)
            frame_num=frame_num[1:]
            #pp(frame_num)
            if fn and ('(' not in fn) and ('>' not in fn) and ('<' not in fn) and ('=' not in fn) and ('/' not in fn):
                l.append(fn)
                if fn not in d_fn_i:
                    d_fn_i[fn]=count
                    count+=1
            #print('read #%d frame: %s'%(int(frame_num), fn))


# this is required since above logic adds a key=0, val='', that's problem for networkx            
d_fn_i = {k:v for k,v in d_fn_i.iteritems() if v!=0}

pp(d_bt)
print(len(d_bt))
G=nx.DiGraph()
#G.add_node(1), covers *ALL* the functions
for key in d_bt:
    #pp(d_bt[key])
    print('Adding %d nodes'%(len(d_bt[key])))
    G.add_nodes_from(d_bt[key])

# add labels
for node in G.nodes():
    G.node[node]['label']=node

# create color list
for node in G.nodes():
    if 'sfltr' in node:
        l_color.append('r')
    else:
        l_color.append('b')


node_labels = nx.get_node_attributes(G,'label')
print('XXX--HT 1')

#now get the reverse mapping of this dict
#d_i_fn = {v: k for k,v in d_fn_i.iteritems()}
d_i_fn = {k:k for k,v in d_fn_i.iteritems()}

# create edge node list of tuples
for key in d_bt:
    fn_tmp = d_bt[key]
    fn_old=fn_tmp[0]
    for fn in fn_tmp[1:]:
        #el.append(tuple([d_fn_i[fn], d_fn_i[fn_old]]))
        el.append(tuple([fn, fn_old]))
        fn_old=deepcopy(fn)

print(G.nodes())
print(len(G.nodes()))
#pp(el)
G.add_edges_from(el)
print(G.nodes())
print(len(G.nodes()))
# DEBUG - fn -> index
#for f, i in d_fn_i.iteritems():
#    print('Index: %d  Function: %s'%(i,f))
#    print(type(i))
#    assert i,'fn->index index NULL!!'
#    assert f,'fn->index fn NULL!!'
#
# DEBUG - index -> fn
#for i, f in d_i_fn.iteritems():
#    print('%d. %s'%(i,f))
#    print(type(i))
#    assert i,'index->fn index NULL!!'
#    assert f,'fn->index fn NULL!!'

print('SIZE index -> fn = %d'%(len(d_i_fn)))
print('SIZE fn -> index = %d'%(len(d_fn_i)))

# draw and save as png
#pos = nx.spring_layout(G,k=0.45,iterations=200)
pos = nx.nx_pydot.graphviz_layout(G, prog='dot')

#nx.draw(G, pos, d_i_fn,node_size=60,font_size=8)
#nx.draw(G, d_i_fn,node_size=60,font_size=8)
#nx.draw_networkx_labels(G, d_i_fn,node_size=60,font_size=8)
#nx.draw(G, pos,node_size=5, edge_size=2, size=2,font_size=8)
nx.draw_networkx_nodes(G, pos, nodelist=None, node_size=10, node_color=l_color, node_shape='o', alpha=1.0, linewidths=None, label=None)
nx.draw_networkx_edges(G, pos, width=0.2, edge_color='k',style='solid',alpha=1.0, arrows=True, label=None)
nx.draw_networkx_labels(G, pos, labels = node_labels, size=8,font_size=3, font_family='sans-serif')
#pp(G.nodes())
GV= nx.nx_pydot.to_pydot(G)
pp(dir(GV))
GV.set_rankdir('BT')
GV.write_png('g.png')
print('G Nodes = %d'%(len(G.nodes())))
print('G Edges = %d'%(len(G.edges())))
print('Total Nodes in HT = %d'%(len(d_i_fn)))
#pp(G.edges())
print('saving image')
plt.axis('off') 
plt.autoscale(True)
plt.savefig("yup.png", dpi=500)
