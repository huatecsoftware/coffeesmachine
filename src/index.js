import dva from 'dva';
import './index.css';

if (window.innerWidth > 1300) {
    window.socket = new WebSocket('ws://127.0.0.1:8765/PLCServer')
    window.socket.onopen = () => {
        window.socket.send('start')
        console.log('数据发送中...')
    }
}

// 1. Initialize
const app = dva();

// 2. Plugins
// app.use({});

// 3. Model
app.model(require('./models/index').default);

// 4. Router
app.router(require('./router').default);

// 5. Start
app.start('#root');
