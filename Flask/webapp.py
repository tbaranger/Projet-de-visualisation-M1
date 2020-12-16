import os
from flask import *
import io
import csv
import json
from collections import OrderedDict
from itertools import islice
from datetime import datetime
import numpy as np

from tulip import tlp

# NE PAS MODIFIER LA LIGNE SUIVANTE
app = Flask(__name__)

# List of graph files
root = os.path.realpath(os.path.dirname(__file__))
#marvelURL = os.path.join(root, "static/data/marvel", "marvel.tlpb")
#FRCinemaURL = os.path.join(root, "static/data/movies", "cinema.francophone2.tlpb")
#FRNetworkURL = os.path.join(root, "static/data/movies", "french.actors.network.tlpb")
#communitiesURL = os.path.join(root, "static/data/movies", "communities.tlpb")
#mainNetworkURL = os.path.join(root, "static/data/movies", "french.actors.network.main.tlpb")

# Windows
marvelURL = r"static\data\marvel\marvel.tlpb"
FRCinemaURL = r"static\data\movies\cinema.francophone2.tlpb"
FRNetworkURL = r"static\data\movies\french.actors.network.tlpb"
communitiesURL = r"static\data\movies\communities.tlpb"
mainNetworkURL = r"static\data\movies\french.actors.network.main.tlpb"

# Fonctions de traitement de données

def parseYears(dates,annees):

    deb=2020
    fin=0

    dateFormatter1="%d/%m/%Y"
    dateFormatter2="%Y-%m-%d"

    for film in dates:
        if "/" in dates[film]:
            dates[film]=datetime.strptime(dates[film],dateFormatter1)
            annees[film]=str(dates[film])[0:4]
            annees[film]=int(datetime.strptime(annees[film],"%Y").year)
            deb=annees[film] if annees[film]<deb else deb
            fin=annees[film] if annees[film]>fin else fin
        elif "-" in dates[film]:
            dates[film]=datetime.strptime(dates[film],dateFormatter2)
            annees[film]=str(dates[film])[0:4]
            annees[film]=int(datetime.strptime(annees[film],"%Y").year)

    return(deb,fin,annees)

def convertGraphToD3Static(url):
    g = tlp.loadGraph(url)
    name = g.getStringProperty("name")
    viewLayout = g.getLayoutProperty("viewLayout")

    nodes = []
    links = []

    for n in g.getNodes():
        dict = {}
        dict["id"] = name[n]
        dict["x"] = viewLayout[n][0]
        dict["y"] = viewLayout[n][1]
        nodes.append(dict)

    for e in g.getEdges():
        dict = {}
        source = {}
        target = {}
        source["x"] = viewLayout[g.source(e)][0]
        source["y"] = viewLayout[g.source(e)][1]
        target["x"] = viewLayout[g.target(e)][0]
        target["y"] = viewLayout[g.target(e)][1]
        dict["source"] = source
        dict["target"] = target
        links.append(dict)

    graph = {}
    graph['links'] = links
    graph['nodes'] = nodes

    return graph

# Routes

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
    k=40 if k<10 or k>80 else k

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
        title = "Heatmap des acteurs et actrices francophones les plus prolifiques",
        actors = actors,
        data=data)

@app.route("/films/<acteur>")
def films(acteur="Jean Reno"):

    # load graph data
    mainGraph = tlp.loadGraph(FRCinemaURL)
    name = mainGraph.getStringProperty("name")
    viewSelection = mainGraph.getBooleanProperty("viewSelection")
    viewSelection.setAllNodeValue(False)
    viewMetric = mainGraph.getDoubleProperty("viewMetric")
    mainGraph.applyDoubleAlgorithm("Degree", viewMetric)

    names = []

    for n in mainGraph.getNodes():
        if name[n]!="" and viewMetric[n]>1:
            names.append(name[n])

    names = np.sort(names)

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
    release_date = g.getStringProperty("release_date")
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
        dict['date'] = release_date[n]
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
        graph=graph,
        nodelink=True,
        names = names)

@app.route("/communities")
def communities():

    # load graph data
    g1 = convertGraphToD3Static(communitiesURL)
    g2 = convertGraphToD3Static(mainNetworkURL)

    return render_template("communities.html",
        title="Communautés du cinéma francophone",
        graph=g1,
        network=g2)

@app.route("/wordcloud1")
def wordcloud1():   # first word cloud (csv)
    return render_template("wordcloud1.html",
        title="The Marvel Universe")

@app.route("/wordcloud2")
def wordcloud2():   # second word cloud (csv)
    return render_template("wordcloud2.html",
        title="The Marvel Universe")

@app.route("/data_movies_nbfilms")
def data_movies_nbfilms():
    g = tlp.loadGraph(FRCinemaURL)

    release_date = g.getStringProperty("release_date")
    original_title = g.getStringProperty("original_title")

    dates={}
    annees={}

    for n in g.getNodes():
        if (original_title[n]!=""):
            dates[original_title[n]] = release_date[n]
            annees[original_title[n]] = release_date[n]

    deb,fin,annees = parseYears(dates,annees)

    nb_films=[]
    for a in range(deb,fin):
        nb=0
        for film in annees:
            if annees[film]==a:
                nb=nb+1
        nb_films.append(nb)

    #csv
    csvdata = io.StringIO()
    writer = csv.writer(csvdata, delimiter=",")

    writer.writerow(("year", "value"))
    for n in range(deb,fin):
       writer.writerow((n,nb_films[n-deb]))

    output = make_response(csvdata.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=data_movies.csv"
    output.headers["Content-type"] = "text/csv"
    return output

@app.route("/data_movies_budget")
def data_movies_budget():
    g = tlp.loadGraph(FRCinemaURL)
    release_date = g.getStringProperty("release_date")
    original_title = g.getStringProperty("original_title")
    budget = g.getIntegerProperty("budget")

    dates={}
    annees={}
    budget_films={}

    for n in g.getNodes():
        if (original_title[n]!="" and budget[n]>0):
            dates[original_title[n]] = release_date[n]
            annees[original_title[n]] = release_date[n]
            budget_films[original_title[n]] = budget[n]

    deb,fin,annees = parseYears(dates,annees)

    budgets_moyens=[]
    for a in range(deb,fin):
        budgets_moyens.append([])
        for film in annees:
            if annees[film]==a:
                budgets_moyens[a-deb].append(budget_films[film])

    for a in range(fin-deb):
        budgets_moyens[a]=sum(budgets_moyens[a])/len(budgets_moyens[a]) if len(budgets_moyens[a])!=0 else 0

    #csv
    csvdata = io.StringIO()
    writer = csv.writer(csvdata, delimiter=",")

    writer.writerow(("year", "value"))
    for n in range(deb,fin):
        if(budgets_moyens[n-deb]!=0):
            writer.writerow((n,budgets_moyens[n-deb]))

    output = make_response(csvdata.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=data_movies_budget.csv"
    output.headers["Content-type"] = "text/csv"

    return output

@app.route("/data_movies_runtime")
def data_movies_runtime():
    g = tlp.loadGraph(FRCinemaURL)
    release_date = g.getStringProperty("release_date")
    original_title = g.getStringProperty("original_title")
    runtime = g.getIntegerProperty("runtime")

    dates={}
    annees={}
    runtime_films={}

    for n in g.getNodes():
        if (original_title[n]!="" and runtime[n]>0):
            dates[original_title[n]] = release_date[n]
            annees[original_title[n]] = release_date[n]
            runtime_films[original_title[n]] = runtime[n]

    deb,fin,annees = parseYears(dates,annees)

    runtime_moyens=[]
    for a in range(deb,fin):
        runtime_moyens.append([])
        for film in annees:
            if annees[film]==a:
                runtime_moyens[a-deb].append(runtime_films[film])

    for a in range(fin-deb):
        runtime_moyens[a]=sum(runtime_moyens[a])/len(runtime_moyens[a]) if len(runtime_moyens[a])!=0 else 0

    #csv
    csvdata = io.StringIO()
    writer = csv.writer(csvdata, delimiter=",")

    writer.writerow(("year", "value"))
    for n in range(deb,fin):
        if(runtime_moyens[n-deb]!=0):
            writer.writerow((n,runtime_moyens[n-deb]))

    output = make_response(csvdata.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=data_movies_runtime.csv"
    output.headers["Content-type"] = "text/csv"

    return output

@app.route("/predicting-profits")
def predicting_profits():
    g = tlp.loadGraph(FRCinemaURL)

    budget = g.getIntegerProperty("budget")
    original_title = g.getStringProperty("original_title")
    popularity = g.getDoubleProperty("popularity")
    release_date = g.getStringProperty("release_date")
    revenue = g.getDoubleProperty("revenue")
    runtime = g.getIntegerProperty("runtime")
    vote_average = g.getDoubleProperty("vote_average")
    vote_count = g.getIntegerProperty("vote_count")

    nb_films=0
    for n in g.getNodes():
        if original_title[n]!="" :
            if popularity[n]>0 and runtime[n]>0 and vote_average[n]>0 and vote_count[n]>0 :
                nb_films=nb_films+1
    return str(nb_films)

@app.route("/nbfilms-scatter")
def nbfilms_scatter():
    return render_template("nbfilms-scatter.html",
        title="Nombre de films par année")

@app.route("/budget-scatter")
def budget_scatter():
    return render_template("budget-scatter.html",
        title="Budget moyen des films par année")

@app.route("/runtime-scatter")
def runtime_scatter():
    return render_template("runtime-scatter.html",
        title="Durée moyenne des films par année")

@app.route("/")
def index():
    return redirect(url_for("films", acteur="François Cluzet"))

if __name__ == "__main__":
   app.run(debug=True)
