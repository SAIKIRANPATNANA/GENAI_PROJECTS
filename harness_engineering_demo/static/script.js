const messageInput = document.getElementById("message");
const sendButton = document.getElementById("sendButton");
const resultCard = document.getElementById("resultCard");
const answerBox = document.getElementById("answer");
const routeBadge = document.getElementById("routeBadge");
const traceBox = document.getElementById("trace");

document.querySelectorAll(".example").forEach((button) => {
    button.addEventListener("click", () => {
        messageInput.value = button.dataset.text;
        messageInput.focus();
    });
});

sendButton.addEventListener("click", async () => {
    const message = messageInput.value.trim();

    if (!message) {
        alert("Please enter a question.");
        return;
    }

    sendButton.disabled = true;
    sendButton.textContent = "Agents are working...";

    resultCard.classList.remove("hidden");
    answerBox.className = "answer";
    answerBox.textContent = "Processing...";
    routeBadge.textContent = "";
    traceBox.innerHTML = "";

    try {
        const response = await fetch("/api/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                message: message,
            }),
        });

        if (!response.ok) {
            throw new Error("Server returned an error.");
        }

        const data = await response.json();

        answerBox.textContent = data.answer;
        routeBadge.textContent = data.route;

        data.trace.forEach((step, index) => {
            const item = document.createElement("div");
            item.className = "trace-item";
            item.textContent = `${index + 1}. ${step}`;
            traceBox.appendChild(item);
        });
    } catch (error) {
        answerBox.className = "answer error";
        answerBox.textContent =
            "Something went wrong. Check the terminal and your GROQ_API_KEY.";
    } finally {
        sendButton.disabled = false;
        sendButton.textContent = "Run Multi-Agent System";
    }
});
