// static/js/priceFormatter.js
document.addEventListener('DOMContentLoaded', function() {
    const formatPrice = (element) => {
      const originalText = element.textContent.trim();
      const numberMatch = originalText.match(/\d+/g);
      
      if (numberMatch) {
        const number = parseInt(numberMatch[0], 10);
        if (!isNaN(number)) {
          const formattedNumber = number.toLocaleString('fa-IR'); // استفاده از فرمت فارسی
          element.textContent = originalText.replace(numberMatch[0], formattedNumber);
        }
      }
    };
  
    document.querySelectorAll('.price, .price_detail').forEach(formatPrice);
  });