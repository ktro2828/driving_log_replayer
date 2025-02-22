# Evaluate perception(Camera)

The performance of Autoware's recognition function (perception) is evaluated by calculating mAP (mean Average Precision) and other indices from the recognition results.

Run the perception module and pass the output perception topic to the evaluation library for evaluation.

Currently, only one camera is supported.

## Preparation

### Model conversion

In perception evaluation, machine learning pre-trained models are used.
The models are automatically downloaded during set-up.
[tensorrt_yolox/CMakeList.txt](https://github.com/autowarefoundation/autoware.universe/blob/main/perception/tensorrt_yolox/CMakeLists.txt#L58)

The downloaded onnx file is not used as is, but is converted into a TensorRT engine file.
Commands for model conversion are available, so source the autoware workspace and execute the commands.
When the conversion command finishes, check that the engine file is output to the directory listed in [tensorrt_yolox.launch.xml](https://github.com/autowarefoundation/autoware.universe/blob/main/perception/tensorrt_yolox/launch/tensorrt_yolo.launch.xml#L6).

An example of the use of autowarefoundation's autoware.universe is shown below.

```shell
# If autoware is installed in $HOME/autoware
source ~/autoware/install/setup.bash
ros2 launch tensorrt_yolox yolox.launch.xml use_decompress:=false build_only:=true

# The engine file appears in ~/autoware/install/tensorrt_yolox/share/tensorrt_yolox/data/yolox-tiny.engine
```

### Modifying the launch file

To evaluate on a single PC, it is necessary to modify launch to output the recognition results of the camera.
Change launch as follows.

```shell
❯ vcs diff src/
.................................
diff --git a/launch/tier4_perception_launch/launch/object_recognition/detection/camera_lidar_fusion_based_detection.launch.xml b/launch/tier4_perception_launch/launch/object_recognition/detection/camera_lidar_fusion_based_detection.launch.xml
index 9ca8ea3df..a35e8d00f 100644
--- a/launch/tier4_perception_launch/launch/object_recognition/detection/camera_lidar_fusion_based_detection.launch.xml
+++ b/launch/tier4_perception_launch/launch/object_recognition/detection/camera_lidar_fusion_based_detection.launch.xml
@@ -30,6 +30,14 @@
   <arg name="remove_unknown" default="true"/>
   <arg name="trust_distance" default="30.0"/>

+  <group>
+    <include file="$(find-pkg-share tensorrt_yolox)/launch/yolox.launch.xml" />
+  </group>
+
+  <group>
+    <include file="$(find-pkg-share bytetrack)/launch/bytetrack.launch.xml" />
+  </group>
+
   <!-- Jetson AGX -->
   <!-- <include file="$(find-pkg-share tensorrt_yolo)/launch/yolo.launch.xml">
     <arg name="image_raw0" value="$(var image_raw0)"/>
diff --git a/launch/tier4_perception_launch/launch/perception.launch.xml b/launch/tier4_perception_launch/launch/perception.launch.xml
index 0a2ef57f6..9a9b06379 100644
--- a/launch/tier4_perception_launch/launch/perception.launch.xml
+++ b/launch/tier4_perception_launch/launch/perception.launch.xml
@@ -33,7 +33,7 @@
   <arg name="camera_info6" default="/sensing/camera/camera6/camera_info"/>
   <arg name="image_raw7" default="/sensing/camera/camera7/image_rect_color"/>
   <arg name="camera_info7" default="/sensing/camera/camera7/camera_info"/>
-  <arg name="image_number" default="6" description="choose image raw number(0-7)"/>
+  <arg name="image_number" default="1" description="choose image raw number(0-7)"/>
   <arg name="use_vector_map" default="true" description="use vector map in prediction"/>
   <arg name="use_pointcloud_map" default="true" description="use pointcloud map in detection"/>
   <arg name="use_object_filter" default="true" description="use object filter"/>
diff --git a/perception/tensorrt_yolox/launch/yolox.launch.xml b/perception/tensorrt_yolox/launch/yolox.launch.xml
index b697b1f50..b9cb53102 100644
--- a/perception/tensorrt_yolox/launch/yolox.launch.xml
+++ b/perception/tensorrt_yolox/launch/yolox.launch.xml
@@ -1,7 +1,7 @@
 <?xml version="1.0"?>
 <launch>
   <arg name="input/image" default="/sensing/camera/camera0/image_rect_color"/>
-  <arg name="output/objects" default="/perception/object_recognition/detection/rois0"/>
+  <arg name="output/objects_yolox" default="/perception/object_recognition/detection/rois0"/>
   <arg name="model_name" default="yolox-tiny"/>
   <arg name="model_path" default="$(find-pkg-share tensorrt_yolox)/data"/>
   <arg name="score_threshold" default="0.35"/>
@@ -16,7 +16,7 @@

   <node pkg="tensorrt_yolox" exec="tensorrt_yolox_node_exe" name="tensorrt_yolox" output="screen">
     <remap from="~/in/image" to="$(var input/image)"/>
-    <remap from="~/out/objects" to="$(var output/objects)"/>
+    <remap from="~/out/objects" to="$(var output/objects_yolox)"/>
     <param name="score_threshold" value="$(var score_threshold)"/>
     <param name="nms_threshold" value="$(var nms_threshold)"/>
     <param name="model_path" value="$(var model_path)/$(var model_name).onnx"/>
```

Currently, only camera No.0 can be evaluated, so if you want to evaluate other cameras, swap the camera numbers. The following example shows how to swap 0 and 3

```shell
--- a/launch/tier4_perception_launch/launch/perception.launch.xml
+++ b/launch/tier4_perception_launch/launch/perception.launch.xml
@@ -17,14 +17,14 @@
   <arg name="input/pointcloud" default="/sensing/lidar/concatenated/pointcloud" description="The topic will be used in the detection module"/>
   <arg name="mode" default="camera_lidar_fusion" description="options: `camera_lidar_radar_fusion`, `camera_lidar_fusion`, `lidar_radar_fusion`, `lidar` or `radar`"/>
   <arg name="lidar_detection_model" default="centerpoint" description="options: `centerpoint`, `apollo`, `pointpainting`, `clustering`"/>
-  <arg name="image_raw0" default="/sensing/camera/camera0/image_rect_color" description="image raw topic name"/>
-  <arg name="camera_info0" default="/sensing/camera/camera0/camera_info" description="camera info topic name"/>
+  <arg name="image_raw0" default="/sensing/camera/camera3/image_rect_color" description="image raw topic name"/>
+  <arg name="camera_info0" default="/sensing/camera/camera3/camera_info" description="camera info topic name"/>
   <arg name="image_raw1" default="/sensing/camera/camera1/image_rect_color"/>
   <arg name="camera_info1" default="/sensing/camera/camera1/camera_info"/>
   <arg name="image_raw2" default="/sensing/camera/camera2/image_rect_color"/>
   <arg name="camera_info2" default="/sensing/camera/camera2/camera_info"/>
-  <arg name="image_raw3" default="/sensing/camera/camera3/image_rect_color"/>
-  <arg name="camera_info3" default="/sensing/camera/camera3/camera_info"/>
+  <arg name="image_raw3" default="/sensing/camera/camera0/image_rect_color"/>
+  <arg name="camera_info3" default="/sensing/camera/camera0/camera_info"/>
   <arg name="image_raw4" default="/sensing/camera/camera4/image_rect_color"/>
   <arg name="camera_info4" default="/sensing/camera/camera4/camera_info"/>
   <arg name="image_raw5" default="/sensing/camera/camera5/image_rect_color"/>
@@ -33,7 +33,7 @@
```

## Evaluation method

The perception_2d evaluation is executed by launching the `perception_2d.launch.py` file.
Launching the file executes the following steps:

1. Execute launch of evaluation node (`perception_2d_evaluator_node`), `logging_simulator.launch` file and `ros2 bag play` command
2. Autoware receives sensor data output from input rosbag and outputs camera, and the perception module performs recognition.
3. The evaluation node subscribes to `/perception/object_recognition/detection{/detected}/rois0` and evaluates data. The result is dumped into a file.
4. When the playback of the rosbag is finished, Autoware's launch is automatically terminated, and the evaluation is completed.

## Evaluation results

The results are calculated for each subscription. The format and available states are described below.

### Perception Normal

When the following conditions are satisfied by executing the evaluation function of perception_eval

1. frame_result.pass_fail_result contains at least one object (`tp_object_results ! = [] and fp_object_results ! = [] and fn_objects ! = []`)
2. no object fail (`frame_result.pass_fail_result.get_fail_object_num() == 0`)

### Perception Error

The perception evaluation output is marked as `Error` when condition for `Normal` is not met.

## Topic name and data type used by evaluation node

Subscribed topics:

| Topic name                                             | Data type                                            |
| ------------------------------------------------------ | ---------------------------------------------------- |
| /perception/object_recognition/detection/rois0         | tier4_perception_msgs/msg/DetectedObjectsWithFeature |
| /perception/object_recognition/detection/tracked/rois0 | tier4_perception_msgs/msg/DetectedObjectsWithFeature |

Published topics:

| Topic name | Data type |
| ---------- | --------- |
| -          | -         |

## Arguments passed to logging_simulator.launch

To make Autoware processing less resource-consuming, modules that are not relevant to evaluation are disabled by passing the `false` parameter as a launch argument.
The following parameters are set to `false`:

- localization: false
- planning: false
- control: false
- sensing: false / true (default value is false. Specify by `LaunchSensing` key for each t4_dataset in the scenario)
- perception_mode: camera_lidar_fusion

**NOTE: The `tf` in the bag is used to align the localization during annotation and simulation. Therefore, localization is invalid.**

## Dependent libraries

The perception evaluation step bases on the [perception_eval](https://github.com/tier4/autoware_perception_evaluation) library.

### Division of roles of driving_log_replayer with dependent libraries

`driving_log_replayer` package is in charge of the connection with ROS. The actual perception evaluation is conducted in [perception_eval](https://github.com/tier4/autoware_perception_evaluation) library.
The [perception_eval](https://github.com/tier4/autoware_perception_evaluation) is a ROS-independent library, it cannot receive ROS objects. Also, ROS timestamps use nanoseconds while the `t4_dataset` format is based on milliseconds (because it uses `nuScenes`), so the values must be properly converted before using the library's functions.

`driving_log_replayer` subscribes the topic output from the perception module of Autoware, converts it to the data format defined in [perception_eval](https://github.com/tier4/autoware_perception_evaluation), and passes it on.
It is also responsible for publishing and visualizing the evaluation results from [perception_eval](https://github.com/tier4/autoware_perception_evaluation) on proper ROS topic.

[perception_eval](https://github.com/tier4/autoware_perception_evaluation) is in charge of the part that compares the detection results passed from `driving_log_replayer` with ground truth data, calculates the index, and outputs the results.

## About simulation

State the information required to run the simulation.

### Topic to be included in the input rosbag

Must contain the required topics in `t4_dataset` format.

The vehicle's ECU CAN and sensors data topics are required for the evaluation to be run correctly.
The following example shows the topic list available in evaluation input rosbag when multiple LiDARs and Cameras are used in a real-world vehicle configuration.

/sensing/lidar/concatenated/pointcloud is used if the scenario LaunchSensing: false.

If there is more than one CAMERA, include all on-board camera_info and image_rect_color_compressed.

| Topic name                                           | Data type                                    |
| ---------------------------------------------------- | -------------------------------------------- |
| /gsm8/from_can_bus                                   | can_msgs/msg/Frame                           |
| /sensing/camera/camera\*/camera_info                 | sensor_msgs/msg/CameraInfo                   |
| /sensing/camera/camera\*/image_rect_color/compressed | sensor_msgs/msg/CompressedImage              |
| /sensing/gnss/ublox/fix_velocity                     | geometry_msgs/msg/TwistWithCovarianceStamped |
| /sensing/gnss/ublox/nav_sat_fix                      | sensor_msgs/msg/NavSatFix                    |
| /sensing/gnss/ublox/navpvt                           | ublox_msgs/msg/NavPVT                        |
| /sensing/imu/tamagawa/imu_raw                        | sensor_msgs/msg/Imu                          |
| /sensing/lidar/concatenated/pointcloud               | sensor_msgs/msg/PointCloud2                  |
| /sensing/lidar/\*/velodyne_packets                   | velodyne_msgs/VelodyneScan                   |
| /tf                                                  | tf2_msgs/msg/TFMessage                       |

The vehicle topics can be included instead of CAN.

| Topic name                                           | Data type                                           |
| ---------------------------------------------------- | --------------------------------------------------- |
| /sensing/camera/camera\*/camera_info                 | sensor_msgs/msg/CameraInfo                          |
| /sensing/camera/camera\*/image_rect_color/compressed | sensor_msgs/msg/CompressedImage                     |
| /sensing/gnss/ublox/fix_velocity                     | geometry_msgs/msg/TwistWithCovarianceStamped        |
| /sensing/gnss/ublox/nav_sat_fix                      | sensor_msgs/msg/NavSatFix                           |
| /sensing/gnss/ublox/navpvt                           | ublox_msgs/msg/NavPVT                               |
| /sensing/imu/tamagawa/imu_raw                        | sensor_msgs/msg/Imu                                 |
| /sensing/lidar/concatenated/pointcloud               | sensor_msgs/msg/PointCloud2                         |
| /sensing/lidar/\*/velodyne_packets                   | velodyne_msgs/VelodyneScan                          |
| /tf                                                  | tf2_msgs/msg/TFMessage                              |
| /vehicle/status/control_mode                         | autoware_auto_vehicle_msgs/msg/ControlModeReport    |
| /vehicle/status/gear_status                          | autoware_auto_vehicle_msgs/msg/GearReport           |
| /vehicle/status/steering_status                      | autoware_auto_vehicle_msgs/SteeringReport           |
| /vehicle/status/turn_indicators_status               | autoware_auto_vehicle_msgs/msg/TurnIndicatorsReport |
| /vehicle/status/velocity_status                      | autoware_auto_vehicle_msgs/msg/VelocityReport       |

### Topics that must not be included in the input rosbag

| Topic name | Data type               |
| ---------- | ----------------------- |
| /clock     | rosgraph_msgs/msg/Clock |

The clock is output by the --clock option of ros2 bag play, so if it is recorded in the bag itself, it is output twice, so it is not included in the bag.

## About Evaluation

State the information necessary for the evaluation.

### Scenario Format

There are two types of evaluation: use case evaluation and database evaluation.
Use case evaluation is performed on a single dataset, while database evaluation uses multiple datasets and takes the average of the results for each dataset.

In the database evaluation, the `vehicle_id` should be able to be set for each data set, since the calibration values may change.
Also, it is necessary to set whether or not to activate the sensing module.

See [sample](https://github.com/tier4/driving_log_replayer/blob/main/sample/perception_2d/scenario.yaml).

### Evaluation Result Format

The evaluation results by [perception_eval](https://github.com/tier4/autoware_perception_evaluation) under the conditions specified in the scenario are output for each frame.
Only the final line has a different format from the other lines since the final metrics are calculated after all data has been flushed.

The format of each frame and the metrics format are shown below.
**NOTE: common part of the result file format, which has already been explained, is omitted.**

Format of each frame:

```json
{
  "Frame": {
    "FrameName": "Frame number of t4_dataset used for evaluation",
    "FrameSkip": "Number of times that an object was requested to be evaluated but the evaluation was skipped because there was no ground truth in the dataset within 75msec",
    "PassFail": {
      "Result": "Success or Fail",
      "Info": [
        {
          "TP": "Number of TPs",
          "FP": "Number of FPs",
          "FN": "Number of FNs"
        }
      ]
    }
  }
}
```

Metrics Data Format:

```json
{
  "Frame": {
    "FinalScore": {
      "Score": {
        "TP": "TP rate of the label",
        "FP": "FP rate of the label",
        "FN": "FN rate of the label",
        "AP": "AP value of the label",
        "APH": "APH value of the label"
      },
      "ConfusionMatrix": {
        "Label(GroundTruth)": "Prediction results"
      }
    }
  }
}
```

### pickle file

In database evaluation, it is necessary to replay multiple rosbags, but due to the ROS specification, it is impossible to use multiple bags in a single launch.
Since one rosbag, i.e., one `t4_dataset`, requires one launch, it is necessary to execute as many launches as the number of datasets contained in the database evaluation.

Since database evaluation cannot be done in a single launch, perception outputs a file `scene_result.pkl` in addition to `result.jsonl` file.
A pickle file is a python object saved as a file, PerceptionEvaluationManager.frame_results of [perception_eval](https://github.com/tier4/autoware_perception_evaluation).
The dataset evaluation can be performed by reading all the objects recorded in the pickle file and outputting the index of the dataset's average.

### Result file of database evaluation

In the case of a database evaluation with multiple datasets in the scenario, a file named `database_result.json` is output to the results directory.

The format is the same as the [Metrics Data Format](#evaluation-result-format).
