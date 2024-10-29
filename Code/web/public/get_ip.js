// get_ip.js

// 异步函数获取公共 IP 地址及其位置信息
async function fetchPublicIP() {
    const ipLocationAPI = `https://get.geojs.io/v1/ip/geo.json`;

    try {
        const response = await fetch(ipLocationAPI);
        if (response.ok) {
            const locationData = await response.json();
            console.log(`IP地址信息: ${JSON.stringify(locationData)}`);
            return {
                ip: locationData.ip,
                country: locationData.country,
                region: locationData.region,
                city: locationData.city,
                district: locationData.district || '',
                isp: locationData.organization || '',
                postalCode: locationData.postal || '',
                areaCode: locationData.area || ''
            };
        } else {
            throw new Error("获取 IP 位置信息失败: 请求失败");
        }
    } catch (error) {
        console.error("获取 IP 位置信息失败:", error);
        throw new Error("获取 IP 位置信息失败");
    }
}

document.addEventListener('DOMContentLoaded', async () => {
    console.log("DOM fully loaded and parsed."); // 确保事件触发

    try {
        const clientIPInfo = await fetchPublicIP();
        console.log(`客户端实机IP信息: ${JSON.stringify(clientIPInfo)}`);
        document.dispatchEvent(new CustomEvent("clientIPFetched", { detail: clientIPInfo }));
    } catch (error) {
        console.error("获取客户端 IP 信息失败:", error);
        document.dispatchEvent(new CustomEvent("clientIPFetchError", { detail: { error: error.message } }));
    }
});
