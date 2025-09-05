import threading

from fastapi import APIRouter, UploadFile, File, status
from fastapi.responses import StreamingResponse, JSONResponse, FileResponse
import os
import cv2
from app.services.detection_service import ObjectDetectionService
from uuid import uuid1
import time

detection_router = APIRouter()
detection_tasks = {}
live_detector = None
upload_detector = None
chunk_size = 1024 * 1024
object_count = None


def detected_live_stream():
    global live_detector
    try:
        live_detector = ObjectDetectionService(video_path=0)
        # detected_frames = detector.detect_objects()
        for frame in live_detector.detect_objects():
            ref, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    except Exception as e:
        print(e)


@detection_router.get("/upload_stream")
def upload_stream():
    global upload_detector

    def generate():
        while upload_detector:
            if hasattr(upload_detector, 'last_processed_frame'):
                frame = upload_detector.last_processed_frame
                _, buffer = cv2.imencode('.jpg', frame)
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            else:
                time.sleep(0.1)

    return StreamingResponse(generate(), media_type="multipart/x-mixed-replace; boundary=frame")


def generate_video_chunks(video_path):
    with open(video_path, 'rb') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            yield chunk


@detection_router.post("/upload_from_local")
async def upload_from_local(file: UploadFile = File(...)):
    global upload_detector
    print(file.filename)
    os.makedirs("uploads", exist_ok=True)
    file_path = os.path.join("uploads", f"i{uuid1()}_{file.filename}")
    # file_path = file_path.replace("-","_")
    print(file_path)
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    detector = ObjectDetectionService(video_path=file_path)
    detection_tasks[file.filename] = detector

    upload_detector = detector
    thread = threading.Thread(target=lambda: [frame for frame in detector.detect_objects()], daemon=True)
    thread.start()

    return {"message": "Processing started", "file_path": file_path, "original_file": file.filename}


@detection_router.post("/display_from_local")
def display_from_local():
    global upload_detector, last_output_video_path, object_count
    if upload_detector:
        output_path, object_count = upload_detector.stop_detection()
        upload_detector = None
        last_output_video_path = output_path
        return JSONResponse({"output_video_path": output_path, "object_count": object_count})
    return JSONResponse({"error": "No active uploaded video detection"}, status_code=404)


@detection_router.get("/live_detection")
def live_detection():
    return StreamingResponse(detected_live_stream(), media_type="multipart/x-mixed-replace; boundary=frame")


@detection_router.post("/stop_detection")
def stop_detection():
    global live_detector, last_output_video_path, object_count
    if live_detector:
        output_path, object_count = live_detector.stop_detection()
        live_detector = None
        last_output_video_path = output_path
        return {"output_video_path": output_path, "object_count": object_count}
    return {"message": "No active detection"}


@detection_router.get("/get_video")
async def get_video():
    global last_output_video_path
    wait_time = 2
    try_count = 0
    if last_output_video_path:
        while try_count < 5:
            if os.path.exists(last_output_video_path) and os.stat(last_output_video_path).st_size > 0:
                file_name = os.path.basename(last_output_video_path)
                file_size = os.stat(last_output_video_path).st_size
                headers = {
                    "content-type": "video/mp4",
                    "accept-ranges": "bytes",
                    "content-encoding": "identity",
                    "content-length": str(file_size),
                    "content-range": f"bytes 0-{file_size - 1}/{file_size}",
                }
                return StreamingResponse(
                    content=generate_video_chunks(last_output_video_path),
                    headers=headers,
                    status_code=status.HTTP_206_PARTIAL_CONTENT,
                    media_type="video/mp4",
                )
                # return FileResponse(last_output_video_path, media_type="video/mp4", filename=file_name)
            else:
                time.sleep(wait_time)
                try_count += 1
    return JSONResponse({"error": "Video not found"}, status_code=404)


@detection_router.get("/get_object_count")
async def get_object_count():
    global object_count

    return JSONResponse(content={"object_count": object_count})


