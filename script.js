// ছবিটি আপলোড করার সাথে সাথে প্রিভিউ দেখানোর ফাংশন
document.getElementById('imageUpload').addEventListener('change', function(event) {
    const [file] = event.target.files;
    if (file) {
        const uploadedImage = document.getElementById('uploadedImage');
        uploadedImage.src = URL.createObjectURL(file);
        uploadedImage.style.display = 'block';
        document.getElementById('resultText').textContent = 'লেখা সনাক্তকরণের জন্য প্রস্তুত...';
    }
});

// এই ফাংশনটি Flask সার্ভারে ছবি পাঠাবে
function processImage() {
    const fileInput = document.getElementById('imageUpload');
    if (fileInput.files.length === 0) {
        alert("দয়া করে একটি ছবি আপলোড করুন!");
        return;
    }

    document.getElementById('resultText').textContent = 'ছবি প্রক্রিয়াকরণ হচ্ছে, অপেক্ষা করুন...';
    
    // ছবি পাঠানোর জন্য FormData ব্যবহার
    const formData = new FormData();
    // 'image' নামটি app.py-এর request.files['image'] এর সাথে মিলতে হবে
    formData.append('image', fileInput.files[0]);

    // Flask সার্ভারের ঠিকানা (আপনার মোবাইলের লোকাল হোস্ট)
    const serverUrl = 'http://127.0.0.1:5000/upload'; 

    fetch(serverUrl, {
        method: 'POST',
        body: formData // ছবি পাঠানো হচ্ছে
    })
    .then(response => response.json())
    .then(data => {
        // সার্ভার থেকে আসা ফলাফল দেখানো
        if (data.error) {
            document.getElementById('resultText').textContent = `ত্রুটি: ${data.error}`;
        } else {
            document.getElementById('resultText').textContent = data.text;
        }
    })
    .catch(error => {
        // সার্ভার না চললে এই ত্রুটি দেখাবে
        document.getElementById('resultText').textContent = `সার্ভারের সাথে সংযোগ করা যায়নি। নিশ্চিত করুন app.py Pydroid 3-এ চলছে।`;
        console.error('Error:', error);
    });
}