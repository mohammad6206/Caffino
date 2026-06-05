function copyPhoneNumber() {
    const number = document.getElementById("phoneNumber").innerText;
    navigator.clipboard.writeText(number).then(() => {
        const msg = document.getElementById("copyMessage");
        msg.style.display = "inline-block";
        setTimeout(() => {
            msg.style.display = "none";
        }, 1500);
    });
}
