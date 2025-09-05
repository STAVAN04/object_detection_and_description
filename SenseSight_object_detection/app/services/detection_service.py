import cv2
from ultralytics import YOLO
from collections import defaultdict
from queue import Queue

import os
import pyttsx3
import threading
from uuid import uuid1
import subprocess

import time

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))


class ObjectDetectionService:
    def __init__(self, video_path, model_path="../yolo11s.pt"):
        # print("Initializing ObjectDetectionService...")
        self.model = YOLO(model_path)
        self.class_list = self.model.names
        self.tts_queue = Queue()
        self.stop_flag = threading.Event()
        self.is_processing = True
        self.video_path = video_path
        self.class_counts = defaultdict(int)
        self.crossed_ids = set()
        self.detection_output_id = str(uuid1())

        self.output_dir = os.path.join(root_dir, "output")
        os.makedirs(self.output_dir, exist_ok=True)

        if self.video_path != 0:
            if not os.path.isabs(video_path):
                self.video_path = os.path.join(root_dir, video_path)
            # self.video_path = os.path.join(root_dir, video_path)
        print(self.video_path)
        self.cap = cv2.VideoCapture(self.video_path, )
        if not self.cap.isOpened():
            raise ValueError("Could not open video file")

        self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fps = int(self.cap.get(cv2.CAP_PROP_FPS))
        self.fps = 5

        self.output_video_path = os.path.join(self.output_dir, f"{self.detection_output_id}_out.avi")
        self.out = cv2.VideoWriter(self.output_video_path, cv2.VideoWriter_fourcc(*'XVID'), self.fps,
                                   (self.frame_width, self.frame_height))
        self.final_output_video_path = os.path.join(self.output_dir, f"{self.detection_output_id}_final_output.webm")

        self.audio_file = os.path.join(self.output_dir, f"{self.detection_output_id}_audio.wav")
        open(self.audio_file, 'w').close()

        self.temp_audio_files_list = []
        self.silent_audio = os.path.join(self.output_dir, f"{self.detection_output_id}_silent_audio.wav")
        self.last_processed_frame = None

        # print("Object DetectionService initialized")

    def stop_detection(self):
        self.merge_audio_files()
        self.merge_audio_video()
        self.is_processing = False
        self.stop_flag.set()
        if self.cap.isOpened():
            self.cap.release()
        self.out.release()
        # cv2.destroyAllWindows()
        # os.remove(self.audio_file)
        # os.remove(self.output_video_path)

        self.tts_queue.queue.clear()
        return self.final_output_video_path, dict(self.class_counts)

    def tts_worker(self):
        engine = pyttsx3.init()
        engine.setProperty('rate', 250)

        while not self.stop_flag.is_set():
            try:
                text = self.tts_queue.get(timeout=0.5)
            except Exception:
                continue
            # text = self.tts_queue.get()
            if text is None:
                break
            if self.video_path == 0:
                engine.say(text)

            temp_audio_file = os.path.join(self.output_dir, f"temp_{uuid1()}.wav")
            engine.save_to_file(text, temp_audio_file)
            engine.runAndWait()

            self.temp_audio_files_list.append(temp_audio_file)
            # print(f"Saved TTS audio: {temp_audio_file}")

            self.tts_queue.task_done()

    def provide_feedback(self, object_center, frame_width, class_name):
        x_center = object_center
        if x_center < frame_width / 5:
            position = "left"
        elif frame_width / 5 <= x_center < frame_width / 2.5:
            position = "slight left"
        elif frame_width / 2.5 <= x_center < frame_width / 1.67:
            position = "center"
        elif frame_width / 1.67 <= x_center < frame_width / 1.25:
            position = "slight right"
        else:
            position = "right"
        message = f"{class_name} on {position}."
        # print(message)
        self.tts_queue.put(message)

    def merge_audio_files(self):
        if not self.temp_audio_files_list:
            # print("No audio files to merge. Creating a silent audio track.")
            subprocess.run([
                "ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono",
                "-t", "1", "-q:a", "9", "-acodec", "libmp3lame", self.silent_audio
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.temp_audio_files_list.append(self.silent_audio)

        list_file = os.path.join(self.output_dir, f"{self.detection_output_id}_audio_list.txt")
        with open(list_file, "w") as f:
            for file in self.temp_audio_files_list:
                f.write(f"file '{file}'\n")
        command = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_file,
            "-c", "copy", self.audio_file
        ]
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        os.remove(list_file)
        for file in self.temp_audio_files_list:
            if os.path.exists(file):
                os.remove(file)
        # [os.remove(i) for i in self.temp_audio_files_list]
        # print("Merged audio file:", self.audio_file)

    def merge_audio_video(self, fps=5):
        # print("Merging audio video...")
        command = [
            'ffmpeg', '-y',
            '-i', self.output_video_path,
            '-i', self.audio_file,
            '-map', '0:v:0?',
            '-map', '1:a:0?',
            '-c:v',  'libvpx',
            '-b:v', '1M',
            '-c:a', 'libopus',
            '-b:a', '128k',
            '-r', f'{fps:.2f}',
            '-shortest',
            '-movflags', '+faststart',
            self.final_output_video_path
        ]
        # command = ['ffmpeg', '-y', '-i', self.output_video_path, '-i', self.audio_file, '-map', '0:v:0?', '-map', '1:a:0?', '-c:v', 'libx264', '-preset', 'slow', '-crf', '23', '-c:a', 'aac', '-b:a', '128k', '-r', f'{fps:.2f}', '-shortest', '-movflags', '+faststart', self.final_output_video_path]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            print("FFmpeg error during merge_audio_video:")
            print(result.stderr.decode())
        else:
            print("Audio and video merged into:", self.final_output_video_path)

    def process_frame(self, frame):
        frame = cv2.resize(frame, (640, 480))

        results = self.model.track(frame, tracker='botsort.yaml', persist=True, conf=0.6, iou=0.6)

        if results and len(results) > 0 and results[0].boxes.data is not None:
            boxes = results[0].boxes.xyxy.cpu()
            # track_ids = results[0].boxes.id.int().cpu().tolist()
            class_indices = results[0].boxes.cls.int().cpu().tolist()
            confidences = results[0].boxes.conf.cpu()

            if hasattr(results[0].boxes, 'id') and results[0].boxes.id is not None:
                track_ids = results[0].boxes.id.int().cpu().tolist()
            else:
                track_ids = []

            for box, track_id, class_id, conf in zip(boxes, track_ids, class_indices, confidences):
                x1, y1, x2, y2 = map(int, box)
                cx = (x1 + x2) // 2
                cy = (y1 + y2) // 2

                class_name = self.class_list[class_id]

                cv2.circle(frame, (cx, cy), 4, (0, 0, 255), -1)
                cv2.putText(frame, f"ID: {track_id} {class_name}", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

                if track_id not in self.crossed_ids:
                    self.crossed_ids.add(track_id)
                    self.class_counts[class_name] += 1
                    self.provide_feedback(cx, 640, class_name)

            y_offset = 30
            for class_name, count in self.class_counts.items():
                cv2.putText(frame, f"{class_name}: {count}", (50, y_offset),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                y_offset += 30

        frame = cv2.resize(frame, (self.frame_width, self.frame_height))
        self.out.write(frame)
        self.last_processed_frame = frame
        return frame

    def detect_objects(self):
        tts_thread = threading.Thread(target=self.tts_worker, daemon=True)
        tts_thread.start()
        try:
            # print("start")
            start_time = time.time()

            while self.cap.isOpened() and self.is_processing:
                ret, frame = self.cap.read()
                if not ret:
                    break

                processed_frame = self.process_frame(frame)
                processed_fps = 1 / (time.time() - start_time)

                yield processed_frame
        except Exception as e:
            print(e)
        finally:
            self.stop_detection()
            # yield self.final_output_video_path, dict(self.class_counts)
