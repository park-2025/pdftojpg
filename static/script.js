document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('upload-form');
    const fileInput = document.getElementById('pdf-file');
    const resultSection = document.getElementById('result-section');
    const imageList = document.getElementById('image-list');
    const downloadAll = document.getElementById('download-all');

    form.addEventListener('submit', async function (event) {
        event.preventDefault();

        const file = fileInput.files[0];
        if (!file) {
            alert("PDF 파일을 선택해주세요!");
            return;
        }

        const formData = new FormData();
        formData.append('pdf_file', file);

        try {
            const response = await fetch('/convert', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error('서버 응답 실패');
            }

            const data = await response.json(); // 이미지 파일 리스트를 받는다고 가정

            // 결과 영역 초기화
            imageList.innerHTML = '';
            resultSection.style.display = 'block';

            // 각 이미지 표시
            data.images.forEach(imgUrl => {
                const img = document.createElement('img');
                img.src = imgUrl;
                img.alt = 'Converted JPG';
                img.style.width = '100%';
                img.style.borderRadius = '10px';
                imageList.appendChild(img);
            });

            // 다운로드 링크 설정 (zip 파일일 수도 있음)
            if (data.download_url) {
                downloadAll.href = data.download_url;
                downloadAll.style.display = 'inline-block';
            } else {
                downloadAll.style.display = 'none';
            }
        } catch (error) {
            console.error('변환 실패:', error);
            alert('PDF 변환 중 오류가 발생했어요!');
        }
    });
});
