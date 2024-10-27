#!/bin/bash

RTSP_URL="rtsp://admin:Gaura108@192.168.86.215:554/11"
YOUTUBE_URL="rtmp://a.rtmp.youtube.com/live2"
YOUTUBE_KEY="74vx-xdv7-fxth-7wrr-7dcf"

#screen -d -m 
#TODO: optimise this ffmpeg command
ffmpeg -rtsp_transport tcp -i ${RTSP_URL} -tune zerolatency -vcodec libx264 -pix_fmt + -c:v copy -c:a aac -strict experimental -f flv ${YOUTUBE_URL}/${YOUTUBE_KEY}
