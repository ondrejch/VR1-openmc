# File to create a Streamlit app for the digital_twin_lab.py exercises. 
# If there are issues running this, please run the notebook version first to ensure all dependencies are installed and data files are in place.
# This app will have two main widgets: one for predicting k-effective and another for visualizing the reconstructed flux from the ROM. 
# The app will load the training data, train the models, and allow users to input parameters to see predictions in real-time.

import sys
from pathlib import Path

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from digital_twin_files.rom.digital_twin import (
    FEATURE_COLUMNS,
    MESH_SHAPE,
    default_test_csv,
    extract_keff,
    fit_digital_twin,
    load_parameter_frame,
)

N_MODES = 11

@st.cache_resource
def train_models():
    # Data folders are next to this file, whatever directory streamlit starts in.
    # Snapshots are assembled in training_set.csv case_id order, matching the feature rows.
    return fit_digital_twin(data_root=HERE, n_modes=N_MODES)

@st.cache_data
def prepare_test_data():
    test_csv = default_test_csv(HERE)
    test_df = load_parameter_frame(test_csv)
    X_test = test_df[list(FEATURE_COLUMNS)].to_numpy(dtype=float)
    y_test_keff = extract_keff(test_df, test_csv.parent)
    return X_test, y_test_keff

st.title('Digital Twin (Standalone widgets)')
st.write('This app recreates the k-eff and digital-twin widgets from the notebook.')

bundle = train_models()
keff_model, surrogate_model, U_r = bundle.keff_model, bundle.flux_model, bundle.pod_basis

st.sidebar.header('Input Parameters')
cr1 = st.sidebar.slider('CR 1 (cm)', 0.0, 84.7, 42.35, 0.1)
cr2 = st.sidebar.slider('CR 2 (cm)', 0.0, 84.7, 42.35, 0.1)
dummy_water = st.sidebar.slider('Dummy Water', 0.50, 1.00, 1.00, 0.01)
fa_water = st.sidebar.slider('FA Water', 0.50, 1.00, 1.00, 0.01)

st.header('K-effective widget')
input_state = np.array([[cr1, cr2, dummy_water, fa_water]])
pred_keff = keff_model.predict(input_state)[0]
st.write(f'Estimated k-effective: {pred_keff:.5f}')

# Show test-set performance
if st.checkbox('Show k-eff test performance'):
    X_test, y_test_keff = prepare_test_data()
    preds = keff_model.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test_keff, preds))
    mae = np.mean(np.abs(y_test_keff - preds))
    r2 = np.corrcoef(y_test_keff, preds)[0,1]**2
    st.write({'RMSE': float(rmse), 'MAE': float(mae), 'R2': float(r2)})
    fig, ax = plt.subplots()
    ax.scatter(y_test_keff, preds, alpha=0.7, color='purple')
    ax.plot([y_test_keff.min(), y_test_keff.max()],[y_test_keff.min(), y_test_keff.max()],'k--')
    ax.set_xlabel('True k-effective')
    ax.set_ylabel('Predicted k-effective')
    ax.set_title('K-effective: True vs Predicted')
    st.pyplot(fig)

st.header('Digital Twin: Predict flux from ROM')
z_index = st.slider('Z slice', 0, MESH_SHAPE[0] - 1, 35)

# Predict modal coefficients and reconstruct
pred_coeffs = surrogate_model.predict(input_state).T
reconstructed_flat = np.dot(U_r, pred_coeffs).flatten()
reconstructed_3d = reconstructed_flat.reshape(MESH_SHAPE)
therm_mid = reconstructed_3d[z_index, :, :, 0]

fig, ax = plt.subplots(figsize=(6,5))
ax.imshow(therm_mid, origin='lower', cmap='viridis')
ax.set_title(f'Reconstructed Thermal Flux (Z={z_index})')
st.pyplot(fig)

st.sidebar.markdown('---')
st.sidebar.write('Run this app with:')
st.sidebar.code('streamlit run digital_twin_files/rom/dt_lab_app.py')
