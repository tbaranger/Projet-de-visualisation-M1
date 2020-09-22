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

    def highlightShortestPath(node1, node2):
        distance = {}
        parents = {}
        
        # Initialisation
        maxDist = graph.numberOfNodes()
        viewSelection.setAllNodeValue(False)
        viewSelection.setAllEdgeValue(False)
        viewColor.setAllNodeValue(tlp.Color(0, 0, 0, 100))
        viewColor.setAllEdgeValue(tlp.Color(0, 0, 0, 100))
        viewLabel.setAllNodeValue('')
        viewLabel[node1] = "Depart"
        viewLabel[node2] = "Arrivee"
        for n in graph.getNodes():
            distance[n] = maxDist
        parents[node1] = False
        
        q = queue.SimpleQueue()
        q.put(node1)
        
        #Path-highlighting algorithm inspired by Djikstra
        while(not q.empty()):
            head = q.get()
            for e in graph.getInOutEdges(head):
                n = graph.opposite(e, head)             
                if distance[n] == maxDist:
                    parents[n] = (head, e)
                    distance[n] = distance[head] + 1
                    if (n == node2):
                        viewSelection[n] = True
                        while(n != node1):
                            e = parents[n][1]
                            n = parents[n][0]
                            viewSelection[e] = True
                            viewSelection[n] = True
                            viewColor[n] = tlp.Color(0, 0, 0, 255)
                            viewColor[e] = tlp.Color(0, 0, 0, 255)
                        viewSelection[node1] = True
                        viewColor[node1] = tlp.Color(0, 0, 0, 255)
                        return True
                    else:
                        q.put(n)
                else:
                    continue
        return False
    
    # Random selection of two distinct nodes
    node1 = graph.getRandomNode()
    node2 = graph.getRandomNode()
    while (node1 == node2):
        node2 = graph.getRandomNode()
        
    highlightShortestPath(graph.getRandomNode(), graph.getRandomNode())
