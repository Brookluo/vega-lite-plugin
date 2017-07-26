import h5py
import six
import json
import requests
import pandas as pd
from vega import VegaLite as vl
import tempfile

from girder.utility.model_importer import ModelImporter
from girder.api.rest import Resource
from girder.api.rest import
from girder import events
from girder.api import access
from girder.api.describe import Description, autoDescribeRoute
from girder.constants import AccessType, TokenScope

class H5Graph(Resource):

    #TODO: Access Control here, right now test only use the public
    # should be user according to requirement
    @access.public(scope = TokenScope.DATA_READ)
    @autoDescribeRoute(
        Description('') #TODO
        .modelParam('id', 'The item ID',
                    model = 'item', level = AccessType.READ, paramType = 'path')
        .param('selection', 'The selection of either phase or amp to show',
                required = True)
        .param('dash', 'syntax for the name of data-sets ',
                required = False, dataType = 'boolean', default = False)
        .param('l_value', 'syntax for the name of data-sets',
                required = False, default = 2)
        .param('m_value', 'syntax for the name of data-sets',
                required = False, default = 2)
        .errorResponse() #TODO
    )
    def graph_gene(self, selection, dash, l_value, m_value):
        data = getData(self, selection, dash, l_value, m_value) #TODO
        with open(tempfile.TemporaryFile) as tmp:
            create_json(tmp, data)
            vega_obj = graph_generator(tmp)
            #TODO: to generate the graph, using either vega obj or json
        return vega_obj






def getData(name, selection, dash = False, l_value = 2, m_value = 2):
    h5f = h5py.File(name, 'r')
    selection = selection.lower().strip()

    if selection != "phase" and selection != "amp":
        print("wrong selection")
        return None
    elif dash == False:
        ds_name = "{}_l{}_m{}".format(selection, l_value, m_value)
    else:
        ds_name = "{}_l{}_m-{}".format(selection, l_value, m_value)

    print(ds_name)
    print(name)

    data_set = h5f[ds_name]
    x_value = list(x for x in data_set['X'])
    y_value = list(y for y in data_set['Y'])
    #there exists single value without pair
    if len(x_value) != len(y_value):
        return None

    #print(len(x_value))
    #print(len(y_value))

    data = {}

    data['values'] = list({'x' : x_value.pop(), 'y' : y_value.pop()} for num in range(len(x_value)))
    #data['names'] = ds_name

    return data

def create_json(target, data, full_syntax = True, mark = "line"):
    if full_syntax:
        jfile = {}
        jfile['data'] = data
        jfile['mark'] = mark
        jfile['encoding'] = {"x":{"field":"x", "type": "quantitative"},
                             "y":{"field":"y", "type": "quantitative"}}
                             #"color":{"field": "Category", "type": "nominal"}}
        jfile['$schema'] = "https://vega.github.io/schema/vega-lite/v3.json"
    else:
        jfile = data

    if jfile != None:
        with open(target, 'w') as write_file:
            json.dump(jfile, write_file)

#graph generator
def graph_generator(f, width = 400, height = 400):
    #TODO:check the whether file  contain a string, if not directly readout
    with open(f, 'r') as fp:
        jfile = json.load(fp)

        if jfile.get('values'):
            data = jfile['values']
            print('get here')
        elif jfile.get('data'):
            data = jfile['data']['values']
        else:
            data = jfile

        with open(tempfile.TemporaryFile) as temp:
            json.dump(data, temp)
            readout = pd.read_json(temp) #TODO could optimize here with vegalite
            graph = vl({
                "width": width,
                "height": height,
                "mark" : "line",
                "encoding": {
                    "x":{
                        "field":"x",
                        "type": "quantitative"
                    },
                    "y":{
                        "field":"y",
                        "type": "quantitative"
                    }
                    }
                },readout)
        #graph.display()
        return graph

def handler(event):





#TODO: find the way to solve the options
def load(info):
    events.bind('data_process', 'Vega-lite visulization', handler)
    h5_create  = H5Graph()
    info['apiRoot'].item.route('GET', (':id', 'dicom'),
        h5_create.graph_gene)
