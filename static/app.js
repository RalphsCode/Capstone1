console.log("JS is Running");

// Get the buttons that need spinner
const startBtn = document.getElementById("start_btn");
const getWxBtn = document.getElementById("get_wx");


// Start Button - show Spinner & disable Button
startBtn.addEventListener("click", () => {
    // Show the spinner
    document.getElementById('spinner').style.display = 'block';

    // Disable the button to prevent multiple clicks
    startBtn.classList.add('loading-btn');
} ) ;

// Get Weather Button - show Spinner & disable Button
getWxBtn.addEventListener("click", (event) => {
    event.preventDefault();
    // Disable the button to prevent multiple clicks
    getWxBtn.classList.add('loading-btn');

    // Show the spinner
    document.getElementById('get_wx_spinner').style.display = 'block';

} ) ;