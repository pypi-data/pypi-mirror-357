# Les Audits-Affaires LLM Evaluation Harness

A comprehensive evaluation framework for assessing Large Language Models on the **Les Audits-Affaires** French legal benchmark dataset.

## 🎯 Overview

This evaluation harness provides a systematic way to evaluate LLMs on French legal tasks using the `legmlai/les-audits-affaires` dataset. The framework uses Azure OpenAI GPT-4o as an expert evaluator to score model responses across five key legal categories:

- **Action Requise** (Required Action)
- **Délai Légal** (Legal Deadline) 
- **Documents Obligatoires** (Required Documents)
- **Impact Financier** (Financial Impact)
- **Conséquences Non-Conformité** (Non-Compliance Consequences)

## 🚀 Features

- **Asynchronous Evaluation**: Efficient batch processing with controlled concurrency
- **Comprehensive Scoring**: 5-category evaluation with detailed justifications
- **Robust Error Handling**: Graceful handling of API failures and retries
- **Multiple Output Formats**: JSON, CSV, Excel, and Markdown reports
- **Progress Tracking**: Real-time progress bars and intermediate result saving
- **Analysis Tools**: Built-in visualization and statistical analysis
- **Flexible Configuration**: Easy customization of evaluation parameters

## 📋 Prerequisites

- Python 3.8+
- Azure OpenAI API access
- Access to your model endpoint (e.g., via ngrok tunnel)

## 🛠️ Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd les-audits-affaires-eval-harness
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**:
Create a `.env` file based on `env_example.txt`:
```bash
cp env_example.txt .env
# Edit .env with your actual API keys and endpoints
```

## ⚙️ Configuration

### Environment Variables

Copy and modify the environment template:

```bash
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-endpoint.cognitiveservices.azure.com/
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_API_VERSION=2024-12-01-preview
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o

# Model to Evaluate Configuration
MODEL_ENDPOINT=https://your-model-endpoint.ngrok-free.app/generate
MODEL_NAME=your-model-name

# Evaluation Configuration
MAX_SAMPLES=1000
BATCH_SIZE=5
TEMPERATURE=0.1
MAX_TOKENS=2048
CONCURRENT_REQUESTS=3
```

### Configuration Files

Key configuration options in `config.py`:

- `SYSTEM_PROMPT`: The system prompt for your model
- `LLM_EVALUATION_PROMPT`: The evaluation prompt template
- `DATASET_NAME`: HuggingFace dataset identifier
- Batch processing and concurrency settings

## 🚀 Usage

### Quick Start

1. **Test your setup**:
```bash
python run_evaluation.py --test-single
```

2. **Run a small evaluation**:
```bash
python run_evaluation.py --max-samples 10
```

3. **Full evaluation**:
```bash
python run_evaluation.py
```

### Command Line Options

```bash
python run_evaluation.py [OPTIONS]

Options:
  --max-samples INT        Maximum samples to evaluate (default: 1000)
  --batch-size INT         Batch size (default: 5)
  --concurrent-requests INT Concurrent requests (default: 3)
  --model-endpoint URL     Model endpoint URL
  --test-single           Test with single sample first
  --dry-run              Load dataset without evaluation
  --help                 Show help message
```

### Programmatic Usage

```python
from evaluator import LesAuditsAffairesEvaluator
import asyncio

async def main():
    evaluator = LesAuditsAffairesEvaluator()
    results = await evaluator.run_evaluation(max_samples=100)
    print(f"Final score: {results['global_score']['mean']:.2f}")

asyncio.run(main())
```

## 📊 Analysis and Visualization

### Generate Analysis Reports

```bash
# Generate comprehensive report
python utils.py --report

# Create visualizations
python utils.py --plots

# Export to Excel
python utils.py --excel

# All analyses
python utils.py --report --plots --excel
```

### Programmatic Analysis

```python
from utils import load_evaluation_results, generate_analysis_report

# Load results
results = load_evaluation_results('results/evaluation_results.json')

# Generate report
report = generate_analysis_report(results)

# Find challenging samples
challenging = find_challenging_samples(results, n_samples=10)
```

## 📁 Output Structure

The evaluation generates several output files in the `results/` directory:

```
results/
├── evaluation_results.json      # Complete results with all data
├── evaluation_summary.json      # Summary statistics only
├── evaluation_summary.csv       # CSV format for analysis
├── detailed_results.jsonl       # Line-by-line detailed results
├── analysis_report.md           # Comprehensive analysis report
├── evaluation_results.xlsx      # Excel with multiple sheets
├── score_distributions.png      # Score distribution plots
├── correlation_heatmap.png      # Category correlation heatmap
└── evaluation.log              # Detailed execution logs
```

## 🔧 Model Integration

### Your Model Endpoint Requirements

Your model endpoint should accept POST requests with this format:

```json
{
  "prompt": "formatted_prompt_string",
  "stream": false,
  "max_new_tokens": 2048,
  "temperature": 0.1
}
```

And return responses in one of these formats:

```json
{"text": "model_response"}
{"content": "model_response"}  
{"message": "model_response"}
{"response": "model_response"}
```

### Chat Template Format

The evaluation uses this chat template format:

```
<|im_start|>system
{SYSTEM_PROMPT}<|im_end|>
<|im_start|>user
{question}

APRÈS ton analyse complète avec les tokens de raisonnement, termine par le format demandé.<|im_end|>
<|im_start|>assistant
<|begin_of_reasoning|>
<|begin_of_thought_planner|>
```

## 📈 Evaluation Metrics

### Scoring System

Each sample receives scores (0-100) across 5 categories:
- **Action Requise**: Required legal actions
- **Délai Légal**: Legal deadlines and timeframes  
- **Documents Obligatoires**: Required documentation
- **Impact Financier**: Financial implications
- **Conséquences Non-Conformité**: Non-compliance consequences

### Global Score
The global score is the arithmetic mean of the 5 category scores.

### Evaluation Criteria
For each category, the Azure OpenAI evaluator assesses:
- **Exactitude juridique**: Legal accuracy
- **Concordance**: Agreement with ground truth
- **Clarté**: Clarity of response
- **Justification**: Quality of legal reasoning

## 🔍 Troubleshooting

### Common Issues

1. **Connection Errors**:
   - Verify your model endpoint is accessible
   - Check ngrok tunnel is active
   - Ensure proper network connectivity

2. **Azure OpenAI Errors**:
   - Verify API key and endpoint
   - Check quota and rate limits
   - Ensure deployment name is correct

3. **Dataset Loading Issues**:
   - Check internet connection
   - Verify HuggingFace dataset access
   - Try loading manually with `datasets` library

4. **Memory Issues**:
   - Reduce `BATCH_SIZE` 
   - Lower `MAX_SAMPLES`
   - Decrease `CONCURRENT_REQUESTS`

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📚 API Reference

### Main Classes

#### `LesAuditsAffairesEvaluator`
Main evaluation class with methods:
- `load_dataset(max_samples)`: Load evaluation dataset
- `run_evaluation(max_samples)`: Execute full evaluation
- `compute_final_metrics(results)`: Calculate final statistics

#### `ModelClient` 
Client for your model with methods:
- `generate_response(question)`: Get model response
- `_format_prompt(question)`: Format input prompt

#### `EvaluatorClient`
Azure OpenAI evaluator client:
- `evaluate_response(question, response, ground_truth)`: Score response

### Utility Functions

#### `utils.py`
- `load_evaluation_results()`: Load saved results
- `create_score_distribution_plot()`: Generate score plots
- `generate_analysis_report()`: Create comprehensive report
- `export_results_to_excel()`: Export to Excel format

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Les Audits-Affaires Dataset**: `legmlai/les-audits-affaires`
- **Azure OpenAI**: For evaluation services
- **HuggingFace**: For dataset hosting and tools

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Search existing issues
3. Create a new issue with detailed information

---

**Happy Evaluating! 🚀** 