# VYUHA (व्यूह): Elite High-Governance Agent Engine

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

**VYUHA** (Sanskrit for *Strategic Formation*) is a production-grade multi-agent orchestration engine designed for high-stakes software development. Unlike traditional "black-box" AI tools, VYUHA operates on a strict **Formation of 16 Lead Agents**, each governed by a rigorous "Plan-Review-Execute" protocol.

---

## 🏗️ The 16-Agent Formation

VYUHA divides the software development lifecycle into specialized domains, each led by a Principal-level agent.

### 🔹 Core Development Suite
- **Sutra (Lead Requirements)**: Autonomously captures and distills complex technical specifications.
- **Dharma (Principal Architect)**: Enforces industry-leading standards and architectural patterns.
- **Kavacha (Chief Auditor)**: Performs exhaustive security audits (OWASP compliance).
- **Vishwakarma (Senior Architect)**: Designs production-grade blueprints and module boundaries.
- **Yantra (Lead Engineer)**: Transforms blueprints into highly optimized source code.
- **Akasha (Connectivity)**: Architectures resilient API topologies and data flows.
- **Lipi (Technical Scribe)**: Generates world-class technical documentation.
- **Sutradhara (Logic Director)**: Orchestrates global system state and mission-critical workflows.

### 🔹 Project Operations Suite
- **Chitra (UI/UX Designer)**: Architectures premium visual languages (Glassmorphism, rich animations).
- **Pariksha (Lead QA)**: Defines exhaustive testing strategies and zero-defect validation.
- **Arjuna (DevOps)**: Architectures production-grade CI/CD and release strategies.
- **Prithvi (Infrastructure)**: Designs resilient cloud architecture and IaC blueprints.

### 🔹 Data & ML Suite
- **Varuna (Lead DBA)**: Designs hyper-optimized, high-performance database schemas.
- **Ganaka (Data Analyst)**: Architectures elite-level ETL/ELT pipelines and data intelligence.
- **Budhi (ML Engineer)**: Proposes algorithmic architectures with mathematical rigor.
- **Yantri (MLOps Architect)**: Manages governed machine learning lifecycles and observability.

---

## 🚀 Key Features

- **🏆 Elite Lead Seniority**: Every agent is instructed with high-fidelity prompts to act as a Principal Lead in their domain.
- **🛡️ High-Governance A2A Bus**: No code is published without cross-review. `Yantra`'s code is audited by `Kavacha` and `Dharma` before reaching production.
- **🔌 Pluggable AI Adapters**: Hot-swap between **Ollama (local)**, **Gemini**, **OpenAI**, and others via `config.yaml`.
- **💻 CLI Direct Execution**: A professional terminal interface with the `vyuha` command.
- **🌍 Open Source & Modular**: MIT licensed and built for extensibility.

---

## 📦 Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/vyuha.git
   cd vyuha
   ```

2. **Set up a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install the package in editable mode**:
   ```bash
   pip install -e .
   ```

4. **Environment Configuration**:
   Create a `.env` file for your API keys:
   ```env
   GEMINI_API_KEY=your_key_here
   OPENAI_API_KEY=your_key_here
   ```

---

## 🛠️ Usage

VYUHA is designed for the terminal. Launch your formation with a build mission:

```bash
vyuha build "Develop a scalable microservices architecture for an e-commerce platform"
```

### Configuration
Modify `config.yaml` to change your AI provider or model settings:

```yaml
provider: "ollama"  # or "gemini", "openai"
model: "llama3.2:1b"
log_level: "INFO"
```

---

## 📜 Governance Model: The "A2A Path"

Every mission in VYUHA follows a governed path:
1. **Input**: `Sutra` captures the requirement.
2. **Drafting**: The lead agent (e.g., `Yantra`) publishes a `PLAN`.
3. **Audit**: Reviewer agents (e.g., `Kavacha`, `Dharma`) intercept and provide technical critiques.
4. **Refined Action**: The lead agent revises until `APPROVED`.
5. **Execution**: The verified artifact is published to the `orchestration/status`.

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 🔮 V2 Roadmap (The Evolution)

- **⚖️ The Jury (Multi-Model Voting)**: Cross-provider consensus for high-stakes code and security reviews.
- **📜 Akasha Records (Time-Travel)**: Step-based rollback for iterative architecture redesign.
- **🚦 Oversight Board (Human-in-the-Loop)**: Manual breakpoints for high-impact infrastructure provisioning.
- **📊 Formation Visualizer**: Real-time ASCII/Mermaid graph of the A2A bus in your terminal.

---

**VYUHA: Precision in Formation.**
