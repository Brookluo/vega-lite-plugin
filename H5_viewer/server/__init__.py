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
from girder.api.rest import boundHandler

class HDF5Item(Resource):

    #TODO: Access Control here, right now test only use the public
    # should be user according to requirement
    @access.public(scope = TokenScope.DATA_READ)
    @autoDescribeRoute(
        Description('') #TODO
        .modelParam('id', 'The item ID',
                    model = 'item', level = AccessType.READ, paramType = 'path')
        .param()
        .errorResponse() #TODO
    )
    def getH5(self, item):
        files = list(ModelImporter.model('item').childFiles(item))
        retval = []
        for i in enumerate(files):
            if h5py.File(i,'r').dims <= 1:
                retval['data'] = getData(i, 'amp')
                retval['meta'] = getMeta(i)
                retval.append(i)
        return retval


def getMeta(name):
    h5f = h5py.File(name,'r')
    return dict(zip(list(h5f.attrs), list(h5f.attrs.values())))


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

    #print(ds_name)
    #print(name)

    data_set = h5f[ds_name]
    x_value = list(x for x in data_set['X'])
    y_value = list(y for y in data_set['Y'])
    #there exists single value without pair
    if len(x_value) != len(y_value):
        return None

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

def process_file(f):
    f['data'] = getData(f, 'amp')
    f['metadata'] = getMeta(f)
    return ModelImporter.model('file').save(f)

@access.public
@boundHandler
def handler(event):
    process_file(event.info['file'])

#TODO: find the way to solve the options
def load(info):
    events.bind('data_process', 'H5_viewer', handler)
    h5_create  = H5Graph()
    info['apiRoot'].item.route('GET', (':id', 'hdf5'),
        h5_create.getH5)
