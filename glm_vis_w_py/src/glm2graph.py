from pyvis.network import Network
import os
import sys
import pathlib
import glm

#This method genrates a title containing all the attributes belonging to an edge or node
def getTitle(attributes):
    titleStr = ""
    for k , v in attributes.items():
        titleStr = titleStr + str(k) + ": " + str(v) + "\n"
    return titleStr

def glm2graph(file_path):
    """_summary_
        This method will take a file path containing a glm file and its includes files
        and generate a static html file contating the visualisation of the glm file.

    Args:
        file_path (String): Args should be a path containing a glm file
        with included files aswell.

    Returns:
        html file: The method will generate a html file that will automatically open in 
        a browser displaying the generated graph. 
    """
    g = Network(height = "100%",width="100%", heading="Power Grid Model Visualizaiton",
                bgcolor="white", font_color="black")
                        
    edge_types = ["overhead_line", "switch", "underground_line", "series_reactor", "triplex_line", "regulator","transformer"]
    node_types = ["load", "triplex_load","capacitor", "node", "triplex_node", "substation", "meter", "triplex_meter","inverter", "diesel_dg"]  
    parent_child_edge_types = ["capacitor", "triplex_meter", "triplex_load", "meter"]

    node_options = {"load": {"color": "#edf2f4", "borderWidth": 6, "shape": "circularImage", "image": "./imgs/node.png"},
                    "triplex_load": {"color": "#ffea00", "borderWidth": 6, "shape": "circularImage","image": "./imgs/node.png"},
                    "capacitor": {"color": "#283618", "borderWidth": 6, "shape": "circularImage","image": "./imgs/capacitor.webp"},
                    "triplex_node": {"color": "#003566", "borderWidth": 6, "shape": "circularImage","image": "./imgs/node.png"},
                    "substation": {"color": "#fca311", "borderWidth": 6, "shape": "circularImage","image": "./imgs/substation.jpg"},
                    "triplex_meter": {"color": "#072ac8", "borderWidth": 6, "shape": "circularImage","image": "./imgs/meter.jpg"},
                    "node": {"color": "#4361ee", "borderWidth": 6, "shape": "circularImage", "image": "./imgs/node.png"},
                    "meter": {"color": "#d90429", "borderWidth": 6, "shape": "circularImage", "image": "./imgs/meter.jpg"},
                    "inverter": {"color": "#c8b6ff", "borderWidth": 6, "shape": "circularImage", "image": "./imgs/inverter.jpg"},
                    "diesel_dg": {"color": "#fee440", "borderWidth": 6, "shape": "circularImage", "image": "./imgs/dieselgen.jpg"}}

    edge_options = {"overhead_line": {"width": 4, "color": "#000000"},
                    "switch": {"width": 4, "color": "#3a0ca3"},
                    "series_reactor": {"width": 4, "color": "#8c0000"},
                    "triplex_line": {"width": 4, "color": "#c86bfa"},
                    "underground_line": {"width": 4, "color": "#FFFF00"},
                    "regulator": {"width": 4, "color": "#ff447d"},
                    "transformer": {"width": 4, "color": "#00FF00"}}
    
    included_files = []

    path = file_path.replace("\\", "/") #replace the path's backward slashes with forward slashes for python
    
    with open (file_path, "r") as glm_file:
        data = glm.load(glm_file)
        includes = data["includes"]
        objects = data["objects"]

        for k in includes: included_files.append("/" + k["value"])
        
        parent_path = pathlib.Path(file_path).parent.resolve() # get the parent path of the original glm file
        index = 0
        
        for f in included_files:
            file_path = str(parent_path) + f
            
            if os.path.isfile(file_path):
                included_files[index] = file_path
            else:
                print("Include files are not in the same path.")
                exit() #script will end if one or more of the includes files are not in the same path
            index += 1
        
        #gather all nodes from file    
        for obj in objects:
            obj_type = obj["name"].split(":")[0]
            attr = obj["attributes"]
            
            if obj_type in node_types:
                node_id = attr["name"]
                g.add_node(node_id, color = node_options[obj_type]["color"],
                                    borderWidth = node_options[obj_type]["borderWidth"],
                                    shape = node_options[obj_type]["shape"], image = node_options[obj_type]["image"],
                                    title = f"Object Type: {obj_type}\n" + getTitle(attr))
    
    #gather all nodes from included files
    for incl_file in included_files:
            with open (incl_file, "r") as glm_file:
                data = glm.load(glm_file)
                objects = data["objects"]
                
                for obj in objects:
                    obj_type = obj["name"].split(":")[0]
                    attr = obj["attributes"]
                    
                    if obj_type in node_types:
                        node_id = attr["name"]
                        g.add_node(node_id, color = node_options[obj_type]["color"],
                                            borderWidth = node_options[obj_type]["borderWidth"],
                                            shape = node_options[obj_type]["shape"], image = node_options[obj_type]["image"],
                                            title = f"Object Type: {obj_type}\n" + getTitle(attr))

    #create all edges from the passed file
    with open (path, "r") as glm_file:
        data = glm.load(glm_file)
        objects = data["objects"]
        
        for obj in objects:
            obj_type = obj["name"].split(":")[0]
            attr = obj["attributes"]
            
            if obj_type in edge_types:
                edge_from = attr["from"].split(":")[1] if ":" in attr["from"] else attr["from"]
                edge_to = attr["to"].split(":")[1] if ":" in attr["to"] else attr["to"]
                
                g.add_edge(edge_from, edge_to, color = edge_options[obj_type]["color"],
                                               width = edge_options[obj_type]["width"],
                                               title = f"Object Type: {obj_type}\n" + getTitle(attr))
            elif obj_type in parent_child_edge_types:#create parent - child edges 
                try:
                    node_id = attr["name"]
                    parent = attr["parent"]
                    g.add_edge(parent,node_id)
                except:
                    pass

    #Create all edges from included files are parent - child 
    for incl_file in included_files:
        with open (incl_file,"r") as glm_file:
            data = glm.load(glm_file)
            objects = data["objects"]
            
            for obj in objects:
                obj_type = obj["name"].split(":")[0]
                attr = obj["attributes"]
                
                if obj_type in node_types:
                    node_id = attr["name"]
                    parent = attr["parent"]
                    g.add_edge(parent,node_id)
    
    #These options were generated from the show buttons function in pyvis after configuring them
    g.set_options("""const options = {
                        "configure": {
                            "enabled": true,
                            "filter": "physics"
                        },
                        "edges": {
                            "smooth": {
                                "enabled": true,
                                "type": "dynamic"
                            }
                        },
                        "interaction": {
                            "hideEdgesOnDrag": true,
                            "hideEdgesOnZoom": true
                        },
                        "physics": {
                            "enabled": true,
                            "barnesHut": {
                            "gravitationalConstant": -30000,
                            "centralGravity": 0,
                            "springConstant": 0.18
                            },
                            "maxVelocity": 150,
                            "minVelocity": 0.75
                        }
                        }
                    """)
    g.show("Graph.html")

# if __name__ == "__main__":
#     glm2graph(sys.argv[1])
glm2graph("data\\IEEE-123_Dynamic_fixed.glm")