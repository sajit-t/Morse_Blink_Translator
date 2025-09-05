function fetchText() {
    fetch("/get_text")
        .then(res => res.json())
        .then(data => {
            document.getElementById("morse-seq").innerText = data.morse;
            document.getElementById("decoded-text").innerText = data.decoded;
        });
}
setInterval(fetchText, 500);

function toggleWebcam() {
    let cam = document.getElementById("webcam");
    cam.style.display = (cam.style.display === "none") ? "block" : "none";
}

function toggleChart() {
    let chart = document.getElementById("chart");
    chart.style.display = (chart.style.display === "none") ? "block" : "none";
}

function clearText() {
    fetch("/clear", { method: "POST" })
        .then(() => {
            document.getElementById("morse-seq").innerText = "";
            document.getElementById("decoded-text").innerText = "";
        });
}
