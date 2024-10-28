#!/bin/bash

RTSP_URL="rtsp://admin:Gaura108@192.168.86.215:554/11"
YOUTUBE_URL="rtmp://a.rtmp.youtube.com/live2"
YOUTUBE_KEY="74vx-xdv7-fxth-7wrr-7dcf"

ffmpeg -rtsp_transport tcp -i ${RTSP_URL} \
  -tune zerolatency -preset ultrafast -f flv \
  -vcodec libx264 -pix_fmt yuv420p -b:v 2M -maxrate 2M -bufsize 4M \
  -c:a aac -b:a 128k -f flv ${YOUTUBE_URL}/${YOUTUBE_KEY}
