let currentStep = 1;
let selectedSource = 'text';
let currentQuiz = [];
let currentQuestionIndex = 0;
let score = 0;
let timerInterval;
let timeLeft = 30;
let selectedFile = null;

function switchSource(source) {
    selectedSource = source;
    document.querySelectorAll('.source-card').forEach(c => c.classList.remove('active'));
    document.querySelectorAll('.source-input').forEach(i => i.classList.remove('active'));
    
    event.currentTarget.classList.add('active');
    document.getElementById(`${source}-input-area`).classList.add('active');
}

function nextStep() {
    if (currentStep === 1) {
        // Validation for step 1
        if (selectedSource === 'text' && document.getElementById('quiz-text').value.trim().length < 10) {
            alert("Please provide more text content."); return;
        }
        if (selectedSource === 'topic' && document.getElementById('quiz-topic').value.trim().length < 5) {
            alert("Please provide a topic prompt."); return;
        }
        if (selectedSource === 'file' && !selectedFile) {
            alert("Please upload a file."); return;
        }

        document.getElementById('step-1').classList.remove('active');
        document.getElementById('step-2').classList.add('active');
        document.getElementById('next-btn').style.display = 'none';
        document.getElementById('prev-btn').style.display = 'block';
        document.getElementById('final-generate-btn').style.display = 'block';
        currentStep = 2;
    }
}

function prevStep() {
    if (currentStep === 2) {
        document.getElementById('step-2').classList.remove('active');
        document.getElementById('step-1').classList.add('active');
        document.getElementById('next-btn').style.display = 'block';
        document.getElementById('prev-btn').style.display = 'none';
        document.getElementById('final-generate-btn').style.display = 'none';
        currentStep = 1;
    }
}

// File Upload Logic
const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const fileStatus = document.getElementById('file-status');

dropZone.onclick = () => fileInput.click();
fileInput.onchange = (e) => {
    if (e.target.files.length > 0) {
        selectedFile = e.target.files[0];
        fileStatus.textContent = `Selected: ${selectedFile.name}`;
        dropZone.style.borderColor = 'var(--primary)';
    }
};

async function generateQuiz() {
    const loader = document.getElementById('loader');
    const btnText = document.getElementById('btn-text');
    const generateBtn = document.getElementById('final-generate-btn');
    const loadingHint = document.getElementById('loading-hint');
    
    const numQ = document.getElementById('num-questions').value;
    
    loadingHint.style.display = numQ > 20 ? 'block' : 'none';
    loader.style.display = 'inline-block';
    btnText.textContent = `Architecting ${numQ} Questions...`;
    generateBtn.disabled = true;

    try {
        let response;
        const numQ = document.getElementById('num-questions').value;
        const difficulty = document.getElementById('difficulty').value;
        const quizType = document.getElementById('quiz-type').value;

        if (selectedSource === 'file') {
            const formData = new FormData();
            formData.append('file', selectedFile);
            formData.append('num_questions', numQ);
            formData.append('difficulty', difficulty);
            formData.append('quiz_type', quizType);

            response = await fetch('/generate', { method: 'POST', body: formData });
        } else {
            const content = selectedSource === 'text' ? 
                           document.getElementById('quiz-text').value : 
                           document.getElementById('quiz-topic').value;

            response = await fetch('/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    text: content, 
                    num_questions: numQ, 
                    difficulty, 
                    quiz_type: quizType 
                })
            });
        }

        const data = await response.json();
        if (data.error) throw new Error(data.error);

        currentQuiz = data;
        startQuiz();
    } catch (err) {
        alert("Error: " + err.message);
    } finally {
        loader.style.display = 'none';
        btnText.textContent = "Generate Quiz";
        generateBtn.disabled = false;
    }
}

function startQuiz() {
    document.getElementById('setup-container').style.display = 'none';
    document.getElementById('quiz-container').style.display = 'block';
    renderQuestion();
}

function renderQuestion() {
    const question = currentQuiz[currentQuestionIndex];
    const display = document.getElementById('question-display');
    const counter = document.getElementById('question-counter');
    
    counter.textContent = `Question ${currentQuestionIndex + 1}/${currentQuiz.length}`;
    document.getElementById('progress-fill').style.width = `${(currentQuestionIndex / currentQuiz.length) * 100}%`;

    display.innerHTML = `
        <div class="question-card" id="q-card">
            <h2 style="margin-bottom: 2.5rem; font-size: 1.6rem; font-weight: 700; line-height: 1.4;">${question.question}</h2>
            <div class="options-grid">
                ${question.options.map((opt, i) => `
                    <button class="option-btn" onclick="checkAnswer(${i})">
                        <span style="font-weight: 800; color: var(--primary); margin-right: 1rem;">${String.fromCharCode(65 + i)}</span>
                        ${opt}
                    </button>
                `).join('')}
            </div>
            <div id="explanation" class="explanation" style="display: none; margin-top: 2rem; animation: slideDown 0.3s ease;">
                <div style="background: rgba(255,255,255,0.03); border: 1px solid var(--glass-border); padding: 1.5rem; border-radius: 1.2rem; border-left: 5px solid var(--primary);">
                    <h4 style="color: var(--primary); margin-bottom: 0.8rem; display: flex; align-items: center; gap: 0.5rem; font-size: 1.1rem;">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>
                        Professional Explanation
                    </h4>
                    <p style="color: var(--text-main); font-size: 1rem; line-height: 1.6;">${question.explanation}</p>
                    <button class="nav-btn primary" style="margin-top: 1.5rem; width: 100%;" id="next-q-btn" onclick="nextQuestion()">
                        ${currentQuestionIndex === currentQuiz.length - 1 ? 'Finish Assessment' : 'Continue to Next Question'}
                    </button>
                </div>
            </div>
        </div>
    `;
    
    document.getElementById('q-card').scrollIntoView({ behavior: 'smooth' });
    startTimer();
}

function startTimer() {
    clearInterval(timerInterval);
    timeLeft = 30;
    updateTimerDisplay();
    timerInterval = setInterval(() => {
        timeLeft--;
        updateTimerDisplay();
        if (timeLeft <= 0) { clearInterval(timerInterval); checkAnswer(-1); }
    }, 1000);
}

function updateTimerDisplay() {
    document.getElementById('timer').textContent = `00:${timeLeft < 10 ? '0' + timeLeft : timeLeft}`;
}

function checkAnswer(selectedIndex) {
    clearInterval(timerInterval);
    const question = currentQuiz[currentQuestionIndex];
    const buttons = document.querySelectorAll('.option-btn');
    buttons.forEach((btn, i) => {
        btn.disabled = true;
        if (i === question.answer) btn.classList.add('correct');
        else if (i === selectedIndex) btn.classList.add('wrong');
    });
    if (selectedIndex === question.answer) score++;
    document.getElementById('explanation').style.display = 'block';
    document.getElementById('next-q-btn').scrollIntoView({ behavior: 'smooth', block: 'center' });
}

function nextQuestion() {
    currentQuestionIndex++;
    if (currentQuestionIndex < currentQuiz.length) renderQuestion();
    else showResults();
}

function showResults() {
    document.getElementById('question-display').style.display = 'none';
    document.getElementById('results-display').style.display = 'block';
    const percentage = Math.round((score / currentQuiz.length) * 100);
    document.getElementById('feedback-title').textContent = percentage >= 80 ? "Assessment Mastered!" : "Good Attempt!";
    document.getElementById('score-text').textContent = `You scored ${score} out of ${currentQuiz.length} (${percentage}%)`;
}
