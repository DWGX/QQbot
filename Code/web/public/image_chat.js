// image_chat.js

// 获取DOM元素
const imageUploadBtn = document.getElementById('imageUploadBtn');
const imageInput = document.getElementById('imageInput');

// 使用全局的 messages 变量
// 不再重新声明 const messages = window.messages;

// 检查必要的元素是否存在
if (!imageUploadBtn || !imageInput || !messages) {
    console.error("图片上传相关的DOM元素未找到。请检查HTML结构。");
}

// 监听上传按钮点击，触发文件选择
imageUploadBtn.addEventListener('click', () => {
    console.log("上传图片按钮被点击");
    imageInput.click();
});

// 处理文件选择
imageInput.addEventListener('change', async (event) => {
    const file = event.target.files[0];
    if (file && (file.type === 'image/png' || file.type === 'image/jpeg')) {
        const reader = new FileReader();
        reader.onload = async function(e) {
            const base64Image = e.target.result.split(',')[1]; // 去除前缀
            // 生成消息ID和时间戳
            const messageId = 'img_' + Date.now();
            const timestamp = new Date().toLocaleTimeString();

            // 显示自己的图片消息（带有锁定的覆盖层）
            displayChatImage('您', base64Image, timestamp, true, messageId);

            // 构建图片消息数据
            const messageData = {
                type: 'image',
                id: messageId,
                content: base64Image
            };

            // 加密消息，确保使用 window.sessionKey
            const encryptedMessage = window.encryptMessage(JSON.stringify(messageData), window.sessionKey);
            if (!encryptedMessage) {
                alert('图片加密失败，请检查控制台获取更多信息。');
                return;
            }

            // 发送加密消息到服务器
            if (ws && ws.readyState === WebSocket.OPEN) {
                ws.send(encryptedMessage);
                console.log('已发送加密图片消息到服务器:', encryptedMessage);
            } else {
                alert('聊天服务器尚未连接，请稍后再试。');
            }

            // 清空文件输入
            imageInput.value = '';
        };
        reader.readAsDataURL(file);
    } else {
        alert('请选择一个PNG或JPEG格式的图片。');
    }
});

// 显示图片消息
function displayChatImage(username, base64Image, timestamp, isOwnMessage = false, messageId = null) {
    const messageElement = document.createElement('div');
    messageElement.classList.add('message');
    if (messageId) {
        messageElement.dataset.messageId = messageId; // 设置消息ID
    }

    const usernameElement = document.createElement('span');
    usernameElement.classList.add('msg-username');
    usernameElement.textContent = username;

    const timeElement = document.createElement('span');
    timeElement.classList.add('msg-time');
    timeElement.textContent = `(${timestamp})`;

    const imageContainer = document.createElement('div');
    imageContainer.classList.add('image-container');

    const imgElement = document.createElement('img');
    imgElement.src = `data:image/png;base64,${base64Image}`;
    imgElement.classList.add('chat-image');
    imgElement.style.display = 'none'; // 初始隐藏

    const lockOverlay = document.createElement('div');
    lockOverlay.classList.add('lock-overlay');

    // 点击解锁图片
    lockOverlay.addEventListener('click', () => {
        imgElement.style.display = 'block';
        lockOverlay.style.display = 'none';
    });

    imageContainer.appendChild(imgElement);
    imageContainer.appendChild(lockOverlay);

    messageElement.appendChild(usernameElement);
    messageElement.appendChild(timeElement);
    messageElement.appendChild(imageContainer);

    // 如果是自己发送的图片，添加撤回和编辑按钮
    if (isOwnMessage && messageId) {
        // 撤回按钮
        const revokeButton = document.createElement('button');
        revokeButton.textContent = '撤回';
        revokeButton.classList.add('revoke-btn', 'unified-btn');
        revokeButton.style.marginLeft = '10px';
        revokeButton.addEventListener('click', function () {
            if (confirm('确定要撤回此图片吗？')) {
                revokeMessage(messageId);
            }
        });

        // 编辑按钮（例如替换图片）
        const editButton = document.createElement('button');
        editButton.textContent = '编辑';
        editButton.classList.add('edit-btn', 'unified-btn');
        editButton.style.marginLeft = '10px';
        editButton.addEventListener('click', function () {
            imageInput.click(); // 重新选择图片
            // 监听文件选择并替换图片
            imageInput.onchange = async function(e) {
                const newFile = e.target.files[0];
                if (newFile && (newFile.type === 'image/png' || newFile.type === 'image/jpeg')) {
                    const reader = new FileReader();
                    reader.onload = async function(event) {
                        const newBase64Image = event.target.result.split(',')[1];
                        // 更新图片显示
                        imgElement.src = `data:image/png;base64,${newBase64Image}`;
                        imgElement.style.display = 'none';
                        lockOverlay.style.display = 'block';

                        // 构建编辑消息数据
                        const editData = {
                            type: 'edit_image',
                            id: messageId,
                            newContent: newBase64Image
                        };

                        // 加密消息
                        const encryptedEdit = window.encryptMessage(JSON.stringify(editData), window.sessionKey);
                        if (!encryptedEdit) {
                            alert('图片编辑加密失败，请检查控制台获取更多信息。');
                            return;
                        }

                        // 发送加密编辑消息到服务器
                        if (ws && ws.readyState === WebSocket.OPEN) {
                            ws.send(encryptedEdit);
                            console.log('已发送加密编辑图片消息到服务器:', encryptedEdit);
                        } else {
                            alert('聊天服务器尚未连接，请稍后再试。');
                        }

                        // 清空文件输入
                        imageInput.value = '';
                    };
                    reader.readAsDataURL(newFile);
                } else {
                    alert('请选择一个PNG或JPEG格式的图片。');
                }
            };
        });

        // 将按钮添加到消息元素中
        messageElement.appendChild(editButton);
        messageElement.appendChild(revokeButton);
    }

    // 将消息元素添加到消息容器中
    messages.appendChild(messageElement);
    messages.scrollTop = messages.scrollHeight; // 滚动到最底部
}

// 处理接收的图片消息
function handleIncomingImageMessage(messageData) {
    const { id, timestamp, username, content } = messageData;
    displayChatImage(username, content, timestamp, false, id);
}

// 监听来自服务器的消息
document.addEventListener('messageReceived', function (event) {
    const messageData = event.detail;
    if (messageData.type === 'image') {
        handleIncomingImageMessage(messageData);
    } else if (messageData.type === 'edit_image') {
        // 处理编辑后的图片
        const { id, newContent } = messageData;
        const messageElements = document.querySelectorAll(`[data-message-id="${id}"]`);
        messageElements.forEach(elem => {
            const imgElement = elem.querySelector('.chat-image');
            const lockOverlay = elem.querySelector('.lock-overlay');
            if (imgElement && lockOverlay) {
                imgElement.src = `data:image/png;base64,${newContent}`;
                imgElement.style.display = 'none';
                lockOverlay.style.display = 'block';
                console.log(`已更新消息ID: ${id} 的图片内容`);
            }
        });
    }
});
