// Get the HTML console output
let consoleOutput = "Temp/Humi: 0.0°C / 0%";

// Regular expression pattern to match temperature and humidity values
const pattern = /Temp\/Humi: (\d+\.\d+)°C \/ (\d+)%/;

// Function to extract temperature and humidity values using the pattern
function extractValues(output) {
    const matches = output.match(pattern);

    if (matches) {
        const temperature = parseFloat(matches[1]);
        const humidity = parseInt(matches[2]);

        // Get the current time in a 24-hour format
        const currentTime = new Date().toLocaleString(undefined, { hour12: false });

        // Save the temperature and humidity values for Python to use
        const savedData = {
            currentTime,
            temperature,
            humidity
        };
        const jsonData = JSON.stringify(savedData);
        sendDataToServer(jsonData);

        console.log("Time:", currentTime);
        console.log("Temperature:", temperature);
        console.log("Humidity:", humidity);
    } else {
        console.log("No temperature and humidity data found in the console output.");
    }
}

function sendDataToServer(data) {
    fetch('http://localhost:5000/data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: data,
    })
    .then(response => response.text())
    .then(data => {
        console.log('Success:', data);
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

// Function to continuously monitor the console output
function monitorConsoleOutput() {
    // 假设控制台的输出被保存在一个 id 为 "console" 的 HTML 元素中
    const consoleElement = document.querySelector("#tempHumiData");

    // 获取元素的文本内容，并将其赋值给 `consoleOutput` 变量
    consoleOutput = consoleElement.textContent;

    extractValues(consoleOutput);
}

// Create a new MutationObserver instance
const observer = new MutationObserver(() => {
    monitorConsoleOutput();
});

// Select the target element to observe
const targetElement = document.querySelector("#tempHumiData");

// Configure the observer to watch for changes in the target element's content
const observerConfig = {
    childList: true,
    subtree: true,
    characterData: true
};

// Start observing the target element
observer.observe(targetElement, observerConfig);
