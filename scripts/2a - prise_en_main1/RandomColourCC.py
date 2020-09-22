# Powered by Python 3.7
# To cancel the modifications performed by the script
# on the current graph, click on the undo button.
# Some useful keyboard shortcuts:
#   * Ctrl + D: comment selected lines.
#   * Ctrl + Shift + D: uncomment selected lines.
#   * Ctrl + I: indent selected lines.
#   * Ctrl + Shift + I: unindent selected lines.
#   * Ctrl + Return: run script.
#   * Ctrl + F: find selected text.
#   * Ctrl + R: replace selected text.
#   * Ctrl + Space: show auto-completion dialog.
from tulip import tlp
import queue
import random
# The updateVisualization(centerViews = True) function can be called
# during script execution to update the opened views
# The pauseScript() function can be called to pause the script execution.
# To resume the script execution, you will have to click on the
# "Run script " button.
# The runGraphScript(scriptFile, graph) function can be called to launch
# another edited script on a tlp.Graph object.
# The scriptFile parameter defines the script name to call
# (in the form [a-zA-Z0-9_]+.py)
# The main(graph) function must be defined
# to run the script on the current graph
def main(graph):
    viewBorderColor = graph['viewBorderColor']
    viewBorderWidth = graph['viewBorderWidth']
    viewColor = graph['viewColor']
    viewFont = graph['viewFont']
    viewFontSize = graph['viewFontSize']
    viewIcon = graph['viewIcon']
    viewLabel = graph['viewLabel']
    viewLabelBorderColor = graph['viewLabelBorderColor']
    viewLabelBorderWidth = graph['viewLabelBorderWidth']
    viewLabelColor = graph['viewLabelColor']
    viewLabelPosition = graph['viewLabelPosition']
    viewLayout = graph['viewLayout']
    viewMetric = graph['viewMetric']
    viewRotation = graph['viewRotation']
    viewSelection = graph['viewSelection']
    viewShape = graph['viewShape']
    viewSize = graph['viewSize']
    viewSrcAnchorShape = graph['viewSrcAnchorShape']
    viewSrcAnchorSize = graph['viewSrcAnchorSize']
    viewTexture = graph['viewTexture']
    viewTgtAnchorShape = graph['viewTgtAnchorShape']
    viewTgtAnchorSize = graph['viewTgtAnchorSize']

    #params = tlp.getDefaultPluginParameters("Connected Component", graph)
    #graph.applyDoubleAlgorithm("Connected Component", params)
    
    # We start by identifying every connected components within the graph,
    # and labelling the nodes belonging to them accordingly (0 -> n-1)
    
    UNVISITED = -1
    viewMetric.setAllNodeValue(UNVISITED)
    i = 0
    
    def labelConnectedComponent(n, i):
      q = queue.SimpleQueue()
      q.put(n)
      viewMetric[n] = i
      while (not q.empty()):
        head = q.get()
        for neighbour in graph.getInOutNodes(head):
          if (viewMetric[neighbour] == UNVISITED):
            q.put(neighbour)
            viewMetric[neighbour] = i
          
    for n in graph.getNodes():
      if (viewMetric[n] == UNVISITED):
        labelConnectedComponent(n, i)
        i = i+1
    
    nbConnectedComponents = int(viewMetric.getNodeMax() + 1)
    colours = []
    for i in range(int(nbConnectedComponents)):
        colours.append((random.randint(0, 255),random.randint(0, 255),random.randint(0, 255),255))
    
    for n in graph.getNodes():
        viewColor[n] = tlp.Color(colours[int(viewMetric[n])])
  
