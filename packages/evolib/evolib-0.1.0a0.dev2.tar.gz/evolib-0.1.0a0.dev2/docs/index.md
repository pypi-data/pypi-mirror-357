# EvoLib Documentation

**EvoLib** is a modular and extensible framework for implementing and analyzing evolutionary algorithms in Python. It supports classical strategies such as (μ, λ) and (μ + λ) Evolution Strategies, Genetic Algorithms, and Neuroevolution – with a strong focus on clarity, modularity, and didactic value.

---

## 🚀 Features

- Individual- and population-level adaptive mutation strategies
- Modular selection methods: tournament, rank-based, roulette, SUS, truncation, Boltzmann
- Multiple crossover operators: heuristic, arithmetic, differential, SBX, etc.
- Configurable via YAML: clean separation of individual and population setups
- Benchmark functions: Sphere, Rosenbrock, Rastrigin, Ackley, Griewank, etc.
- Built-in loss functions (MSE, MAE, Huber, Cross-Entropy)
- Plotting utilities for fitness trends, mutation tracking, diversity
- Designed for extensibility: clean core/operator/utils split
- Sphinx-based documentation with Markdown support

---

## 📂 Project Structure

```
evolib/
├── core/           # Population, Individual
├── operators/      # Crossover, mutation, selection, replacement
├── utils/          # Losses, plotting, config loaders, benchmarks
├── globals/        # Enums and constants
├── config/         # YAML config files
├── examples/       # Educational and benchmark scripts
└── api.py          # Central access point (auto-generated)
```

---

## 📦 Installation

```bash
git clone https://github.com/your-username/evolib.git
cd evolib

# Optional: create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install EvoLib
pip install -e .
```

Requirements: Python 3.9+ and packages in `requirements.txt`.

---

## 🧪 Quickstart Example

```python
from evolib import Pop, Indiv, evolve_mu_lambda, mse_loss, sphere

def fitness(indiv: Indiv) -> None:
    indiv.fitness = mse_loss(0.0, sphere(indiv.para))

pop = Pop(config_path="config/population.yaml")
for _ in range(pop.max_generations):
    evolve_mu_lambda(pop, fitness)
    print(pop)
```

---

## 📚 Examples

Explore the `examples/` directory for hands-on experiments:

- `1_Getting_Started/`: Basic usage, mutation, fitness
- `2_Evolution/`: Step-by-step evolution strategies
- `3_History_Tracking_Plotting/`: Plotting and comparison
- `4_Adaptiv_Mutation/`: Decay and adaptive mutation
- `5_Multi_Objective/`: For future extension
- `6_Neural_Control/`, `7_Flappy_Bird/`, `8_Lunar_Lander/`: Neuroevolution applications

```{toctree}
:maxdepth: 2
:caption: API Modules

api_population
api_individual
api_mutation
api_selection
api_benchmarks
api_crossover
api_replacement
api_strategy
api_reproduction
api_plotting
api_loss_functions
api_config_loader
api_copy_indiv
api_history_logger
api_registry
api_math_utils
api_config_validator
api_enums
api_numeric
api_utils
```

---

## 🪪 License

This project is licensed under the [MIT License](../LICENSE.md).

---

## 🙏 Acknowledgments

Inspired by classical evolutionary computation techniques and designed for clarity, modularity, and pedagogical use. Contributions welcome!

