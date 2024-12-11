# ISKCON-Broadcast

The application orchestrates 1 or more cameras and outputs them into an opencv imshow composite output image.

Run ISKCON broadcast program:

From the command line:
```bash
python video_stream.py --debug-time 04:30
```
Configure ISKCON broadcast program:

there are two main configuration files:

* mode_config.yaml
* orchestration.yaml

* An *orchestration.yaml* consists of one or more *programmes*.
* A *programme* (e.g. Morning Programme, Lunchtime Programme, etc.) comprises of a number of *events* (e.g. Mangala Aarti, Tulsi Aarti, etc).
* An *event* comprises a number of *actions*, being the main programmable instruction set.
* There are two primary types of action: *output* and *input*. Output actions change the OpenCV imshow written image. Input actions change the various OpenCM imread read images/streams.
* 

How 

```yaml
programmes:
  - name: "Morning Programme"
    start_time: "04:30"
    end_time: "08:45"
    events:
      - name: "Mangala Aarti"
        start_time: "04:30"
        end_time: "04:55"
        actions:
          - action: "play_video"
            file: "assets/mangala_arati.mp4"
            duration: 10
          - action: "play_audio"
            file: "assets/flute_music.mp3"
            duration: 10
          - action: "video_mode"
            type: "dual_mode"
            mode: "dual_0_topleft_small_1_bottomright_large"
            duration: 20
          - action: "camera_move"
            camera: 0
            type: "ToPos"
            marker: Deities
            speed: 15
            duration: 1
          - action: "camera_move"
            camera: 0
            type: "Left"
            speed: 20
            duration: 3.0
          - action: "camera_move"
            camera: 0
            type: "ZoomInc"
            speed: 10
            duration: 1.5
          - action: "camera_move"
            camera: 0
            type: "Right"
            speed: 20
            duration: 3.0
          - action: "camera_move"
            camera: 0
            type: "ZoomDec"
            speed: 10
            duration: 1.5
          - action: "video_mode"
            type: "left_column_right_main"
            mode: "left_column_12_right_main_0"
            duration: 10
          - action: "video_mode"
            type: "full_screen"
            mode: "fullscreen_0"
            duration: 10
          - action: "camera_move"
            camera: 0
            type: "Left"
            speed: 25
            duration: 1.5

      - name: "Tulsi Aarti"
        start_time: "04:55"
        end_time: "05:15"
        actions:
          - action: "video_mode"
            type: "full_screen"
            mode: "fullscreen_0"
            duration: 60
          - action: "camera_move"
            camera: 0
            type: "ToPos"
            marker: Class
            speed: 20
            duration: 1.5
```
