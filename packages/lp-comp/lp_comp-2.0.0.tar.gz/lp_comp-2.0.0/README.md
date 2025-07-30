# COMP (COMpromise Planning)

###### &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp; - by [Mykyta Kyselov (TheMegistone4Ever)](https://github.com/TheMegistone4Ever).

COMP is a Python library designed for mathematical modeling and coordinated planning in two-level
organizational-production systems.
It provides tools to find compromise solutions that balance the interests of a central coordinating body
(the "Center") and its subordinate elements (subsystems or production units).
The library implements various mathematical models (linear and preparatory work for combinatorial) and coordination
strategies based on the [research](https://doi.org/10.20998/2079-0023.2023.02.01)
of [Prof. O. A. Pavlov](https://orcid.org/0000-0002-6524-6410)
and [Bachelor M. Ye. Kyselov](https://orcid.org/0009-0005-3686-3419).
It also includes a graphical user interface (GUI) for easier interaction, data management, and visualization of results.

The package is available on PyPI: [`lp-comp`](https://pypi.org/project/lp-comp/).

## Table of Contents

1. [Getting Started](#1-getting-started)
    1. [Project Overview](#11-project-overview)
    2. [Features](#12-features)
2. [Core Concepts & Theory](#2-core-concepts--theory)
    1. [Two-Level Organizational-Production Systems](#21-two-level-organizational-production-systems)
    2. [Coordinated Planning Problem](#22-coordinated-planning-problem)
    3. [Coordination Strategies (Linear Models)](#23-coordination-strategies-linear-models)
        1. [Strict Priority (`CenterLinearFirst`)](#231-strict-priority-centerlinearfirst)
        2. [Guaranteed Concession (`CenterLinearSecond`)](#232-guaranteed-concession-centerlinearsecond)
        3. [Weighted Balance (`CenterLinearThird`)](#233-weighted-balance-centerlinearthird)
    4. [Coordination Strategies](#24-coordination-strategies)
    5. [Coordinated Planning with Shared Resources](#25-coordinated-planning-with-shared-resources)
    6. [Empirical Complexity for Parallelization](#26-empirical-complexity-for-parallelization)
3. [Prerequisites](#3-prerequisites)
    1. [System Requirements](#31-system-requirements)
    2. [Software Requirements](#32-software-requirements)
4. [Installation & Setup](#4-installation--setup)
    1. [Installing from PyPI (Recommended for Users)](#41-installing-from-pypi-recommended-for-users)
    2. [Setup for Development or Running from Source](#42-setup-for-development-or-running-from-source)
        1. [Clone Repository](#421-clone-repository)
        2. [Setup Virtual Environment (Recommended)](#422-setup-virtual-environment-recommended)
        3. [Install Dependencies](#423-install-dependencies)
5. [Running the Application](#5-running-the-application)
    1. [Command-Line Interface (CLI)](#51-command-line-interface-cli)
    2. [Graphical User Interface (GUI)](#52-graphical-user-interface-gui)
6. [Project Structure](#6-project-structure)
7. [Code Overview](#7-code-overview)
    1. [Core Library (`comp/`)](#71-core-library-comp)
    2. [Examples (`examples/`)](#72-examples-examples)
    3. [Tests (`tests/`)](#73-tests-tests)
8. [Visualization of Empirical Analysis](#8-visualization-of-empirical-analysis)
9. [Testing](#9-testing)
10. [Publishing to PyPI (For Maintainers)](#10-publishing-to-pypi-for-maintainers)
    1. [Clean Previous Builds](#101-clean-previous-builds)
    2. [Build the Package](#102-build-the-package)
    3. [Test with TestPyPI (Recommended)](#103-test-with-testpypi-recommended)
        1. [Upload to TestPyPI](#1031-upload-to-testpypi)
        2. [Install from TestPyPI and Verify](#1032-install-from-testpypi-and-verify)
    4. [Publish to PyPI (Main Release)](#104-publish-to-pypi-main-release)
    5. [Verify Installation from PyPI](#105-verify-installation-from-pypi)
11. [License](#11-license)

## 1. Getting Started

### 1.1 Project Overview

The COMP library provides a framework for addressing coordinated planning problems in hierarchical systems, specifically
two-level organizational-production systems (Дворівнева Організаційно-Виробнича Система - ДОВС).
In such systems, a central authority (Center) needs to coordinate the plans of several subordinate Elements,
each with its own local goals and constraints.
The core challenge is to find plans that are not only feasible but also represent a fair compromise between the
Center's global goals and the Elements' local interests.

This project implements:

* Data models to represent the structure and parameters of the Center and Elements.
* Solver modules for different types of Element-level optimization problems (currently linear, with a foundation for
  future combinatorial models).
* Three distinct coordination strategies for the Center to derive compromise plans.
* Parallel execution of subproblems using a heuristic scheduling algorithm based on empirical complexity estimates of
  the simplex method.
* A PyQt5-based GUI for data loading, configuration, execution of planning tasks, and visualization/saving of results.

### 1.2 Features

* **Mathematical Modeling:** Define two-level systems with a Center and multiple Elements.
* **Element Models:**
    * `ElementLinearFirst`: Standard linear programming model for an element.
    * `ElementLinearSecond`: Linear programming model with additional private decision variables for an element,
      allowing for more nuanced negotiation.
* **Coordination Strategies:**
    * `STRICT_PRIORITY`: Center prioritizes its goals first, then allows elements to optimize within those bounds.
    * `GUARANTEED_CONCESSION`: Center ensures elements achieve a certain percentage of their individual optimal
      performance.
    * `WEIGHTED_BALANCE`: Center uses a weighted sum approach to balance its goals with those of the elements,
      iterating to find a preferred solution.
* **Solvers:** Utilizes Google OR-Tools (specifically the GLOP solver) for underlying linear programming tasks.
* **Parallelization:** Employs a custom heuristic based on an empirical model of LP solver complexity to distribute
  tasks across multiple processor cores for faster computation.
* **Data Handling:**
    * JSON format for loading and saving system configurations and results.
    * Data generation capabilities for creating test scenarios.
* **Graphical User Interface (GUI):**
    * Load system data from JSON files.
    * Configure Center settings (coordination type, parallelization parameters).
    * Inspect Element data.
    * Run coordinated planning calculations.
    * View results in a user-friendly format.
    * Copy results to clipboard or save detailed results to a JSON file.
* **Extensibility:** Designed with a modular structure to facilitate the addition of new element models or coordination
  algorithms.

## 2. Core Concepts & Theory

### 2.1 Two-Level Organizational-Production Systems

The system architecture considered is a two-level hierarchy:

* **Center:** The central decision-making unit responsible for overall system performance and coordination.
* **Elements:** Subordinate units (e.g., departments, production lines) that have their own local goals, resources,
  and constraints.
  Elements can be of different types (e.g., `DECENTRALIZED`, `NEGOTIATED`).

### 2.2 Coordinated Planning Problem

The fundamental problem is to determine plans $\pi_l$ for each element $l$ such that the overall system
utility $\Phi(\pi)$ is maximized, while also considering the local interests $h_l(\pi_l)$ of each element.
This often involves navigating conflicting goals.
The general formulation seeks to:

$$
\max_{\pi} \Phi(\pi)
$$

Subject to: $\forall \pi_l \in Y_l, l = \overline{1,k}$ (where $Y_l$ is the set of feasible plans for element $l$)
And a compromise condition, which can be expressed, for example, as:

$$
h_l(\pi_l) \ge \max_{y_l \in Y_l} \{h_l(y_l) - \chi_l(\pi_l, y_l)\}
$$

where $\chi_l$ is a penalty function for deviating from an element-optimal plan $y_l$.

The COMP library focuses on constructive methods to find such compromise plans based on modifying objective functions
and constraints.

### 2.3 Coordination Strategies (Linear Models)

The library implements three primary strategies for linear models, based on
the [work](https://doi.org/10.20998/2079-0023.2023.02.01)
of [Prof. O. A. Pavlov](https://orcid.org/0000-0002-6524-6410)
and [Bachelor M. Ye. Kyselov](https://orcid.org/0009-0005-3686-3419):

#### 2.3.1 Strict Priority (`CenterLinearFirst`)

The Center first dictates terms based on its own goals.

1. For each element $e$, the Center determines the optimal value of its own functional:
   $f_{c\_opt\_e} = \max (d_e^T y_e)$
   Subject to element $e$'s constraints: $A^e y_e \le b_e$, $0 \le b_{ej}^1 \le y_{ej} \le b_{ej}^2$.
2. Then, element $e$ optimizes its local objective $c_e^T y_e$ under the additional constraint that the Center's
   goal for it must be met:

$$
\max (c_e^T y_e)
$$

Subject to element $e$'s original constraints and $d_e^T y_e = f_{c\_opt\_e}$.

#### 2.3.2 Guaranteed Concession (`CenterLinearSecond`)

The Center ensures that each element achieves at least a certain fraction of its own best possible performance.

1. For each element $e$, its individual optimal functional value $f_{el\_opt\_e}$ is determined:
    * For `ElementLinearFirst` type: $f_{el\_opt\_e} = \max (c_e^T y_e)$
    * For `ElementLinearSecond` type (with private variables $y_e^* $): $f_{el\_opt\_e} = \max (c_e^T y_e^* )$
      Subject to its own constraints.
2. The Center then optimizes its functional $d_e^T y_e$ for element $e$, subject to element $e$'s original
   constraints and the concession constraint:
    * For `ElementLinearFirst` type: $c_e^T y_e \ge f_{el\_opt\_e} \cdot (1 - \delta_e)$
    * For `ElementLinearSecond` type: $c_e^T y_e^* \ge f_{el\_opt\_e} \cdot (1 - \delta_e)$
      where $\delta_e$ is the concession parameter ($0 \le \delta_e \le 1$).

#### 2.3.3 Weighted Balance (`CenterLinearThird`)

The Center uses a weighted sum to combine its goals with the element's goals.

For each element $e$ and for each weight $\omega_e$ from a predefined set `element_data.w`:
The following combined goal is maximized:

* For `ElementLinearFirst` type:

$$
\max ((d_e^T + \omega_e \cdot c_e^T) y_e )
$$

* For `ElementLinearSecond` type:

$$
\max (d_e^T y_e + \omega_e \cdot c_e^T y_e^* )
$$

Subject to element $e$'s original constraints.

After solving for all $\omega_e$, the solution (plan and $\omega_e$ value) that maximizes the element's own
standalone quality functional ($c_e^T y_e$ or $c_e^T y_e^*$) is chosen for that element.

### 2.4 Coordination Strategies

While the current implementation focuses on linear models,
the [theoretical framework](https://doi.org/10.20998/2079-0023.2023.02.01) also encompasses combinatorial models for
elements, particularly for scheduling problems.
The $k$-th element's production model can be aggregated into a single device.
The set of possible production plans is interpreted as the set of all feasible job
schedules $\sigma_k \in \{\text{schedules}\}$.
Each job $j$ in the schedule $\sigma_k$ has a processing time $l_{kj}$.
The $j$-th job is interpreted as the $j$-th series of identical products, and $l_{kj}$ uniquely defines the size of
the $j$-th series.
Each $j$-th series is divided into two subsets.
The first subset of products belongs to the system as
a whole, the second to the $k$-th element.
That is, $l_{kj} = l_{kj}^S + l_{kj}^E$, where $l_{kj}^S = \alpha \cdot l_{kj}$
and $l_{kj}^E = (1-\alpha) \cdot l_{kj}$, with $0 \le \alpha \le 1$.
The proportion $\alpha$ is set by the center and accounts for the interest of the $k$-th element.
Jobs are processed on the device without interruption.
The order of job execution in any schedule $\sigma_k$ is constrained by technological limitations,
specified by a directed acyclic graph.
Let $t=0$ be the conventional start time of the device.

**Element's Objective (Combinatorial Model):**
The unconditional criterion for the operational efficiency of the $k$-th element's production is:

$$
\max_{\sigma_k} \sum_{j=1}^{n_k} \omega_j^{el}(T_k) (T_k - C_{kj}(\sigma_k)) \implies \min_{\sigma_k} \sum_{j=1}^{n_k} \omega_j^{el}(T_k) C_{kj}(\sigma_k)
$$

where:

* $\sigma_k$ is a feasible schedule for element $k$.
* $n_k$ is the number of jobs for an element $k$.
* $\omega_j^{el}(T_k) > 0$ are weight coefficients for the $j$-th job of element $k$.
* $T_k$ is a target completion time or a parameter influencing weights.
* $C_{kj}(\sigma_k)$ is the completion time of job $j$ for an element $k$ under schedule $\sigma_k$.
  This is an NP-hard combinatorial optimization problem,
  and its efficient solution (PSC-algorithm) is presented in [10]
  of the article.

**Center's Objective (for Combinatorial Elements):**
The criterion for the organizational-production system as a whole, when elements have combinatorial models, is:

$$
\sum_{k=1}^{m} \max_{\sigma_k} \sum_{j=1}^{n_k} \omega_j^{c}(T_k) (T_k - C_{kj}(\sigma_k)) \implies \sum_{k=1}^{m} \min_{\sigma_k} \sum_{j=1}^{n_k} \omega_j^{c}(T_k) C_{kj}(\sigma_k)
$$

where:

* $m$ is the total number of elements.
* $\omega_j^{c}(T_k) > 0$ are weight coefficients set by the Center for a job $j$ of element $k$.

The problem of finding a compromise solution for this model decomposes into $m$ independent subproblems.

**Compromise Criteria (Combinatorial Model - Theoretical):**

**First Compromise Criterion (Strict Priority by Center):**
The element $l$ must choose a schedule $\sigma_l^*$ such that:

$$
\sigma_l^* = \arg \min_{\sigma_l \in \{\sigma_l^c\}} \sum_{j=1}^{n_l} \omega_j^{el}(T_l) C_{lj}(\sigma_l)
$$

where $\{\sigma_l^c\}$ is the set of schedules that are optimal for the Center's goal for element $l$:

$$
\sigma_l^c = \left\lbrace \sigma_l \middle| \sum_{j=1}^{n_l} \omega_j^{c}(T_l) C_{lj}(\sigma_l) = f_{opt_l}^c \right\rbrace
$$

And $f_{opt_l}^c = \min_{\sigma_l} \sum_{j=1}^{n_l} \omega_j^{c}(T_l) C_{lj}(\sigma_l)$.
Finding $\sigma_l^*$ involves first finding $f_{opt_l}^c$ using a PSC algorithm, then solving a modified problem
with the functional:

$$
\min_{\sigma_l} \sum_{j=1}^{n_l} (a \cdot \omega_j^{c}(T_l) + \omega_j^{el}(T_l)) C_{lj}(\sigma_l)
$$

where $a > 0$ is a large enough number.

**Second Compromise Criterion (Guaranteed Concession for Element):**
The Center chooses a schedule for element $l$ by solving:

$$
\sigma_l^{**} = \arg \min_{\sigma_l} \sum_{j=1}^{n_l} \omega_j^{c}(T_l) C_{lj}(\sigma_l)
$$

Subject to:

$$
\sum_{j=1}^{n_l} \omega_j^{el}(T_l) C_{lj}(\sigma_l) \le f_{opt_l}^{el} + \Delta_l
$$

Where $f_{opt_l}^{el} = \min_{\sigma_l} \sum_{j=1}^{n_l} \omega_j^{el}(T_l) C_{lj}(\sigma_l)$ (element's best
performance), and $\Delta_l \ge 0$ is the concession.
This criterion can be implemented via a recurrent procedure modifying weighting coefficients $a_1 \ge 0, a_2 > 0$
in the combined goal:

$$
\min_{\sigma_l} \sum_{j=1}^{n_l} [a_1 \omega_j^{el}(T_l) + a_2 \omega_j^{c}(T_l)] C_{lj}(\sigma_l)
$$

to manage the trade-off between $\sum \omega_j^{c}C_{lj} - f_{opt_l}^c$
and $\sum \omega_j^{el}C_{lj} - f_{opt_l}^{el}$.

### 2.5 Coordinated Planning with Shared Resources

This section outlines the compromise solution for a two-level system where elements have linear models and share a
common resource constraint.
The components of the non-negative vectors $b_l$ (resource availability for element $l$)
become variables, subject to the overall constraint $\sum_{l=1}^m b_l \le \mathbf{B}$, where $\mathbf{B}$ is the
total resource vector available to the Center.

**Compromise Solution:**
The Center seeks to find plans $y_l$ and resource allocations $b_l$ for each element $l = \overline{1,m}$ by
solving:

$$
(y_1^* , ..., y_m^* , b_1^* , ..., b_m^* ) = \arg \max_{y_l, b_l} \sum_{l=1}^m d_l^T y_l
$$

Subject to:

* Element constraints: $A^l y_l \le b_l$ for each element $l$.
* Shared resource constraint: $\sum_{l=1}^m b_l \le \mathbf{B}$.
* Non-negativity and bounds: $b_l \ge 0$, $0 \le b_{lj}^1 \le y_{lj} \le b_{lj}^2$ (original bounds on decision
  variables).
* Performance guarantee for each element: $c_l^T y_l \ge f_l$ for each element $l$, where $f_l$ are target
  performance levels set by the Center.

This formulation extends the basic linear models by introducing interdependent resource allocation decided by the Center
to maximize its global goal while satisfying individual element performance targets.

### 2.6 Empirical Complexity for Parallelization

To efficiently parallelize the solving of multiple element subproblems, the COMP library uses a heuristic scheduling
algorithm implemented in the `get_order` function.
This algorithm distributes the LP tasks (element subproblems)
among available processor threads aiming to minimize the makespan (total time to complete all tasks).
The effectiveness of such a heuristic depends on accurately estimating the duration of each subproblem.

The duration of each LP task is estimated using an empirical formula derived from statistical analysis of the standard
simplex method's performance:

$$
\text{Task Duration} \approx |0.63 \cdot m^{2.96} \cdot n^{0.02} \cdot (\ln n)^{1.62} + 4.04 \cdot m^{-4.11} \cdot n^{2.92}|
$$

Where $m$ is the number of constraints and $n$ is the number of variables in the LP problem for a specific element.
The absolute value ensures a positive duration estimate.

**Derivation of the Empirical Formula:**

This formula was developed through dedicated research to model the computational complexity of the simplex method:

1. **Problem:** The core challenge was to find an analytical expression for the number of arithmetic operations (as a
   proxy for execution time) based on the LP problem's dimensions ($m$ constraints, $n$ variables).
2. **Models Explored:** Various models were analyzed, including those based on known theoretical estimates (e.g.,
   interpretations of Borgwardt's model, smoothed analysis, Adler-Megiddo) and proposed generalized linear and mixed
   interpretations.
3. **Best Fit Model:** A mixed generalized model of the form $am^b n^c (\ln n)^d + km^g n^h$ was found to provide the
   best fit to empirical data.
4. **Experimental Validation:** The model and its coefficients were validated through extensive simulation experiments.
   This involved:
    * Five series of independent simulations using two distinct datasets (one for parameter estimation, one for
      verification).
    * Varying $m$ (constraints) and $n$ (variables) over a wide range (e.g., 200 to 2000).
    * Generating 5 independent LP problems for each $(m, n)$ combination, resulting in a large dataset (e.g., 13,690 LP
      tasks per series).
    * Recording the exact number of arithmetic operations for each solved LP task.
5. **Resulting Coefficients:** The statistical analysis yielded the
   coefficients $a \approx 0.63, b \approx 2.96, c \approx 0.02,
   d \approx 1.62, k \approx 4.04, g \approx -4.11, h \approx 2.92$, leading to the formula above.

**The `get_order` Heuristic using Estimated Durations:**

The `get_order` function uses these estimated durations within the `get_multi_device_order_A0` scheduling heuristic
as follows:

1. **Operation Representation:** Each element's LP subproblem, characterized by its size $(m, n)$, is treated as an
   `Operation` object.
   The `empiric(size_tuple)` function calculates its estimated duration using the formula.
2. **Initial Assignment (LPT - Longest Processing Time):**
    * The `get_multi_device_heuristic_order` function performs an initial assignment.
    * All `Operation` objects (LP tasks) are sorted by their estimated durations in descending order.
    * Each operation, starting with the longest, is assigned to the device (representing a thread) that currently has
      the minimum accumulated total processing time.
3. **Iterative Refinement (Load Balancing):**
    * After the initial LPT assignment, `get_multi_device_order_A0` attempts to further balance the load across devices.
    * It calculates an `average_deadline` (total estimated work divided by the number of threads).
    * The heuristic then iteratively identifies the most "lagged" device (whose total workload significantly exceeds the
      average deadline) and "advanced" devices (whose total workload is significantly below the average).
    * It attempts to perform task swaps between the most lagged device and the advanced devices using various
      permutation strategies:
        * `make_permutation_1_1`: Swap one task from lagged with one from advanced.
        * `make_permutation_1_2`: Swap one task from lagged with two from advanced.
        * `make_permutation_2_1`: Swap two tasks from lagged with one from advanced.
        * `make_permutation_2_2`: Swap two tasks from lagged with two from advanced.
    * A swap is made if it reduces the lagged device's end time sufficiently without causing it to finish too early
      relative to the average deadline.
    * This iterative refinement continues until the end times of all devices are balanced within a specified tolerance,
      or no further beneficial permutations can be found.
4. **Output Schedule:** The `get_order` function returns a list of lists, where each inner list contains the original
   indices of the tasks assigned to a specific thread.

`ParallelExecutor` uses this generated schedule to distribute the actual execution of the element subproblems across the
available processor cores.

## 3. Prerequisites

### 3.1 System Requirements

* **Operating System:** Windows (tested), macOS, Linux (Python is cross-platform, GUI tested on Windows).
* **CPU:** Modern multi-core processor recommended for parallel features.
* **RAM:** 4GB+, 8GB or more recommended for larger problems.

### 3.2 Software Requirements

* **Python:** Version 3.12 or newer (developed with 3.12).
* **Pip:** For installing Python packages.
* Dependencies as listed in `requirements.txt` (or installed automatically via pip from PyPI):
    * `numpy~=2.2.5`
    * `PyQt5~=5.15.11`
    * `tabulate~=0.9.0`
    * `ortools~=9.12.4544`

## 4. Installation & Setup

### 4.1. Installing from PyPI (Recommended for Users)

The `lp-comp` package is available on PyPI and TestPyPI. Users can install it using pip:

**From PyPI (stable releases):**

```bash
pip install lp-comp
```

This will install the latest stable version of the library and its dependencies.

* Project on PyPI: [https://pypi.org/project/lp-comp/](https://pypi.org/project/lp-comp/)

  <img src="images/pypi_uploaded.png" alt="lp-comp on PyPI" width="800"/>

**From TestPyPI (for testing pre-releases):**

```bash
pip install -i https://test.pypi.org/simple/ lp-comp
```

* Project on TestPyPI: [https://test.pypi.org/project/lp-comp/](https://test.pypi.org/project/lp-comp/)

  <img src="images/pypi_test_uploaded.png" alt="lp-comp on TestPyPI" width="800"/>

After installation, User can verify it by checking User’s installed packages (e.g., `pip list` or in User’s IDE).

  <img src="images/pypi_packages_installed.png" alt="lp-comp installed in PyCharm" width="800"/>

### 4.2. Setup for Development or Running from Source

If a User wants to contribute to the project, run examples directly from the source code, or modify the library, follow
these steps:

#### 4.2.1. Clone Repository

```bash
git clone https://github.com/TheMegistone4Ever/COMP.git
cd COMP
```

#### 4.2.2. Setup Virtual Environment (Recommended)

It is highly recommended to use a virtual environment to manage project dependencies.

```bash
# Create a virtual environment (e.g., named .venv)
python -m venv .venv

# Activate the virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
```

#### 4.2.3. Install Dependencies

Install the required Python packages using pip:

```bash
pip install -r requirements.txt
```

For development, including building and publishing the package, User might also want to install:

```bash
pip install build twine
```

## 5. Running the Application

The COMP library can be used programmatically or via its GUI.

### 5.1 Command-Line Interface (CLI)

The `examples/` directory contains scripts to demonstrate core functionalities.

* **Data Generation & Solver Execution:**
  The `examples/main.py` script demonstrates how to:
    1. Generate sample `CenterData` and save it to `examples/center_data_generated.json` if it does not exist.
    2. Load `CenterData` from the generated JSON file.
    3. Configure the Center with a specific coordination strategy (e.g., `WEIGHTED_BALANCE`).
    4. Instantiate and run the `CenterSolver`.
    5. Print results to the console and save detailed results to `examples/center_results_output.json`.

  To run this example (from the cloned repository, within the activated virtual environment):
  ```bash
  python examples/main.py
  ```
  *Console Output Example (partial):*

  <img src="images/ui_tab_results.png" alt="Console output from main.py showing partial results table" width="800"/>
  *(Note: This image shows GUI results tab, but the console output format is similar in structure.)*

  If User have installed `lp-comp` via pip into an environment, User can test its core functionality by adapting
  `examples/main.py` to run in that environment.
  The images in the [Publishing to PyPI](#10-publishing-to-pypi-for-maintainers) section show this kind of verification.

### 5.2 Graphical User Interface (GUI)

The GUI provides an interactive way to work with the COMP library.

* **Launching the GUI:**
    * **From source code (e.g., within the cloned repository and activated virtual environment):**
      ```bash
      python examples/run_gui.py
      ```
    * **After installing the package via pip:**
      If an entry point script (`comp-gui`) was configured during installation
      ```bash
      comp-gui 
      ```
      Alternatively, User can usually run the GUI module directly:
      ```bash
      python -m comp.gui_launcher
      ```

* **Data Loading Tab:**
  Allows users to load system data from a `.json` file.
  *Initial View:*

  <img src="images/ui_tab_load_data.png" alt="GUI - Data Loading Tab (Initial)" width="800"/>

  *File Dialog for Loading Data:*

  <img src="images/ui_dialog_load_data.png" alt="GUI - File Dialog for Loading Data" width="800"/>

  *Data Loaded Confirmation:*

  <img src="images/ui_data_loaded.png" alt="GUI - Data Loaded Confirmation" width="800"/>

* **Configuration & Run Tab:**
  After loading data, this tab allows users to:
    * Select Elements for display.
    * Configure Center parameters (number of threads, parallelization threshold, coordination type).
    * View data for selected elements or the entire center.
    * Run the coordinated planning calculation.

  <img src="images/ui_tab_setup.png" alt="GUI - Configuration & Run Tab" width="800"/>

* **Result Tab:**
  Displays the results of the calculation.
    * Textual summary of the solution, including chosen parameters and objective values;
    * Button to "Copy to Clipboard";
    * Button to "Save to .json file";

  *Results Display:*

  <img src="images/ui_tab_results.png" alt="GUI - Results Tab" width="800"/>

  *Copy to Clipboard Action:*

  <img src="images/ui_copied_to_buffer_msg.png" alt="GUI - Copied to Clipboard Message" width="800"/>

  <img src="images/ui_copied_to_buffer.png" alt="GUI - Copy to Clipboard button" width="800"/>

  *Save Results Action:*

  <img src="images/ui_dialog_save_results.png" alt="GUI - File Dialog for Saving Results" width="800"/>

  <img src="images/ui_results_saved_msg.png" alt="GUI - Results Saved Message" width="800"/>

  <img src="images/ui_results_saved.png" alt="GUI - Results Saved Confirmation in status bar" width="800"/>

## 6. Project Structure

```
COMP/
├── .gitattributes
├── .gitignore
├── LICENSE.md
├── MANIFEST.in
├── README.md
├── pyproject.toml
├── requirements.txt
├── setup.cfg
├── setup.py
├── version.txt
├── comp/
│   ├── __init__.py
│   ├── _version.py
│   ├── gui_launcher.py
│   ├── io/
│   │   ├── __init__.py
│   │   └── json_io.py
│   ├── media/
│   │   ├── __init__.py
│   │   └── COMP.ico
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── center.py
│   │   └── element.py
│   ├── parallelization/
│   │   ├── __init__.py
│   │   ├── heuristic.py
│   │   ├── parallel_executor.py
│   │   └── core/
│   │       ├── __init__.py
│   │       ├── device.py
│   │       ├── empiric.py
│   │       └── operation.py
│   ├── solvers/
│   │   ├── __init__.py
│   │   ├── factories.py
│   │   ├── center/
│   │   │   ├── __init__.py
│   │   │   ├── linear/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── first.py
│   │   │   │   ├── second.py
│   │   │   │   └── third.py
│   │   │   └── linked/
│   │   │       ├── __init__.py
│   │   │       └── first.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── center.py
│   │   │   └── element.py
│   │   └── element/
│   │       ├── __init__.py
│   │       └── linear/
│   │           ├── __init__.py
│   │           ├── first.py
│   │           └── second.py
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── config_run_tab.py
│   │   ├── data_load_tab.py
│   │   ├── main_window.py
│   │   ├── results_tab.py
│   │   ├── styles.py
│   │   └── worker.py
│   └── utils/
│       ├── __init__.py
│       ├── assertions.py
│       ├── helpers.py
│       └── json_base_serializer.py
├── examples/
│   ├── __init__.py
│   ├── center_data_generated.json
│   ├── center_results_output.json
│   ├── main.py
│   ├── run_gui.py
│   └── data/
│       ├── __init__.py
│       └── generator.py
├── images/
│   ├── General_Mixed_W1_linear_2d.png
│   ├── General_Mixed_W1_linear_3d.png
│   ├── General_Mixed_W1_log_2d.png
│   ├── General_Mixed_W1_log_3d.png
│   ├── General_Mixed_W2_linear_2d.png
│   ├── General_Mixed_W2_linear_3d.png
│   ├── General_Mixed_W2_log_2d.png
│   ├── General_Mixed_W2_log_3d.png
│   ├── pypi_build_success.png
│   ├── pypi_building.png
│   ├── pypi_clearing.png
│   ├── pypi_env_check.png
│   ├── pypi_packages_installed.png
│   ├── pypi_sol_check.png
│   ├── pypi_test_env_check.png
│   ├── pypi_test_sol_check.png
│   ├── pypi_test_upload.png
│   ├── pypi_test_uploaded.png
│   ├── pypi_upload.png
│   ├── pypi_uploaded.png
│   ├── ui_copied_to_buffer.png
│   ├── ui_copied_to_buffer_msg.png
│   ├── ui_data_loaded.png
│   ├── ui_dialog_load_data.png
│   ├── ui_dialog_save_results.png
│   ├── ui_results_saved.png
│   ├── ui_results_saved_msg.png
│   ├── ui_tab_load_data.png
│   ├── ui_tab_results.png
│   ├── ui_tab_setup.png
│   └── unit_tests_results.png
└── tests/
    ├── __init__.py
    └── test_core.py
```

## 7. Code Overview

### 7.1 Core Library (`comp/`)

* **`comp/_version.py`**: Defines the package version (`__version__`).
* **`comp/__init__.py`**: Makes `__version__` available at the package level (`from comp import __version__`).
* **`comp/gui_launcher.py`**: Contains the `main_app_entry` function for launching the PyQt5 GUI.
  This is the target for `python -m comp.gui_launcher`.
* **`comp.models`**: Contains dataclasses defining the structure of the system:
    * `BaseConfig`, `BaseData`: Base classes for configuration and data.
    * `CenterConfig`, `CenterData`, `CenterType`: Define the Center's properties, data, and coordination strategies.
    * `ElementConfig`, `ElementData`, `ElementType`, `ElementSolution`: Define Element properties, data, types, and
      solution structure.
* **`comp.io`**: Handles data input/output.
    * `json_io.py`: Functions to load `CenterData` from JSON files, with custom parsing for enums, numpy arrays, and
      nested dataclasses.
* **`comp.solvers`**: Core logic for optimization.
    * `core/`: Abstract base classes and common solver logic.
        * `BaseSolver`: Abstract base for all solvers.
        * `ElementSolver`: Base for element-level solvers, integrating with OR-Tools.
        * `CenterSolver`: Base for center-level solvers, managing element solvers and parallel execution.
    * `element/linear/`: Concrete implementations of element solvers.
        * `first.py` (`ElementLinearFirst`): Implements the first linear model for an element.
        * `second.py` (`ElementLinearSecond`): Implements the second linear model with private decision variables.
    * `center/linear/`: Concrete implementations of center coordination strategies.
        * `first.py` (`CenterLinearFirst`): Implements the "Strict Priority" strategy.
        * `second.py` (`CenterLinearSecond`): Implements the "Guaranteed Concession" strategy.
        * `third.py` (`CenterLinearThird`): Implements the "Weighted Balance" strategy.
    * `center/linked/`: Concrete implementations of linked center coordination strategies.
        * `first.py` (`CenterLinkedFirst`): Implements the first linked strategy.
    * `factories.py`: Factory functions (`new_element_solver`, `new_center_solver`) to create appropriate solver
      instances based on configuration.
* **`comp.parallelization`**: Logic for parallel execution of element subproblems.
    * `core/empiric.py`: Implements the empirical formula to estimate LP solving time.
    * `core/device.py`, `core/operation.py`: Data structures for the scheduling heuristic.
    * `heuristic.py`: Implements the `get_order` function, a multi-device scheduling heuristic (LPT + iterative
      refinement) to determine task distribution among threads.
    * `parallel_executor.py`: `ParallelExecutor` class using `concurrent.futures.ProcessPoolExecutor` to run tasks in
      parallel according to the order from the heuristic.
* **`comp.utils`**: Utility functions.
    * `assertions.py`: Custom assertion functions for input validation.
    * `helpers.py`: String formatting (`stringify`, `tab_out`), LP sum utilities.
    * `json_base_serializer.py`: Custom JSON serializer for numpy arrays, enums, etc., and a `save_to_json` utility.
* **`comp.ui`**: PyQt5 based Graphical User Interface.
    * `main_window.py` (`MainWindow`): The main application window, hosting tabs.
    * `data_load_tab.py` (`DataLoadTab`): Tab for loading data from JSON.
    * `config_run_tab.py` (`ConfigRunTab`): Tab for configuring center parameters and running calculations.
    * `results_tab.py` (`ResultsTab`): Tab for displaying results and providing copy/save functionality.
    * `worker.py` (`SolverWorker`): QObject for running solver calculations in a background thread to keep the GUI
      responsive.
    * `styles.py`: Stylesheet for the GUI.
    * `media/COMP.ico`: Application icon.

### 7.2 Examples (`examples/`)

* `main.py`: Demonstrates CLI usage: data generation, loading, solver instantiation, running coordination, and saving
  results.
* `run_gui.py`: Entry point to launch the PyQt5 GUI application when running from source.
  It typically imports and calls `main_app_entry` from `comp.gui_launcher`.
* `data/generator.py` (`DataGenerator`): Class for generating random `CenterData` for testing and examples.
* `center_data_generated.json`: Example data file that can be generated by `main.py`.
* `center_results_output.json`: Example results file that can be generated by `main.py`.

### 7.3 Tests (`tests/`)

* `test_core.py`: Contains unit tests for various components including assertions, helpers, JSON serialization, models,
  data generator, parallelization, and solver factories/types.

## 8. Visualization of Empirical Analysis

The plots below visualize data related to the empirical complexity analysis of the simplex method, which informs the
parallelization heuristically used in COMP.
`W1` and `W2` refer to different datasets used during the empirical study.

*3D Plot - General Mixed Model (Linear Scale) - W1:*

<img src="images/General_Mixed_W1_linear_3d.png" alt="3D Plot - General Mixed (Linear Scale) - W1" width="800"/>

*3D Plot - General Mixed Model (Logarithmic Scale) - W1:*

<img src="images/General_Mixed_W1_log_3d.png" alt="3D Plot - General Mixed (Log Scale) - W1" width="800"/>

*3D Plot - General Mixed Model (Linear Scale) - W2:*

<img src="images/General_Mixed_W2_linear_3d.png" alt="3D Plot - General Mixed (Linear Scale) - W2" width="800"/>

*3D Plot - General Mixed Model (Logarithmic Scale) - W2:*

<img src="images/General_Mixed_W2_log_3d.png" alt="3D Plot - General Mixed (Log Scale) - W2" width="800"/>

*2D Plots - Operations vs. m (Linear Scale) - W1:*

<img src="images/General_Mixed_W1_linear_2d.png" alt="2D Plots - General Mixed - Operations vs. m (Linear Scale) - W1" width="800"/>

*2D Plots - Operations vs. m (Logarithmic Scale) - W1:*

<img src="images/General_Mixed_W1_log_2d.png" alt="2D Plots - General Mixed - Operations vs. m (Log Scale) - W1" width="800"/>

*2D Plots - Operations vs. m (Linear Scale) - W2:*

<img src="images/General_Mixed_W2_linear_2d.png" alt="2D Plots - General Mixed - Operations vs. m (Linear Scale) - W2" width="800"/>

*2D Plots - Operations vs. m (Logarithmic Scale) - W2:*

<img src="images/General_Mixed_W2_log_2d.png" alt="2D Plots - General Mixed - Operations vs. m (Log Scale) - W2" width="800"/>

## 9. Testing

Unit tests are implemented using Python's `unittest` framework and can be found in the `tests/` directory.
They cover core utilities, data models, data generation, parallelization logic, and solver factories.

To run tests (from the root of the cloned repository, with the virtual environment activated):

```bash
python -m unittest tests.test_core
```

*Example Test Output:*

<img src="images/unit_tests_results.png" alt="Unit Test Results" width="800"/>

## 10. Publishing to PyPI (For Maintainers)

This section outlines the steps to build and publish the `lp-comp` package to PyPI and TestPyPI.
Ensure User have `build` and `twine` installed (`pip install build twine`).

### 10.1. Clean Previous Builds

Before creating new distribution files, it is good practice to remove any old ones from the `dist/`, `build/`, and
`*.egg-info` directories.

*(Example PowerShell commands as shown in User’s screenshot, adapt as needed for User’s OS/shell)*

```powershell
if (Test-Path -Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path -Path "dist") { Remove-Item -Recurse -Force "dist" }
if (Test-Path -Path "lp_comp.egg-info") { Remove-Item -Recurse -Force "lp_comp.egg-info" } # Adjust egg-info name if needed
```

<img src="images/pypi_clearing.png" alt="Clearing build artifacts" width="800"/>

### 10.2. Build the Package

Use the `build` package to create the source distribution (`.tar.gz`) and wheel (`.whl`).
This process typically uses `pyproject.toml` for build configuration.

```bash
python -m build
```

<img src="images/pypi_building.png" alt="Building the package" width="800"/>

This will create the distribution files in the `dist/` directory.
<img src="images/pypi_build_success.png" alt="Successful package build" width="800"/>

### 10.3. Test with TestPyPI (Recommended)

#### 10.3.1. Upload to TestPyPI

Upload the distributions to TestPyPI to ensure everything works correctly before publishing to the main PyPI.

```bash
twine upload --repository testpypi dist/*
```

User will be prompted for User’s TestPyPI username and password (or API token).
<img src="images/pypi_test_upload.png" alt="Uploading to TestPyPI" width="800"/>

#### 10.3.2. Install from TestPyPI and Verify

Create a fresh virtual environment, install the package from TestPyPI, and run some checks.

```bash
# In a new, clean virtual environment
pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple lp-comp
pip list # Check if lp-comp and dependencies are installed
```

<img src="images/pypi_test_env_check.png" alt="Installing and checking from TestPyPI" width="800"/>

Run an example script (e.g., `examples/main.py`, ensuring it uses the installed package) to verify functionality.
User might need to adapt paths or copy necessary example files (`examples/main.py`,
`examples/center_data_generated.json`) to User’s test location if running outside the source tree.
<img src="images/pypi_test_sol_check.png" alt="Running example with TestPyPI version" width="800"/>

### 10.4. Publish to PyPI (Main Release)

Once a User is confident that the package is working correctly, upload it to the official Python Package Index (PyPI).

```bash
twine upload dist/*
```

User will be prompted for User’s PyPI username and password (or API token).
<img src="images/pypi_upload.png" alt="Uploading to PyPI" width="800"/>

### 10.5. Verify Installation from PyPI

As a final check, install the package from the main PyPI in a clean environment and verify.

```bash
# In a new, clean virtual environment
pip install lp-comp
pip list # Check if lp-comp and dependencies are installed
```

<img src="images/pypi_env_check.png" alt="Installing and checking from PyPI" width="800"/>

User can also run an example to confirm, similar to the TestPyPI verification.
<img src="images/pypi_sol_check.png" alt="Running example with PyPI version" width="800"/>

## 11. License

The project is licensed under the [CC BY-NC 4.0 License](LICENSE.md).