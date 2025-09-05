const API_BASE_URL = '';

// =========================
// UPLOAD VIDEO SECTION
// =========================
const videoFileInput = document.getElementById('videoFile');
const uploadBtn = document.getElementById('uploadBtn');
const stopUploadBtn = document.getElementById('stopUpload');
const uploadLoader = document.getElementById('uploadLoader');
const uploadStatus = document.getElementById('uploadStatus');
const processedVideo = document.getElementById('processedVideo');
const processedSource = document.getElementById('processedSource');


const showLiveProcessing = document.getElementById('showLiveProcessing');
const uploadStreamDiv = document.getElementById('uploadStream');
const uploadLiveImage = document.getElementById('uploadLiveImage');

let uploadedFileName = '';

videoFileInput.addEventListener('change', () => {
    uploadBtn.textContent = videoFileInput.files.length ? "Submit" : "Upload";
});

uploadBtn.addEventListener('click', async () => {
    if (!videoFileInput.files.length) {
        alert("Please select a video file.");
        return;
    }
    const file = videoFileInput.files[0];
    uploadedFileName = file.name;
    uploadLoader.style.display = 'block';
    uploadBtn.disabled = true;
    uploadBtn.textContent = "Uploading...";
    const formData = new FormData();
    formData.append('file', file);
    try {
        uploadStatus.textContent = "Uploading and processing video...";
        const response = await fetch(`${API_BASE_URL}/upload_from_local`, { method: 'POST', body: formData });
        const data = await response.json();
        uploadStatus.textContent = `Processing started for file: ${uploadedFileName}`;
        uploadLoader.style.display = 'block';
        uploadBtn.style.display = 'none';
        stopUploadBtn.style.display = 'inline-block';
    } catch (error) {
        console.error('Error uploading video:', error);
        uploadStatus.textContent = "Error uploading video.";
        uploadLoader.style.display = 'none';
        uploadBtn.disabled = false;
        uploadBtn.textContent = "Submit";
    }
});

stopUploadBtn.addEventListener('click', async () => {
    try {
        uploadStatus.textContent = "Stopping detection and finalizing output...";
        const response = await fetch(`${API_BASE_URL}/display_from_local`, { method: 'POST' });
        const data = await response.json();
        if (data.error) {
            uploadStatus.textContent = data.error;
        } else {
            processedSource.src = `${API_BASE_URL}/get_video`;
            processedVideo.style.display = 'block';
            processedVideo.load();
            uploadLoader.style.display = 'none';

            // Format object counts
            const counts = data.object_count ? Object.entries(data.object_count)
                .map(([obj, count]) => `${count} ${obj}${count !== 1 ? 's' : ''}`)
                .join(', ') : 'no objects';

            uploadStatus.textContent = `Detection complete. Found: ${counts}.`;
            // uploadStatus.textContent = `Detection stopped. Object counts: ${JSON.stringify(data.object_count)}`;
        }
        uploadStreamDiv.style.display = 'none';
        showLiveProcessing.checked = false;
    } catch (error) {
        console.error('Error stopping detection:', error);
        uploadStatus.textContent = "Error stopping detection.";
    }
});


// Add checkbox handler
showLiveProcessing.addEventListener('change', () => {
    if (showLiveProcessing.checked) {
        uploadLiveImage.src = `${API_BASE_URL}/upload_stream`;
        uploadStreamDiv.style.display = 'block';
    } else {
        uploadLiveImage.src = '';
        uploadStreamDiv.style.display = 'none';
    }
});

// =========================
// LIVE DETECTION SECTION
// =========================
const startLiveBtn = document.getElementById('startLive');
const stopLiveBtn = document.getElementById('stopLive');
const liveStatus = document.getElementById('liveStatus');
const liveStreamDiv = document.getElementById('liveStream');
const liveImage = document.getElementById('liveImage');
const liveOutputVideo = document.getElementById('liveOutputVideo');
const liveOutputSource = document.getElementById('liveOutputSource');
const liveLoader = document.getElementById('liveLoader');

startLiveBtn.addEventListener('click', () => {
    try{
        liveStatus.textContent = "Live detection started...";
        liveImage.src = `/live_detection`;
        liveStreamDiv.style.display = 'block';
        startLiveBtn.style.display = 'none';
        stopLiveBtn.style.display = 'inline-block';
        liveLoader.style.display = 'block';
    } catch (error) {
        console.error('Error in live detection:', error);
        liveStatus.textContent = "Error stopping live detection.";
        liveLoader.style.display = "none";
    }
    
});

stopLiveBtn.addEventListener('click', async () => {
    try {
        liveStatus.textContent = "Stopping live detection...";
        const response = await fetch(`/stop_detection`, {method: 'POST'});
        const data = await response.json();

        if (data.error) {
            liveStatus.textContent = data.error;
        } else {
            liveImage.src = '';
            liveStreamDiv.style.display = 'none';
            stopLiveBtn.style.display = 'none';
            startLiveBtn.style.display = 'inline-block';

            if (data.output_video_path) {
                liveOutputSource.src = `/get_video`;
                liveOutputVideo.style.display = 'block';
                liveOutputVideo.load();
                console.log(data.output_video_path)
                liveLoader.style.display = 'none';
            }

            // Format object counts
            const counts = data.object_count ? Object.entries(data.object_count)
                .map(([obj, count]) => `${count} ${obj}${count !== 1 ? 's' : ''}`)
                .join(', ') : 'no objects';

            liveStatus.textContent = `Detection complete. Found ${counts}.`;
        }
    } catch (error) {
        console.error('Error stopping live detection:', error);
        liveStatus.textContent = "Error stopping live detection.";
        liveLoader.style.display = "none";
    }
});
