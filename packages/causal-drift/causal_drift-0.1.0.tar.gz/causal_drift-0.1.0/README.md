# deepCausal

**deepCausal** is a Python library for causal feature ranking and selection based on residual treatment effect estimation.  
It uses double machine learning and residualization techniques to estimate the causal impact (ATE) of each feature on a continuous or categorical outcome.

## 🔍 Key Features

- Supports both **continuous** and **categorical** outcomes
- Uses **residual-on-residual regression** for causal interpretation
- Identifies **confounders** automatically
- Ranks features by **causal strength**, not just correlation

## 🚀 Usage 

from deepCausal import DeepCausal
import pandas as pd
import numpy as np

df = pd.DataFrame({
    'X1': np.random.randn(100),
    'X2': np.random.rand(100),
    'X3': np.random.randn(100),
    'Y': np.random.randn(100)
})

X = df[['X1', 'X2', 'X3']]
y = df['Y']

model = DeepCausal()
model.fit(X, y, outcome_type='continuous')

print(model.get_feature_ate())

📄 License
This project is licensed under the MIT License. 

🧪 Disclaimer
This method is experimental and currently under research evaluation. Feedback and pull requests are welcome!
