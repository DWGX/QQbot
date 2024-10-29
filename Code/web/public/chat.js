// chat.js

// 获取DOM元素
window.messages = document.getElementById('messages');
const chatForm = document.getElementById('chatForm');
const chatInput = document.getElementById('chatInput');
const getKeyBtn = document.getElementById('getKeyBtn');
const keyDisplay = document.getElementById('keyDisplay');
const userKeySpan = document.getElementById('userKey');
const onlineUsersDiv = document.getElementById('onlineUsers');

// 检查DOM元素是否存在
if (!window.messages || !chatForm || !chatInput || !getKeyBtn || !keyDisplay || !userKeySpan || !onlineUsersDiv) {
    console.error("One or more DOM elements were not found. Please check the HTML structure.");
}

// 将 PRE_SHARED_KEY 附加到 window 对象，使其在全局范围内可访问
window.PRE_SHARED_KEY = 'G6JrXcZLw1Q8P3F7d9K0M2N4B6V8Y1A3'; // 替换为您的32字符密钥

// 将 sessionKey 附加到 window 对象，使其在全局范围内可访问
window.sessionKey = null; // WordArray
let ws = null;
let reconnectInterval = 5000; // 5秒后重连

let ownIP = null; // 存储自己的IP

// 验证预共享密钥长度
console.log(`Client PRE_SHARED_KEY length: ${window.PRE_SHARED_KEY.length} characters`); // 应为32

if (window.PRE_SHARED_KEY.length !== 32) {
    console.error("预共享密钥长度不正确。应为32字符。");
    alert("预共享密钥长度不正确。请联系管理员。");
}

// 加密函数
window.encryptMessage = function encryptMessage(message, keyWordArray) {
    try {
        // 确保密钥是 WordArray 类型
        if (typeof keyWordArray === 'string') {
            keyWordArray = CryptoJS.enc.Base64.parse(keyWordArray);
        }

        // 检查 keyWordArray 是否正确初始化
        if (!keyWordArray || !keyWordArray.words) {
            throw new Error('Invalid keyWordArray');
        }

        // 生成随机IV
        const iv = CryptoJS.lib.WordArray.random(16); // 128位IV
        const encrypted = CryptoJS.AES.encrypt(message, keyWordArray, {
            iv: iv,
            mode: CryptoJS.mode.CBC,
            padding: CryptoJS.pad.Pkcs7
        });
        // 将IV和密文拼接并进行Base64编码
        const ivCiphertext = iv.concat(encrypted.ciphertext);
        return CryptoJS.enc.Base64.stringify(ivCiphertext);
    } catch (error) {
        console.error('加密消息失败:', error);
        return null;
    }
}

// 解密函数
window.decryptMessage = function decryptMessage(encryptedMessage, keyWordArray) {
    try {
        // 确保密钥是 WordArray 类型
        if (typeof keyWordArray === 'string') {
            keyWordArray = CryptoJS.enc.Base64.parse(keyWordArray);
        }

        // 检查 keyWordArray 是否正确初始化
        if (!keyWordArray || !keyWordArray.words) {
            throw new Error('Invalid keyWordArray');
        }

        const ivCiphertext = CryptoJS.enc.Base64.parse(encryptedMessage);
        const iv = CryptoJS.lib.WordArray.create(ivCiphertext.words.slice(0, 4)); // 16 bytes = 4 words
        const ciphertext = CryptoJS.lib.WordArray.create(ivCiphertext.words.slice(4));

        const decrypted = CryptoJS.AES.decrypt({ ciphertext: ciphertext }, keyWordArray, {
            iv: iv,
            mode: CryptoJS.mode.CBC,
            padding: CryptoJS.pad.Pkcs7
        });
        const plaintext = decrypted.toString(CryptoJS.enc.Utf8);
        return plaintext;
    } catch (error) {
        console.error('解密消息失败:', error);
        return null;
    }
}


// 显示聊天消息
function displayChatMessage(username, text, timestamp, isOwnMessage = false, messageId = null) {
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

    const textElement = document.createElement('span');
    textElement.classList.add('msg-text');
    textElement.textContent = text;

    messageElement.appendChild(usernameElement);
    messageElement.appendChild(timeElement);
    messageElement.appendChild(textElement);

    // 如果是自己发送的消息，添加撤回和编辑按钮
    if (isOwnMessage && messageId) {
        // 撤回按钮
        const revokeButton = document.createElement('button');
        revokeButton.textContent = '撤回';
        revokeButton.classList.add('revoke-btn', 'unified-btn');
        revokeButton.style.marginLeft = '10px';
        revokeButton.addEventListener('click', function () {
            if (confirm('确定要撤回此消息吗？')) {
                revokeMessage(messageId);
            }
        });

        // 编辑按钮
        const editButton = document.createElement('button');
        editButton.textContent = '编辑';
        editButton.classList.add('edit-btn', 'unified-btn');
        editButton.style.marginLeft = '10px';
        editButton.addEventListener('click', function () {
            const newContent = prompt('编辑您的消息：', text);
            if (newContent !== null && newContent.trim() !== '') {
                editMessage(messageId, newContent.trim());
            }
        });

        // 将按钮添加到消息元素中
        messageElement.appendChild(editButton);
        messageElement.appendChild(revokeButton);
    }

    // 将消息元素添加到消息容器中
    window.messages.appendChild(messageElement);
    window.messages.scrollTop = window.messages.scrollHeight; // 滚动到最底部
}

// 显示系统消息
function displaySystemMessage(text) {
    const messageElement = document.createElement('div');
    messageElement.classList.add('message');

    const usernameElement = document.createElement('span');
    usernameElement.classList.add('msg-username');
    usernameElement.textContent = '系统';

    const timeElement = document.createElement('span');
    timeElement.classList.add('msg-time');
    const timestamp = new Date().toLocaleTimeString();
    timeElement.textContent = `(${timestamp})`;

    const textElement = document.createElement('span');
    textElement.classList.add('msg-text');
    textElement.textContent = text;

    messageElement.appendChild(usernameElement);
    messageElement.appendChild(timeElement);
    messageElement.appendChild(textElement);

    window.messages.appendChild(messageElement);
    window.messages.scrollTop = window.messages.scrollHeight; // 滚动到最底部
}

function displayYourIP(ip, country, region, city, district, isp) {
    onlineUsersDiv.innerHTML = `<h3>实机IP</h3>
    <p>IP: ${ip}</p>
    <p>国家: ${country}</p>
    <p>省份: ${region}</p>
    <p>城市: ${city}</p>
    <p>区: ${district}</p>
    <p>运营商: ${isp}</p>
    <h3>在线用户</h3>`;
    console.log('显示 IP 信息: ', { ip, country, region, city, district, isp });
}

// 更新在线用户列表
function updateOnlineUsers(users) {
    onlineUsersDiv.innerHTML = `<h3>实机IP</h3>
    <p>${ownIP}</p>
    <h3>在线用户</h3>`;

    if (users.length === 0) {
        onlineUsersDiv.innerHTML += '<p>暂无在线用户。</p>';
    } else {
        const ul = document.createElement('ul');
        for (const user of users) {
            // 跳过自己
            if (user.ip === ownIP) {
                continue;
            }

            // 跳过本地IP
            if (user.ip === '127.0.0.1' || user.ip === '::1') {
                continue;
            }

            const li = document.createElement('li');
            li.textContent = `    ${user.ip}`;
            ul.appendChild(li);
        }
        if (ul.children.length === 0) {
            onlineUsersDiv.innerHTML += '<p>暂无在线用户。</p>';
        } else {
            onlineUsersDiv.appendChild(ul);
        }
    }
}

// 连接到 WebSocket 服务器
function connectWebSocket() {
    if (!window.sessionKey) {
        console.log('等待接收会话密钥...');
    }

    // 如果已经存在连接，先关闭
    if (ws) {
        ws.close();
    }

    // 请将下面的URL替换为您的服务器地址和端口
    const serverIP = 'dwgx.e2.luyouxia.net'; // 替换为您的服务器IP
    const serverPort = '20008'; // 替换为您的服务器端口，例如20008
    const wsProtocol = location.protocol === 'https:' ? 'wss' : 'ws';
    const wsUrl = `${wsProtocol}://${serverIP}:${serverPort}`;

    console.log(`尝试连接 WebSocket 服务器: ${wsUrl}`);
    ws = new WebSocket(wsUrl);

    ws.onopen = function () {
        console.log('已连接到聊天服务器');
        displaySystemMessage('已连接到聊天服务器');

        // 连接后发送用户的真实 IP 地址给服务器
        const ipData = {
            type: 'client_ip',
            ip: ownIP
        };
        ws.send(JSON.stringify(ipData));
        console.log('已发送客户端 IP 地址给服务器:', ipData);

        // 连接后发送用户的密钥交换请求
        const keyExchangeRequest = {
            type: 'request_session_key'
        };
        ws.send(JSON.stringify(keyExchangeRequest));
    };

    ws.onmessage = function (event) {
        const encryptedMsg = event.data;

        // 首先处理会话密钥消息
        if (!window.sessionKey) {
            // 会话密钥消息类型为 'session_key'
            try {
                const messageData = JSON.parse(encryptedMsg);
                if (messageData.type === 'session_key') {
                    // 使用预共享密钥解密会话密钥
                    const decryptedSessionKey = window.decryptMessage(messageData.session_key, CryptoJS.enc.Utf8.parse(window.PRE_SHARED_KEY));
                    if (decryptedSessionKey) {
                        // decryptedSessionKey 是 Base64 编码的 session_key_bytes
                        const sessionKeyWordArray = CryptoJS.enc.Base64.parse(decryptedSessionKey);
                        window.sessionKey = sessionKeyWordArray;
                        userKeySpan.textContent = decryptedSessionKey;
                        displaySystemMessage('会话密钥已接收，开始安全通信。');

                        // 触发 messageReceived 事件
                        document.dispatchEvent(new CustomEvent('messageReceived', { detail: messageData }));

                        return;
                    } else {
                        console.error('会话密钥解密失败');
                        displaySystemMessage('会话密钥解密失败。');
                        return;
                    }
                }
            } catch (error) {
                console.error('处理会话密钥消息失败:', error);
                displaySystemMessage('处理会话密钥消息失败。');
                return;
            }
        }

        if (window.sessionKey) {
            const decryptedMsg = window.decryptMessage(encryptedMsg, window.sessionKey);
            if (decryptedMsg) {
                try {
                    const messageData = JSON.parse(decryptedMsg);

                    if (messageData.type === 'message') {
                        const { id, timestamp, username, content } = messageData;
                        displayChatMessage(username, content, timestamp, false, id);
                    } else if (messageData.type === 'revoke') {
                        const { id } = messageData;
                        // 删除对应的消息
                        const messageElements = document.querySelectorAll(`[data-message-id="${id}"]`);
                        messageElements.forEach(elem => elem.remove());
                    } else if (messageData.type === 'edit') {
                        const { id, newContent } = messageData;
                        // 查找对应的消息并更新内容
                        const messageElements = document.querySelectorAll(`[data-message-id="${id}"]`);
                        messageElements.forEach(elem => {
                            const textElement = elem.querySelector('.msg-text');
                            if (textElement) {
                                textElement.textContent = newContent;
                            }
                        });
                    } else if (messageData.type === 'system') {
                        displaySystemMessage(messageData.content);
                    } else if (messageData.type === 'update_online_users') {
                        const users = messageData.users;
                        updateOnlineUsers(users);
                    } else if (messageData.type === 'your_ip') {
                        const { ip, country, region, city, district, isp } = messageData;
                        ownIP = ip;
                        displayYourIP(ip, country, region, city, district, isp);
                    }

                    // 触发 messageReceived 事件
                    document.dispatchEvent(new CustomEvent('messageReceived', { detail: messageData }));

                } catch (error) {
                    console.error('消息解析失败:', error);
                }
            } else {
                console.error('解密消息失败');
            }
        }
    };

    ws.onclose = function (event) {
        displaySystemMessage('已断开与聊天服务器的连接');
        // 自动重连
        setTimeout(() => {
            displaySystemMessage('尝试重新连接聊天服务器...');
            connectWebSocket();
        }, reconnectInterval);
    };

    ws.onerror = function (error) {
        console.error('WebSocket错误:', error);
        displaySystemMessage('WebSocket连接出现错误，请稍后重试。');
    };
}

// 获取密钥的功能（在此方案中不需要生成密钥）
getKeyBtn.addEventListener('click', function () {
    alert('会话密钥将在连接时自动生成。');
});

// 显示预共享密钥
document.addEventListener('DOMContentLoaded', function () {
    keyDisplay.style.display = 'block';
    userKeySpan.textContent = '生成中...';
    displaySystemMessage('使用预共享密钥。系统正在连接聊天服务器。');
    // 连接将在获取IP后触发
});

// 处理获取 IP 失败的情况
document.addEventListener('clientIPFetchError', function (event) {
    const errorMsg = event.detail.error;
    console.error("获取客户端 IP 失败:", errorMsg);
    displaySystemMessage("获取客户端 IP 失败，无法连接聊天服务器。");
});

// 处理获取 IP 成功的情况
document.addEventListener('clientIPFetched', function (event) {
    const ipInfo = event.detail;
    console.log("获取到的 IP 信息:", ipInfo); // 调试日志
    ownIP = ipInfo.ip;
    displayYourIP(ipInfo.ip, ipInfo.country, ipInfo.region, ipInfo.city, ipInfo.district, ipInfo.isp);
    console.log("已显示 IP 信息，准备连接 WebSocket"); // 调试日志
    // 连接WebSocket
    connectWebSocket();
});

// 页面加载时的初始化逻辑
document.addEventListener('DOMContentLoaded', function () {
    // 隐藏加载动画并显示主容器
    const loadingOverlay = document.getElementById('loadingOverlay');
    const mainContainer = document.getElementById('mainContainer');
    if (loadingOverlay && mainContainer) {
        loadingOverlay.style.display = 'none';
        mainContainer.style.display = 'block';
        console.log('隐藏加载动画并显示主容器');
    } else {
        console.error('加载动画或主容器未找到');
    }

    // 平滑滚动效果
    const links = document.querySelectorAll('nav a');
    for (const link of links) {
        link.addEventListener('click', smoothScroll);
    }

    // 加入频道按钮点击事件
    const joinChannelButtons = document.querySelectorAll('.join-channel-btn');
    joinChannelButtons.forEach(button => {
        button.addEventListener('click', function () {
            window.location.href = 'https://pd.qq.com/s/9m10fpwyu';
        });
    });

    // 卡片翻转事件
    const flipButtons = document.querySelectorAll('.flip-btn');
    flipButtons.forEach(button => {
        button.addEventListener('click', function () {
            const cardInner = this.closest('.card-inner');
            cardInner.classList.toggle('is-flipped');
        });
    });

    const flipBackButtons = document.querySelectorAll('.flip-back-btn');
    flipBackButtons.forEach(button => {
        button.addEventListener('click', function () {
            const cardInner = this.closest('.card-inner');
            cardInner.classList.toggle('is-flipped');
        });
    });
});

// 绑定表单提交事件
if (chatForm) {
    chatForm.addEventListener('submit', async function (e) {
        e.preventDefault(); // 阻止默认提交行为
        const message = chatInput.value.trim();
        if (message === '') return;

        // 生成消息ID和时间戳
        const messageId = 'msg_' + Date.now();
        const timestamp = new Date().toLocaleTimeString();

        // 显示自己的消息
        displayChatMessage('您', message, timestamp, true, messageId);

        // 构建消息数据
        const messageData = {
            type: 'message',
            id: messageId,
            content: message
        };

        // 加密消息
        const encryptedMessage = window.encryptMessage(JSON.stringify(messageData), window.sessionKey);
        if (!encryptedMessage) {
            alert('消息加密失败，请检查控制台获取更多信息。');
            return;
        }

        // 发送加密消息到服务器
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(encryptedMessage);
        } else {
            alert('聊天服务器尚未连接，请稍后再试。');
        }

        // 清空输入框
        chatInput.value = '';
    });
} else {
    console.error('chatForm 元素未找到。');
}

// 撤回消息函数
async function revokeMessage(messageId) {
    if (ws && ws.readyState === WebSocket.OPEN) {
        const revokeData = {
            type: 'revoke',
            id: messageId
        };
        const revokeString = JSON.stringify(revokeData);
        const encryptedRevoke = window.encryptMessage(revokeString, window.sessionKey);
        if (!encryptedRevoke) {
            alert('消息撤回加密失败，请检查控制台获取更多信息。');
            return;
        }
        ws.send(encryptedRevoke);
        // 本地删除消息
        const messageElements = document.querySelectorAll(`[data-message-id="${messageId}"]`);
        messageElements.forEach(elem => elem.remove());
    } else {
        alert('聊天服务器尚未连接，请稍后再试。');
    }
}

// 编辑消息函数
async function editMessage(messageId, newContent) {
    if (ws && ws.readyState === WebSocket.OPEN) {
        const editData = {
            type: 'edit',
            id: messageId,
            newContent: newContent
        };
        const editString = JSON.stringify(editData);
        const encryptedEdit = window.encryptMessage(editString, window.sessionKey);
        if (!encryptedEdit) {
            alert('消息编辑加密失败，请检查控制台获取更多信息。');
            return;
        }
        ws.send(encryptedEdit);
        // 本地更新消息内容
        const messageElements = document.querySelectorAll(`[data-message-id="${messageId}"]`);
        messageElements.forEach(elem => {
            const textElement = elem.querySelector('.msg-text');
            if (textElement) {
                textElement.textContent = newContent;
            }
        });
    } else {
        alert('聊天服务器尚未连接，请稍后再试。');
    }
}

// smoothScroll函数
function smoothScroll(e) {
    e.preventDefault();
    const targetId = this.getAttribute('href').substring(1);
    const targetElement = document.getElementById(targetId);
    if (targetElement) {
        const targetPosition = targetElement.offsetTop;
        window.scrollTo({
            top: targetPosition - 70,
            behavior: 'smooth'
        });
    }
}
