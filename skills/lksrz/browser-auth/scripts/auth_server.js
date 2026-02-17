const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const { chromium } = require('playwright-core');
const path = require('path');
const fs = require('fs');
const crypto = require('crypto');

async function startServer({ 
    port = 19191, 
    host = '127.0.0.1',
    chromiumPath = '/usr/bin/chromium-browser', 
    sessionFile = 'session.json',
    token = crypto.randomBytes(16).toString('hex'),
    proxy = process.env.BROWSER_PROXY || 'socks5://127.0.0.1:40000'
}) {
    const app = express();
    const server = http.createServer(app);
    const io = new Server(server);

    // Middleware to check token in URL
    app.get('/', (req, res) => {
        if (req.query.token !== token) {
            return res.status(403).send('Forbidden: Invalid or missing token');
        }
        const indexPath = path.join(__dirname, '../assets/index.html');
        res.sendFile(indexPath);
    });

    // Socket.io middleware for token auth
    io.use((socket, next) => {
        const socketToken = socket.handshake.query.token;
        if (socketToken === token) {
            return next();
        }
        return next(new Error('Authentication error'));
    });

    io.on('connection', async (socket) => {
        console.log('User authenticated and connected to browser tunnel');
        
        let useProxy = false;
        if (proxy) {
            // Simple check if proxy is available (optional improvement)
            useProxy = true;
        }

        const browser = await chromium.launch({
            executablePath: chromiumPath,
            headless: true,
            proxy: useProxy ? { server: proxy } : undefined,
            args: [
                '--no-sandbox', 
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--single-process'
            ]
        });
        
        const context = await browser.newContext({
            viewport: { width: 1280, height: 720 },
            userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        });
        
        const page = await context.newPage();
        await page.goto('https://google.com');

        const sendScreenshot = async () => {
            try {
                if (page.isClosed()) return;
                const buffer = await page.screenshot({ type: 'jpeg', quality: 50 });
                socket.emit('screenshot', buffer.toString('base64'));
            } catch (e) {}
        };

        const interval = setInterval(sendScreenshot, 400);

        socket.on('mouseClick', async ({ x, y }) => {
            try { await page.mouse.click(x, y); await sendScreenshot(); } catch (e) {}
        });

        socket.on('type', async ({ text }) => {
            try { await page.keyboard.type(text); await sendScreenshot(); } catch (e) {}
        });

        socket.on('key', async ({ key }) => {
            try { await page.keyboard.press(key); await sendScreenshot(); } catch (e) {}
        });

        socket.on('goto', async ({ url }) => {
            try { await page.goto(url.startsWith('http') ? url : `https://${url}`); await sendScreenshot(); } catch (e) {}
        });

        socket.on('done', async () => {
            const cookies = await context.cookies();
            const storage = await page.evaluate(() => JSON.stringify(localStorage));
            fs.writeFileSync(sessionFile, JSON.stringify({ cookies, storage }, null, 2));
            console.log(`Session saved to ${sessionFile}`);
            socket.emit('captured', { success: true });
        });

        socket.on('disconnect', async () => {
            clearInterval(interval);
            await browser.close();
            console.log('Browser closed on disconnect');
        });
    });

    server.listen(port, host, () => {
        console.log(`\n🚀 BROWSER AUTH SERVER READY`);
        console.log(`Host: ${host}`);
        console.log(`Port: ${port}`);
        console.log(`Token: ${token}`);
        console.log(`\nAccess URL: http://${host === '0.0.0.0' ? 'YOUR_IP' : host}:${port}/?token=${token}\n`);
    });

    return server;
}

if (require.main === module) {
    const args = process.argv.slice(2);
    const port = parseInt(args[0]) || 19191;
    const sessionFile = args[1] || 'session.json';
    const host = process.env.AUTH_HOST || '127.0.0.1';
    const token = process.env.AUTH_TOKEN || crypto.randomBytes(16).toString('hex');
    
    startServer({ port, host, sessionFile, token });
}

module.exports = { startServer };
