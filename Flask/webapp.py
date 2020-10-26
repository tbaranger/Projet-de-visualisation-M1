import os
from flask import *
import io
import csv
import json
from collections import OrderedDict
from itertools import islice

from tulip import tlp

# NE PAS MODIFIER LA LIGNE SUIVANTE
app = Flask(__name__)

# List of graph files
root = os.path.realpath(os.path.dirname(__file__))
marvelURL = os.path.join(root, "static/data/marvel", "marvel.tlpb")
FRCinemaURL = os.path.join(root, "static/data/movies", "cinema.francophone2.tlpb")
FRNetworkURL = os.path.join(root, "static/data/movies", "french.actors.network.tlpb")

@app.route("/getMarvelData/<int:k>")
def getMarvelData(k=30, graph=marvelURL):

    # load graph data
    g = tlp.loadGraph(graph)

    # compute node degree
    viewMetric = g.getDoubleProperty("viewMetric")
    g.applyDoubleAlgorithm("Degree", viewMetric)

    viewIcon = g.getStringProperty("viewIcon")
    viewLabel = g.getStringProperty("viewLabel")
    degree={}
    for n in viewIcon.getNodesEqualTo("md-human"):
        degree[viewLabel[n]]=int(viewMetric[n])
    best = OrderedDict(sorted(degree.items(), key=lambda t: t[1], reverse=True))
    bestk = list(islice(best.items(),k))

    #produce a csv return it
    csvdata = io.StringIO()
    writer = csv.writer(csvdata, delimiter=",")

    writer.writerow(("name", "degree"))
    for n in bestk:
        writer.writerow(n)

    output = make_response(csvdata.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=data_marvel.csv"
    output.headers["Content-type"] = "text/csv"
    return output

@app.route("/actors-heatmap/<int:k>")
def actorsHeatmap(k=40):

    g = tlp.loadGraph(FRNetworkURL)
    name = g.getStringProperty("name")
    viewMetric = g.getDoubleProperty("viewMetric")
    value = g.getIntegerProperty("value")

    degree = g.getDoubleProperty("degree")
    params = tlp.getDefaultPluginParameters("Degree", g)
    params['metric'] = value
    g.applyDoubleAlgorithm("Degree", degree, params)

    topActors = []
    actors = []

    i=0
    for n in viewMetric.getSortedNodes(ascendingOrder = False):
        if (i==k):
            break
        else:
            i = i+1
            topActors.append(n)
            actor = {}
            actor['name'] = name[n]
            actors.append(actor)

    data = []
    for i in range(k):
        sum = 0
        for j in range(k):
            row = {}
            row['actor1'] = name[topActors[i]]
            row['actor2'] = name[topActors[j]]
            row['collaborations'] = 0
            for e in g.getEdges(topActors[i], topActors[j]):
                row['collaborations'] += value[e]
                sum += value[e]
            for e in g.getEdges(topActors[j], topActors[i]):
                row['collaborations'] += value[e]
                sum += value[e]
            data.append(row)
        data[i*k+i]['collaborations'] = sum # diagonal values
        actors[i]['count'] = sum

    return render_template("acteurs_heatmap.html",
        title = "Heatmap des acteurs et actrices français(es) les plus prolifiques",
        actors = actors,
        data=data)

@app.route("/films/<acteur>")
def films(acteur="Jean Reno"):

    # load graph data
    mainGraph = tlp.loadGraph(FRCinemaURL)
    name = mainGraph.getStringProperty("name")
    viewSelection = mainGraph.getBooleanProperty("viewSelection")
    viewSelection.setAllNodeValue(False)

    # Subgraph corresponding to the actor in parameter
    i = 0
    for n in name.getNodesEqualTo(acteur):
        i = i+1
        viewSelection[n] = True
    if (i == 0):
        return 'There was a problem generating a graph for actor '+acteur

    params = tlp.getDefaultPluginParameters('Reachable SubGraph', mainGraph)

    params['edge direction'] = "all edges"
    params['distance'] = 2

    mainGraph.applyBooleanAlgorithm('Reachable SubGraph', params)
    mainGraph.addSubGraph(viewSelection, name="acteurd2")
    g = mainGraph.getSubGraph("acteurd2")

    # specific film data
    actorID = g.getIntegerProperty("actorID")
    name = g.getStringProperty("name")
    #budget = g.getIntegerProperty("budget")
    #filmID = g.getIntegerProperty("filmID")
    #original_language = g.getStringProperty("original_language")
    original_title = g.getStringProperty("original_title")
    #popularity = g.getDoubleProperty("popularity")
    #release_date = g.getStringProperty("release_date")
    #revenue = g.getDoubleProperty("revenue")
    #runtime = g.getIntegerProperty("runtime")
    #vote_average = g.getDoubleProperty("vote_average")
    #vote_count = g.getIntegerProperty("vote_count")

    # useful tulip data
    #viewColor = g.getColorProperty("viewColor")
    #viewIcon = g.getStringProperty("viewIcon")
    #viewLabel = g.getStringProperty("viewLabel")
    viewMetric = g.getDoubleProperty("viewMetric")
    viewSelection = g.getBooleanProperty("viewSelection")

    # Creates a D3-readable graph
    g.applyDoubleAlgorithm("Degree", viewMetric)

    nodes = []
    links = []

    for n in g.getNodes():
        dict = {}
        dict["id"] = original_title[n] if (actorID[n] == 0) else name[n]
        dict["degree"] = viewMetric[n]
        dict["name"] = name[n]
        dict["original_title"] = original_title[n]
        nodes.append(dict)

    for e in g.getEdges():
        dict = {}
        dict["source"] = original_title[g.source(e)] if (actorID[g.source(e)] == 0) else name[g.source(e)]
        dict["target"] = original_title[g.target(e)] if (actorID[g.target(e)] == 0) else name[g.target(e)]
        links.append(dict)

    graph = {}
    graph['links'] = links
    graph['nodes'] = nodes

    return render_template("acteur_films.html",
        title="Les Films de "+acteur,
        acteur=acteur,
        graph=graph)

@app.route("/wordcloud1")
def wordcloud1():   # first word cloud (csv)
    return render_template("wordcloud1.html",
        title="The Marvel Universe")

@app.route("/wordcloud2")
def wordcloud2():   # second word cloud (csv)
    return render_template("wordcloud2.html",
        title="The Marvel Universe")

@app.route("/")
def index():
    return redirect(url_for("actorsHeatmap", k=40))

if __name__ == "__main__":
   app.run(debug=True)
