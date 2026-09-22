Here is the comprehensive **Validation Test Cases Matrix** designed to ensure the **Antigravity Swarm Command Deck (ASCD)** functions flawlessly across both Web (Desktop) and Mobile environments.

Given the SCADA-like nature of this interface (WebGL, high-frequency WebSockets, code editors, and complex data visualization), the validation strategy relies heavily on **End-to-End (E2E) testing**, **Touch Gesture Emulation**, and **Visual Regression Testing**.

---

### 🌐 1. Core Infrastructure & Real-Time Telemetry

*Objective: Ensure the application backbone can handle large volumes of real-time data from the Gemini swarm without crashing the browser or draining mobile batteries.*

| Test ID | Component | Action / Scenario | Expected Result (Desktop Web) | Expected Result (Mobile Web / PWA) |
| --- | --- | --- | --- | --- |
| **COR-01** | **Responsive Layout** | Load the app and resize the viewport from 1920px down to 375px. | Left Sidebar is visible. Top HUD shows all metrics side-by-side. | Sidebar collapses into a Hamburger menu or Bottom Nav. Top HUD becomes a swipeable carousel to prevent text truncation. |
| **COR-02** | **WebSocket Stress** | Inject 200 agent log events and token updates per second via a Redis stream mock. | UI maintains 60 FPS. DOM virtualization works (no memory leaks or UI freezing). | Same. List virtualization keeps the DOM tree small, preventing mobile CPU overheating. |
| **COR-03** | **Network Resiliency** | Disconnect the internet for 15 seconds, then reconnect. | UI dims with a red "Offline - Read Only" banner. Upon reconnection, it fetches missed Redis events and updates state seamlessly without a full page reload. | Same. Handles Wi-Fi $\leftrightarrow$ 4G/5G network handovers gracefully without losing session state. |

---

### 🧬 2. Deck 1: The Forge (Engineering, Physics & Code)

*Objective: Validate the complex interaction with graph nodes, 3D math rendering, and the IDE components on both mouse and touch interfaces.*

| Test ID | Component | Action / Scenario | Expected Result (Desktop Web) | Expected Result (Mobile Web / PWA) |
| --- | --- | --- | --- | --- |
| **FRG-01** | **DAG Architecture** | Move a microservice node from one branch to another in the React Flow graph. | Node moves smoothly via drag-and-drop. Edge lines reconnect dynamically. Event is dispatched to the backend. | Drag-and-drop triggers via **Long-Press**. 1-finger pan and 2-finger pinch-to-zoom work without scrolling the entire web page (scroll lock). |
| **FRG-02** | **Physics Engine** | Load a 3D Three.js simulation alongside KaTeX math formulas. | WebGL canvas renders. Rotates smoothly with mouse click-and-drag. Math formulas render without raw syntax visible. | Canvas scales to screen width. Touch rotation works. Fallback to 2D plot if the mobile GPU fails WebGL context creation. |
| **FRG-03** | **Lean 4 Tribunal** | Inject code containing an unproven theorem (the `sorry` keyword) into the Monaco Editor. | The Theorem Gutter instantly flashes a red 🚨 icon on the exact line. | Monaco editor switches to a mobile-friendly view. Gutter icon remains visible without horizontal overflow. |

---

### ⚔️ 3. Deck 2: Proving Grounds (QA & UI Validation)

*Objective: Validate data-heavy visualization and pixel-perfect comparison tools.*

| Test ID | Component | Action / Scenario | Expected Result (Desktop Web) | Expected Result (Mobile Web / PWA) |
| --- | --- | --- | --- | --- |
| **PRV-01** | **QA Fuzzing Heatmap** | Load a 100x100 matrix (10,000 cells) of Agent test results. | Canvas rendering displays all cells instantly. Hovering over a red cell opens a tooltip with the crash stack trace. | Tooltip is triggered by a **Tap**. Scrolling inside the canvas works smoothly without triggering native pull-to-refresh. |
| **PRV-02** | **Holographic Diff** | Use the Image Compare Slider (Baseline Figma UI vs Agent Generated UI). | Clicking and dragging the vertical slider left/right reveals magenta pixels (Pixelmatch diff). | Slider follows the finger precisely. **Crucial:** Does not trigger the mobile browser's native "swipe right to go back" gesture. |

---

### ⚙️ 4. Deck 3: Engine Room (Admin, RL & MCP Servers)

*Objective: Validate the management of AI tools, Token FinOps, and Human-in-the-loop reinforcement learning.*

| Test ID | Component | Action / Scenario | Expected Result (Desktop Web) | Expected Result (Mobile Web / PWA) |
| --- | --- | --- | --- | --- |
| **ENG-01** | **RL Tinder (DPO)** | Evaluate an Agent's generated code snippet for the nightly training dataset. | Click "Accept" or "Reject" buttons. The next code card loads instantly. | **Swipe Gestures:** Swiping the card Right = Accept, Left = Reject. Card animates off-screen and updates the Redis dataset counter silently. |
| **ENG-02** | **Context Treemap** | View the memory allocation of Gemini's 2 Million token context. | D3.js Treemap displays correctly. Clicking a block (e.g., 'GitHub Docs') triggers a "Drill-down" animation into that specific category. | Same. Tap to drill-down, with a highly visible "Back/Zoom out" button for fat-finger accessibility. |
| **ENG-03** | **Memory Pruning** | Remove a false memory node from the Vector 3D Graph. | Right-click node $\to$ Select "Prune". Node explodes into particles and the Agent's vector memory is purged. | **Long-press** node $\to$ Select "Prune" from the floating context menu. |
| **ENG-04** | **MCP Patchbay** | Toggle off the `MCP Bash Terminal` server to restrict Agent access. | Switch disables, shows a loading spinner, then turns grey. Toast notification confirms MCP shutdown. | Switch hit-area is large enough (min 44x44px for iOS/Android accessibility standards). Same visual feedback. |

---

### 🕹️ 5. God Mode (Emergency Interruptions)

*Objective: The most critical feature—ensuring a human can halt, steer, and rewind the AI swarm at any moment.*

| Test ID | Component | Action / Scenario | Expected Result (Desktop Web) | Expected Result (Mobile Web / PWA) |
| --- | --- | --- | --- | --- |
| **GOD-01** | **Halt Execution** | While the Swarm is actively generating code, press the `Spacebar`. | UI dims globally (Overlay). Swarm status changes to `PAUSED`. The floating command terminal appears and auto-focuses. | Tap the red floating action button (FAB) 🛑. UI dims, terminal opens, and the **virtual keyboard opens without hiding the input field**. |
| **GOD-02** | **Steer & Resume** | Type "Fix the SQL injection using parameterized queries" and press `Enter`. | Terminal disappears. Graph creates a new "Human Correction" node, and the swarm resumes processing (`RUNNING`). | Same. The virtual keyboard closes automatically upon submission. |
| **GOD-03** | **Time-Travel Slider** | Open the bottom drawer and drag the time slider to "-45 minutes". | The entire UI (Graph, Code, Chat) re-renders to match the exact Redis state from 45 mins ago. Swarm status says `READ-ONLY REPLAY`. | Bottom drawer slides up smoothly. Slider drag works without interfering with the drawer's vertical scroll. |

---

### 🛠️ Recommended Automation Setup (Playwright)

To ensure this UI never regresses during rapid development, you should automate these test cases directly on your 32GB Linux CI machine using **Playwright**. Playwright allows you to perfectly emulate mobile touch events, safe areas, and pixel-matching.

**Example `playwright.config.ts` setup:**

```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e-ui',
  fullyParallel: true, // Maximizes your Linux CPU threads
  expect: {
    // Strict pixel validation for WebGL/Canvas (0.1% tolerance)
    toMatchSnapshot: { maxDiffPixelRatio: 0.001 },
  },
  projects: [
    {
      name: 'Desktop Chromium - Cyberpunk Theme',
      use: { 
        ...devices['Desktop Chrome'], 
        colorScheme: 'dark', 
        viewport: { width: 1920, height: 1080 }
      },
    },
    {
      name: 'Mobile Safari - Touch Control',
      use: { 
        ...devices['iPhone 14 Pro'], 
        hasTouch: true, // Automatically converts clicks to touch events (taps, swipes)
        isMobile: true 
      },
    },
  ],
});

```

**Pro-Tip for testing the Swarm UI:**
Never run real Gemini Ultra API calls during these UI tests to save costs and avoid flakiness. Use Playwright's network interception (`page.route()`) to inject heavy mock JSON payloads into the WebSockets, validating that your React/Next.js frontend can handle the extreme load of a fully operational agent swarm.