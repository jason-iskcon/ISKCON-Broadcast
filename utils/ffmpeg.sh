#!/bin/bash

RTSP_URL="rtsp://admin:Gaura108@192.168.86.215:554/11"
YOUTUBE_URL="rtmp://a.rtmp.youtube.com/live2"
YOUTUBE_KEY="74vx-xdv7-fxth-7wrr-7dcf"

ffmpeg -rtsp_transport tcp -i ${RTSP_URL} \
  -tune zerolatency -preset ultrafast \
  -vf "scale=1920:1080" -b:v 15M -maxrate 15M -bufsize 30M \
  -vcodec libx264 -pix_fmt yuv420p -g 60 \
  -c:a aac -b:a 128k -ar 44100 -f flv ${YOUTUBE_URL}/${YOUTUBE_KEY}
