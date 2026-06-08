const colors = [
    { name: 'Blue', value: '#3b82f6', hex: '255,0,0' },      // BGR logic maps to frontend nicely if we just send index or hex
    { name: 'Green', value: '#22c55e', hex: '0,255,0' },
    { name: 'Red', value: '#ef4444', hex: '0,0,255' },
    { name: 'Yellow', value: '#eab308', hex: '0,255,255' },
    { name: 'Pink', value: '#ec4899', hex: '255,0,255' },
    { name: 'Orange', value: '#f97316', hex: '0,165,255' },
    { name: 'Purple', value: '#a855f7', hex: '255,0,128' },
    { name: 'Cyan', value: '#06b6d4', hex: '255,255,0' }
];

let state = {
    colorIndex: 0,
    brushSize: 5,
    mode: 'Hover',
    fps: 0
};

// Initialize UI
let isDraggingSlider = false;

function init() {
    setupColors();
    setupTools();
    pollStatus(); // Immediately update the UI state on refresh/load
    
    // Start polling status
    setInterval(pollStatus, 500); // 2 fps polling for UI updates
}

function setupColors() {
    const palette = document.getElementById('color-palette');
    colors.forEach((c, idx) => {
        const swatch = document.createElement('div');
        swatch.className = 'color-swatch';
        swatch.style.backgroundColor = c.value;
        swatch.style.color = c.value; // for box-shadow currentColor
        swatch.title = c.name;
        
        swatch.onclick = () => {
            sendCommand('set_color', { index: idx });
        };
        palette.appendChild(swatch);
    });
}

function setupTools() {
    // Slider
    const slider = document.getElementById('brush-slider');
    const display = document.getElementById('brush-size-display');
    
    slider.onmousedown = () => { isDraggingSlider = true; };
    slider.onmouseup = () => { isDraggingSlider = false; };
    slider.ontouchstart = () => { isDraggingSlider = true; };
    slider.ontouchend = () => { isDraggingSlider = false; };
    
    slider.oninput = (e) => {
        const val = parseInt(e.target.value);
        display.innerText = val;
        sendCommand('set_brush_size', { size: val });
    };

    // Buttons
    document.getElementById('btn-clear').onclick = () => sendCommand('clear');
    document.getElementById('btn-undo').onclick = () => sendCommand('undo');
    
    document.getElementById('btn-save').onclick = () => {
        sendCommand('save');
        const btn = document.getElementById('btn-save');
        const originalText = btn.innerHTML;
        btn.innerHTML = '<span>Saved!</span>';
        setTimeout(() => btn.innerHTML = originalText, 1000);
    };
    
    document.getElementById('btn-eraser').onclick = () => sendCommand('eraser');

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        if (e.ctrlKey && e.key.toLowerCase() === 'z') {
            sendCommand('undo');
            e.preventDefault();
        } else if (e.key.toLowerCase() === 's') {
            sendCommand('save');
            e.preventDefault();
        }
    });
}

// Network communication
async function sendCommand(action, payload = {}) {
    try {
        await fetch('/api/command', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action, ...payload })
        });
        // Immediate visual feedback where possible (optimistic update)
        if (action === 'set_color') {
            updateUIColor(payload.index);
        } else if (action === 'eraser') {
            updateUIMode('Eraser');
        }
    } catch (e) {
        console.error("Failed to send command:", e);
    }
}

async function pollStatus() {
    try {
        const res = await fetch('/api/status');
        const data = await res.json();
        
        // Update state
        state = data;
        
        // Update UI
        document.getElementById('stat-fps').innerText = data.fps;
        document.getElementById('stat-mode').innerText = data.mode;
        document.getElementById('hud-mode').innerText = data.mode;
        
        if (!isDraggingSlider && document.activeElement !== document.getElementById('brush-slider')) {
            document.getElementById('brush-slider').value = data.brushSize;
            document.getElementById('brush-size-display').innerText = data.brushSize;
        }
        
        updateUIColor(data.colorIndex);
        
        // Update tool highlights
        document.getElementById('btn-eraser').classList.toggle('active', data.mode === 'Eraser');
        
    } catch (e) {
        // Ignore fetch errors during polling
    }
}

function updateUIColor(idx) {
    if(idx < 0 || idx >= colors.length) return;
    
    // Update swatches
    document.querySelectorAll('.color-swatch').forEach((el, i) => {
        el.classList.toggle('active', i === idx);
    });
    
    // Update HUD indicator
    const hudColor = document.getElementById('hud-color');
    hudColor.style.backgroundColor = colors[idx].value;
}

function updateUIMode(mode) {
    document.getElementById('stat-mode').innerText = mode;
    document.getElementById('hud-mode').innerText = mode;
}

// Run
window.onload = init;
