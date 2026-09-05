const video = document.getElementById("videoPlayer");
const playBtn = document.getElementById("playPauseBtn");
const centerPlay = document.getElementById("centerPlay");
const rewindBtn = document.getElementById("rewindBtn");
const forwardBtn = document.getElementById("forwardBtn");
const volumeSlider = document.getElementById("volumeSlider");
const fullscreenBtn = document.getElementById("fullscreenBtn");
const speedControl = document.getElementById("speedControl");
const progressBar = document.getElementById("progressBar");
const currentTimeEl = document.getElementById("currentTime");
const durationEl = document.getElementById("duration");
const playerContainer = document.getElementById("playerContainer");
const loadingSpinner = document.getElementById("loadingSpinner");
const playerControls = document.getElementById("playerControls");
const theaterBtn = document.getElementById("theaterBtn");
const theaterWrapper = document.getElementById("theaterWrapper");

function formatTime(seconds){
const mins = Math.floor(seconds / 60);
const secs = Math.floor(seconds % 60);
return `${String(mins).padStart(2,"0")}:${String(secs).padStart(2,"0")}`;
}

function updatePlayButtons(){

    if(video.paused){

        playBtn.innerHTML = "▶";

        centerPlay.style.display = "flex";

    }else{

        playBtn.innerHTML = "⏸";

        centerPlay.style.display = "none";

    }

}

function togglePlay(){
if(video.paused){
video.play();
}
else{
video.pause();
}
updatePlayButtons();
}

playBtn.addEventListener("click", togglePlay);
centerPlay.addEventListener("click", togglePlay);
video.addEventListener("dblclick", () => {

    if(!document.fullscreenElement){

        playerContainer.requestFullscreen();

    }else{

        document.exitFullscreen();

    }

});

// 📱 Mobile double-tap gestures

// 📱 MOBILE DOUBLE-TAP GESTURES
// Left side  → Rewind 10 seconds
// Right side → Forward 10 seconds

let lastTap = 0;
let tapTimer = null;

video.addEventListener("touchend", (e) => {

    const currentTime = Date.now();

    const tapLength = currentTime - lastTap;

    if (tapLength < 300 && tapLength > 0) {

        clearTimeout(tapTimer);

        const touch = e.changedTouches[0];

        const rect = video.getBoundingClientRect();

        const tapX = touch.clientX - rect.left;

        const videoWidth = rect.width;

        // LEFT SIDE → REWIND
        if (tapX < videoWidth / 2) {

            video.currentTime = Math.max(
                0,
                video.currentTime - 10
            );

            showControls();

        }

        // RIGHT SIDE → FORWARD
        else {

            if (video.duration) {

                video.currentTime = Math.min(
                    video.duration,
                    video.currentTime + 10
                );

            }

            showControls();

        }

    } else {

        // Normal single tap
        tapTimer = setTimeout(() => {

            togglePlay();

        }, 250);

    }

    lastTap = currentTime;

});

rewindBtn.addEventListener("click", () => {
video.currentTime = Math.max(0, video.currentTime - 10);
});

forwardBtn.addEventListener("click", () => {
video.currentTime = Math.min(video.duration || 0, video.currentTime + 10);
});

volumeSlider.addEventListener("input", () => {
video.volume = volumeSlider.value;
});

fullscreenBtn.addEventListener("click", () => {
if(!document.fullscreenElement){
playerContainer.requestFullscreen();
}
else{
document.exitFullscreen();
}
});



video.addEventListener("waiting", () => {

    loadingSpinner.style.display = "block";

});

video.addEventListener("playing", () => {

    loadingSpinner.style.display = "none";

});

video.addEventListener("canplay", () => {

    loadingSpinner.style.display = "none";

});

video.addEventListener("loadedmetadata", () => {
durationEl.textContent = formatTime(video.duration);
});

video.addEventListener("timeupdate", () => {
currentTimeEl.textContent = formatTime(video.currentTime);
if(video.duration){
progressBar.value = (video.currentTime / video.duration) * 100;
}
});

function updateProgress(value){
    if(video.duration){
        video.currentTime = (value / 100) * video.duration;
    }
}

progressBar.addEventListener("input", () => {
    updateProgress(progressBar.value);
});

progressBar.addEventListener("change", () => {
    updateProgress(progressBar.value);
});

video.addEventListener("play", updatePlayButtons);
video.addEventListener("pause", updatePlayButtons);

document.addEventListener("keydown", (e) => {
if(e.target.tagName === "INPUT") return;

switch(e.key.toLowerCase()){
case " ":
e.preventDefault();
togglePlay();
break;
case "arrowleft":
video.currentTime = Math.max(0, video.currentTime - 10);
break;

case "arrowright":
video.currentTime = Math.min(video.duration, video.currentTime + 10);
break;

case "arrowup":
e.preventDefault();
video.volume = Math.min(1, video.volume + 0.1);
volumeSlider.value = video.volume;
break;

case "arrowdown":
e.preventDefault();
video.volume = Math.max(0, video.volume - 0.1);
volumeSlider.value = video.volume;
break;

case "m":
video.muted = !video.muted;
break;
case "f":
fullscreenBtn.click();
break;
}
});

updatePlayButtons();

let hideTimer;

function showControls(){

    playerControls.style.opacity = "1";

    clearTimeout(hideTimer);

    if(!video.paused){

        hideTimer = setTimeout(() => {

            playerControls.style.opacity = "0";

        },3000);

    }

}

playerContainer.addEventListener("mousemove", showControls);

playerContainer.addEventListener("mouseleave", () => {

    if(!video.paused){

        playerControls.style.opacity="0";

    }

});

video.addEventListener("play", showControls);

video.addEventListener("pause", () => {

    playerControls.style.opacity="1";

});

speedControl.addEventListener("change", () => {

    video.playbackRate = parseFloat(speedControl.value);

});

theaterBtn.addEventListener("click", () => {

    theaterWrapper.classList.toggle("theater-mode");

});

video.addEventListener("ended", () => {

    const nextButton = document.querySelector(
        'a[href^="/watch/"]'
    );

    if(nextButton){

        window.location.href = nextButton.href;

    }

});