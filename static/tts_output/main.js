document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("download-form");
    const statusDiv = document.getElementById("status");
    const downloadLinkDiv = document.getElementById("download-link");

    form.addEventListener("submit", function (e) {
        e.preventDefault();

        statusDiv.innerHTML = "⏳ Downloading... Please wait.";
        downloadLinkDiv.innerHTML = "";

        const formData = new FormData(form);
        fetch("/download", {
            method: "POST",
            body: formData,
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.status === "success") {
                    statusDiv.innerHTML = "✅ Download successful!";
                    downloadLinkDiv.innerHTML = `
                        <a href="/downloads/${data.file_name}" class="btn btn-success mt-3" download>
                            📥 Download File
                        </a>
                    `;
                } else {
                    statusDiv.innerHTML = `❌ Error: ${data.message}`;
                }
            })
            .catch((error) => {
                statusDiv.innerHTML = `❌ Error: ${error.message}`;
            });
    });
});
