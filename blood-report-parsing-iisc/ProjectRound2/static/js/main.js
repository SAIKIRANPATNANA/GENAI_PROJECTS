document.addEventListener('DOMContentLoaded', function() {
    // History functionality
    const historyBtn = document.getElementById('historyBtn');
    const historyPanel = document.getElementById('historyPanel');
    const patientList = document.getElementById('patientList');
    
    historyBtn.addEventListener('click', () => {
        const isVisible = historyPanel.style.display === 'block';
        historyPanel.style.display = isVisible ? 'none' : 'block';
        if (!isVisible) {
            loadHistoryPatients();
        }
    });
    
    async function loadHistoryPatients() {
        try {
            const response = await fetch('/api/user_patients_with_reports', {
                method: 'GET',
                credentials: 'same-origin'
            });
            if (!response.ok) throw new Error('Failed to fetch patients');
            const data = await response.json();
            
            patientList.innerHTML = '';
            
            if (!data.patients || data.patients.length === 0) {
                const noHistoryMessage = document.createElement('div');
                noHistoryMessage.className = 'no-history-message';
                noHistoryMessage.textContent = 'No history available';
                patientList.appendChild(noHistoryMessage);
                return;
            }
            
            data.patients.forEach(patient => {
                const patientCard = document.createElement('div');
                patientCard.className = 'patient-card';
                
                const patientName = document.createElement('div');
                patientName.className = 'patient-name';
                patientName.textContent = patient.name;
                
                const timestampList = document.createElement('ul');
                timestampList.className = 'timestamp-list';
                
                patient.reports.forEach(report => {
                    const timestampItem = document.createElement('li');
                    timestampItem.className = 'timestamp-item';
                    const date = new Date(report.timestamp);
                    const options = {
                        year: 'numeric',
                        month: '2-digit',
                        day: '2-digit',
                        hour: '2-digit',
                        minute: '2-digit',
                        second: '2-digit',
                        hour12: false
                    };
                    timestampItem.textContent = date.toLocaleString('en-IN', options);
                    
                    timestampItem.addEventListener('click', () => {
                        try {
                            currentReport = report.parsed_report;
                            displayResults({
                                report: report.parsed_report,
                                plots: [], // Historical reports don't have plots
                                insights: [] // Historical reports don't have insights
                            });
                            
                            // Switch to report tab
                            document.querySelector('.tab-btn[data-tab="report"]').click();
                            resultsSection.style.display = 'block';
                        } catch (error) {
                            console.error('Error displaying report:', error);
                            alert('Failed to display report, once refresh the page and try again.');
                        }
                    });
                    
                    timestampList.appendChild(timestampItem);
                });
                
                patientCard.appendChild(patientName);
                patientCard.appendChild(timestampList);
                patientList.appendChild(patientCard);
            });
        } catch (error) {
            console.error('Error loading patients:', error);
            alert('Failed to load patients');
        }
    }

    const uploadForm = document.getElementById('uploadForm');
    const loader = document.getElementById('loader');
    const resultsSection = document.querySelector('.results-section');
    const logoutBtn = document.getElementById('logoutBtn');
    let currentReport = null;
    let sessionId = null;

    // Tab switching
    document.querySelectorAll('.tab-btn').forEach(button => {
        button.addEventListener('click', () => {
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
            
            button.classList.add('active');
            const targetTab = document.getElementById(button.dataset.tab);
            targetTab.classList.add('active');
        });
    });

    // Logout functionality
    logoutBtn.addEventListener('click', async () => {
        try {
            const response = await fetch('/logout', {
                method: 'POST',
                credentials: 'same-origin'
            });
            if (response.ok) {
                window.location.href = '/login';
            } else {
                throw new Error('Logout failed');
            }
        } catch (error) {
            alert('Error during logout: ' + error.message);
        }
    });

    // Initialize chat session
    function initializeChatSession() {
        // Create a unique session ID using timestamp and random number
        sessionId = `chat_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        // Clear previous chat messages
        if (chatMessages) {
            chatMessages.innerHTML = '';
            appendMessage('System', '🟢 Chat session started! You can now ask questions about the blood report. 💬');
        }
    }

    // Chat functionality
    const messageInput = document.getElementById('messageInput');
    const sendButton = document.getElementById('sendMessage');
    const chatMessages = document.getElementById('chatMessages');

    if (sendButton) {
        sendButton.addEventListener('click', sendMessage);
    }

    if (messageInput) {
        messageInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
    }

    async function sendMessage() {
        const message = messageInput.value.trim();
        if (!message || !currentReport) {
            if (!currentReport) {
                alert('Please upload a report first before starting the chat.');
            }
            return;
        }

        if (!sessionId) {
            initializeChatSession();
        }

        messageInput.disabled = true;
        sendButton.disabled = true;

        appendMessage('You', message);
        messageInput.value = '';

        const typingIndicator = appendTypingIndicator();

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                credentials: 'same-origin',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message,
                    report: currentReport,
                    session_id: sessionId
                })
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();
            typingIndicator.remove();
            appendMessage('Assistant', data.response);
        } catch (error) {
            console.error('Error:', error);
            typingIndicator.remove();
            appendMessage('System', 'Error: Failed to get response from assistant');
        } finally {
            messageInput.disabled = false;
            sendButton.disabled = false;
            messageInput.focus();
        }
    }

    // File upload handling
    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const fileInput = document.getElementById('reportFile');
        const file = fileInput.files[0];
        
        if (!file) {
            alert('Please select a file');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        loader.style.display = 'block';
        resultsSection.style.display = 'none';

        try {
            const response = await fetch('/upload', {
                method: 'POST',
                credentials: 'same-origin',
                body: formData
            });

            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }

            currentReport = data.report;
            displayResults(data);
            resultsSection.style.display = 'block';
            
            // Initialize new chat session when new report is uploaded
            initializeChatSession();
            
        } catch (error) {
            alert('Error processing report: ' + error.message);
        } finally {
            loader.style.display = 'none';
        }
    });

    // Role selection
    const roleSelect = document.getElementById('roleSelect');
    if (roleSelect) {
        roleSelect.addEventListener('change', (e) => {
            currentRole = e.target.value;
        });
    }

    function appendMessage(sender, message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message message-${sender.toLowerCase()}`;
        
        // Create the header with sender and timestamp
        const headerDiv = document.createElement('div');
        headerDiv.className = 'message-header';
        headerDiv.innerHTML = `
            <strong>${sender}</strong>
            <span class="message-time">${new Date().toLocaleTimeString()}</span>
        `;
        
        // Create the content div and render markdown if it's from the Assistant
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        if (sender === 'Assistant') {
            // Sanitize and render markdown
            contentDiv.innerHTML = marked.parse(message, {
                breaks: true,
                sanitize: true
            });
        } else {
            // For user messages, just escape HTML and preserve line breaks
            contentDiv.textContent = message;
        }
        
        // Assemble the message
        messageDiv.appendChild(headerDiv);
        messageDiv.appendChild(contentDiv);
        
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function appendTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message message-typing';
        typingDiv.innerHTML = `
            <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
            </div>
        `;
        chatMessages.appendChild(typingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        return typingDiv;
    }

    function displayResults(data) {
        // Display report details with tables and download button
        const reportContent = document.getElementById('reportContent');
        
        // Check if this is a multi-report (contains ehr field)
        if (data.report.ehr) {
            // For multi-reports, display the EHR markdown content
            reportContent.innerHTML = `
                <div class="report-actions">
                    <button id="downloadReportBtn" class="download-btn">
                        Download Report (JSON)
                    </button>
                </div>
                <div class="ehr-content markdown-body">
                    ${marked.parse(data.report.ehr)}
                </div>
            `;
        } else {
            // For regular single reports, display the usual tables
            reportContent.innerHTML = `
                <div class="report-actions">
                    <button id="downloadReportBtn" class="download-btn">
                        Download Report (JSON)
                    </button>
                </div>
                <div class="info-tables-container">
                    <div class="info-table">
                        <h3>Patient Information</h3>
                        <table class="results-table">
                            <tbody>
                                ${generatePatientInfoRows(data.report.patient_info)}
                            </tbody>
                        </table>
                    </div>
                    <div class="info-table">
                        <h3>Laboratory Information</h3>
                        <table class="results-table">
                            <tbody>
                                ${generateLabInfoRows(data.report.lab_info, data.report.test_name)}
                            </tbody>
                        </table>
                    </div>
                </div>
                <div class="lab-results-table">
                    <h3>Test Results</h3>
                    <div class="table-container">
                        <table class="results-table">
                            <thead>
                                <tr>
                                    <th>Parameter</th>
                                    <th>Value</th>
                                    <th>Reference Range</th>
                                    <th>Unit</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${generateTableRows(data.report.lab_results)}
                            </tbody>
                        </table>
                    </div>
                </div>
            `;
        }

        // Add helper functions for generating table rows
        function generatePatientInfoRows(patientInfo) {
            return Object.entries(patientInfo)
                .map(([key, value]) => `
                    <tr>
                        <th>${formatKey(key)}</th>
                        <td>${value || 'N/A'}</td>
                    </tr>
                `).join('');
        }

        function generateLabInfoRows(labInfo, testName) {
            let rows = `
                <tr>
                    <th>Test Name</th>
                    <td>${testName || 'N/A'}</td>
                </tr>
            `;
            
            rows += Object.entries(labInfo)
                .map(([key, value]) => {
                    if (typeof value === 'object') {
                        // Handle nested objects like lab_contact
                        return Object.entries(value)
                            .map(([subKey, subValue]) => `
                                <tr>
                                    <th>${formatKey(key + '_' + subKey)}</th>
                                    <td>${subValue || 'N/A'}</td>
                                </tr>
                            `).join('');
                    }
                    return `
                        <tr>
                            <th>${formatKey(key)}</th>
                            <td>${value || 'N/A'}</td>
                        </tr>
                    `;
                }).join('');
            return rows;
        }

        function formatKey(key) {
            return key.split('_')
                .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                .join(' ');
        }

        // Add event listener for download button
        document.getElementById('downloadReportBtn').addEventListener('click', () => {
            downloadReport(data.report);
        });
        
        // Modify the plots display
        const plotsContent = document.getElementById('plotsContent');
        plotsContent.innerHTML = ''; // Clear existing plots
        
        // Create a container for plots
        const plotsContainer = document.createElement('div');
        plotsContainer.className = 'plots-container-vertical';
        
        // Display plots from the static/plots directory
        if (data.report.lab_results) {
            Object.keys(data.report.lab_results).forEach(param => {
                const details = data.report.lab_results[param];
                if (details.status !== 'Normal') {
                    const plotCard = document.createElement('div');
                    plotCard.className = 'plot-card-vertical';
                    
                    const plotImg = document.createElement('img');
                    plotImg.src = `/static/plots/${param.replace(/\s+/g, '_')}.png`;
                    plotImg.alt = `${param} Plot`;
                    plotImg.className = 'result-plot';
                    
                    // Add load error handling
                    plotImg.onerror = function() {
                        this.parentElement.innerHTML = `
                            <div class="plot-error">
                                <p>Plot not available for ${param}</p>
                            </div>
                        `;
                    };
                    
                    const plotTitle = document.createElement('h4');
                    plotTitle.textContent = param;
                    
                    plotCard.appendChild(plotTitle);
                    plotCard.appendChild(plotImg);
                    plotsContainer.appendChild(plotCard);
                }
            });
        }
        
        plotsContent.appendChild(plotsContainer);
        
        // Display insights
        const insightsContent = document.getElementById('insightsContent');
        if (data.insights && data.insights.abnormal_parameters) {
            insightsContent.innerHTML = formatInsights(data.insights);
        }
    }

    function generateTableRows(labResults) {
        return Object.entries(labResults)
            .map(([param, details]) => `
                <tr class="status-${details.status.toLowerCase()}">
                    <td>${param}</td>
                    <td>${details.value}</td>
                    <td>${details.reference_range}</td>
                    <td>${details.unit}</td>
                    <td>${details.status}</td>
                </tr>
            `).join('');
    }

    function formatInsights(insights) {
        return `
            <div class="insights-container">
                ${insights.abnormal_parameters.map(param => `
                    <div class="insight-card">
                        <h3>${param.parameter} (${param.status})</h3>
                        <div class="insight-section">
                            <h4>Possible Health Effects:</h4>
                            <ul>
                                ${param.possible_disease.map(disease => `<li>${disease}</li>`).join('')}
                            </ul>
                        </div>
                        <div class="insight-section">
                            <h4>Possible Causes:</h4>
                            <ul>
                                ${param.possible_causes.map(cause => `<li>${cause}</li>`).join('')}
                            </ul>
                        </div>
                        <div class="insight-section">
                            <h4>Dietary Suggestions:</h4>
                            <ul>
                                ${param.dietary_suggestions.map(suggestion => `<li>${suggestion}</li>`).join('')}
                            </ul>
                        </div>
                        <div class="insight-section">
                            <h4>Lifestyle Changes:</h4>
                            <ul>
                                ${param.lifestyle_changes.map(change => `<li>${change}</li>`).join('')}
                            </ul>
                        </div>
                        <div class="insight-section">
                            <h4>Medical Advice:</h4>
                            <p>${param.medical_advice}</p>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    function downloadReport(report) {
        const dataStr = JSON.stringify(report, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(dataBlob);
        const downloadLink = document.createElement('a');
        downloadLink.href = url;
        downloadLink.download = 'blood_report.json';
        document.body.appendChild(downloadLink);
        downloadLink.click();
        document.body.removeChild(downloadLink);
        URL.revokeObjectURL(url);
    }
}); 

// Trends functionality
document.addEventListener('DOMContentLoaded', function() {
    const patientSelect = document.getElementById('patientSelect');
    const testNameSelect = document.getElementById('testNameSelect');
    const parameterSelect = document.getElementById('parameterSelect');
    const profileReport = document.getElementById('profileReport');
    const trendPlot = document.getElementById('trendPlot');
    let currentReportIds = [];

    // Load patients when trends tab is clicked
    document.querySelector('button[data-tab="trends"]').addEventListener('click', loadPatients);

    // Load patients list
    async function loadPatients() {
        try {
            const response = await fetch('/get_patients', {
                credentials: 'same-origin'  // Include cookies in the request
            });
            
            if (response.redirected) {
                window.location.href = response.url;
                return;
            }
            
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }

            patientSelect.innerHTML = '<option value="">Select Patient</option>';
            data.patients.forEach(patient => {
                const option = document.createElement('option');
                option.value = patient;
                option.textContent = patient;
                patientSelect.appendChild(option);
            });

            testNameSelect.disabled = true;
            parameterSelect.disabled = true;
            profileReport.innerHTML = '';
            trendPlot.innerHTML = '';
        } catch (error) {
            console.error('Error loading patients:', error);
            alert('Failed to load patients list');
        }
    }

    // Handle patient selection
    patientSelect.addEventListener('change', async function() {
        const trendsLoader = document.getElementById('trendsLoader');
        trendsLoader.style.display = 'flex';
        testNameSelect.innerHTML = '<option value="">Select Test Name</option>';
        testNameSelect.disabled = true;
        parameterSelect.disabled = true;
        profileReport.innerHTML = '';
        trendPlot.innerHTML = '';

        if (!this.value) return;

        try {
            const response = await fetch('/get_test_names', {
                method: 'POST',
                credentials: 'same-origin',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    patient_name: this.value
                })
            });

            console.log('Test names response:', response);
            const data = await response.json();
            console.log('Test names data:', data);

            if (data.error) {
                throw new Error(data.error);
            }

            data.grouped_tests.forEach(group => {
                console.log('Processing test group:', group);
                const option = document.createElement('option');
                option.value = JSON.stringify(group.report_ids);
                option.textContent = group.standardized_test_name;
                testNameSelect.appendChild(option);
            });

            testNameSelect.disabled = false;
        } catch (error) {
            console.error('Error loading test names:', error);
            alert('Failed to load test names');
        } finally {
            trendsLoader.style.display = 'none';
        }
    });

    // Handle test name selection
    testNameSelect.addEventListener('change', async function() {
        parameterSelect.innerHTML = '<option value="">Select Parameter</option>';
        parameterSelect.disabled = true;
        profileReport.innerHTML = '';
        trendPlot.innerHTML = '';

        const trendsLoader = document.getElementById('trendsLoader');
        trendsLoader.style.display = 'flex';

        if (!this.value) return;

        try {
            currentReportIds = JSON.parse(this.value);
            console.log('Selected report IDs:', currentReportIds);
            
            const response = await fetch('/get_lab_results', {
                method: 'POST',
                credentials: 'same-origin',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    report_ids: currentReportIds
                })
            });

            console.log('Lab results response:', response);
            const data = await response.json();
            console.log('Lab results data:', data);

            if (data.error) {
                throw new Error(data.error);
            }

            // Load parameters into select
            data.parameters.forEach(param => {
                const option = document.createElement('option');
                option.value = param;
                option.textContent = param;
                parameterSelect.appendChild(option);
            });

            parameterSelect.disabled = false;

            // Load and display profiling report
            if (data.report_url) {
                profileReport.innerHTML = `<iframe src="${data.report_url}" style="width: 100%; height: 100%; border: none;"></iframe>`;
            }
        } catch (error) {
            console.error('Error loading lab results:', error);
            alert('Failed to load lab results');
        } finally {
            trendsLoader.style.display = 'none';
        }
    });

    // Handle parameter selection
    parameterSelect.addEventListener('change', async function() {
        trendPlot.innerHTML = '';
        if (!this.value) return;

        const trendsLoader = document.getElementById('trendsLoader');
        trendsLoader.style.display = 'flex';

        try {
            const response = await fetch('/get_parameter_trend', {
                method: 'POST',
                credentials: 'same-origin',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    report_ids: currentReportIds,
                    parameter: this.value
                })
            });

            const data = await response.json();
            if (data.error) {
                throw new Error(data.error);
            }

            // Display the trend plot
            trendPlot.innerHTML = `<img src="${data.plot_url}" style="width: 100%; height: auto;">`;
        } catch (error) {
            console.error('Error loading parameter trend:', error);
            alert('Failed to load parameter trend');
        } finally {
            trendsLoader.style.display = 'none';
        }
    });
});