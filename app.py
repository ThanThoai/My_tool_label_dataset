import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px
from skimage import io
import os
from dash.dependencies import Input, Output, State
import json

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

dir_img = "images/"
list_img = [os.path.join(dir_img, i) for i in os.listdir(dir_img)]
dir_anno = "anno"
json_check_path = 'check.json'
# print(len(dir_img))
if not os.path.isdir(dir_anno):
    os.mkdir(dir_anno)

data = None
if not os.path.isfile(json_check_path):
    with open(json_check_path, mode="w+") as j:
        data = {}
        for img in list_img:
            result = {
                "status" : 0,
                "num_ques" : 0
            }
            img_name = img.split('/')[-1].split('.')[0]
            data[img_name] = result
        json.dump(data, j)
else:
    data = json.load(open(json_check_path, 'r'))


def refesh_img(list_img, data):
    list_img_checked = []
    for img in list_img:
        # print(img)
        img_name = img.split('/')[-1].split('.')[0]
        # print(img_name)
        if not int(data[img_name]['status']):
            list_img_checked.append(img)
    return list_img_checked

list_img_checked = refesh_img(list_img, data)

img_index = 0
fig = px.imshow(io.imread(list_img_checked[img_index]), binary_backend="jpg")
TYPE_QUES = ['queryGlobal', 'verifyGlobal', 'chooseGlobal', 'queryAttr', 'verifyAttr', 'verifyAttrs', 'chooseAttr', 'exist', 'existRel', 'logicOr', 'logicAnd', 'queryObject', 'chooseObject', 'queryRel', 'verifyRel','chooseRel', 'chooseObjRel', 'compare', 'common', 'twoSame', 'twoDiff', 'allSame', 'allDiff']

app.layout = html.Div(
    [
        html.Div(
            [   
                html.Div(
                    [
                        html.H2("Image Show:"),
                        dcc.Graph(
                            id = "div-image",
                            figure = fig,
                        ),
                        html.Div(
                            id = "div-info", 
                            children = "", 
                            style = { 
                                'margin-left': '550px',
                                'margin-bottom': '10px',
                                'verticalAlign': 'middle'
                            }
                        )
                    ]
                ),
                html.Div(
                    [
                        html.Button("Prev", id = "btn-prev", n_clicks = 0),
                        html.Button("Next", id = "btn-next", n_clicks = 0),
                    ],
                    style = { 
                        'margin-left': '550px',
                        'margin-bottom': '10px',
                        'verticalAlign': 'middle'
                    }
                )
            ]
        ),
        html.Div(
            [   
                html.Div(
                    [
                        html.H5("Question type:"),
                        dcc.Dropdown(
                            id = "dp-ques", 
                            options = [{"label" : i, "value" : i} for i in TYPE_QUES],
                            style = {
                                'width': '220px',
                                'font-size': '90%',
                                'height': '40px',
                           }
                        ),
                        html.H5("Question: "),
                        # html.Br(),
                        dcc.Input(id = "ip-ques", type = "text"),
                        html.H5("Answer: "),
                        # html.Br(),
                        dcc.Input(id = "ip-ans", type = "text"),
                    ]
                ),
                html.Div(
                    [
                        html.Button("Save", id = "btn-save", n_clicks = 0),
                    ],
                    style = { 
                        'margin-left': '550px',
                        'margin-bottom': '10px',
                        'verticalAlign': 'middle'
                    }
                )
            ]
        )
    ]
)

@app.callback(
    Output("div-image", "figure"),
    Input("btn-prev", "n_clicks"),
    Input("btn-next", "n_clicks")
)
def updateimg(prev_clicks, next_clicks):
    global img_index
    global list_img_checked
    global data
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if "btn-prev" in changed_id:
        if img_index > 0:
            img_index -= 1
    elif "btn-next" in changed_id:
        if img_index < len(list_img_checked) - 1:
            img_index += 1
    fig = px.imshow(io.imread(list_img_checked[img_index]), binary_backend="jpg")
    return fig


@app.callback(
    Output("div-info", "children"),
    Input("btn-save", "n_clicks"),
    Input("dp-ques", "value"),
    Input("ip-ques", "value"),
    Input("ip-ans", "value")
)
def save(btn_save, type_ques, ques, ans):
    global data
    global img_index
    global list_img_checked
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if "btn-save" in changed_id:
        if len(ques) * len(ans) > 0:
            img_name = list_img_checked[img_index].split("/")[-1].split(".")[0]
            anno = None
            if not os.path.isfile(os.path.join(dir_anno, img_name + ".json")):
                with open(os.path.join(dir_anno, img_name + ".json"), 'w+') as f:
                    anno = {
                        "id" : img_name,
                        "result" : [],
                        "num_ques" : 1,
                    }
                    anno["result"].append({
                        "question" : ques,
                        "answer" : ans,
                        "type" : type_ques
                    })
                    json.dump(anno, f)
                    data[img_name]["num_ques"] += 1
                    return "Image has 1 questions!!!"
            else:
                anno = json.load(open(os.path.join(dir_anno, img_name + ".json"), 'r'))
                if img_name == anno["id"]:
                    anno["result"].append({
                        "question" : ques,
                        "answer" : ans,
                        "type" : type_ques
                    })
                    anno["num_ques"] += 1
                    json.dump(anno, open(os.path.join(dir_anno, img_name + ".json"), 'w+'))
                    data[img_name]["num_ques"] += 1
                    if data[img_name]["num_ques"] == 5:
                        data[img_name]["status"] = 1
                    json.dump(data, open(json_check_path, 'w+'))
                    list_img_checked = refesh_img(list_img_checked, data)
                    return "Image has %d question!!!" %(int(anno["num_ques"]))
                else:
                    return "ERROR!!"

        
        

if __name__ == '__main__':
    app.run_server(debug=False)