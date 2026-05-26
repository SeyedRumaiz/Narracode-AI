/* Synapse AI — Client Logic */

const API_URL = 'http://localhost:8000';

document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const codeTextarea = document.getElementById('code-textarea');
    const lineNumbersGutter = document.getElementById('line-numbers');
    const analyzeBtn = document.getElementById('analyze-btn');
    const analyzeSpinner = document.getElementById('analyze-spinner');
    const languageSelect = document.getElementById('language-select');
    
    // Status Dot
    const apiStatusDot = document.getElementById('api-status-dot');
    const apiStatusText = document.getElementById('api-status-text');
    const modeSelect = document.getElementById('mode-select');
    const streamOutputText = document.getElementById('stream-output-text');

    // States
    const stateIdle = document.getElementById('state-idle');
    const stateLoading = document.getElementById('state-loading');
    const stateError = document.getElementById('state-error');
    const stateSuccess = document.getElementById('state-success');

    // Loader Steps
    const loaderTitle = document.getElementById('loader-title');
    const loaderDescription = document.getElementById('loader-description');
    const steps = [
        document.getElementById('step-1'),
        document.getElementById('step-2'),
        document.getElementById('step-3')
    ];

    // Error Display
    const errorMessage = document.getElementById('error-message');
    const errorConfigAction = document.getElementById('error-config-action');

    // Success Tabs & Content
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabPanels = document.querySelectorAll('.tab-panel');

    // Results elements
    const detectedLanguageBadge = document.getElementById('detected-language-badge');
    const explanationContent = document.getElementById('explanation-content');
    const storyContent = document.getElementById('story-content');
    const qaListItems = document.getElementById('qa-list-items');
    const bugBadgeCount = document.getElementById('bug-badge-count');
    const noBugsContainer = document.getElementById('no-bugs-container');
    const bugListContainer = document.getElementById('bug-list-container');
    const bugListItems = document.getElementById('bug-list-items');
    
    const fixedCodeSection = document.getElementById('fixed-code-section');
    const fixedCodeBlock = document.getElementById('fixed-code-block');
    const copyFixedBtn = document.getElementById('copy-fixed-btn');
    const copyIcon = document.getElementById('copy-icon');
    const copyText = document.getElementById('copy-text');
    
    const suggestionsListItems = document.getElementById('suggestions-list-items');

    // Complexity tab elements
    const timeComplexityValue = document.getElementById('time-complexity-value');
    const timeComplexityBar = document.getElementById('time-complexity-bar');
    const spaceComplexityValue = document.getElementById('space-complexity-value');
    const spaceComplexityBar = document.getElementById('space-complexity-bar');
    const complexityExplanationContent = document.getElementById('complexity-explanation-content');

    const oldTimeComplexityValue = document.getElementById('old-time-complexity');
    const oldTimeBar = document.getElementById('old-time-bar');
    const newTimeComplexityValue = document.getElementById('new-time-complexity');
    const newTimeBar = document.getElementById('new-time-bar');

    // Docs & Tests tab elements
    const docstringCodeBlock = document.getElementById('docstring-code-block');
    const copyDocstringBtn = document.getElementById('copy-docstring-btn');
    const copyDocstringIcon = document.getElementById('copy-docstring-icon');
    const copyDocstringText = document.getElementById('copy-docstring-text');

    const testsCodeBlock = document.getElementById('tests-code-block');
    const copyTestsBtn = document.getElementById('copy-tests-btn');
    const copyTestsIcon = document.getElementById('copy-tests-icon');
    const copyTestsText = document.getElementById('copy-tests-text');

    // State Variables
    let currentFixedCode = '';
    let currentDocstring = '';
    let currentUnitTests = '';
    let currentLanguage = 'python';

    // Complexity rating helper
    function setComplexityGauge(elementVal, elementBar, complexity) {
        const cleanComp = (complexity || 'O(1)').replace(/\s+/g, '').toLowerCase();
        let percent = 20;
        let color = 'var(--accent-emerald)'; // default green

        if (cleanComp.includes('o(1)')) {
            percent = 20;
            color = 'var(--accent-emerald)';
        } else if (cleanComp.includes('log')) {
            percent = 40;
            color = 'var(--accent-emerald)';
        } else if (cleanComp.includes('o(n)') && !cleanComp.includes('log')) {
            percent = 60;
            color = 'var(--accent-cyan)';
        } else if (cleanComp.includes('nlog')) {
            percent = 70;
            color = 'var(--accent-indigo)';
        } else if (cleanComp.includes('n^2') || cleanComp.includes('n2')) {
            percent = 85;
            color = 'var(--accent-amber)';
        } else { // O(2^n), O(n!), O(n^3)
            percent = 100;
            color = 'var(--accent-rose)';
        }

        elementVal.textContent = complexity || 'O(1)';
        elementBar.style.width = `${percent}%`;
        elementBar.style.backgroundColor = color;
    }

    function stripCodeFences(text) {
        if (typeof text !== 'string') return text;
        let cleaned = text.trim();
        if (cleaned.startsWith('```')) {
            const lines = cleaned.split('\n');
            if (lines.length >= 2 && lines[lines.length - 1].trim() === '```') {
                cleaned = lines.slice(1, -1).join('\n');
            } else {
                cleaned = lines.slice(1).join('\n');
            }
        }
        return cleaned.trim();
    }

    function safeCodeLanguage(lang) {
        if (!lang) return 'python';
        const normalized = lang.toLowerCase().trim();
        if (normalized === 'c++') return 'cpp';
        if (normalized === 'auto-detect' || normalized === 'auto' || normalized === 'detect') return 'python';
        return normalized;
    }

    // Initialize Lucide Icons
    lucide.createIcons();

    // Backend Connectivity Verification
    async function checkApiStatus() {
        try {
            const res = await fetch(`${API_URL}/`);
            if (res.ok) {
                apiStatusDot.className = 'status-dot online';
                apiStatusText.textContent = 'Backend Online';
            } else {
                throw new Error();
            }
        } catch (e) {
            apiStatusDot.className = 'status-dot offline';
            apiStatusText.textContent = 'Backend Offline';
        }
    }
    
    checkApiStatus();
    // Poll API status every 10 seconds
    setInterval(checkApiStatus, 10000);

    // Textarea Line Number Syncing
    function updateLineNumbers() {
        const lines = codeTextarea.value.split('\n');
        const count = Math.max(1, lines.length);
        
        let gutterContent = '';
        for (let i = 1; i <= count; i++) {
            gutterContent += i + '\n';
        }
        lineNumbersGutter.textContent = gutterContent;
    }

    // Scrolling synchronization
    codeTextarea.addEventListener('scroll', () => {
        lineNumbersGutter.scrollTop = codeTextarea.scrollTop;
    });

    // Content change synchronization
    codeTextarea.addEventListener('input', updateLineNumbers);
    updateLineNumbers(); // Run initially

    // Keyboard Shortcut (Cmd+Enter / Ctrl+Enter to trigger analysis)
    codeTextarea.addEventListener('keydown', (e) => {
        if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
            e.preventDefault();
            analyzeBtn.click();
        }
    });

    const container = document.getElementById('swipe-container');
    const panels = document.querySelectorAll('.tab-panel');
    const buttons = document.querySelectorAll('.tab-btn');

    let currentIndex = 0;

    // move using scrollLeft
    function goToTab(index) {
        if (index < 0 || index >= panels.length) return;

        currentIndex = index;

        const width = container.clientWidth;

        container.scrollTo({
            left: width * index,
            behavior: 'smooth'
        });

        buttons.forEach((b, i) => {
            b.classList.toggle('active', i === index);
        });
    }

    // tab click
    buttons.forEach((btn, index) => {
        btn.addEventListener('click', () => {
            goToTab(index);
        });
    });

    // swipe
    let startX = 0;

    container.addEventListener('touchstart', (e) => {
        startX = e.touches[0].clientX;
    });

    container.addEventListener('touchend', (e) => {
        const endX = e.changedTouches[0].clientX;
        const diff = startX - endX;

        if (diff > 50) goToTab(currentIndex + 1);
        if (diff < -50) goToTab(currentIndex - 1);
    });

    // Loader Animation Steps
    let stepTimers = [];
    
    function startLoaderAnimation() {
        // Reset loader UI
        steps.forEach(s => s.classList.remove('active'));
        loaderTitle.textContent = 'Analyzing Code';
        loaderDescription.textContent = 'Deconstructing syntax trees and examining logical execution pathways...';
        steps[0].classList.add('active');
        
        // Progress steps timeline
        const stepConfigs = [
            {
                delay: 1500,
                title: 'Reviewing Logic Flows',
                desc: 'Scanning variables, loops, conditional paths, and function executions...',
                activate: 1
            },
            {
                delay: 3500,
                title: 'Formulating Fixes',
                desc: 'Synthesizing recommendations, resolving errors, and compiling best-practice improvements...',
                activate: 2
            }
        ];

        stepConfigs.forEach(config => {
            const timer = setTimeout(() => {
                loaderTitle.textContent = config.title;
                loaderDescription.textContent = config.desc;
                steps[config.activate].classList.add('active');
            }, config.delay);
            stepTimers.push(timer);
        });
    }

    function stopLoaderAnimation() {
        stepTimers.forEach(clearTimeout);
        stepTimers = [];
    }

    // Panel State Swapper
    function showState(activeState) {
        [stateIdle, stateLoading, stateError, stateSuccess].forEach(state => {
            state.classList.remove('active');
        });
        activeState.classList.add('active');
    }

    // API Submission (Analysis Request)
    analyzeBtn.addEventListener('click', async () => {
        const codeInput = codeTextarea.value.trim();
        if (!codeInput) {
            codeTextarea.focus();
            return;
        }

        const selectedLang = languageSelect.value;
        const selectedMode = modeSelect.value;

        // Toggle UI loading states
        analyzeBtn.disabled = true;
        analyzeSpinner.classList.add('active');
        showState(stateLoading);
        startLoaderAnimation();
        streamOutputText.textContent = 'Waiting for live tokens...';

        try {
            const result = await streamAnalysis(codeInput, selectedLang, selectedMode);

            stopLoaderAnimation();
            renderAnalysisResults(result);
            showState(stateSuccess);

            // Default to overview tab on success
            tabButtons[0].click();

        } catch (err) {
            stopLoaderAnimation();
            errorMessage.textContent = err.message || 'Unable to communicate with the analysis server. Please make sure the backend FastAPI application is running.';
            
            // Show configuration guide if API key is not configured
            if (err.status === 503 || (err.message && err.message.includes('API key not configured'))) {
                errorConfigAction.style.display = 'block';
            } else {
                errorConfigAction.style.display = 'none';
            }

            showState(stateError);
        } finally {
            analyzeBtn.disabled = false;
            analyzeSpinner.classList.remove('active');
        }
    });

    async function streamAnalysis(code, language, mode) {
        const response = await fetch(`${API_URL}/stream-analyse`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                code,
                language,
                mode,
                session_id: 'default'
            })
        });

        if (!response.ok) {
            const result = await response.json();
            throw { message: result.detail || 'Streaming analysis failed.', status: response.status };
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        let assembledResult = null;

        const parseEventChunk = (chunk) => {
            let eventType = 'message';
            let data = '';
            const lines = chunk.split('\n');
            lines.forEach((line) => {
                if (line.startsWith('event:')) {
                    eventType = line.replace('event:', '').trim();
                }
                if (line.startsWith('data:')) {
                    data += line.replace('data:', '').trim();
                }
            });

            if (!data) return;
            try {
                const payload = JSON.parse(data);
                if (eventType === 'token') {
                    streamOutputText.textContent += payload.text;
                    streamOutputText.scrollTop = streamOutputText.scrollHeight;
                }
                if (eventType === 'result') {
                    assembledResult = payload;
                }
            } catch (error) {
                streamOutputText.textContent += data;
            }
        };

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;
            buffer += decoder.decode(value, { stream: true });
            let parts = buffer.split('\n\n');
            buffer = parts.pop();
            parts.forEach(parseEventChunk);
        }
        if (buffer) {
            parseEventChunk(buffer);
        }

        if (!assembledResult) {
            throw { message: 'Streaming finished without a parseable result.' };
        }

        return assembledResult;
    }

    // Rendering Engine
    function renderAnalysisResults(data) {
        currentLanguage = data.language || 'python';
        currentFixedCode = data.fixed_code || '';

        // 1. Render Overview
        detectedLanguageBadge.textContent = currentLanguage;
        explanationContent.textContent = data.explanation || 'No explanation provided.';

        // 2. Render Code Story
        if (storyContent) {
            storyContent.textContent = data.story || 'No story provided.';
        }

        // 2.3 Render Flowchart
        const flowchartContainer = document.getElementById('flowchart-container');

        if (flowchartContainer) {
            const chart = data.flowchart || `flowchart TD\n    A[Start] --> B[Process Code]\n    B --> C[Generate Analysis]\n    C --> D[End]`;
            const flowchartId = `generatedFlowchart-${Date.now()}`;

            flowchartContainer.innerHTML = '';

            mermaid.render(flowchartId, chart).then(({ svg }) => {
                flowchartContainer.innerHTML = svg;
            }).catch(err => {
                console.error("Mermaid render error:", err);
                flowchartContainer.innerHTML = '<p class="explanation-text">Unable to render flowchart. Please check the code structure or try a simpler snippet.</p>';
            });
        }
        // 2.5 Render Q&A Mode
        if (qaListItems) {
            qaListItems.innerHTML = '';
            const questions = data.questions || [];
            if (questions.length === 0) {
                qaListItems.innerHTML = '<p class="explanation-text">No Q&As generated for this code snippet.</p>';
            } else {
                questions.forEach((item, index) => {
                    const qaCard = document.createElement('div');
                    qaCard.style.padding = '1rem';
                    qaCard.style.borderRadius = 'var(--radius-sm)';
                    qaCard.style.backgroundColor = 'rgba(255, 255, 255, 0.01)';
                    qaCard.style.border = '1px solid var(--border-color)';
                    qaCard.style.display = 'flex';
                    qaCard.style.flexDirection = 'column';
                    qaCard.style.gap = '0.5rem';

                    qaCard.innerHTML = `
                        <div style="font-weight: 600; color: var(--accent-cyan); display: flex; gap: 0.5rem; align-items: flex-start;">
                            <span style="background: rgba(6, 182, 212, 0.1); color: var(--accent-cyan); border-radius: 4px; padding: 0.1rem 0.35rem; font-size: 0.8rem; font-family: monospace;">Q${index + 1}</span>
                            <span>${item.question}</span>
                        </div>
                        <div style="color: var(--text-secondary); line-height: 1.6; padding-left: 2rem; font-size: 0.95rem;">
                            ${item.answer}
                        </div>
                    `;
                    qaListItems.appendChild(qaCard);
                });
            }
        }

        // 2.7 Render Complexity Mode
        currentDocstring = stripCodeFences(data.docstring || '');
        currentUnitTests = stripCodeFences(data.unit_tests || '');

        if (timeComplexityValue && timeComplexityBar) {
            setComplexityGauge(timeComplexityValue, timeComplexityBar, data.time_complexity);
        }
        if (spaceComplexityValue && spaceComplexityBar) {
            setComplexityGauge(spaceComplexityValue, spaceComplexityBar, data.space_complexity);
        }
        if (complexityExplanationContent) {
            complexityExplanationContent.textContent = data.complexity_explanation || 'No complexity analysis provided.';
        }

        // Render Optimizer Tab
        const optimizedCodeBlock = document.getElementById('optimized-code-block');
        const optimizationComparisonContent = document.getElementById('optimization-comparison-content');

        if (optimizationComparisonContent) {
            optimizationComparisonContent.textContent =
                data.optimization_comparison ||
                'No optimization analysis available.';
        }

        if (optimizedCodeBlock) {
            const optimizedCode = stripCodeFences(data.optimized_code || '// No optimized code generated');
            optimizedCodeBlock.textContent = optimizedCode;

            let prismLang = safeCodeLanguage(currentLanguage);
            optimizedCodeBlock.className = `language-${prismLang}`;
            Prism.highlightElement(optimizedCodeBlock);
        }

        if (oldTimeComplexityValue && oldTimeBar) {
            setComplexityGauge(oldTimeComplexityValue, oldTimeBar, data.time_complexity || 'O(1)');
        }
        if (newTimeComplexityValue && newTimeBar) {
            setComplexityGauge(newTimeComplexityValue, newTimeBar, data.optimized_time_complexity || data.time_complexity || 'O(1)');
        }

        // 2.8 Render Docs & Tests Mode
        if (docstringCodeBlock) {
            docstringCodeBlock.textContent = currentDocstring;
            let prismLang = currentLanguage.toLowerCase();
            if (prismLang === 'c++') prismLang = 'cpp';
            docstringCodeBlock.className = `language-${prismLang}`;
            Prism.highlightElement(docstringCodeBlock);
        }
        if (testsCodeBlock) {
            testsCodeBlock.textContent = currentUnitTests;
            let prismLang = currentLanguage.toLowerCase();
            if (prismLang === 'c++') prismLang = 'cpp';
            testsCodeBlock.className = `language-${prismLang}`;
            Prism.highlightElement(testsCodeBlock);
        }

        // 3. Render Bugs & Fixes
        const bugs = data.bugs || [];
        bugBadgeCount.textContent = bugs.length;

        if (bugs.length === 0) {
            noBugsContainer.classList.add('active');
            bugListContainer.style.display = 'none';
        } else {
            noBugsContainer.classList.remove('active');
            bugListContainer.style.display = 'flex';
            
            // Populate bug cards
            bugListItems.innerHTML = '';
            bugs.forEach(bug => {
                const bugCard = document.createElement('div');
                const severityClass = (bug.severity || 'medium').toLowerCase();
                bugCard.className = `bug-card ${severityClass}`;

                const lineInfo = bug.line ? `Line ${bug.line}: ` : 'General: ';
                const bugType = bug.type || 'Bug';
                const severity = bug.severity || 'Medium';
                
                bugCard.innerHTML = `
                    <div class="bug-meta">
                        <span class="bug-line-tag"><i data-lucide="hash" style="width:12px;height:12px;vertical-align:middle;margin-right:2px;"></i>${lineInfo}</span>
                        <span class="bug-type-tag">${bugType}</span>
                        <span class="bug-severity-badge">${severity}</span>
                    </div>
                    <p class="bug-description">${bug.description}</p>
                `;
                bugListItems.appendChild(bugCard);
            });
        }

        // Populate and highlight fixed code
        if (currentFixedCode) {
            fixedCodeSection.style.display = 'flex';
            fixedCodeBlock.textContent = currentFixedCode;
            
            // Map languages to Prism supported naming
            let prismLang = currentLanguage.toLowerCase();
            if (prismLang === 'c++') prismLang = 'cpp';
            
            fixedCodeBlock.className = `language-${prismLang}`;
            
            // Re-run Prism highlighter
            Prism.highlightElement(fixedCodeBlock);
        } else {
            fixedCodeSection.style.display = 'none';
        }

        // 4. Render Improvements Suggestions
        const improvements = data.improvements || [];
        suggestionsListItems.innerHTML = '';
        
        if (improvements.length === 0) {
            const fallbackLi = document.createElement('li');
            fallbackLi.textContent = 'Code adheres well to industry standards. No optimization modifications needed.';
            suggestionsListItems.appendChild(fallbackLi);
        } else {
            improvements.forEach(tip => {
                const li = document.createElement('li');
                li.textContent = tip;
                suggestionsListItems.appendChild(li);
            });
        }

        // Re-bind Lucide icons on dynamically created items
        lucide.createIcons();
    }

    // Clipboard Integration
    copyFixedBtn.addEventListener('click', () => {
        if (!currentFixedCode) return;
        
        navigator.clipboard.writeText(currentFixedCode).then(() => {
            // Visual success feedback
            copyIcon.setAttribute('data-lucide', 'check');
            copyText.textContent = 'Copied!';
            copyFixedBtn.style.borderColor = 'var(--accent-emerald)';
            copyFixedBtn.style.color = 'var(--accent-emerald)';
            
            lucide.createIcons();

            setTimeout(() => {
                copyIcon.setAttribute('data-lucide', 'copy');
                copyText.textContent = 'Copy Code';
                copyFixedBtn.style.borderColor = 'var(--border-color)';
                copyFixedBtn.style.color = 'var(--text-primary)';
                lucide.createIcons();
            }, 2000);
        }).catch(err => {
            console.error('Failed to copy text: ', err);
        });
    });

    const copyOptimizedBtn = document.getElementById('copy-optimized-btn');
    const copyOptimizedIcon = document.getElementById('copy-optimized-icon');
    const copyOptimizedText = document.getElementById('copy-optimized-text');

    copyOptimizedBtn.addEventListener('click', () => {
        const optimizedCode =
            document.getElementById('optimized-code-block').textContent;

        if (!optimizedCode) return;

        navigator.clipboard.writeText(optimizedCode).then(() => {

            copyOptimizedIcon.setAttribute('data-lucide', 'check');
            copyOptimizedText.textContent = 'Copied!';

            lucide.createIcons();

            setTimeout(() => {
                copyOptimizedIcon.setAttribute('data-lucide', 'copy');
                copyOptimizedText.textContent = 'Copy Optimized Code';

                lucide.createIcons();
            }, 2000);
        });
    });

    copyDocstringBtn.addEventListener('click', () => {
        if (!currentDocstring) return;
        
        navigator.clipboard.writeText(currentDocstring).then(() => {
            copyDocstringIcon.setAttribute('data-lucide', 'check');
            copyDocstringText.textContent = 'Copied!';
            copyDocstringBtn.style.borderColor = 'var(--accent-emerald)';
            copyDocstringBtn.style.color = 'var(--accent-emerald)';
            
            lucide.createIcons();

            setTimeout(() => {
                copyDocstringIcon.setAttribute('data-lucide', 'copy');
                copyDocstringText.textContent = 'Copy Docstring';
                copyDocstringBtn.style.borderColor = 'var(--border-color)';
                copyDocstringBtn.style.color = 'var(--text-primary)';
                lucide.createIcons();
            }, 2000);
        }).catch(err => {
            console.error('Failed to copy text: ', err);
        });
    });

    copyTestsBtn.addEventListener('click', () => {
        if (!currentUnitTests) return;
        
        navigator.clipboard.writeText(currentUnitTests).then(() => {
            copyTestsIcon.setAttribute('data-lucide', 'check');
            copyTestsText.textContent = 'Copied!';
            copyTestsBtn.style.borderColor = 'var(--accent-emerald)';
            copyTestsBtn.style.color = 'var(--accent-emerald)';
            
            lucide.createIcons();

            setTimeout(() => {
                copyTestsIcon.setAttribute('data-lucide', 'copy');
                copyTestsText.textContent = 'Copy Tests';
                copyTestsBtn.style.borderColor = 'var(--border-color)';
                copyTestsBtn.style.color = 'var(--text-primary)';
                lucide.createIcons();
            }, 2000);
        }).catch(err => {
            console.error('Failed to copy text: ', err);
        });
    });
});
