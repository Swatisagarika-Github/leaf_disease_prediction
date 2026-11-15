
// ============================================================
// GET HTML ELEMENTS
// ============================================================

const imageInput = document.getElementById("imageInput");

const previewContainer =
    document.getElementById("previewContainer");

const preview =
    document.getElementById("preview");

const predictButton =
    document.getElementById("predictButton");

const loading =
    document.getElementById("loading");

const result =
    document.getElementById("result");

const diseaseInfo =
    document.getElementById("diseaseInfo");

const languageSelect =
    document.getElementById("languageSelect");


// ============================================================
// IMAGE PREVIEW
// ============================================================

imageInput.addEventListener(
    "change",
    function () {

        const file = this.files[0];

        if (!file) {

            previewContainer.style.display = "none";

            preview.src = "";

            return;
        }


        // Check image

        if (!file.type.startsWith("image/")) {

            alert("Please select a valid image.");

            imageInput.value = "";

            return;
        }


        // Create preview

        const reader =
            new FileReader();


        reader.onload =
            function (event) {

                preview.src =
                    event.target.result;

                preview.style.display =
                    "block";

                previewContainer.style.display =
                    "block";
            };


        reader.readAsDataURL(file);
    }
);


// ============================================================
// PREDICT BUTTON
// ============================================================

predictButton.addEventListener(
    "click",
    async function () {

        // ----------------------------------------------------
        // CHECK IMAGE
        // ----------------------------------------------------

        const file =
            imageInput.files[0];


        if (!file) {

            alert(
                "Please select a leaf image first."
            );

            return;
        }


        // ----------------------------------------------------
        // DISABLE BUTTON
        // ----------------------------------------------------

        predictButton.disabled =
            true;


        predictButton.innerText =
            "🔄 Analyzing...";


        // ----------------------------------------------------
        // SHOW LOADING
        // ----------------------------------------------------

        loading.style.display =
            "block";


        result.innerHTML =
            "";

        diseaseInfo.style.display =
            "none";


        // ----------------------------------------------------
        // CREATE FORM DATA
        // ----------------------------------------------------

        const formData =
            new FormData();


        formData.append(
            "image",
            file
        );


        formData.append(
            "language",
            languageSelect.value
        );


        try {

            // ------------------------------------------------
            // SEND REQUEST TO FLASK
            // ------------------------------------------------

            const response =
                await fetch(
                    "/predict",
                    {
                        method: "POST",
                        body: formData
                    }
                );


            // ------------------------------------------------
            // GET JSON
            // ------------------------------------------------

            const data =
                await response.json();


            // ------------------------------------------------
            // CHECK ERROR
            // ------------------------------------------------

            if (!response.ok) {

                throw new Error(
                    data.error ||
                    "Prediction failed."
                );
            }


            if (data.error) {

                throw new Error(
                    data.error
                );
            }


            // ------------------------------------------------
            // DISPLAY CNN RESULT
            // ------------------------------------------------

            result.innerHTML = `

                <div class="result-card">

                    <h2>
                        🌿 Prediction Result
                    </h2>

                    <p>
                        <strong>
                            Disease:
                        </strong>

                        ${escapeHtml(
                            data.display_name ||
                            data.disease
                        )}
                    </p>

                    <p>
                        <strong>
                            Model Class:
                        </strong>

                        ${escapeHtml(
                            data.disease
                        )}
                    </p>

                    <p class="confidence">

                        <strong>
                            Confidence:
                        </strong>

                        ${Number(
                            data.confidence
                        ).toFixed(2)}%

                    </p>

                    <p>
                        <strong>
                            Gemini:
                        </strong>

                        Disease information generated successfully.
                    </p>

                </div>

            `;


            // ------------------------------------------------
            // DISPLAY DISEASE INFORMATION
            // ------------------------------------------------

            document.getElementById(
                "plant"
            ).textContent =
                data.plant ||
                "Information not available";


            document.getElementById(
                "symptoms"
            ).textContent =
                data.symptoms ||
                "Information not available";


            document.getElementById(
                "cause"
            ).textContent =
                data.cause ||
                "Information not available";


            // ------------------------------------------------
            // TREATMENT
            // ------------------------------------------------

            document.getElementById(
                "treatment"
            ).innerHTML =
                formatText(
                    data.treatment
                );


            // ------------------------------------------------
            // PREVENTION
            // ------------------------------------------------

            document.getElementById(
                "prevention"
            ).innerHTML =
                formatText(
                    data.prevention
                );


            // ------------------------------------------------
            // FARMER ADVICE
            // ------------------------------------------------

            document.getElementById(
                "farmerAdvice"
            ).textContent =
                data.farmer_advice ||
                "Information not available";


            // ------------------------------------------------
            // SHOW INFORMATION
            // ------------------------------------------------

            diseaseInfo.style.display =
                "block";


            // Scroll to result

            diseaseInfo.scrollIntoView({
                behavior: "smooth",
                block: "start"
            });

        }

        catch (error) {

            console.error(
                "Prediction error:",
                error
            );


            result.innerHTML = `

                <div class="result-card">

                    <h2>
                        ❌ Error
                    </h2>

                    <p>
                        ${escapeHtml(
                            error.message
                        )}
                    </p>

                </div>

            `;

        }

        finally {

            // ------------------------------------------------
            // HIDE LOADING
            // ------------------------------------------------

            loading.style.display =
                "none";


            // ------------------------------------------------
            // ENABLE BUTTON
            // ------------------------------------------------

            predictButton.disabled =
                false;


            predictButton.innerText =
                "🔍 Predict Disease";
        }

    }
);


// ============================================================
// FORMAT GEMINI TEXT
// ============================================================

function formatText(text) {

    if (!text) {

        return `
            <p>
                Information not available
            </p>
        `;
    }


    // Convert new lines to paragraphs/list-like text

    const lines =
        String(text)
            .split("\n")
            .map(
                line => line.trim()
            )
            .filter(
                line => line.length > 0
            );


    if (lines.length === 0) {

        return `
            <p>
                Information not available
            </p>
        `;
    }


    // If Gemini returns bullet points

    const bulletLines =
        lines.filter(
            line =>
                line.startsWith("-") ||
                line.startsWith("•") ||
                line.startsWith("*")
        );


    if (
        bulletLines.length ===
        lines.length &&
        bulletLines.length > 0
    ) {

        return `

            <ul>

                ${bulletLines.map(
                    line => {

                        const clean =
                            line.replace(
                                /^[-•*]\s*/,
                                ""
                            );

                        return `
                            <li>
                                ${escapeHtml(clean)}
                            </li>
                        `;
                    }
                ).join("")}

            </ul>

        `;
    }


    // Otherwise paragraphs

    return lines.map(
        line => `
            <p>
                ${escapeHtml(line)}
            </p>
        `
    ).join("");

}


// ============================================================
// HTML ESCAPE
// ============================================================

function escapeHtml(value) {

    if (value === null ||
        value === undefined) {

        return "";
    }


    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

