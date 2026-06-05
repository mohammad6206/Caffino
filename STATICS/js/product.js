document.addEventListener('DOMContentLoaded', function () {
    const priceElements = document.querySelectorAll('.price');

    function formatPrice(price) {
        const number = parseInt(price.replace(/[^0-9]/g, ''), 10);
        if (isNaN(number)) {
            return price;
        }
        const formattedNumber = number.toLocaleString('en-US');
        return `قیمت : ${formattedNumber}  تومان`; // اضافه کردن پیشوند و پسوند
    }

    priceElements.forEach(element => {
        const originalPrice = element.textContent;
        const formattedPrice = formatPrice(originalPrice);
        element.textContent = formattedPrice;
    });
})