# python3 generate_graph.py --graph graph.config --setup setup.config
#import argparse
#
#graph_parser = argparse.ArgumentParser()
#graph_parser.add_argument('--graph', required=True, type=str)
#graph_parser.add_argument('--setup', required=True, type=str)
#
#args = graph_parser.parse_args()
#
#GRAPH_CONFIG_NAME = args.graph # "graph.config"
#SETUP_CONFIG_NAME = args.setup # "setup.config"

def main(SETUP_CONFIG_NAME, GRAPH_CONFIG_NAME):
    CAMERA_NUM = 16
    GRAPH_ID = 102
    PYTHON_OPENCV_PORT = 7200
    PYTHON_JSON_PORT = 8070
    
    f_setup = open(SETUP_CONFIG_NAME, "r")
    lines = f_setup.readlines()
    f_setup.close()
    for line in lines:
        if line.startswith("used_cam_num"):
            cam_num_line = line.split()
            CAMERA_NUM = int(cam_num_line[2])
        elif line.startswith("graph_id"):
            graph_id_line = line.split()
            GRAPH_ID = int(graph_id_line[2])
        elif line.startswith("python"):
            python_port_line = line.split()
            PYTHON_OPENCV_PORT = int(python_port_line[2])
        elif line.startswith("json"):
            json_port_line = line.split()
            PYTHON_JSON_PORT = int(json_port_line[2])
    
    STREAMPULLERID = 300
    VDEC = 1100
    SORT = 400
    MERGE = 2000
    MODEL_PATH = "./data/models/yolov3_b4.om" # "./data/models/yolov3-tiny_b4-gr.om"
    # Start graph.
    data = """graphs {
      graph_id: #_graph_id
      priority: 1
    """
    data = data.replace("#_graph_id", str(GRAPH_ID))
    
    # StreamPullerEngine.
    for i in range(CAMERA_NUM):
        data += """
      engines {
        id: #_engine_id
        engine_name: "#_engine_name"
        side: HOST
        thread_num: 1
        ai_config {
          items {
            name: "init_config"
            value: ""
          }
          items {
            name: "channel_id"
            value: '#_channel_id'
          }
        }
      }
        """
        data = data.replace("#_engine_id", str(STREAMPULLERID+i))
        data = data.replace("#_engine_name", "StreamPullerEngine")
        data = data.replace("#_channel_id", str(i))
    
    # VdecEngine.
    for i in range(CAMERA_NUM):
        data += """
      engines {
        id: #_engine_id
        engine_name: "#_engine_name"
        side: DEVICE
        thread_num: 1
        so_name: "./device/libVdecEngine.so"
        ai_config {
          items {
            name: "init_config"
            value: ""
          }
          items {
            name: "passcode"
            value: ""
          }
        }
      }
        """
        data = data.replace("#_engine_id", str(VDEC+i))
        data = data.replace("#_engine_name", "VdecEngine")
    
    # SORTEngine.
    for i in range(CAMERA_NUM):
        data += """
      engines {
        id: #_engine_id
        engine_name: "#_engine_name"
        side: DEVICE
        thread_num: 1
        so_name: "./device/libSORTEngine.so"
        ai_config {
          items {
            name: "init_config"
            value: ""
          }
          items {
            name: "passcode"
            value: ""
          }
          items {
            name: "continuityThreshold"
            value: "1"
          }
          items {
            name: "adjacencyThreshold"
            value: "0.15"
          }
          items {
            name: "trackThreshold"
            value: "0.6"
          }
        }
      }
        """
        data = data.replace("#_engine_id", str(SORT+i))
        data = data.replace("#_engine_name", "SORTEngine")
    
    # Detection.
    data += """
      engines {
        id: #_engine_id
        engine_name: "#_engine_name"
        side: DEVICE
        thread_num: 1
        so_name: "./device/libgomp.so"
        so_name: "./device/libObjectDetectionEngine.so"
        ai_config {
          items {
            name: "model"
            value: "#_model_path"
          }
          items {
            name: "init_config"
            value: ""
          }
          items {
            name: "passcode"
            value: ""
          }
          items {
            name: "batch_size"
            value: "#_batch_size"
          }
          items {
            name: "input_channel"
            value: "3"
          }
          items {
            name: "input_width"
            value: "#_input_width"
          }
          items {
            name: "input_height"
            value: "#_input_height"
          }
          items {
            name: "max_object_num_per_frame"
            value: "#_max_object_num_per_frame"
          }
        }
      }
        """
    data = data.replace("#_engine_id", str(1001))
    data = data.replace("#_engine_name", "ObjectDetectionEngine")
    data = data.replace("#_model_path", MODEL_PATH)
    data = data.replace("#_batch_size", str(4))
    data = data.replace("#_input_width", str(416))
    data = data.replace("#_input_height", str(416))
    data = data.replace("#_max_object_num_per_frame", str(20))
    
    # StreamDataOutput.
    data += """
      engines {
        id: #_engine_id
        engine_name: "#_engine_name"
        side: HOST
        thread_num: 1
        ai_config {
          items {
            name: "json_port"
            value: "#_json_port"
          }
          items {
            name: "python_port"
            value: "#_python_port"
          }
          items {
            name: "rtsp_link"
            value: "#_rtsp_link"
          }
          items {
            name: "feature_lib_path"
            value: "./data/featurelib/Featurelib.bin"
          }
          items {
            name: "feature_len"
            value: "512"
          }
          items {
            name: "feature_num"
            value: "#_feature_num"
          }
        }
      }
        """
    data = data.replace("#_json_port", str(PYTHON_JSON_PORT))
    data = data.replace("#_python_port", str(PYTHON_OPENCV_PORT))
    data = data.replace("#_engine_id", str(3000))
    data = data.replace("#_engine_name", "StreamDataOutputEngine")
    data = data.replace("#_rtsp_link", "rtsp://127.0.0.1/live.sdp")
    data = data.replace("#_feature_num", str(5))
    
    
    # StreamPullerEngine.
    for i in range(CAMERA_NUM):
        data += """
      engines {
        id: #_engine_id
        engine_name: "#_engine_name"
        side: HOST
        thread_num: 1
      }
        """
        data = data.replace("#_engine_id", str(MERGE+i))
        data = data.replace("#_engine_name", "MergeEngine")
        data = data.replace("#_channel_id", str(i))
    
    # Connects.
    # StreamPuller->Vdec.
    for i in range(CAMERA_NUM):
        data += """
      connects {
        src_engine_id: #_src_engine_id
        src_port_id: #_src_port_id
        target_engine_id: #_target_engine_id
        target_port_id: #_target_port_id
      }
        """
        data = data.replace("#_src_engine_id", str(STREAMPULLERID+i))
        data = data.replace("#_src_port_id", str(0))
        data = data.replace("#_target_engine_id", str(VDEC+i))
        data = data.replace("#_target_port_id", str(0))
    
    # Vdec->Detection.
    for i in range(CAMERA_NUM):
        data += """
      connects {
        src_engine_id: #_src_engine_id
        src_port_id: #_src_port_id
        target_engine_id: #_target_engine_id
        target_port_id: #_target_port_id
      }
        """
        data = data.replace("#_src_engine_id", str(VDEC+i))
        data = data.replace("#_src_port_id", str(0))
        data = data.replace("#_target_engine_id", str(1001))
        data = data.replace("#_target_port_id", str(0))
    
    # Detection->SORT.
    for i in range(CAMERA_NUM):
        data += """
      connects {
        src_engine_id: #_src_engine_id
        src_port_id: #_src_port_id
        target_engine_id: #_target_engine_id
        target_port_id: #_target_port_id
      }
        """
        data = data.replace("#_src_engine_id", str(1001))
        data = data.replace("#_src_port_id", str(i))
        data = data.replace("#_target_engine_id", str(SORT+i))
        data = data.replace("#_target_port_id", str(0))
    
    
    # SORT->Merge.
    for i in range(CAMERA_NUM):
        data += """
      connects {
        src_engine_id: #_src_engine_id
        src_port_id: #_src_port_id
        target_engine_id: #_target_engine_id
        target_port_id: #_target_port_id
      }
        """
        data = data.replace("#_src_engine_id", str(SORT+i))
        data = data.replace("#_src_port_id", str(0))
        data = data.replace("#_target_engine_id", str(MERGE+i))
        data = data.replace("#_target_port_id", str(0))
    
    # Merge->StreamOutput.
    for i in range(CAMERA_NUM):
        data += """
      connects {
        src_engine_id: #_src_engine_id
        src_port_id: #_src_port_id
        target_engine_id: #_target_engine_id
        target_port_id: #_target_port_id
      }
        """
        data = data.replace("#_src_engine_id", str(MERGE+i))
        data = data.replace("#_src_port_id", str(0))
        data = data.replace("#_target_engine_id", str(3000))
        data = data.replace("#_target_port_id", str(0))
    
    # Vdec->StreamOutput.
    for i in range(CAMERA_NUM):
        data += """
      connects {
        src_engine_id: #_src_engine_id
        src_port_id: #_src_port_id
        target_engine_id: #_target_engine_id
        target_port_id: #_target_port_id
      }
        """
        data = data.replace("#_src_engine_id", str(VDEC+i))
        data = data.replace("#_src_port_id", str(1))
        data = data.replace("#_target_engine_id", str(3000))
        data = data.replace("#_target_port_id", str(1))
    
    # End graph.
    data += """
    }
    """
    
    lines = data.split('\n')
    
    graph_config = open(GRAPH_CONFIG_NAME, 'w')
    for line in lines:
        graph_config.writelines(line)
        graph_config.writelines('\n')
    graph_config.close()
